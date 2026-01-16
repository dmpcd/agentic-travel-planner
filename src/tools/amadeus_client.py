"""
Amadeus API Client
Client for Amadeus Travel API (flights and hotels).
Free tier: 2000 API calls/month

Get your API keys at: https://developers.amadeus.com/
"""
import httpx
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import asyncio

from src.tools.api_config import get_api_config


class AmadeusClient:
    """
    Client for Amadeus Travel APIs.
    
    Handles authentication and provides methods for:
    - Flight offers search
    - Hotel search
    - Location/airport lookup
    """
    
    def __init__(self):
        self.config = get_api_config()
        self._access_token: Optional[str] = None
        self._token_expires_at: Optional[datetime] = None
    
    async def _get_access_token(self) -> str:
        """
        Get OAuth2 access token for Amadeus API.
        Tokens are cached and refreshed when expired.
        """
        # Check if we have a valid cached token
        if self._access_token and self._token_expires_at:
            if datetime.now() < self._token_expires_at:
                return self._access_token
        
        # Request new token
        auth_url = f"{self.config.amadeus_base_url}/v1/security/oauth2/token"
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                auth_url,
                data={
                    "grant_type": "client_credentials",
                    "client_id": self.config.amadeus_api_key,
                    "client_secret": self.config.amadeus_api_secret
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if response.status_code != 200:
                raise Exception(f"Amadeus auth failed: {response.text}")
            
            data = response.json()
            self._access_token = data["access_token"]
            # Token expires in 30 minutes, refresh 5 minutes early
            self._token_expires_at = datetime.now() + timedelta(seconds=data["expires_in"] - 300)
            
            return self._access_token
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make authenticated request to Amadeus API"""
        token = await self._get_access_token()
        url = f"{self.config.amadeus_base_url}{endpoint}"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.request(
                method=method,
                url=url,
                params=params,
                json=json_data,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Amadeus API error ({response.status_code}): {response.text}")
    
    # ============================================
    # FLIGHT SEARCH
    # ============================================
    
    async def search_flights(
        self,
        origin: str,
        destination: str,
        departure_date: str,
        adults: int = 1,
        max_results: int = 10,
        non_stop: bool = False,
        max_price: Optional[int] = None,
        currency: str = "USD"
    ) -> List[Dict[str, Any]]:
        """
        Search for flight offers.
        
        Args:
            origin: IATA airport code (e.g., "JFK")
            destination: IATA airport code (e.g., "NRT")
            departure_date: Date in YYYY-MM-DD format
            adults: Number of adult passengers
            max_results: Maximum number of results
            non_stop: Only return non-stop flights
            max_price: Maximum price in specified currency
            currency: Currency code (default USD)
            
        Returns:
            List of flight offers
        """
        params = {
            "originLocationCode": origin.upper(),
            "destinationLocationCode": destination.upper(),
            "departureDate": departure_date,
            "adults": adults,
            "max": max_results,
            "currencyCode": currency
        }
        
        if non_stop:
            params["nonStop"] = "true"
        
        if max_price:
            params["maxPrice"] = max_price
        
        try:
            response = await self._make_request(
                "GET",
                "/v2/shopping/flight-offers",
                params=params
            )
            return response.get("data", [])
        except Exception as e:
            print(f"⚠️ Amadeus flight search failed: {e}")
            return []
    
    # ============================================
    # HOTEL SEARCH
    # ============================================
    
    async def search_hotels_by_city(
        self,
        city_code: str,
        radius: int = 10,
        radius_unit: str = "KM",
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search for hotels by city code.
        
        Args:
            city_code: IATA city code (e.g., "TYO" for Tokyo)
            radius: Search radius from city center
            radius_unit: KM or MILE
            max_results: Maximum number of results
            
        Returns:
            List of hotel properties
        """
        params = {
            "cityCode": city_code.upper(),
            "radius": radius,
            "radiusUnit": radius_unit,
            "hotelSource": "ALL"
        }
        
        try:
            response = await self._make_request(
                "GET",
                "/v1/reference-data/locations/hotels/by-city",
                params=params
            )
            hotels = response.get("data", [])
            return hotels[:max_results]
        except Exception as e:
            print(f"⚠️ Amadeus hotel search failed: {e}")
            return []
    
    async def search_hotels_by_geocode(
        self,
        latitude: float,
        longitude: float,
        radius: int = 20,
        radius_unit: str = "KM",
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search for hotels by geographic coordinates.
        
        Args:
            latitude: Latitude of location
            longitude: Longitude of location
            radius: Search radius from coordinates
            radius_unit: KM or MILE
            max_results: Maximum number of results
            
        Returns:
            List of hotel properties
        """
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "radius": radius,
            "radiusUnit": radius_unit,
            "hotelSource": "ALL"
        }
        
        try:
            response = await self._make_request(
                "GET",
                "/v1/reference-data/locations/hotels/by-geocode",
                params=params
            )
            hotels = response.get("data", [])
            return hotels[:max_results]
        except Exception as e:
            print(f"⚠️ Amadeus geocode hotel search failed: {e}")
            return []
    
    async def get_hotel_offers(
        self,
        hotel_ids: List[str],
        check_in: str,
        check_out: str,
        adults: int = 2,
        currency: str = "USD"
    ) -> List[Dict[str, Any]]:
        """
        Get hotel offers with prices for specific hotels.
        
        Args:
            hotel_ids: List of Amadeus hotel IDs
            check_in: Check-in date (YYYY-MM-DD)
            check_out: Check-out date (YYYY-MM-DD)
            adults: Number of adult guests
            currency: Currency code
            
        Returns:
            List of hotel offers with pricing
        """
        params = {
            "hotelIds": ",".join(hotel_ids[:20]),  # Max 20 hotels per request
            "checkInDate": check_in,
            "checkOutDate": check_out,
            "adults": adults,
            "currency": currency
        }
        
        try:
            response = await self._make_request(
                "GET",
                "/v3/shopping/hotel-offers",
                params=params
            )
            return response.get("data", [])
        except Exception as e:
            print(f"⚠️ Amadeus hotel offers failed: {e}")
            return []
    
    # ============================================
    # LOCATION LOOKUP
    # ============================================
    
    async def search_airport(self, keyword: str) -> List[Dict[str, Any]]:
        """
        Search for airports by city name or code.
        
        Args:
            keyword: City name or airport code
            
        Returns:
            List of matching airports/cities
        """
        params = {
            "keyword": keyword,
            "subType": "AIRPORT,CITY"
        }
        
        try:
            response = await self._make_request(
                "GET",
                "/v1/reference-data/locations",
                params=params
            )
            return response.get("data", [])
        except Exception as e:
            print(f"⚠️ Amadeus location search failed: {e}")
            return []


# Note: City/airport code lookups are handled by location_resolver.py
# which has comprehensive mappings for 300+ cities worldwide


# Test if run directly
if __name__ == "__main__":
    async def test():
        config = get_api_config()
        
        if not config.has_amadeus_credentials:
            print("⚠️ Amadeus API credentials not configured")
            print("Set AMADEUS_API_KEY and AMADEUS_API_SECRET in .env")
            return
        
        client = AmadeusClient()
        
        print("\n" + "=" * 60)
        print("TESTING AMADEUS API CLIENT")
        print("=" * 60)
        
        # Test airport search
        print("\n📍 Searching for Tokyo airports...")
        airports = await client.search_airport("Tokyo")
        for airport in airports[:3]:
            print(f"   {airport.get('iataCode')}: {airport.get('name')}")
        
        # Test flight search
        print("\n🛫 Searching for flights JFK → NRT...")
        flights = await client.search_flights(
            origin="JFK",
            destination="NRT",
            departure_date="2026-04-15",
            adults=1,
            max_results=3
        )
        print(f"   Found {len(flights)} flight offers")
        
        print("\n✅ Amadeus API client working!")
    
    asyncio.run(test())
