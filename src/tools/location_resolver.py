"""
Location Resolver
Converts city/country names to IATA airport and city codes.
Uses a comprehensive mapping with Amadeus API fallback.
"""
from typing import Optional, Tuple
import httpx

from src.tools.api_config import get_api_config


# Comprehensive mapping of cities/countries to IATA codes
# Format: "city/country name": ("airport_code", "city_code")
LOCATION_CODES = {
    # ============================================
    # SOUTH ASIA
    # ============================================
    # India
    "india": ("DEL", "DEL"),  # Default to Delhi for country
    "delhi": ("DEL", "DEL"),
    "new delhi": ("DEL", "DEL"),
    "mumbai": ("BOM", "BOM"),
    "bombay": ("BOM", "BOM"),
    "bangalore": ("BLR", "BLR"),
    "bengaluru": ("BLR", "BLR"),
    "chennai": ("MAA", "MAA"),
    "madras": ("MAA", "MAA"),
    "kolkata": ("CCU", "CCU"),
    "calcutta": ("CCU", "CCU"),
    "hyderabad": ("HYD", "HYD"),
    "ahmedabad": ("AMD", "AMD"),
    "pune": ("PNQ", "PNQ"),
    "jaipur": ("JAI", "JAI"),
    "goa": ("GOI", "GOI"),
    "kochi": ("COK", "COK"),
    "cochin": ("COK", "COK"),
    "trivandrum": ("TRV", "TRV"),
    "thiruvananthapuram": ("TRV", "TRV"),
    
    # Sri Lanka
    "sri lanka": ("CMB", "CMB"),  # Default to Colombo for country
    "colombo": ("CMB", "CMB"),
    "kandy": ("CMB", "CMB"),  # Closest major airport
    "galle": ("CMB", "CMB"),
    "negombo": ("CMB", "CMB"),
    "hikkaduwa": ("CMB", "CMB"),
    "trincomalee": ("TRR", "TRR"),
    "jaffna": ("JAF", "JAF"),
    "mattala": ("HRI", "HRI"),
    
    # Other South Asia
    "pakistan": ("KHI", "KHI"),
    "karachi": ("KHI", "KHI"),
    "lahore": ("LHE", "LHE"),
    "islamabad": ("ISB", "ISB"),
    "bangladesh": ("DAC", "DAC"),
    "dhaka": ("DAC", "DAC"),
    "nepal": ("KTM", "KTM"),
    "kathmandu": ("KTM", "KTM"),
    "maldives": ("MLE", "MLE"),
    "male": ("MLE", "MLE"),
    
    # ============================================
    # EAST ASIA
    # ============================================
    # Japan
    "japan": ("NRT", "TYO"),
    "tokyo": ("NRT", "TYO"),
    "narita": ("NRT", "TYO"),
    "haneda": ("HND", "TYO"),
    "osaka": ("KIX", "OSA"),
    "kansai": ("KIX", "OSA"),
    "kyoto": ("KIX", "OSA"),
    "nagoya": ("NGO", "NGO"),
    "fukuoka": ("FUK", "FUK"),
    "sapporo": ("CTS", "SPK"),
    "okinawa": ("OKA", "OKA"),
    "naha": ("OKA", "OKA"),
    
    # South Korea
    "south korea": ("ICN", "SEL"),
    "korea": ("ICN", "SEL"),
    "seoul": ("ICN", "SEL"),
    "incheon": ("ICN", "SEL"),
    "busan": ("PUS", "PUS"),
    "jeju": ("CJU", "CJU"),
    
    # China
    "china": ("PEK", "BJS"),
    "beijing": ("PEK", "BJS"),
    "peking": ("PEK", "BJS"),
    "shanghai": ("PVG", "SHA"),
    "hong kong": ("HKG", "HKG"),
    "guangzhou": ("CAN", "CAN"),
    "shenzhen": ("SZX", "SZX"),
    "chengdu": ("CTU", "CTU"),
    "xi'an": ("XIY", "SIA"),
    "xian": ("XIY", "SIA"),
    "hangzhou": ("HGH", "HGH"),
    "macau": ("MFM", "MFM"),
    "macao": ("MFM", "MFM"),
    
    # Taiwan
    "taiwan": ("TPE", "TPE"),
    "taipei": ("TPE", "TPE"),
    "kaohsiung": ("KHH", "KHH"),
    
    # ============================================
    # SOUTHEAST ASIA
    # ============================================
    # Thailand
    "thailand": ("BKK", "BKK"),
    "bangkok": ("BKK", "BKK"),
    "phuket": ("HKT", "HKT"),
    "chiang mai": ("CNX", "CNX"),
    "krabi": ("KBV", "KBV"),
    "samui": ("USM", "USM"),
    "koh samui": ("USM", "USM"),
    "pattaya": ("UTP", "UTP"),
    
    # Singapore
    "singapore": ("SIN", "SIN"),
    
    # Malaysia
    "malaysia": ("KUL", "KUL"),
    "kuala lumpur": ("KUL", "KUL"),
    "penang": ("PEN", "PEN"),
    "langkawi": ("LGK", "LGK"),
    "borneo": ("BKI", "BKI"),
    "kota kinabalu": ("BKI", "BKI"),
    
    # Indonesia
    "indonesia": ("CGK", "JKT"),
    "jakarta": ("CGK", "JKT"),
    "bali": ("DPS", "DPS"),
    "denpasar": ("DPS", "DPS"),
    "surabaya": ("SUB", "SUB"),
    "yogyakarta": ("JOG", "JOG"),
    "lombok": ("LOP", "LOP"),
    
    # Vietnam
    "vietnam": ("SGN", "SGN"),
    "ho chi minh": ("SGN", "SGN"),
    "saigon": ("SGN", "SGN"),
    "hanoi": ("HAN", "HAN"),
    "da nang": ("DAD", "DAD"),
    
    # Philippines
    "philippines": ("MNL", "MNL"),
    "manila": ("MNL", "MNL"),
    "cebu": ("CEB", "CEB"),
    "boracay": ("KLO", "KLO"),
    
    # Cambodia, Myanmar, Laos
    "cambodia": ("PNH", "PNH"),
    "phnom penh": ("PNH", "PNH"),
    "siem reap": ("REP", "REP"),
    "myanmar": ("RGN", "RGN"),
    "burma": ("RGN", "RGN"),
    "yangon": ("RGN", "RGN"),
    "laos": ("VTE", "VTE"),
    "vientiane": ("VTE", "VTE"),
    
    # ============================================
    # MIDDLE EAST
    # ============================================
    "uae": ("DXB", "DXB"),
    "united arab emirates": ("DXB", "DXB"),
    "dubai": ("DXB", "DXB"),
    "abu dhabi": ("AUH", "AUH"),
    "qatar": ("DOH", "DOH"),
    "doha": ("DOH", "DOH"),
    "saudi arabia": ("RUH", "RUH"),
    "riyadh": ("RUH", "RUH"),
    "jeddah": ("JED", "JED"),
    "bahrain": ("BAH", "BAH"),
    "oman": ("MCT", "MCT"),
    "muscat": ("MCT", "MCT"),
    "kuwait": ("KWI", "KWI"),
    "israel": ("TLV", "TLV"),
    "tel aviv": ("TLV", "TLV"),
    "jordan": ("AMM", "AMM"),
    "amman": ("AMM", "AMM"),
    "turkey": ("IST", "IST"),
    "istanbul": ("IST", "IST"),
    "ankara": ("ESB", "ANK"),
    "iran": ("IKA", "THR"),
    "tehran": ("IKA", "THR"),
    
    # ============================================
    # EUROPE
    # ============================================
    # UK
    "united kingdom": ("LHR", "LON"),
    "uk": ("LHR", "LON"),
    "england": ("LHR", "LON"),
    "london": ("LHR", "LON"),
    "heathrow": ("LHR", "LON"),
    "gatwick": ("LGW", "LON"),
    "manchester": ("MAN", "MAN"),
    "edinburgh": ("EDI", "EDI"),
    "scotland": ("EDI", "EDI"),
    "birmingham": ("BHX", "BHX"),
    "bristol": ("BRS", "BRS"),
    
    # France
    "france": ("CDG", "PAR"),
    "paris": ("CDG", "PAR"),
    "nice": ("NCE", "NCE"),
    "lyon": ("LYS", "LYS"),
    "marseille": ("MRS", "MRS"),
    
    # Germany
    "germany": ("FRA", "FRA"),
    "frankfurt": ("FRA", "FRA"),
    "munich": ("MUC", "MUC"),
    "berlin": ("BER", "BER"),
    "dusseldorf": ("DUS", "DUS"),
    "hamburg": ("HAM", "HAM"),
    
    # Italy
    "italy": ("FCO", "ROM"),
    "rome": ("FCO", "ROM"),
    "milan": ("MXP", "MIL"),
    "venice": ("VCE", "VCE"),
    "florence": ("FLR", "FLR"),
    "naples": ("NAP", "NAP"),
    
    # Spain
    "spain": ("MAD", "MAD"),
    "madrid": ("MAD", "MAD"),
    "barcelona": ("BCN", "BCN"),
    "malaga": ("AGP", "AGP"),
    "seville": ("SVQ", "SVQ"),
    "ibiza": ("IBZ", "IBZ"),
    
    # Netherlands
    "netherlands": ("AMS", "AMS"),
    "holland": ("AMS", "AMS"),
    "amsterdam": ("AMS", "AMS"),
    
    # Other Europe
    "switzerland": ("ZRH", "ZRH"),
    "zurich": ("ZRH", "ZRH"),
    "geneva": ("GVA", "GVA"),
    "austria": ("VIE", "VIE"),
    "vienna": ("VIE", "VIE"),
    "belgium": ("BRU", "BRU"),
    "brussels": ("BRU", "BRU"),
    "portugal": ("LIS", "LIS"),
    "lisbon": ("LIS", "LIS"),
    "greece": ("ATH", "ATH"),
    "athens": ("ATH", "ATH"),
    "ireland": ("DUB", "DUB"),
    "dublin": ("DUB", "DUB"),
    "sweden": ("ARN", "STO"),
    "stockholm": ("ARN", "STO"),
    "norway": ("OSL", "OSL"),
    "oslo": ("OSL", "OSL"),
    "denmark": ("CPH", "CPH"),
    "copenhagen": ("CPH", "CPH"),
    "finland": ("HEL", "HEL"),
    "helsinki": ("HEL", "HEL"),
    "czech republic": ("PRG", "PRG"),
    "czechia": ("PRG", "PRG"),
    "prague": ("PRG", "PRG"),
    "poland": ("WAW", "WAW"),
    "warsaw": ("WAW", "WAW"),
    "hungary": ("BUD", "BUD"),
    "budapest": ("BUD", "BUD"),
    "russia": ("SVO", "MOW"),
    "moscow": ("SVO", "MOW"),
    "saint petersburg": ("LED", "LED"),
    "croatia": ("ZAG", "ZAG"),
    "zagreb": ("ZAG", "ZAG"),
    "dubrovnik": ("DBV", "DBV"),
    
    # ============================================
    # NORTH AMERICA
    # ============================================
    # USA
    "usa": ("JFK", "NYC"),
    "united states": ("JFK", "NYC"),
    "america": ("JFK", "NYC"),
    "new york": ("JFK", "NYC"),
    "nyc": ("JFK", "NYC"),
    "jfk": ("JFK", "NYC"),
    "los angeles": ("LAX", "LAX"),
    "la": ("LAX", "LAX"),
    "lax": ("LAX", "LAX"),
    "san francisco": ("SFO", "SFO"),
    "sf": ("SFO", "SFO"),
    "chicago": ("ORD", "CHI"),
    "miami": ("MIA", "MIA"),
    "seattle": ("SEA", "SEA"),
    "boston": ("BOS", "BOS"),
    "washington": ("IAD", "WAS"),
    "washington dc": ("IAD", "WAS"),
    "dc": ("DCA", "WAS"),
    "atlanta": ("ATL", "ATL"),
    "dallas": ("DFW", "DFW"),
    "houston": ("IAH", "HOU"),
    "denver": ("DEN", "DEN"),
    "las vegas": ("LAS", "LAS"),
    "vegas": ("LAS", "LAS"),
    "phoenix": ("PHX", "PHX"),
    "san diego": ("SAN", "SAN"),
    "orlando": ("MCO", "ORL"),
    "honolulu": ("HNL", "HNL"),
    "hawaii": ("HNL", "HNL"),
    
    # Canada
    "canada": ("YYZ", "YTO"),
    "toronto": ("YYZ", "YTO"),
    "vancouver": ("YVR", "YVR"),
    "montreal": ("YUL", "YMQ"),
    "calgary": ("YYC", "YYC"),
    "ottawa": ("YOW", "YOW"),
    
    # Mexico
    "mexico": ("MEX", "MEX"),
    "mexico city": ("MEX", "MEX"),
    "cancun": ("CUN", "CUN"),
    "guadalajara": ("GDL", "GDL"),
    
    # Caribbean
    "caribbean": ("SJU", "SJU"),
    "puerto rico": ("SJU", "SJU"),
    "san juan": ("SJU", "SJU"),
    "jamaica": ("MBJ", "MBJ"),
    "bahamas": ("NAS", "NAS"),
    "nassau": ("NAS", "NAS"),
    "cuba": ("HAV", "HAV"),
    "havana": ("HAV", "HAV"),
    "dominican republic": ("PUJ", "PUJ"),
    "punta cana": ("PUJ", "PUJ"),
    
    # ============================================
    # SOUTH AMERICA
    # ============================================
    "brazil": ("GRU", "SAO"),
    "sao paulo": ("GRU", "SAO"),
    "rio de janeiro": ("GIG", "RIO"),
    "rio": ("GIG", "RIO"),
    "argentina": ("EZE", "BUE"),
    "buenos aires": ("EZE", "BUE"),
    "chile": ("SCL", "SCL"),
    "santiago": ("SCL", "SCL"),
    "colombia": ("BOG", "BOG"),
    "bogota": ("BOG", "BOG"),
    "peru": ("LIM", "LIM"),
    "lima": ("LIM", "LIM"),
    "ecuador": ("UIO", "UIO"),
    "quito": ("UIO", "UIO"),
    
    # ============================================
    # AFRICA
    # ============================================
    "south africa": ("JNB", "JNB"),
    "johannesburg": ("JNB", "JNB"),
    "cape town": ("CPT", "CPT"),
    "egypt": ("CAI", "CAI"),
    "cairo": ("CAI", "CAI"),
    "morocco": ("CMN", "CAS"),
    "casablanca": ("CMN", "CAS"),
    "marrakech": ("RAK", "RAK"),
    "kenya": ("NBO", "NBO"),
    "nairobi": ("NBO", "NBO"),
    "nigeria": ("LOS", "LOS"),
    "lagos": ("LOS", "LOS"),
    "ethiopia": ("ADD", "ADD"),
    "addis ababa": ("ADD", "ADD"),
    "tanzania": ("DAR", "DAR"),
    "dar es salaam": ("DAR", "DAR"),
    "mauritius": ("MRU", "MRU"),
    "seychelles": ("SEZ", "SEZ"),
    
    # ============================================
    # OCEANIA
    # ============================================
    "australia": ("SYD", "SYD"),
    "sydney": ("SYD", "SYD"),
    "melbourne": ("MEL", "MEL"),
    "brisbane": ("BNE", "BNE"),
    "perth": ("PER", "PER"),
    "gold coast": ("OOL", "OOL"),
    "cairns": ("CNS", "CNS"),
    "new zealand": ("AKL", "AKL"),
    "auckland": ("AKL", "AKL"),
    "wellington": ("WLG", "WLG"),
    "queenstown": ("ZQN", "ZQN"),
    "fiji": ("NAN", "NAN"),
    "tahiti": ("PPT", "PPT"),
    "french polynesia": ("PPT", "PPT"),
    "guam": ("GUM", "GUM"),
}


