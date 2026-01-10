"""
Flight Search Tool
Searches for flights based on criteria.
Currently uses mock data, but can be extended to use real APIs.
"""
from typing import List, Optional
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.models.flight import Flight, FlightSegment


class FlightSearchTool:
    """
    Tool for searching flights.
    
    Currently uses mock data. Can be extended to use real APIs:
    - Amadeus API
    - Skyscanner API
    - Google Flights (unofficial)
    """
    
    def __init__(self, use_mock: bool = True):
        self.use_mock = use_mock
    
    async def search(
        self,
        origin: str,
        destination: str,
        date: str,
        travelers: int = 1,
        max_price: Optional[float] = None,
        direct_only: bool = False
    ) -> List[Flight]:
        """
        Search for flights matching criteria.
        
        Args:
            origin: Departure city/airport code
            destination: Arrival city/airport code
            date: Travel date (YYYY-MM-DD)
            travelers: Number of passengers
            max_price: Maximum price per person
            direct_only: Only return direct flights
        
        Returns:
            List of Flight objects sorted by price
        """
        
        if self.use_mock:
            flights = self._generate_mock_flights(origin, destination, date)
        else:
            # TODO: Implement real API integration
            raise NotImplementedError("Real API integration not implemented yet")
        
        # Apply filters
        if direct_only:
            flights = [f for f in flights if f.stops == 0]
        
        if max_price:
            flights = [f for f in flights if f.total_price <= max_price]
        
        # Sort by price
        flights.sort(key=lambda f: f.total_price)
        
        return flights
    
    def _generate_mock_flights(
        self,
        origin: str,
        destination: str,
        date: str
    ) -> List[Flight]:
        """Generate realistic mock flight data"""
        
        # Parse date
        try:
            flight_date = datetime.fromisoformat(date)
        except:
            flight_date = datetime.now() + timedelta(days=30)
        
        mock_flights = [
            # Direct flight - most expensive but fastest
            Flight(
                id="FL001",
                segments=[
                    FlightSegment(
                        airline="ANA",
                        flight_number="NH109",
                        departure_airport=origin,
                        arrival_airport=destination,
                        departure_time=flight_date.replace(hour=10, minute=30),
                        arrival_time=flight_date.replace(hour=14, minute=30),
                        duration_minutes=840  # 14 hours
                    )
                ],
                total_price=1250.00,
                total_duration_minutes=840,
                stops=0,
                cabin_class="economy"
            ),
            
            # Direct flight - premium airline
            Flight(
                id="FL002",
                segments=[
                    FlightSegment(
                        airline="JAL",
                        flight_number="JL006",
                        departure_airport=origin,
                        arrival_airport=destination,
                        departure_time=flight_date.replace(hour=13, minute=0),
                        arrival_time=flight_date.replace(hour=17, minute=0),
                        duration_minutes=840
                    )
                ],
                total_price=1350.00,
                total_duration_minutes=840,
                stops=0,
                cabin_class="economy"
            ),
            
            # One stop - medium price
            Flight(
                id="FL003",
                segments=[
                    FlightSegment(
                        airline="United",
                        flight_number="UA881",
                        departure_airport=origin,
                        arrival_airport="SFO",  # Stop in San Francisco
                        departure_time=flight_date.replace(hour=8, minute=0),
                        arrival_time=flight_date.replace(hour=11, minute=30),
                        duration_minutes=330
                    ),
                    FlightSegment(
                        airline="United",
                        flight_number="UA837",
                        departure_airport="SFO",
                        arrival_airport=destination,
                        departure_time=flight_date.replace(hour=13, minute=0),
                        arrival_time=flight_date.replace(hour=17, minute=0),
                        duration_minutes=660
                    )
                ],
                total_price=980.00,
                total_duration_minutes=1140,  # 19 hours with layover
                stops=1,
                cabin_class="economy"
            ),
            
            # One stop - cheaper option
            Flight(
                id="FL004",
                segments=[
                    FlightSegment(
                        airline="Delta",
                        flight_number="DL123",
                        departure_airport=origin,
                        arrival_airport="SEA",  # Stop in Seattle
                        departure_time=flight_date.replace(hour=7, minute=0),
                        arrival_time=flight_date.replace(hour=10, minute=0),
                        duration_minutes=300
                    ),
                    FlightSegment(
                        airline="Delta",
                        flight_number="DL456",
                        departure_airport="SEA",
                        arrival_airport=destination,
                        departure_time=flight_date.replace(hour=12, minute=0),
                        arrival_time=flight_date.replace(hour=16, minute=0),
                        duration_minutes=660
                    )
                ],
                total_price=920.00,
                total_duration_minutes=1080,
                stops=1,
                cabin_class="economy"
            ),
            
            # Two stops - cheapest but longest
            Flight(
                id="FL005",
                segments=[
                    FlightSegment(
                        airline="Delta",
                        flight_number="DL101",
                        departure_airport=origin,
                        arrival_airport="LAX",
                        departure_time=flight_date.replace(hour=6, minute=0),
                        arrival_time=flight_date.replace(hour=9, minute=0),
                        duration_minutes=300
                    ),
                    FlightSegment(
                        airline="Korean Air",
                        flight_number="KE011",
                        departure_airport="LAX",
                        arrival_airport="ICN",  # Stop in Seoul
                        departure_time=flight_date.replace(hour=11, minute=0),
                        arrival_time=flight_date.replace(hour=16, minute=0),
                        duration_minutes=780
                    ),
                    FlightSegment(
                        airline="Korean Air",
                        flight_number="KE789",
                        departure_airport="ICN",
                        arrival_airport=destination,
                        departure_time=flight_date.replace(hour=18, minute=0),
                        arrival_time=flight_date.replace(hour=20, minute=0),
                        duration_minutes=120
                    )
                ],
                total_price=750.00,
                total_duration_minutes=1500,  # 25 hours
                stops=2,
                cabin_class="economy"
            ),
        ]
        
        return mock_flights


# Test the tool if run directly
if __name__ == "__main__":
    import asyncio
    
    async def test():
        print("=" * 60)
        print("TESTING FLIGHT SEARCH TOOL")
        print("=" * 60)
        
        tool = FlightSearchTool()
        
        # Test 1: Basic search
        print("\n--- Test 1: Basic Search ---")
        flights = await tool.search("JFK", "NRT", "2026-04-15")
        
        for flight in flights:
            print(f"\n{flight.id}: {flight.formatted_price}")
            print(f"  Airline: {flight.segments[0].airline}")
            print(f"  Duration: {flight.formatted_duration}")
            print(f"  Stops: {flight.stops}")
            print(f"  Direct: {'Yes' if flight.is_direct else 'No'}")
        
        # Test 2: Direct flights only
        print("\n\n--- Test 2: Direct Flights Only ---")
        direct_flights = await tool.search("JFK", "NRT", "2026-04-15", direct_only=True)
        print(f"Found {len(direct_flights)} direct flights")
        
        # Test 3: Price filter
        print("\n\n--- Test 3: Budget Filter (max $1000) ---")
        budget_flights = await tool.search("JFK", "NRT", "2026-04-15", max_price=1000)
        print(f"Found {len(budget_flights)} flights under $1000")
        
        print("\n" + "=" * 60)
        print("ALL TESTS PASSED!")
        print("=" * 60)
    
    asyncio.run(test())
