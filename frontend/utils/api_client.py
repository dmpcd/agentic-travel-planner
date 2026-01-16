"""
API Client for Travel Planner Backend
Wraps the LangGraph backend for use in Streamlit.
"""
import asyncio
from datetime import date
from typing import Dict, Any, Optional, List
from dataclasses import dataclass


@dataclass
class TripRequest:
    """Travel request data structure."""
    origin: str
    destination: str
    departure_date: date
    return_date: date
    travelers: int = 2
    budget: Optional[float] = None
    interests: List[str] = None
    hotel_preferences: Optional[str] = None
    flight_preferences: Optional[str] = None
    additional_notes: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API call."""
        return {
            "origin": self.origin,
            "destination": self.destination,
            "departure_date": self.departure_date.isoformat(),
            "return_date": self.return_date.isoformat(),
            "travelers": self.travelers,
            "budget": self.budget,
            "interests": self.interests or [],
            "hotel_preferences": self.hotel_preferences,
            "flight_preferences": self.flight_preferences,
            "additional_notes": self.additional_notes,
        }


@dataclass
class TripResults:
    """Parsed trip planning results."""
    outbound_flights: List[Dict[str, Any]]
    return_flights: List[Dict[str, Any]]
    hotels: List[Dict[str, Any]]
    activities: List[Dict[str, Any]]
    total_cost: float
    within_budget: bool
    summary: str
    budget_analysis: Dict[str, Any]
    errors: List[str]
    
    @property
    def flights(self) -> List[Dict[str, Any]]:
        """All flights combined."""
        return self.outbound_flights + self.return_flights
    
    @classmethod
    def from_state(cls, state: Dict[str, Any]) -> "TripResults":
        """Create TripResults from LangGraph state."""
        flights_data = state.get("flights", {})
        hotels_data = state.get("hotels", {})
        activities_data = state.get("activities", {})
        
        return cls(
            outbound_flights=flights_data.get("outbound_flights", []),
            return_flights=flights_data.get("return_flights", []),
            hotels=hotels_data.get("hotels", []),
            activities=activities_data.get("activities", []),
            total_cost=state.get("total_cost", 0),
            within_budget=state.get("within_budget", True),
            summary=state.get("trip_summary", ""),
            budget_analysis=state.get("budget_analysis", {}),
            errors=state.get("errors", [])
        )


class TravelPlannerClient:
    """
    Client for the Travel Planner backend.
    Provides a clean interface for the Streamlit app.
    """
    
    def __init__(self):
        self._loop = None
    
    def _get_loop(self):
        """Get or create an event loop."""
        try:
            return asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop
    
    def plan_trip(self, request: TripRequest) -> TripResults:
        """
        Execute the travel planning workflow.
        
        Args:
            request: TripRequest with travel details
            
        Returns:
            TripResults with flights, hotels, activities, etc.
        """
        import sys
        import os
        
        # Add project root to path
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
        
        from src.agents.travel_graph import plan_trip
        
        loop = self._get_loop()
        state = loop.run_until_complete(plan_trip(request.to_dict()))
        
        return TripResults.from_state(state)
    
    @staticmethod
    def get_outbound_flights(results: TripResults) -> List[Dict[str, Any]]:
        """Get outbound flights from results."""
        # First half of flights are typically outbound
        mid = len(results.flights) // 2
        return results.flights[:mid] if mid > 0 else results.flights
    
    @staticmethod
    def get_return_flights(results: TripResults) -> List[Dict[str, Any]]:
        """Get return flights from results."""
        mid = len(results.flights) // 2
        return results.flights[mid:] if mid > 0 else []
    
    @staticmethod
    def get_top_hotels(results: TripResults, limit: int = 5) -> List[Dict[str, Any]]:
        """Get top hotel recommendations."""
        return results.hotels[:limit]
    
    @staticmethod
    def get_activities_by_category(results: TripResults) -> Dict[str, List[Dict[str, Any]]]:
        """Group activities by category."""
        by_category = {}
        for activity in results.activities:
            category = activity.get("category", "other")
            # Handle enum values
            if hasattr(category, "value"):
                category = category.value
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(activity)
        return by_category