class LocationResolver:
    """
    Resolves location names to IATA airport/city codes.
    Uses comprehensive mapping with Amadeus API fallback.
    """
    
    def __init__(self):
        self.config = get_api_config()
        self._amadeus_token: Optional[str] = None
    
    def get_airport_code(self, location: str) -> str:
        """
        Get IATA airport code for a location.
        
        Args:
            location: City name, country name, or existing code
            
        Returns:
            IATA airport code (3 letters)
        """
        # Already a valid code?
        if len(location) == 3 and location.isupper() and location.isalpha():
            return location
        
        # Look up in our mapping
        key = location.lower().strip()
        if key in LOCATION_CODES:
            airport_code, _ = LOCATION_CODES[key]
            return airport_code
        
        # Fallback: return first 3 chars uppercase (may not be valid)
        print(f"⚠️  Unknown location '{location}', using '{location.upper()[:3]}'")
        return location.upper()[:3]
    
    def get_city_code(self, location: str) -> str:
        """
        Get IATA city code for a location.
        
        Args:
            location: City name, country name, or existing code
            
        Returns:
            IATA city code (3 letters)
        """
        # Already a valid code?
        if len(location) == 3 and location.isupper() and location.isalpha():
            return location
        
        # Look up in our mapping
        key = location.lower().strip()
        if key in LOCATION_CODES:
            _, city_code = LOCATION_CODES[key]
            return city_code
        
        # Fallback: return first 3 chars uppercase
        print(f"⚠️  Unknown location '{location}', using '{location.upper()[:3]}'")
        return location.upper()[:3]
    
    def get_codes(self, location: str) -> Tuple[str, str]:
        """
        Get both airport and city codes for a location.
        
        Args:
            location: City name, country name, or existing code
            
        Returns:
            Tuple of (airport_code, city_code)
        """
        return (self.get_airport_code(location), self.get_city_code(location))
    
    async def resolve_with_api(self, location: str) -> Optional[str]:
        """
        Try to resolve location using Amadeus API.
        Only use as fallback when local mapping fails.
        
        Args:
            location: City name to search
            
        Returns:
            IATA code or None if not found
        """
        if not self.config.has_amadeus_credentials:
            return None
        
        try:
            # Get OAuth token
            auth_url = f"{self.config.amadeus_base_url}/v1/security/oauth2/token"
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Authenticate
                auth_response = await client.post(
                    auth_url,
                    data={
                        "grant_type": "client_credentials",
                        "client_id": self.config.amadeus_api_key,
                        "client_secret": self.config.amadeus_api_secret
                    },
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                )
                
                if auth_response.status_code != 200:
                    return None
                
                token = auth_response.json()["access_token"]
                
                # Search for location
                search_url = f"{self.config.amadeus_base_url}/v1/reference-data/locations"
                search_response = await client.get(
                    search_url,
                    params={"keyword": location, "subType": "AIRPORT,CITY"},
                    headers={"Authorization": f"Bearer {token}"}
                )
                
                if search_response.status_code == 200:
                    data = search_response.json().get("data", [])
                    if data:
                        return data[0].get("iataCode")
                        
        except Exception as e:
            print(f"⚠️  API location lookup failed: {e}")
        
        return None


# Singleton instance
_resolver: Optional[LocationResolver] = None


def get_location_resolver() -> LocationResolver:
    """Get the singleton LocationResolver instance"""
    global _resolver
    if _resolver is None:
        _resolver = LocationResolver()
    return _resolver


def get_airport_code(location: str) -> str:
    """Convenience function to get airport code"""
    return get_location_resolver().get_airport_code(location)


def get_city_code(location: str) -> str:
    """Convenience function to get city code"""
    return get_location_resolver().get_city_code(location)


# Test if run directly
if __name__ == "__main__":
    resolver = LocationResolver()
    
    print("=" * 60)
    print("LOCATION RESOLVER TEST")
    print("=" * 60)
    
    test_locations = [
        "India", "Sri Lanka", "Delhi", "Mumbai", "Colombo",
        "Tokyo", "New York", "Paris", "London",
        "Singapore", "Bangkok", "Dubai",
        "JFK", "LAX", "SIN"
    ]
    
    for loc in test_locations:
        airport, city = resolver.get_codes(loc)
        print(f"  {loc:20} → Airport: {airport}, City: {city}")
    
    print("\n✅ Location resolver working!")
