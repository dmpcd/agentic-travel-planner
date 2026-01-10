"""
Hotel Agent
AI agent responsible for searching and recommending hotels.
"""
from typing import Any, Dict, List
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from src.agents.base_agent import BaseAgent
from src.models.hotel import Hotel
from src.tools.hotel_search import HotelSearchTool


class HotelAgent(BaseAgent):
    """Agent responsible for finding and recommending hotels"""
    
    def __init__(self):
        super().__init__(
            name="Hotel Agent",
            description="Searches and recommends the best hotels"
        )
        self.hotel_tool = HotelSearchTool()
        self.add_tool(self.hotel_tool)
    
    @property
    def system_prompt(self) -> str:
        return """You are a hotel recommendation expert. Analyze hotel options considering:

1. Location (closer to city center is better)
2. Rating (user reviews are important)
3. Value for money (balance price with quality)
4. Amenities (what's included)
5. Star rating (hotel class)

Recommend the BEST hotel with clear reasoning. Consider:
- Budget travelers prefer good value
- Luxury travelers want premium experience
- Location is crucial for tourism

Keep response concise (3-5 sentences). State your recommendation and key reasons."""

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Search and recommend hotels"""
        
        # Search for hotels
        hotels = await self.hotel_tool.search(
            destination=input_data["destination"],
            check_in=input_data["check_in"],
            check_out=input_data["check_out"],
            guests=input_data.get("guests", 2),
            max_price_per_night=input_data.get("max_price_per_night")
        )
        
        # AI analysis
        analysis_prompt = f"""Analyze these hotel options in {input_data["destination"]}:

{self._format_hotels(hotels)}

USER REQUIREMENTS:
- Guests: {input_data.get('guests', 2)}
- Budget: ${input_data.get('max_price_per_night', 'flexible')} per night
- Preferences: {input_data.get('preferences', 'none specified')}

Recommend the BEST hotel. Be specific and concise."""
        
        reasoning = await self.think(analysis_prompt)
        
        return {
            "hotels": [h.model_dump() for h in hotels],
            "recommended": hotels[0].model_dump() if hotels else None,
            "reasoning": reasoning,
            "total_found": len(hotels)
        }
    
    def _format_hotels(self, hotels: List[Hotel]) -> str:
        """Format hotels for AI analysis"""
        if not hotels:
            return "No hotels found"
        
        result = []
        for i, hotel in enumerate(hotels[:5], 1):
            result.append(
                f"Hotel {i}: {hotel.name}\n"
                f"  - Rating: {hotel.user_rating}/10 ({hotel.rating_category})\n"
                f"  - Price: {hotel.formatted_price}\n"
                f"  - Stars: {hotel.star_rating}⭐\n"
                f"  - Distance: {hotel.distance_to_center_km}km from center\n"
                f"  - Amenities: {', '.join(hotel.amenities[:4])}"
            )
        return "\n\n".join(result)


if __name__ == "__main__":
    import asyncio
    
    async def test():
        print("=" * 70)
        print("TESTING HOTEL AGENT WITH AI")
        print("=" * 70)
        
        agent = HotelAgent()
        
        result = await agent.execute({
            "destination": "Tokyo",
            "check_in": "2026-04-15",
            "check_out": "2026-04-20",
            "guests": 2,
            "max_price_per_night": 250,
            "preferences": "good location, close to attractions"
        })
        
        print(f"\nFound {result['total_found']} hotels")
        print("\n" + "-" * 70)
        print("AI RECOMMENDATION:")
        print("-" * 70)
        print(result['reasoning'])
        
        if result['recommended']:
            hotel = result['recommended']
            print("\n" + "-" * 70)
            print("RECOMMENDED HOTEL:")
            print("-" * 70)
            print(f"Name: {hotel['name']}")
            print(f"Price: ${hotel['price_per_night']}/night")
            print(f"Rating: {hotel['user_rating']}/10")
        
        print("\n" + "=" * 70)
        print("HOTEL AGENT TEST COMPLETE!")
        print("=" * 70)
    
    asyncio.run(test())
