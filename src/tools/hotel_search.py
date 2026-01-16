"""
Hotel Search Tool
Searches for hotels using Amadeus API with mock data fallback.
"""
from typing import List, Optional
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from src.models.hotel import Hotel
from src.tools.api_config import get_api_config
from src.tools.amadeus_client import AmadeusClient
from src.tools.location_resolver import get_city_code as resolve_city_code, LOCATION_CODES
from src.tools.geoapify_client import GeoapifyClient


class HotelSearchTool:
    """
    Tool for searching hotels.
    
    Uses Amadeus API when credentials are available,
    falls back to mock data otherwise.
    """
    
    def __init__(self, use_mock: Optional[bool] = None):
        """
        Initialize the hotel search tool.
        
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
        return self.config.should_use_mock_hotels
    
    @property
    def amadeus_client(self) -> AmadeusClient:
        """Lazy-load Amadeus client"""
        if self._amadeus_client is None:
            self._amadeus_client = AmadeusClient()
        return self._amadeus_client
    
    @property
    def geoapify_client(self) -> GeoapifyClient:
        """Lazy-load Geoapify client for geocoding"""
        if not hasattr(self, '_geoapify_client') or self._geoapify_client is None:
            self._geoapify_client = GeoapifyClient()
        return self._geoapify_client
    
    async def search(
        self,
        destination: str,
        check_in: str,
        check_out: str,
        guests: int = 2,
        max_price_per_night: Optional[float] = None,
        min_rating: float = 7.0
    ) -> List[Hotel]:
        """
        Search for hotels matching criteria.
        
        Args:
            destination: City name or code
            check_in: Check-in date (YYYY-MM-DD)
            check_out: Check-out date (YYYY-MM-DD)
            guests: Number of guests
            max_price_per_night: Maximum price per night
            min_rating: Minimum user rating (1-10)
        
        Returns:
            List of Hotel objects sorted by rating
        """
        
        if self.use_mock:
            print("🏨 Using mock hotel data")
            hotels = self._generate_mock_hotels(destination)
        else:
            print("🏨 Searching Amadeus API for real hotels...")
            hotels = await self._search_real_hotels(
                destination, check_in, check_out, guests
            )
        
        # Apply filters
        if max_price_per_night:
            hotels = [h for h in hotels if h.price_per_night <= max_price_per_night]
        
        hotels = [h for h in hotels if h.user_rating >= min_rating]
        
        # Sort by rating
        hotels.sort(key=lambda h: h.user_rating, reverse=True)
        
        return hotels
    
    async def _search_real_hotels(
        self,
        destination: str,
        check_in: str,
        check_out: str,
        guests: int
    ) -> List[Hotel]:
        """Search hotels using Amadeus API"""
        try:
            hotel_list = []
            
            # Check if this is a major city with its own code
            dest_lower = destination.lower().strip()
            has_unique_code = dest_lower in LOCATION_CODES and LOCATION_CODES[dest_lower][1] != "CMB"
            
            # For smaller cities/towns (like Galle, Hikkaduwa), use geocode-based search
            if not has_unique_code and len(destination) > 3:
                print(f"📍 Using geocode search for: {destination}")
                coords = await self.geoapify_client.geocode_city(destination)
                
                if coords and coords.get("lat") and coords.get("lon"):
                    print(f"   Found coordinates: ({coords['lat']:.4f}, {coords['lon']:.4f})")
                    hotel_list = await self.amadeus_client.search_hotels_by_geocode(
                        latitude=coords["lat"],
                        longitude=coords["lon"],
                        radius=30,  # 30km radius for beach towns
                        radius_unit="KM"
                    )
            
            # Fallback to city code search if geocode didn't work
            if not hotel_list:
                city_code = await self._get_city_code(destination)
                print(f"📍 Using city code search: {city_code}")
                hotel_list = await self.amadeus_client.search_hotels_by_city(
                    city_code=city_code,
                    radius=25,
                    radius_unit="KM"
                )
            
            if not hotel_list:
                print("⚠️  No hotels found from API, falling back to mock data")
                return self._generate_mock_hotels(destination)
            
            # Get offers for top hotels (limit to save API calls)
            hotel_ids = [h.get("hotelId") for h in hotel_list[:15] if h.get("hotelId")]
            
            if not hotel_ids:
                return self._generate_mock_hotels(destination)
            
            # Get pricing (this may fail if no availability)
            try:
                offers = await self.amadeus_client.get_hotel_offers(
                    hotel_ids=hotel_ids[:10],  # Limit to 10 for API efficiency
                    check_in=check_in,
                    check_out=check_out,
                    adults=guests
                )
                
                if offers:
                    parsed = self._parse_amadeus_hotels_with_offers(hotel_list, offers)
                    if parsed:
                        # If we got some hotels with offers, also add basic hotels 
                        # to fill out the list
                        hotel_ids_with_offers = {h.id for h in parsed}
                        remaining_hotels = [h for h in hotel_list 
                                          if h.get("hotelId") not in hotel_ids_with_offers]
                        if remaining_hotels:
                            basic_hotels = self._parse_amadeus_hotels_basic(remaining_hotels)
                            parsed.extend(basic_hotels)
                        return parsed
            except Exception as e:
                print(f"⚠️  Could not get hotel pricing: {e}")
            
            # If no offers, return basic hotel info with estimated prices
            basic_hotels = self._parse_amadeus_hotels_basic(hotel_list)
            if basic_hotels:
                return basic_hotels
            
            # Final fallback to mock data
            print("⚠️  Could not parse API hotels, falling back to mock data")
            return self._generate_mock_hotels(destination)
            
        except Exception as e:
            print(f"⚠️  Amadeus API error: {e}")
            print("   Falling back to mock hotel data")
            return self._generate_mock_hotels(destination)
    
    async def _get_city_code(self, location: str) -> str:
        """Convert city/country name to IATA city code using location resolver"""
        return resolve_city_code(location)
    
    def _parse_amadeus_hotels_with_offers(
        self, 
        hotel_list: List[dict], 
        offers: List[dict]
    ) -> List[Hotel]:
        """Parse hotels with pricing information"""
        hotels = []
        
        # Create hotel lookup
        hotel_lookup = {h.get("hotelId"): h for h in hotel_list}
        
        for idx, offer in enumerate(offers):
            try:
                hotel_data = offer.get("hotel", {})
                hotel_id = hotel_data.get("hotelId", f"HTL{idx+1:03d}")
                
                # Get additional info from hotel list
                extra_info = hotel_lookup.get(hotel_id, {})
                
                # Get price from offers
                offers_list = offer.get("offers", [])
                price = 0.0
                if offers_list:
                    price_data = offers_list[0].get("price", {})
                    total = float(price_data.get("total", 0))
                    # Estimate per night (assume 1 night if can't calculate)
                    price = total if total < 1000 else total / 3  # rough estimate
                
                # Star rating - safely extract
                rating_val = hotel_data.get("rating") or extra_info.get("rating")
                try:
                    star_rating = float(rating_val) if rating_val else 4.0
                except (ValueError, TypeError):
                    star_rating = 4.0
                
                # Distance - safely extract
                distance_data = extra_info.get("distance", {})
                distance = 5.0  # default
                if isinstance(distance_data, dict):
                    try:
                        distance = float(distance_data.get("value", 5.0))
                    except (ValueError, TypeError):
                        distance = 5.0
                
                hotel = Hotel(
                    id=hotel_id,
                    name=hotel_data.get("name", extra_info.get("name", "Unknown Hotel")) or "Unknown Hotel",
                    address=self._format_address(hotel_data.get("address", {})) or "Unknown",
                    star_rating=min(max(star_rating, 1.0), 5.0),
                    user_rating=min(star_rating * 2, 10.0),  # Estimate from stars
                    price_per_night=price if price > 0 else 150.0,
                    amenities=self._extract_amenities(hotel_data),
                    distance_to_center_km=distance
                )
                hotels.append(hotel)
                
            except Exception as e:
                print(f"⚠️  Error parsing hotel: {e}")
                continue
        
        return hotels
    
    def _parse_amadeus_hotels_basic(self, hotel_list: List[dict]) -> List[Hotel]:
        """Parse hotels with estimated prices (no offer data)"""
        hotels = []
        
        for idx, hotel_data in enumerate(hotel_list[:10]):
            try:
                # Amadeus doesn't always provide star rating, estimate from chain
                rating_raw = hotel_data.get("rating")
                if rating_raw:
                    try:
                        rating = float(rating_raw)
                    except (ValueError, TypeError):
                        rating = 4.0  # Default to 4 star
                else:
                    # Estimate rating based on hotel chain (luxury chains = 5 star)
                    chain = hotel_data.get("chainCode", "")
                    luxury_chains = ["SG", "FS", "RC", "JW", "LC", "PH", "PA"]  # Shangri-La, Four Seasons, etc
                    rating = 5.0 if chain in luxury_chains else 4.0
                
                estimated_price = {
                    1: 50, 2: 80, 3: 120, 4: 200, 5: 350
                }.get(int(rating), 150)
                
                # Get distance safely
                distance_data = hotel_data.get("distance", {})
                distance = 5.0
                if isinstance(distance_data, dict):
                    dist_val = distance_data.get("value", 5.0)
                    try:
                        distance = float(dist_val) if dist_val else 5.0
                    except (ValueError, TypeError):
                        distance = 5.0
                
                # Get address
                address_data = hotel_data.get("address", {})
                address_lines = address_data.get("lines", [])
                city_name = address_data.get("cityName", "")
                address = ", ".join(address_lines) if address_lines else city_name
                
                hotel = Hotel(
                    id=hotel_data.get("hotelId", f"HTL{idx+1:03d}"),
                    name=hotel_data.get("name", "Unknown Hotel") or "Unknown Hotel",
                    address=address or "Unknown",
                    star_rating=min(max(rating, 1.0), 5.0),
                    user_rating=min(rating * 1.8 + 1, 10.0),  # Estimate user rating from stars
                    price_per_night=float(estimated_price),
                    amenities=self._extract_amenities({"rating": rating}),
                    distance_to_center_km=distance
                )
                hotels.append(hotel)
                
            except Exception as e:
                print(f"⚠️  Error parsing hotel {idx}: {e}")
                continue
        
        # If no hotels parsed, return empty and let caller fall back to mock
        return hotels
    
    def _format_address(self, address_data: dict) -> str:
        """Format address from API response"""
        lines = address_data.get("lines", [])
        city = address_data.get("cityName", "")
        
        if lines:
            return f"{', '.join(lines)}, {city}"
        return city
    
    def _extract_amenities(self, hotel_data: dict) -> List[str]:
        """Extract amenities from hotel data"""
        amenities = ["WiFi"]  # Default
        
        # Add based on rating
        rating = hotel_data.get("rating", 0)
        if rating >= 4:
            amenities.extend(["Restaurant", "Gym"])
        if rating >= 5:
            amenities.extend(["Spa", "Pool", "Concierge"])
        
        return amenities
    
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
        
        config = get_api_config()
        print(f"\nAPI Mode: {'MOCK' if config.should_use_mock_hotels else 'REAL (Amadeus)'}")
        
        tool = HotelSearchTool()
        hotels = await tool.search("Tokyo", "2026-04-15", "2026-04-20", guests=2)
        
        for hotel in hotels[:5]:  # Show top 5
            print(f"\n{hotel.name}")
            print(f"  Rating: {hotel.user_rating}/10 ({hotel.rating_category})")
            print(f"  Price: {hotel.formatted_price}")
            print(f"  Stars: {hotel.star_rating}⭐")
        
        print(f"\nFound {len(hotels)} hotels!")
        print("\nHotel Search Tool works!")
    
    asyncio.run(test())
