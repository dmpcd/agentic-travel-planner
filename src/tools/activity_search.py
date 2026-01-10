"""
Activity Search Tool
Searches for activities and attractions.
Currently uses mock data.
"""
from typing import List, Optional
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from src.models.activity import Activity, ActivityCategory


class ActivitySearchTool:
    """Tool for searching activities"""
    
    def __init__(self, use_mock: bool = True):
        self.use_mock = use_mock
    
    async def search(
        self,
        destination: str,
        interests: List[str] = [],
        max_price: Optional[float] = None
    ) -> List[Activity]:
        """Search for activities"""
        
        activities = self._generate_mock_activities(destination)
        
        # Filter by interests if provided
        if interests:
            activities = [a for a in activities 
                         if any(interest.lower() in a.category.value or 
                               interest.lower() in [t.lower() for t in a.tags]
                               for interest in interests)]
        
        # Filter by price
        if max_price:
            activities = [a for a in activities if a.price <= max_price]
        
        # Sort by rating
        activities.sort(key=lambda a: a.rating, reverse=True)
        
        return activities
    
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
        
        tool = ActivitySearchTool()
        
        print("\n--- Test 1: All Activities ---")
        activities = await tool.search("Tokyo")
        print(f"Found {len(activities)} activities")
        
        print("\n--- Test 2: Filter by Interests (food, technology) ---")
        filtered = await tool.search("Tokyo", interests=["food", "technology"])
        for activity in filtered[:3]:
            print(f"\n{activity.name}")
            print(f"  Category: {activity.category.value}")
            print(f"  Price: {activity.formatted_price}")
            print(f"  Rating: {activity.rating}⭐")
        
        print("\nActivity Search Tool works!")
    
    asyncio.run(test())
