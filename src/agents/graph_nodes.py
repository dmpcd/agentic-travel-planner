"""
LangGraph Node Functions
Each function is a node in the travel planning workflow graph.
Nodes receive state, execute their task, and return updated state.
"""
from typing import Dict, Any
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from src.agents.state import TravelPlanState
from src.agents.flight_agent import FlightAgent
from src.agents.hotel_agent import HotelAgent
from src.agents.activity_agent import ActivityAgent
from src.agents.budget_agent import BudgetAgent
from src.agents.base_agent import BaseAgent


# ============================================
# SEARCH NODES - Parallel execution possible
# ============================================

async def flight_search_node(state: TravelPlanState) -> Dict[str, Any]:
    """
    Node: Search for flights
    
    Executes FlightAgent to find and recommend flights.
    Updates state with flight options and recommendations.
    """
    print("\n" + "=" * 70)
    print("🛫 GRAPH NODE: Searching for flights...")
    print("=" * 70)
    
    try:
        agent = FlightAgent()
        
        results = await agent.execute({
            "origin": state["origin"],
            "destination": state["destination"],
            "departure_date": state["departure_date"],
            "return_date": state["return_date"],
            "travelers": state["travelers"],
            "max_price": (state["budget"] * 0.4 / state["travelers"]) if state.get("budget") else None,
            "preferences": state.get("flight_preferences")
        })
        
        print(f"✓ Found {results['total_flights_found']} flight options")
        
        return {
            "flights": results
        }
        
    except Exception as e:
        print(f"✗ Error in flight search: {str(e)}")
        return {
            "flights": {},
            "errors": [f"Flight search failed: {str(e)}"]
        }


async def hotel_search_node(state: TravelPlanState) -> Dict[str, Any]:
    """
    Node: Search for hotels
    
    Executes HotelAgent to find and recommend accommodations.
    Updates state with hotel options and recommendations.
    """
    print("\n" + "=" * 70)
    print("🏨 GRAPH NODE: Searching for hotels...")
    print("=" * 70)
    
    try:
        agent = HotelAgent()
        
        results = await agent.execute({
            "destination": state["destination"],
            "check_in": state["departure_date"],
            "check_out": state["return_date"],
            "guests": state["travelers"],
            "max_price_per_night": (state["budget"] * 0.35 / state["days"]) if state.get("budget") else None,
            "preferences": state.get("hotel_preferences")
        })
        
        print(f"✓ Found {results['total_found']} hotel options")
        
        return {
            "hotels": results
        }
        
    except Exception as e:
        print(f"✗ Error in hotel search: {str(e)}")
        return {
            "hotels": {},
            "errors": [f"Hotel search failed: {str(e)}"]
        }


async def activity_search_node(state: TravelPlanState) -> Dict[str, Any]:
    """
    Node: Search for activities
    
    Executes ActivityAgent to find and recommend things to do.
    Updates state with activity options and recommendations.
    """
    print("\n" + "=" * 70)
    print("🎯 GRAPH NODE: Finding activities...")
    print("=" * 70)
    
    try:
        agent = ActivityAgent()
        
        results = await agent.execute({
            "destination": state["destination"],
            "interests": state["interests"],
            "days": state["days"],
            "budget": (state["budget"] * 0.15) if state.get("budget") else None
        })
        
        print(f"✓ Found {results['total_found']} activity options")
        
        return {
            "activities": results
        }
        
    except Exception as e:
        print(f"✗ Error in activity search: {str(e)}")
        return {
            "activities": {},
            "errors": [f"Activity search failed: {str(e)}"]
        }


# ============================================
# ANALYSIS NODES
# ============================================

async def budget_analysis_node(state: TravelPlanState) -> Dict[str, Any]:
    """
    Node: Analyze budget
    
    Executes BudgetAgent to calculate costs and check budget constraints.
    Determines if optimization is needed.
    """
    print("\n" + "=" * 70)
    print("💰 GRAPH NODE: Analyzing budget...")
    print("=" * 70)
    
    try:
        agent = BudgetAgent()
        
        results = await agent.execute({
            "flights": state["flights"],
            "hotels": state["hotels"],
            "activities": state["activities"],
            "total_budget": state.get("budget"),
            "travelers": state["travelers"],
            "days": state["days"]
        })
        
        total_cost = results["total_cost"]
        within_budget = results["within_budget"]
        
        print(f"✓ Total cost: ${total_cost:,.2f}")
        if state.get("budget"):
            status = "Within budget ✓" if within_budget else "Over budget ✗"
            print(f"  {status}")
        
        # Determine if we need optimization
        needs_optimization = False
        if state.get("budget") and not within_budget:
            if state["optimization_iteration"] < 3:  # Max 3 optimization attempts
                needs_optimization = True
                print("  → Will attempt to optimize costs")
        
        return {
            "budget_analysis": results,
            "within_budget": within_budget,
            "total_cost": total_cost,
            "needs_optimization": needs_optimization,
            "optimization_iteration": state["optimization_iteration"] + 1 if needs_optimization else state["optimization_iteration"]
        }
        
    except Exception as e:
        print(f"✗ Error in budget analysis: {str(e)}")
        return {
            "budget_analysis": {},
            "errors": [f"Budget analysis failed: {str(e)}"]
        }


