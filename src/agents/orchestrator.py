"""
Travel Planner Orchestrator
Convenience functions for executing the LangGraph travel planning workflow.

This simplified module replaces the previous OrchestratorAgent class.
The actual orchestration is handled by the LangGraph workflow.
"""
from typing import Any, Dict
from datetime import datetime

from src.agents.travel_graph import travel_planning_app
from src.agents.state import create_initial_state
from src.models.travel_request import TravelRequest


async def plan_trip(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute the full trip planning workflow using LangGraph.
    
    This is the main entry point for the travel planner.
    
    Args:
        input_data: Dictionary with travel request data containing:
            - origin: Starting location
            - destination: Travel destination
            - departure_date: Trip start date
            - return_date: Trip end date
            - budget: Total budget (optional)
            - travelers: Number of travelers
            - interests: List of interests (optional)
            - hotel_preferences: Hotel preferences (optional)
            - flight_preferences: Flight preferences (optional)
    
    Returns:
        Complete trip plan with all recommendations
    """
    print("\n" + "=" * 70)
    print("🌍 LANGGRAPH TRAVEL PLANNER")
    print("=" * 70)
    
    # Parse and display the request
    request = TravelRequest(**input_data)
    days = (request.return_date - request.departure_date).days
    
    print(f"\n📋 Trip Request:")
    print(f"   From: {request.origin}")
    print(f"   To: {request.destination}")
    print(f"   Dates: {request.departure_date} to {request.return_date} ({days} days)")
    print(f"   Travelers: {request.travelers}")
    print(f"   Budget: ${request.budget:,.2f}" if request.budget else "   Budget: Flexible")
    print(f"   Interests: {', '.join(request.interests)}" if request.interests else "")
    
    print("\n" + "-" * 70)
    print("🚀 Executing LangGraph workflow...")
    print("-" * 70)
    
    # Create initial state
    initial_state = create_initial_state(input_data)
    
    # Execute the graph
    final_state = await travel_planning_app.ainvoke(initial_state)
    
    print("\n" + "=" * 70)
    print("✓ LANGGRAPH EXECUTION COMPLETE!")
    print("=" * 70)
    
    # Format and return the output
    return {
        "trip_summary": final_state["trip_summary"],
        "destination": final_state["destination"],
        "dates": {
            "departure": final_state["departure_date"],
            "return": final_state["return_date"],
            "duration_days": final_state["days"]
        },
        "travelers": final_state["travelers"],
        "flights": final_state["flights"],
        "hotels": final_state["hotels"],
        "activities": final_state["activities"],
        "budget": final_state["budget_analysis"],
        "created_at": final_state["created_at"],
        
        # LangGraph metadata
        "metadata": {
            "optimization_iterations": final_state["optimization_iteration"],
            "within_budget": final_state["within_budget"],
            "total_cost": final_state["total_cost"],
            "errors": final_state["errors"]
        }
    }


# ============================================
# TESTING
# ============================================

if __name__ == "__main__":
    import asyncio
    from datetime import date
    
    async def test():
        print("\n" + "=" * 70)
        print("🌍 TESTING TRAVEL PLANNER")
        print("=" * 70)
        
        # Plan a complete trip
        result = await plan_trip({
            "origin": "New York",
            "destination": "Tokyo",
            "departure_date": date(2026, 4, 15),
            "return_date": date(2026, 4, 20),
            "budget": 3000.0,
            "travelers": 2,
            "interests": ["food", "technology", "culture"],
            "hotel_preferences": "close to city center",
            "flight_preferences": "prefer direct flights"
        })
        
        # Display results
        print("\n\n" + "=" * 70)
        print("YOUR COMPLETE TRAVEL PLAN")
        print("=" * 70)
        
        print("\n" + "-" * 70)
        print("TRIP SUMMARY:")
        print("-" * 70)
        print(result['trip_summary'])
        
        print("\n" + "-" * 70)
        print("BUDGET BREAKDOWN:")
        print("-" * 70)
        breakdown = result['budget']['breakdown']
        print(f"Flights:      ${breakdown['flights']:>10,.2f}")
        print(f"Hotels:       ${breakdown['hotels']:>10,.2f}")
        print(f"Activities:   ${breakdown['activities']:>10,.2f}")
        print(f"Meals & Misc: ${breakdown['meals_and_misc']:>10,.2f}")
        print("-" * 70)
        print(f"TOTAL:        ${breakdown['total']:>10,.2f}")
        print(f"BUDGET:       ${breakdown['budget']:>10,.2f}")
        print(f"REMAINING:    ${breakdown['remaining']:>10,.2f}")
        
        print("\n" + "-" * 70)
        print("RECOMMENDED HOTEL:")
        print("-" * 70)
        hotel = result['hotels']['recommended']
        print(f"{hotel['name']}")
        print(f"Rating: {hotel['user_rating']}/10")
        print(f"Price: ${hotel['price_per_night']}/night")
        
        print("\n" + "-" * 70)
        print("RECOMMENDED ACTIVITIES:")
        print("-" * 70)
        for i, activity in enumerate(result['activities']['recommended'][:5], 1):
            print(f"{i}. {activity['name']} - {activity['category']}")
        
        print("\n\n" + "=" * 70)
        print("TRAVEL PLANNER TEST COMPLETE!")
        print("=" * 70)
        
    asyncio.run(test())
