"""
Activity Search Tool
Searches for activities using Geoapify API with mock data fallback.
"""
from typing import List, Optional
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from src.models.activity import Activity, ActivityCategory
from src.tools.api_config import get_api_config
from src.tools.geoapify_client import GeoapifyClient


class ActivitySearchTool:
    """
    Tool for searching activities and attractions.
    
    Uses Geoapify API when API key is available,
    falls back to mock data otherwise.
    """
    
    def __init__(self, use_mock: Optional[bool] = None):
        """
        Initialize the activity search tool.
        
        Args:
            use_mock: Force mock mode. If None, auto-detect based on API config.
        """
        self.config = get_api_config()
        self._use_mock = use_mock
        self._geoapify_client = None
    
    @property
    def use_mock(self) -> bool:
        """Determine whether to use mock data"""
        if self._use_mock is not None:
            return self._use_mock
        return self.config.should_use_mock_activities
    
    @property
    def geoapify_client(self) -> GeoapifyClient:
        """Lazy-load Geoapify client"""
        if self._geoapify_client is None:
            self._geoapify_client = GeoapifyClient()
        return self._geoapify_client
    
    async def search(
        self,
        destination: str,
        interests: List[str] = [],
        max_price: Optional[float] = None
    ) -> List[Activity]:
        """
        Search for activities matching criteria.
        
        Args:
            destination: City name
            interests: List of user interests to filter by
            max_price: Maximum price (note: Geoapify doesn't provide pricing)
        
        Returns:
            List of Activity objects sorted by rating
        """
        
        if self.use_mock:
            print("🎯 Using mock activity data")
            activities = self._generate_mock_activities(destination)
        else:
            print("🎯 Searching Geoapify API for real activities...")
            activities = await self._search_real_activities(destination, interests)
        
        # Filter by interests if provided (for mock data)
        if interests and self.use_mock:
            activities = [a for a in activities 
                         if any(interest.lower() in a.category.value or 
                               interest.lower() in [t.lower() for t in a.tags]
                               for interest in interests)]
        
        # Filter by price (note: API doesn't provide pricing, so mostly for mock)
        if max_price:
            activities = [a for a in activities if a.price <= max_price]
        
        # Sort by rating
        activities.sort(key=lambda a: a.rating, reverse=True)
        
        return activities
    
    async def _search_real_activities(
        self,
        destination: str,
        interests: List[str]
    ) -> List[Activity]:
        """Search activities using Geoapify API"""
        try:
            places = await self.geoapify_client.search_activities(
                city_name=destination,
                interests=interests,
                limit=15
            )
            
            if not places:
                print("⚠️  No activities found from API, falling back to mock data")
                return self._generate_mock_activities(destination)
            
            return self._parse_geoapify_activities(places, destination)
            
        except Exception as e:
            print(f"⚠️  Geoapify API error: {e}")
            print("   Falling back to mock activity data")
            return self._generate_mock_activities(destination)
    
    def _parse_geoapify_activities(
        self, 
        places: List[dict], 
        destination: str
    ) -> List[Activity]:
        """Parse Geoapify API response into Activity models"""
        activities = []
        
        for idx, place in enumerate(places):
            try:
                # Map Geoapify categories to our categories
                categories = place.get("categories", [])
                category = self._map_categories_to_activity_category(categories)
                
                # Estimate rating (Geoapify doesn't provide ratings, use distance as proxy)
                # Closer to center = higher rating assumption
                distance = place.get("distance", 5000)
                rating = max(3.5, min(5.0, 5.0 - (distance / 10000)))
                
                # Estimate duration based on category
                duration = self._estimate_duration(category)
                
                # Create activity
                activity = Activity(
                    id=place.get("id", f"ACT{idx+1:03d}")[:20],
                    name=place.get("name", "Unknown Place"),
                    description=place.get("description", "") or f"A popular {category.value} attraction in {destination}",
                    category=category,
                    location=place.get("address", "") or destination,
                    duration_hours=duration,
                    price=0,  # Geoapify doesn't provide pricing
                    rating=round(rating, 1),
                    best_time=self._suggest_best_time(category),
                    tags=self._extract_tags_from_categories(categories)
                )
                activities.append(activity)
                
            except Exception as e:
                print(f"⚠️  Error parsing activity: {e}")
                continue
        
        return activities
    
    def _map_categories_to_activity_category(self, categories: List[str]) -> ActivityCategory:
        """Map Geoapify categories to our ActivityCategory"""
        categories_str = ",".join(categories).lower()
        
        if any(k in categories_str for k in ["museum", "theatre", "cultural", "historic"]):
            return ActivityCategory.CULTURE
        elif any(k in categories_str for k in ["natural", "beach", "park", "leisure.park"]):
            return ActivityCategory.NATURE
        elif any(k in categories_str for k in ["catering", "restaurant", "cafe", "food"]):
            return ActivityCategory.FOOD
        elif any(k in categories_str for k in ["shop", "mall", "commercial"]):
            return ActivityCategory.SHOPPING
        elif any(k in categories_str for k in ["amusement", "entertainment", "cinema"]):
            return ActivityCategory.ENTERTAINMENT
        elif any(k in categories_str for k in ["tourism.sights", "tower", "monument", "attraction"]):
            return ActivityCategory.SIGHTSEEING
        elif any(k in categories_str for k in ["sport", "activity"]):
            return ActivityCategory.ADVENTURE
        elif any(k in categories_str for k in ["religion", "church", "temple", "worship"]):
            return ActivityCategory.CULTURE
        else:
            return ActivityCategory.SIGHTSEEING
    
    def _extract_tags_from_categories(self, categories: List[str]) -> List[str]:
        """Extract relevant tags from Geoapify categories"""
        tags = []
        
        tag_mapping = {
            "tourism": "must-see",
            "historic": "historic",
            "museum": "museum",
            "natural": "nature",
            "beach": "beach",
            "park": "park",
            "cultural": "cultural",
            "religion": "spiritual",
            "catering": "food",
            "commercial": "shopping",
            "entertainment": "entertainment",
        }
        
        for cat in categories:
            cat_lower = cat.lower()
            for key, tag in tag_mapping.items():
                if key in cat_lower and tag not in tags:
                    tags.append(tag)
        
        if not tags:
            tags = ["sightseeing"]
        
        return tags[:5]
    
    def _estimate_duration(self, category: ActivityCategory) -> float:
        """Estimate visit duration based on category"""
        duration_map = {
            ActivityCategory.CULTURE: 2.0,
            ActivityCategory.NATURE: 3.0,
            ActivityCategory.FOOD: 1.5,
            ActivityCategory.SHOPPING: 2.0,
            ActivityCategory.ENTERTAINMENT: 2.5,
            ActivityCategory.SIGHTSEEING: 1.5,
            ActivityCategory.ADVENTURE: 3.0,
            ActivityCategory.RELAXATION: 2.0,
        }
        return duration_map.get(category, 2.0)
    
    def _suggest_best_time(self, category: ActivityCategory) -> str:
        """Suggest best time to visit based on category"""
        time_map = {
            ActivityCategory.CULTURE: "morning",
            ActivityCategory.NATURE: "morning",
            ActivityCategory.FOOD: "afternoon",
            ActivityCategory.SHOPPING: "afternoon",
            ActivityCategory.ENTERTAINMENT: "evening",
            ActivityCategory.SIGHTSEEING: "morning",
            ActivityCategory.ADVENTURE: "morning",
            ActivityCategory.RELAXATION: "afternoon",
        }
        return time_map.get(category, "afternoon")
    
    def _generate_mock_activities(self, destination: str) -> List[Activity]:
        """Generate mock activity data"""
        return [
            Activity(
                id="ACT001",
                name="Visit Senso-ji Temple",
                description="Tokyo's oldest and most significant Buddhist temple",
                category=ActivityCategory.CULTURE,
                location="Asakusa, Tokyo",
                duration_hours=2.0,
                price=0,
                rating=4.7,
                best_time="morning",
                tags=["historic", "spiritual", "photography", "free"]
            ),
            Activity(
                id="ACT002",
                name="Tokyo Skytree Observation Deck",
                description="Breathtaking 360° views from Japan's tallest structure",
                category=ActivityCategory.SIGHTSEEING,
                location="Sumida, Tokyo",
                duration_hours=2.5,
                price=28.00,
                rating=4.6,
                best_time="evening",
                tags=["views", "photography", "landmark"]
            ),
            Activity(
                id="ACT003",
                name="Tsukiji Outer Market Food Tour",
                description="Explore Tokyo's famous fish market and try fresh sushi",
                category=ActivityCategory.FOOD,
                location="Tsukiji, Tokyo",
                duration_hours=3.0,
                price=85.00,
                rating=4.8,
                best_time="morning",
                tags=["food", "sushi", "local experience"]
            ),
            Activity(
                id="ACT004",
                name="teamLab Borderless Digital Art Museum",
                description="Immersive digital art experience with interactive exhibits",
                category=ActivityCategory.ENTERTAINMENT,
                location="Odaiba, Tokyo",
                duration_hours=2.5,
                price=32.00,
                rating=4.9,
                best_time="afternoon",
                tags=["art", "technology", "interactive", "instagram-worthy"]
            ),
            Activity(
                id="ACT005",
                name="Meiji Shrine",
                description="Serene Shinto shrine surrounded by forest in the heart of Tokyo",
                category=ActivityCategory.CULTURE,
                location="Shibuya, Tokyo",
                duration_hours=1.5,
                price=0,
                rating=4.6,
                best_time="morning",
                tags=["spiritual", "nature", "peaceful", "free"]
            ),
            Activity(
                id="ACT006",
                name="Robot Restaurant Show",
                description="Vibrant, futuristic dinner show with robots and neon lights",
                category=ActivityCategory.ENTERTAINMENT,
                location="Shinjuku, Tokyo",
                duration_hours=1.5,
                price=65.00,
                rating=4.2,
                best_time="evening",
                tags=["entertainment", "unique", "technology", "dinner show"]
            ),
            Activity(
                id="ACT007",
                name="Shibuya Crossing Experience",
                description="Cross the world's busiest intersection and explore the area",
                category=ActivityCategory.SIGHTSEEING,
                location="Shibuya, Tokyo",
                duration_hours=1.0,
                price=0,
                rating=4.5,
                best_time="evening",
                tags=["iconic", "photography", "shopping", "free"]
            ),
            Activity(
                id="ACT008",
                name="Akihabara Electronics District",
                description="Explore Tokyo's famous electronics and anime district",
                category=ActivityCategory.SHOPPING,
                location="Akihabara, Tokyo",
                duration_hours=3.0,
                price=0,
                rating=4.4,
                best_time="afternoon",
                tags=["technology", "anime", "shopping", "free"]
            ),
            Activity(
                id="ACT009",
                name="Traditional Tea Ceremony",
                description="Experience authentic Japanese tea ceremony with kimono rental",
                category=ActivityCategory.CULTURE,
                location="Asakusa, Tokyo",
                duration_hours=1.5,
                price=55.00,
                rating=4.7,
                best_time="afternoon",
                tags=["cultural", "traditional", "tea", "kimono"]
            ),
            Activity(
                id="ACT010",
                name="Ueno Park & Museums",
                description="Explore Tokyo's largest park with multiple museums",
                category=ActivityCategory.CULTURE,
                location="Ueno, Tokyo",
                duration_hours=4.0,
                price=10.00,
                rating=4.5,
                best_time="morning",
                tags=["park", "museums", "nature", "art"]
            ),
        ]


if __name__ == "__main__":
    import asyncio
    
    async def test():
        print("=" * 60)
        print("TESTING ACTIVITY SEARCH TOOL")
        print("=" * 60)
        
        config = get_api_config()
        print(f"\nAPI Mode: {'MOCK' if config.should_use_mock_activities else 'REAL (Geoapify)'}")
        
        tool = ActivitySearchTool()
        
        print("\n--- Test 1: All Activities ---")
        activities = await tool.search("Tokyo")
        print(f"Found {len(activities)} activities")
        
        for activity in activities[:5]:  # Show top 5
            print(f"\n{activity.name}")
            print(f"  Category: {activity.category.value}")
            print(f"  Price: {activity.formatted_price}")
            print(f"  Rating: {activity.rating}⭐")
        
        print("\n--- Test 2: Filter by Interests (food, culture) ---")
        filtered = await tool.search("Tokyo", interests=["food", "culture"])
        print(f"Found {len(filtered)} activities matching interests")
        
        print("\nActivity Search Tool works!")
    
    asyncio.run(test())
