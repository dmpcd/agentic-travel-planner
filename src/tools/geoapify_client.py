"""
Geoapify Places API Client
Client for Geoapify Places API (activities and points of interest).
Free tier: 3000 API calls/day (no credit card required)

Get your API key at: https://myprojects.geoapify.com/
"""
import httpx
from typing import Optional, Dict, Any, List

from src.tools.api_config import get_api_config


class GeoapifyClient:
    """
    Client for Geoapify Places API.
    
    Provides access to:
    - Points of Interest (POIs)
    - Tourist attractions
    - Restaurants, museums, landmarks, etc.
    """
    
    BASE_URL = "https://api.geoapify.com/v2"
    GEOCODE_URL = "https://api.geoapify.com/v1/geocode"
    
    def __init__(self):
        self.config = get_api_config()
    
    async def _make_request(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make request to Geoapify API"""
        if params is None:
            params = {}
        
        params["apiKey"] = self.config.geoapify_api_key
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, params=params)
            
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Geoapify API error ({response.status_code}): {response.text}")
    
    async def geocode_city(self, city_name: str) -> Optional[Dict[str, Any]]:
        """
        Get coordinates and details for a city.
        
        Args:
            city_name: Name of the city
            
        Returns:
            Dict with lat, lon, formatted address, etc.
        """
        try:
            result = await self._make_request(
                f"{self.GEOCODE_URL}/search",
                params={
                    "text": city_name,
                    "type": "city",
                    "limit": 1
                }
            )
            
            features = result.get("features", [])
            if features:
                props = features[0].get("properties", {})
                coords = features[0].get("geometry", {}).get("coordinates", [0, 0])
                return {
                    "lat": coords[1],
                    "lon": coords[0],
                    "name": props.get("city", props.get("name", city_name)),
                    "country": props.get("country", ""),
                    "place_id": props.get("place_id", "")
                }
            return None
        except Exception as e:
            print(f"⚠️ Geocoding failed: {e}")
            return None
    
    async def search_places(
        self,
        lat: float,
        lon: float,
        categories: Optional[List[str]] = None,
        radius: int = 10000,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Search for places/POIs near coordinates.
        
        Args:
            lat: Latitude
            lon: Longitude
            categories: Filter by category codes
                Options: tourism, tourism.sights, tourism.attraction,
                        catering, catering.restaurant, entertainment,
                        entertainment.museum, natural, religion,
                        commercial.shopping_mall, leisure, sport
            radius: Search radius in meters
            limit: Maximum number of results
            
        Returns:
            List of places with details
        """
        params = {
            "filter": f"circle:{lon},{lat},{radius}",
            "limit": limit,
            "lang": "en"
        }
        
        if categories:
            params["categories"] = ",".join(categories)
        else:
            # Default: tourist attractions, sights, entertainment
            params["categories"] = "tourism.sights,tourism.attraction,entertainment,catering.restaurant,natural"
        
        try:
            result = await self._make_request(f"{self.BASE_URL}/places", params=params)
            
            features = result.get("features", [])
            places = []
            
            for feature in features:
                props = feature.get("properties", {})
                coords = feature.get("geometry", {}).get("coordinates", [0, 0])
                
                if props.get("name"):  # Only include named places
                    places.append({
                        "id": props.get("place_id", ""),
                        "name": props.get("name", ""),
                        "categories": props.get("categories", []),
                        "lat": coords[1],
                        "lon": coords[0],
                        "address": props.get("formatted", ""),
                        "city": props.get("city", ""),
                        "country": props.get("country", ""),
                        "distance": props.get("distance", 0),
                        "opening_hours": props.get("opening_hours", ""),
                        "website": props.get("website", ""),
                        "description": props.get("description", "")
                    })
            
            return places
        except Exception as e:
            print(f"⚠️ Place search failed: {e}")
            return []
    
    async def search_activities(
        self,
        city_name: str,
        interests: List[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        High-level method to search for activities in a city.
        
        Args:
            city_name: Name of the city
            interests: List of user interests to filter by
            limit: Maximum number of results
            
        Returns:
            List of activities with details
        """
        # Get city coordinates
        coords = await self.geocode_city(city_name)
        if not coords:
            print(f"⚠️ Could not find coordinates for {city_name}")
            return []
        
        # Map interests to Geoapify categories
        categories = self._map_interests_to_categories(interests or [])
        
        # Search for places
        places = await self.search_places(
            lat=coords["lat"],
            lon=coords["lon"],
            categories=categories,
            radius=15000,  # 15km radius
            limit=limit
        )
        
        return places
    
    def _map_interests_to_categories(self, interests: List[str]) -> List[str]:
        """
        Map user interests to valid Geoapify category codes.
        
        Valid Geoapify categories include:
        - beach, beach.beach_resort
        - natural.water, natural.water.sea, natural.water.reef
        - sport.dive_centre, sport.swimming_pool
        - commercial.outdoor_and_sport.water_sports, commercial.outdoor_and_sport.diving
        - rental.boat
        - entertainment.water_park
        - catering.restaurant.seafood
        """
        interest_mapping = {
            # Water activities - using VALID Geoapify categories
            "beach": ["beach", "beach.beach_resort", "natural.water.sea", "sport.swimming_pool"],
            "beaches": ["beach", "beach.beach_resort", "natural.water.sea", "sport.swimming_pool"],
            "surfing": ["beach", "beach.beach_resort", "commercial.outdoor_and_sport.water_sports", "rental.boat"],
            "surf": ["beach", "beach.beach_resort", "commercial.outdoor_and_sport.water_sports"],
            "diving": ["sport.dive_centre", "commercial.outdoor_and_sport.diving", "natural.water.reef", "rental.boat"],
            "snorkeling": ["sport.dive_centre", "commercial.outdoor_and_sport.diving", "natural.water.reef", "beach"],
            "corals": ["natural.water.reef", "sport.dive_centre", "commercial.outdoor_and_sport.diving", "beach"],
            "coral": ["natural.water.reef", "sport.dive_centre", "commercial.outdoor_and_sport.diving", "beach"],
            "reef": ["natural.water.reef", "sport.dive_centre", "commercial.outdoor_and_sport.diving"],
            "ocean": ["natural.water.sea", "beach", "beach.beach_resort", "rental.boat"],
            "water sports": ["commercial.outdoor_and_sport.water_sports", "sport.swimming_pool", "rental.boat", "beach"],
            "swimming": ["sport.swimming_pool", "beach", "beach.beach_resort", "entertainment.water_park"],
            "kayaking": ["commercial.outdoor_and_sport.water_sports", "rental.boat", "natural.water"],
            "fishing": ["commercial.outdoor_and_sport.fishing", "rental.boat", "natural.water"],
            "boating": ["rental.boat", "natural.water.sea", "commercial.outdoor_and_sport.water_sports"],
            "scuba": ["sport.dive_centre", "commercial.outdoor_and_sport.diving", "rental.boat"],
            
            # Nature & outdoors
            "nature": ["natural", "leisure.park", "natural.water", "natural.forest"],
            "wildlife": ["natural", "entertainment.zoo", "entertainment.aquarium", "leisure.park"],
            "hiking": ["natural", "leisure.park", "tourism.sights", "natural.forest", "natural.mountain"],
            "mountain": ["natural.mountain", "natural.mountain.peak", "natural.mountain.cliff", "tourism.sights"],
            
            # Food & dining
            "food": ["catering.restaurant", "catering.cafe", "catering.fast_food"],
            "seafood": ["catering.restaurant.seafood", "catering.restaurant.fish", "catering.restaurant"],
            "dining": ["catering.restaurant", "catering.cafe"],
            
            # Culture & history
            "culture": ["entertainment.museum", "entertainment.culture", "tourism.attraction"],
            "history": ["tourism.sights.memorial", "tourism.sights.archaeological_site", "tourism.sights.ruines"],
            "art": ["entertainment.museum", "entertainment.culture.gallery", "entertainment.culture.arts_centre"],
            "religion": ["religion", "tourism.sights.place_of_worship"],
            "architecture": ["tourism.sights", "tourism.sights.castle", "tourism.sights.tower"],
            
            # Entertainment & leisure
            "shopping": ["commercial.shopping_mall", "commercial.marketplace"],
            "nightlife": ["catering.bar", "catering.pub", "adult.nightclub"],
            "adventure": ["sport", "leisure", "activity", "commercial.outdoor_and_sport"],
            "entertainment": ["entertainment", "entertainment.cinema", "entertainment.theme_park"],
            "sightseeing": ["tourism.sights", "tourism.attraction", "tourism.sights.tower"],
            "relaxation": ["leisure.park", "leisure.spa", "beach", "beach.beach_resort"],
            "spa": ["leisure.spa", "leisure.spa.sauna", "leisure.spa.public_bath"],
        }
        
        if not interests:
            return ["tourism.sights", "tourism.attraction", "entertainment", "catering.restaurant"]
        
        categories = set()
        for interest in interests:
            interest_lower = interest.lower().strip()
            mapped = interest_mapping.get(interest_lower, [])
            if mapped:
                categories.update(mapped)
            else:
                # Try partial matching for compound interests
                for key, values in interest_mapping.items():
                    if key in interest_lower or interest_lower in key:
                        categories.update(values)
                        break
                else:
                    # Default fallback for unknown interests
                    categories.add("tourism.sights")
        
        return list(categories) if categories else ["tourism.sights", "tourism.attraction"]


# Test if run directly
if __name__ == "__main__":
    import asyncio
    
    async def test():
        config = get_api_config()
        
        if not config.has_geoapify_key:
            print("⚠️ Geoapify API key not configured")
            print("Get your free key at: https://myprojects.geoapify.com/")
            return
        
        client = GeoapifyClient()
        
        print("\n" + "=" * 60)
        print("TESTING GEOAPIFY API CLIENT")
        print("=" * 60)
        
        # Test geocoding
        print("\n📍 Getting coordinates for Tokyo...")
        coords = await client.geocode_city("Tokyo")
        if coords:
            print(f"   Found: {coords['name']}, {coords['country']}")
            print(f"   Coordinates: ({coords['lat']}, {coords['lon']})")
        
        # Test place search
        print("\n🎯 Searching for activities in Tokyo...")
        activities = await client.search_activities(
            city_name="Tokyo",
            interests=["culture", "food"],
            limit=5
        )
        
        for activity in activities:
            print(f"\n   📍 {activity.get('name', 'Unknown')}")
            print(f"      Categories: {', '.join(activity.get('categories', [])[:3])}")
            print(f"      Address: {activity.get('address', 'N/A')}")
        
        print(f"\n✅ Found {len(activities)} activities!")
    
    asyncio.run(test())
