"""
Travel Planning Tools

This package provides tools for searching flights, hotels, and activities.
Each tool supports both real API integration and mock data fallback:

- FlightSearchTool: Uses Amadeus API (fallback: mock data)
- HotelSearchTool: Uses Amadeus API (fallback: mock data)
- ActivitySearchTool: Uses Geoapify API (fallback: mock data)

Configuration is handled through environment variables:
- AMADEUS_API_KEY, AMADEUS_API_SECRET: For flights and hotels
- GEOAPIFY_API_KEY: For activities
- USE_MOCK_DATA: Set to 'true' to force mock data
"""

# Search tools
from .flight_search import FlightSearchTool
from .hotel_search import HotelSearchTool
from .activity_search import ActivitySearchTool

# API clients
from .api_config import APIConfig, get_api_config
from .amadeus_client import AmadeusClient
from .geoapify_client import GeoapifyClient

__all__ = [
    # Search tools
    'FlightSearchTool',
    'HotelSearchTool',
    'ActivitySearchTool',
    # Configuration
    'APIConfig',
    'get_api_config',
    # API clients
    'AmadeusClient',
    'GeoapifyClient',
]
