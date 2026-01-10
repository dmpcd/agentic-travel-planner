"""
Flight Agent
AI agent responsible for searching and recommending flights.
"""
from typing import Any, Dict, List
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.agents.base_agent import BaseAgent
from src.models.flight import Flight
from src.tools.flight_search import FlightSearchTool


class FlightAgent(BaseAgent):
    """
    Agent responsible for searching and recommending flights.
    
    Capabilities:
    - Search flights based on criteria
    - Compare prices, durations, and convenience
    - Recommend best options using AI reasoning
    - Consider user preferences and trade-offs
    """
    
    def __init__(self):
        super().__init__(
            name="Flight Agent",
            description="Searches and recommends the best flights"
        )
        self.flight_tool = FlightSearchTool()
        self.add_tool(self.flight_tool)
    
    @property
    def system_prompt(self) -> str:
        return """You are a flight search expert agent. Your job is to:

1. Analyze flight options considering:
   - Price (lower is better, but consider value)
   - Duration (shorter is better)
   - Number of stops (direct is strongly preferred)
   - Departure/arrival times (reasonable hours preferred)
   - Airline reputation

2. Recommend the BEST option with clear reasoning

3. Consider trade-offs intelligently:
   - A slightly more expensive direct flight is usually better than a cheap flight with 2 stops
   - Very early morning or late night flights should be noted
   - Long layovers should be mentioned

4. Keep your response concise and actionable (3-5 sentences max)

5. Format: 
   - State your recommendation clearly
   - Give 2-3 key reasons
   - Mention any important considerations"""

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Search for flights and return AI-powered recommendations.
        
        Input:
            {
                "origin": "JFK",
                "destination": "NRT", 
                "departure_date": "2026-04-15",
                "return_date": "2026-04-20",
                "travelers": 2,
                "max_price": 1500,
                "preferences": "direct flight preferred"
            }
        
        Output:
            {
                "outbound_flights": [...],
                "return_flights": [...],
                "recommended_outbound": {...},
                "recommended_return": {...},
                "reasoning": "..."
            }
        """
        # Search for outbound flights
        outbound_flights = await self.flight_tool.search(
            origin=input_data["origin"],
            destination=input_data["destination"],
            date=input_data["departure_date"],
            travelers=input_data.get("travelers", 1),
            max_price=input_data.get("max_price")
        )
        
        # Search for return flights
        return_flights = await self.flight_tool.search(
            origin=input_data["destination"],
            destination=input_data["origin"],
            date=input_data["return_date"],
            travelers=input_data.get("travelers", 1),
            max_price=input_data.get("max_price")
        )
        
        # Use AI to analyze and recommend
        analysis_prompt = f"""Analyze these flight options and recommend the best choice:

OUTBOUND FLIGHTS ({input_data["origin"]} → {input_data["destination"]}):
{self._format_flights(outbound_flights)}

RETURN FLIGHTS ({input_data["destination"]} → {input_data["origin"]}):
{self._format_flights(return_flights)}

USER PREFERENCES:
- Budget: ${input_data.get('max_price', 'flexible')} per person
- Travelers: {input_data.get('travelers', 1)}
- Preferences: {input_data.get('preferences', 'none specified')}

Recommend the BEST outbound and return flight combination. Be specific and concise."""
        
        reasoning = await self.think(analysis_prompt)
        
        return {
            "outbound_flights": [f.model_dump() for f in outbound_flights],
            "return_flights": [f.model_dump() for f in return_flights],
            "recommended_outbound": outbound_flights[0].model_dump() if outbound_flights else None,
            "recommended_return": return_flights[0].model_dump() if return_flights else None,
            "reasoning": reasoning,
            "total_flights_found": len(outbound_flights) + len(return_flights)
        }
    
    def _format_flights(self, flights: List[Flight]) -> str:
        """Format flights for AI analysis"""
        if not flights:
            return "No flights found"
        
        result = []
        for i, flight in enumerate(flights[:5], 1):  # Limit to top 5
            airline = flight.segments[0].airline
            result.append(
                f"Option {i}: {flight.id}\n"
                f"  - Price: {flight.formatted_price}\n"
                f"  - Duration: {flight.formatted_duration}\n"
                f"  - Stops: {flight.stops} ({'Direct' if flight.is_direct else 'Connecting'})\n"
                f"  - Airline: {airline}"
            )
        return "\n\n".join(result)


# Test the Flight Agent if run directly
if __name__ == "__main__":
    import asyncio
    
    async def test_flight_agent():
        print("=" * 70)
        print("TESTING FLIGHT AGENT WITH AI")
        print("=" * 70)
        
        # Create agent
        agent = FlightAgent()
        
        print("\n" + "=" * 70)
        print("SCENARIO: New York to Tokyo, April 15-20, Budget $3000")
        print("=" * 70)
        
        # Execute agent
        result = await agent.execute({
            "origin": "JFK",
            "destination": "NRT",
            "departure_date": "2026-04-15",
            "return_date": "2026-04-20",
            "travelers": 2,
            "max_price": 1500,
            "preferences": "prefer direct flights if reasonable price"
        })
        
        print(f"\nFound {result['total_flights_found']} total flights")
        print(f"   - {len(result['outbound_flights'])} outbound options")
        print(f"   - {len(result['return_flights'])} return options")
        
        print("\n" + "-" * 70)
        print("AI RECOMMENDATION:")
        print("-" * 70)
        print(result['reasoning'])
        
        if result['recommended_outbound']:
            print("\n" + "-" * 70)
            print("RECOMMENDED OUTBOUND FLIGHT:")
            print("-" * 70)
            outbound = result['recommended_outbound']
            print(f"Flight ID: {outbound['id']}")
            print(f"Price: ${outbound['total_price']}")
            print(f"Stops: {outbound['stops']}")
        
        if result['recommended_return']:
            print("\n" + "-" * 70)
            print("RECOMMENDED RETURN FLIGHT:")
            print("-" * 70)
            return_f = result['recommended_return']
            print(f"Flight ID: {return_f['id']}")
            print(f"Price: ${return_f['total_price']}")
            print(f"Stops: {return_f['stops']}")
        
        print("\n" + "=" * 70)
        print("FLIGHT AGENT TEST COMPLETE!")
        print("=" * 70)
        print("\nYour first AI agent is working!")
        print("It can search flights AND use AI to recommend the best options!")
        
    asyncio.run(test_flight_agent())
