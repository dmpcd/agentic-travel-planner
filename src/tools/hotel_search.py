"""
Hotel Search Tool
Searches for hotels based on criteria.
Currently uses mock data.
"""
from typing import List, Optional
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from src.models.hotel import Hotel


class HotelSearchTool:
    """Tool for searching hotels"""
    
    def __init__(self, use_mock: bool = True):
        self.use_mock = use_mock
    
    async def search(
        self,
        destination: str,
        check_in: str,
        check_out: str,
        guests: int = 2,
        max_price_per_night: Optional[float] = None,
        min_rating: float = 7.0
    ) -> List[Hotel]:
        """Search for hotels"""
        
        hotels = self._generate_mock_hotels(destination)
        
        # Apply filters
        if max_price_per_night:
            hotels = [h for h in hotels if h.price_per_night <= max_price_per_night]
        
        hotels = [h for h in hotels if h.user_rating >= min_rating]
        
        # Sort by rating
        hotels.sort(key=lambda h: h.user_rating, reverse=True)
        
        return hotels
    
    def _generate_mock_hotels(self, destination: str) -> List[Hotel]:
        """Generate mock hotel data"""
        return [
            Hotel(
                id="HTL001",
                name="Park Hyatt Tokyo",
                address="3-7-1-2 Nishi Shinjuku, Shinjuku-ku",
                star_rating=5.0,
                user_rating=9.3,
                price_per_night=450.00,
                amenities=["WiFi", "Pool", "Spa", "Restaurant", "Gym", "Bar"],
                distance_to_center_km=2.5
            ),
            Hotel(
                id="HTL002",
                name="The Peninsula Tokyo",
                address="1-8-1 Yurakucho, Chiyoda-ku",
                star_rating=5.0,
                user_rating=9.2,
                price_per_night=480.00,
                amenities=["WiFi", "Spa", "Restaurant", "Gym", "Concierge"],
                distance_to_center_km=0.8
            ),
            Hotel(
                id="HTL003",
                name="Hotel Gracery Shinjuku",
                address="1-19-1 Kabukicho, Shinjuku-ku",
                star_rating=4.0,
                user_rating=8.5,
                price_per_night=180.00,
                amenities=["WiFi", "Restaurant", "24hr Reception"],
                distance_to_center_km=1.2
            ),
            Hotel(
                id="HTL004",
                name="Mitsui Garden Hotel Ginza",
                address="8-13-1 Ginza, Chuo-ku",
                star_rating=4.0,
                user_rating=8.7,
                price_per_night=220.00,
                amenities=["WiFi", "Restaurant", "Laundry", "Hot Spring Bath"],
                distance_to_center_km=1.5
            ),
            Hotel(
                id="HTL005",
                name="Capsule Hotel Anshin Oyado",
                address="2-15-3 Kabukicho, Shinjuku-ku",
                star_rating=3.0,
                user_rating=7.8,
                price_per_night=45.00,
                amenities=["WiFi", "Lockers", "Shared Bath"],
                distance_to_center_km=1.8
            ),
        ]


if __name__ == "__main__":
    import asyncio
    
    async def test():
        print("=" * 60)
        print("TESTING HOTEL SEARCH TOOL")
        print("=" * 60)
        
        tool = HotelSearchTool()
        hotels = await tool.search("Tokyo", "2026-04-15", "2026-04-20", guests=2)
        
        for hotel in hotels:
            print(f"\n{hotel.name}")
            print(f"  Rating: {hotel.user_rating}/10 ({hotel.rating_category})")
            print(f"  Price: {hotel.formatted_price}")
            print(f"  Stars: {hotel.star_rating}⭐")
        
        print("\nHotel Search Tool works!")
    
    asyncio.run(test())
