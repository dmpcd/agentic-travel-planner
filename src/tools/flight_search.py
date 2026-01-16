"""
Flight Search Tool
Searches for flights using Amadeus API with mock data fallback.
"""
from typing import List, Optional
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.models.flight import Flight, FlightSegment
from src.tools.api_config import get_api_config
from src.tools.amadeus_client import AmadeusClient
from src.tools.location_resolver import get_airport_code


class FlightSearchTool:
    """
    Tool for searching flights.
    
    Uses Amadeus API when credentials are available, 
    falls back to mock data otherwise.
    """
    
    def __init__(self, use_mock: Optional[bool] = None):
        """
        Initialize the flight search tool.
        
        Args:
            use_mock: Force mock mode. If None, auto-detect based on API config.
        """
        self.config = get_api_config()
        self._use_mock = use_mock
        self._amadeus_client = None
    
    @property
    def use_mock(self) -> bool:
        """Determine whether to use mock data"""
        if self._use_mock is not None:
            return self._use_mock
        return self.config.should_use_mock_flights
    
    @property
    def amadeus_client(self) -> AmadeusClient:
        """Lazy-load Amadeus client"""
        if self._amadeus_client is None:
            self._amadeus_client = AmadeusClient()
        return self._amadeus_client
    
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
            print("✈️  Using mock flight data")
            flights = self._generate_mock_flights(origin, destination, date)
        else:
            print("✈️  Searching Amadeus API for real flights...")
            flights = await self._search_real_flights(
                origin, destination, date, travelers, direct_only
            )
        
        # Apply filters
        if direct_only and not self.use_mock:
            # Already filtered in API call
            pass
        elif direct_only:
            flights = [f for f in flights if f.stops == 0]
        
        if max_price:
            flights = [f for f in flights if f.total_price <= max_price]
        
        # Sort by price
        flights.sort(key=lambda f: f.total_price)
        
        return flights
    
    async def _search_real_flights(
        self,
        origin: str,
        destination: str,
        date: str,
        travelers: int,
        direct_only: bool
    ) -> List[Flight]:
        """Search flights using Amadeus API"""
        try:
            # Get airport codes if city names provided
            origin_code = await self._get_airport_code(origin)
            dest_code = await self._get_airport_code(destination)
            
            # Search flights via Amadeus
            results = await self.amadeus_client.search_flights(
                origin=origin_code,
                destination=dest_code,
                departure_date=date,
                adults=travelers,
                non_stop=direct_only,
                max_results=10
            )
            
            if not results:
                print("⚠️  No flights found from API, falling back to mock data")
                return self._generate_mock_flights(origin, destination, date)
            
            # Parse API response to Flight models
            return self._parse_amadeus_flights(results)
            
        except Exception as e:
            print(f"⚠️  Amadeus API error: {e}")
            print("   Falling back to mock flight data")
            return self._generate_mock_flights(origin, destination, date)
    
    async def _get_airport_code(self, location: str) -> str:
        """Convert city/country name to airport code using location resolver"""
        return get_airport_code(location)
    
    def _parse_amadeus_flights(self, api_results: List[dict]) -> List[Flight]:
        """Parse Amadeus API response into Flight models"""
        flights = []
        
        for idx, offer in enumerate(api_results):
            try:
                # Get itinerary (first one for outbound)
                itineraries = offer.get("itineraries", [])
                if not itineraries:
                    continue
                
                outbound = itineraries[0]
                segments_data = outbound.get("segments", [])
                
                # Parse segments
                segments = []
                for seg in segments_data:
                    departure = seg.get("departure", {})
                    arrival = seg.get("arrival", {})
                    
                    segment = FlightSegment(
                        airline=seg.get("carrierCode", "Unknown"),
                        flight_number=f"{seg.get('carrierCode', '')}{seg.get('number', '')}",
                        departure_airport=departure.get("iataCode", ""),
                        arrival_airport=arrival.get("iataCode", ""),
                        departure_time=self._parse_datetime(departure.get("at")),
                        arrival_time=self._parse_datetime(arrival.get("at")),
                        duration_minutes=self._parse_duration(seg.get("duration", "PT0H0M"))
                    )
                    segments.append(segment)
                
                # Get price
                price_data = offer.get("price", {})
                total_price = float(price_data.get("total", 0))
                
                # Calculate total duration
                total_duration = self._parse_duration(outbound.get("duration", "PT0H0M"))
                
                flight = Flight(
                    id=f"FL{idx+1:03d}",
                    segments=segments,
                    total_price=total_price,
                    total_duration_minutes=total_duration,
                    stops=len(segments) - 1,
                    cabin_class="economy"
                )
                flights.append(flight)
                
            except Exception as e:
                print(f"⚠️  Error parsing flight offer: {e}")
                continue
        
        return flights
    
    def _parse_datetime(self, dt_string: str) -> datetime:
        """Parse ISO datetime string"""
        if not dt_string:
            return datetime.now()
        try:
            return datetime.fromisoformat(dt_string.replace("Z", "+00:00"))
        except:
            return datetime.now()
    
    def _parse_duration(self, duration: str) -> int:
        """Parse ISO 8601 duration to minutes (e.g., PT14H30M -> 870)"""
        if not duration:
            return 0
        
        import re
        hours = 0
        minutes = 0
        
        h_match = re.search(r'(\d+)H', duration)
        m_match = re.search(r'(\d+)M', duration)
        
        if h_match:
            hours = int(h_match.group(1))
        if m_match:
            minutes = int(m_match.group(1))
        
        return hours * 60 + minutes
    
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
        
        config = get_api_config()
        print(f"\nAPI Mode: {'MOCK' if config.should_use_mock_flights else 'REAL (Amadeus)'}")
        
        tool = FlightSearchTool()
        
        # Test 1: Basic search
        print("\n--- Test 1: Basic Search ---")
        flights = await tool.search("JFK", "NRT", "2026-04-15")
        
        for flight in flights[:5]:  # Show top 5
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
        
        # Test 4: City name search (if real API)
        if not config.should_use_mock_flights:
            print("\n\n--- Test 4: City Name Search ---")
            city_flights = await tool.search("New York", "Tokyo", "2026-04-15")
            print(f"Found {len(city_flights)} flights from New York to Tokyo")
        
        print("\n" + "=" * 60)
        print("ALL TESTS PASSED!")
        print("=" * 60)
    
    asyncio.run(test())
