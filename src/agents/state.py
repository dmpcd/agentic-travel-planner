"""
LangGraph State Definition
Defines the shared state that flows through all nodes in the travel planning graph.
"""
from typing import TypedDict, List, Dict, Any, Annotated, Optional
import operator
from datetime import date


class TravelPlanState(TypedDict):
    """
    Shared state across all agents in the LangGraph workflow.
    
    This state is passed between nodes and updated as the graph executes.
    Each node can read from and write to this state.
    """
    
    # ============================================
    # INPUT - User's travel request
    # ============================================
    origin: str
    destination: str
    departure_date: str  # ISO format: YYYY-MM-DD
    return_date: str
    budget: Optional[float]
    travelers: int
    interests: List[str]
    hotel_preferences: Optional[str]
    flight_preferences: Optional[str]
    
    # ============================================
    # AGENT OUTPUTS - Results from each agent
    # ============================================
    flights: Dict[str, Any]  # FlightAgent results
    hotels: Dict[str, Any]   # HotelAgent results
    activities: Dict[str, Any]  # ActivityAgent results
    budget_analysis: Dict[str, Any]  # BudgetAgent results
    
    # ============================================
    # CONTROL FLOW - Graph routing decisions
    # ============================================
    within_budget: bool  # Is the plan within budget?
    optimization_iteration: int  # How many times we've tried to optimize
    needs_optimization: bool  # Should we try to optimize costs?
    
    # ============================================
    # OUTPUT - Final results
    # ============================================
    trip_summary: str  # AI-generated trip summary
    total_cost: float  # Total trip cost
    
    # ============================================
    # ERROR HANDLING - Accumulated errors
    # ============================================
    errors: Annotated[List[str], operator.add]  # List of any errors encountered
    
    # ============================================
    # METADATA
    # ============================================
    days: int  # Trip duration in days
    created_at: str  # Timestamp


# ============================================
# HELPER FUNCTIONS
# ============================================

def create_initial_state(input_data: Dict[str, Any]) -> TravelPlanState:
    """
    Create the initial state from user input.
    
    Args:
        input_data: Raw input from TravelRequest
        
    Returns:
        Initial TravelPlanState ready for graph execution
    """
    # Calculate trip duration
    from datetime import datetime
    departure = datetime.fromisoformat(str(input_data["departure_date"]))
    return_date = datetime.fromisoformat(str(input_data["return_date"]))
    days = (return_date - departure).days
    
    return TravelPlanState(
        # Input fields
        origin=input_data["origin"],
        destination=input_data["destination"],
        departure_date=str(input_data["departure_date"]),
        return_date=str(input_data["return_date"]),
        budget=input_data.get("budget"),
        travelers=input_data.get("travelers", 1),
        interests=input_data.get("interests", []),
        hotel_preferences=input_data.get("hotel_preferences"),
        flight_preferences=input_data.get("flight_preferences"),
        
        # Initialize agent outputs as empty
        flights={},
        hotels={},
        activities={},
        budget_analysis={},
        
        # Initialize control flow
        within_budget=True,  # Assume true initially
        optimization_iteration=0,
        needs_optimization=False,
        
        # Initialize outputs
        trip_summary="",
        total_cost=0.0,
        
        # Initialize error list
        errors=[],
        
        # Metadata
        days=days,
        created_at=datetime.now().isoformat()
    )


def state_to_dict(state: TravelPlanState) -> Dict[str, Any]:
    """Convert state to a regular dictionary for JSON serialization"""
    return dict(state)


if __name__ == "__main__":
    # Test the state creation
    from datetime import date
    
    test_input = {
        "origin": "New York",
        "destination": "Tokyo",
        "departure_date": date(2026, 4, 15),
        "return_date": date(2026, 4, 20),
        "budget": 3000.0,
        "travelers": 2,
        "interests": ["food", "technology", "culture"]
    }
    
    state = create_initial_state(test_input)
    
    print("=" * 70)
    print("TRAVEL PLAN STATE CREATED")
    print("=" * 70)
    print(f"\nDestination: {state['destination']}")
    print(f"Days: {state['days']}")
    print(f"Budget: ${state['budget']}")
    print(f"Travelers: {state['travelers']}")
    print(f"Interests: {', '.join(state['interests'])}")
    print("\nState structure is ready for LangGraph!")
