"""
API Configuration
Centralized configuration for external API services.
Supports real APIs with automatic fallback to mock data.
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from functools import lru_cache
from dotenv import load_dotenv

load_dotenv()


class APIConfig(BaseSettings):
    """
    Configuration for all external APIs.
    
    Set USE_MOCK_DATA=true to force mock data (useful for testing).
    If API keys are missing, mock data is used automatically.
    """
    
    # ============================================
    # GENERAL SETTINGS
    # ============================================
    use_mock_data: bool = False  # Force mock data if True
    
    # ============================================
    # AMADEUS API (Flights & Hotels)
    # ============================================
    # Get free API keys at: https://developers.amadeus.com/
    amadeus_api_key: Optional[str] = None
    amadeus_api_secret: Optional[str] = None
    amadeus_base_url: str = "https://test.api.amadeus.com"  # Use test environment
    
    # ============================================
    # GEOAPIFY API (Activities/POIs)
    # ============================================
    # Get free API key at: https://myprojects.geoapify.com/
    # Free tier: 3000 API calls/day (no credit card required)
    geoapify_api_key: Optional[str] = None
    geoapify_base_url: str = "https://api.geoapify.com/v2"
    
    # ============================================
    # OPEN-METEO API (Weather - no key needed!)
    # ============================================
    openmeteo_base_url: str = "https://api.open-meteo.com/v1"
    
    # ============================================
    # PERPLEXITY API (LLM - already configured)
    # ============================================
    perplexity_api_key: Optional[str] = None
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"
    
    # ============================================
    # HELPER PROPERTIES
    # ============================================
    
    @property
    def has_amadeus_credentials(self) -> bool:
        """Check if Amadeus API credentials are configured"""
        return bool(self.amadeus_api_key and self.amadeus_api_secret)
    
    @property
    def has_geoapify_key(self) -> bool:
        """Check if Geoapify API key is configured"""
        return bool(self.geoapify_api_key)

    @property
    def should_use_mock_flights(self) -> bool:
        """Determine if mock flight data should be used"""
        return self.use_mock_data or not self.has_amadeus_credentials
    
    @property
    def should_use_mock_hotels(self) -> bool:
        """Determine if mock hotel data should be used"""
        return self.use_mock_data or not self.has_amadeus_credentials
    
    @property
    def should_use_mock_activities(self) -> bool:
        """Determine if mock activity data should be used"""
        return self.use_mock_data or not self.has_geoapify_key


@lru_cache()
def get_api_config() -> APIConfig:
    """Get cached API configuration instance"""
    return APIConfig()


def print_api_status():
    """Print status of all API configurations"""
    config = get_api_config()
    
    print("\n" + "=" * 60)
    print("🔧 API CONFIGURATION STATUS")
    print("=" * 60)
    
    print(f"\n📊 Force Mock Data: {config.use_mock_data}")
    
    print("\n🛫 FLIGHTS & HOTELS (Amadeus API):")
    if config.has_amadeus_credentials:
        print("   ✅ API credentials configured")
        print(f"   📍 Base URL: {config.amadeus_base_url}")
    else:
        print("   ⚠️  No credentials - using MOCK DATA")
        print("   💡 Get free key: https://developers.amadeus.com/")
    
    print("\n🎯 ACTIVITIES (Geoapify API):")
    if config.has_geoapify_key:
        print("   ✅ API key configured")
        print(f"   📍 Base URL: {config.geoapify_base_url}")
    else:
        print("   ⚠️  No API key - using MOCK DATA")
        print("   💡 Get free key: https://myprojects.geoapify.com/")
    
    print("\n🌤️ WEATHER (Open-Meteo API):")
    print("   ✅ No key required - FREE unlimited access!")
    print(f"   📍 Base URL: {config.openmeteo_base_url}")
    
    print("\n🤖 LLM (Perplexity API):")
    if config.perplexity_api_key:
        print("   ✅ API key configured")
    else:
        print("   ❌ No API key - LLM features won't work")
    
    print("\n" + "=" * 60)


# Test if run directly
if __name__ == "__main__":
    print_api_status()
