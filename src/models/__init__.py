"""
This file makes the models directory a Python package.
It also exports all models for easy importing.
"""

# Import all models so they can be imported directly from src.models
from .travel_request import TravelRequest
from .flight import Flight, FlightSegment
from .hotel import Hotel
from .activity import Activity, ActivityCategory

# Future models:
# from .itinerary import TripItinerary, DayPlan, DayPlanItem

# This allows you to do:
# from src.models import TravelRequest, Flight, Hotel, Activity
# Instead of:
# from src.models.travel_request import TravelRequest

__all__ = [
    'TravelRequest',
    'Flight',
    'FlightSegment',
    'Hotel',
    'Activity',
    'ActivityCategory',
    # 'TripItinerary',
]