async def generate_summary_node(state: TravelPlanState) -> Dict[str, Any]:
    """
    Node: Generate final trip summary
    
    Uses AI to create an engaging summary of the complete travel plan.
    This is the final node before END.
    """
    print("\n" + "=" * 70)
    print("📋 GRAPH NODE: Generating trip summary...")
    print("=" * 70)
    
    try:
        # Use a base agent for summary generation
        agent = BaseAgent.__new__(BaseAgent)
        agent.__init__(
            name="Summary Generator",
            description="Creates engaging trip summaries"
        )
        
        # Get recommended options
        hotel = state["hotels"].get("recommended", {})
        hotel_name = hotel.get("name", "Unknown Hotel")
        hotel_price = hotel.get("price_per_night", 0)
        
        num_activities = len(state["activities"].get("recommended", []))
        
        summary_prompt = f"""Create an engaging trip summary for this travel plan:

DESTINATION: {state['destination']}
DURATION: {state['days']} days
TRAVELERS: {state['travelers']}

SELECTED OPTIONS:
- Flights: ${state['budget_analysis']['breakdown']['flights']:,.2f}
- Hotel: {hotel_name} - ${hotel_price}/night
- Activities: {num_activities} curated experiences
- Total Cost: ${state['total_cost']:,.2f}

USER INTERESTS: {', '.join(state['interests']) if state['interests'] else 'General tourism'}

Create an exciting 5-7 sentence summary that highlights why this is a perfect trip plan.
Make it engaging and mention specific highlights."""
        
        summary = await agent.think(summary_prompt)
        
        print("✓ Trip summary generated")
        
        return {
            "trip_summary": summary
        }
        
    except Exception as e:
        print(f"✗ Error generating summary: {str(e)}")
        return {
            "trip_summary": "Trip plan created successfully. Details available in the full breakdown.",
            "errors": [f"Summary generation failed: {str(e)}"]
        }


# ============================================
# CONDITIONAL ROUTING FUNCTIONS
# ============================================

def should_optimize_route(state: TravelPlanState) -> str:
    """
    Conditional edge: Determine next step after budget analysis.
    
    Returns:
        "optimize" - Need to find cheaper options
        "generate_summary" - Budget is good, proceed to summary
    """
    if state["needs_optimization"]:
        print("\n⚠️  ROUTING: Budget exceeded, will optimize...")
        return "optimize"
    else:
        print("\n✓ ROUTING: Budget OK, generating summary...")
        return "generate_summary"


def check_max_iterations_route(state: TravelPlanState) -> str:
    """
    Conditional edge: Check if we've tried too many optimization iterations.
    
    Returns:
        "search_flights" - Try another optimization round
        "generate_summary" - Give up and generate summary with current options
    """
    if state["optimization_iteration"] >= 3:
        print("\n⚠️  ROUTING: Max optimization attempts reached, proceeding with current plan...")
        return "generate_summary"
    else:
        print(f"\n🔄 ROUTING: Optimization attempt {state['optimization_iteration']}/3...")
        return "search_flights"


# ============================================
# TESTING
# ============================================

if __name__ == "__main__":
    import asyncio
    from datetime import date
    from src.agents.state import create_initial_state
    
    async def test_nodes():
        print("\n" + "=" * 70)
        print("TESTING GRAPH NODES")
        print("=" * 70)
        
        # Create initial state
        state = create_initial_state({
            "origin": "New York",
            "destination": "Tokyo",
            "departure_date": date(2026, 4, 15),
            "return_date": date(2026, 4, 20),
            "budget": 3000.0,
            "travelers": 2,
            "interests": ["food", "technology"]
        })
        
        # Test flight node
        flight_update = await flight_search_node(state)
        state.update(flight_update)
        
        # Test hotel node
        hotel_update = await hotel_search_node(state)
        state.update(hotel_update)
        
        # Test activity node
        activity_update = await activity_search_node(state)
        state.update(activity_update)
        
        # Test budget node
        budget_update = await budget_analysis_node(state)
        state.update(budget_update)
        
        # Test routing
        next_step = should_optimize_route(state)
        print(f"\nNext step: {next_step}")
        
        # Test summary node
        summary_update = await generate_summary_node(state)
        state.update(summary_update)
        
        print("\n" + "=" * 70)
        print("ALL NODES TESTED SUCCESSFULLY!")
        print("=" * 70)
        print(f"\nFinal cost: ${state['total_cost']:,.2f}")
        print(f"Within budget: {state['within_budget']}")
        print(f"\nSummary:\n{state['trip_summary'][:200]}...")
    
    asyncio.run(test_nodes())
