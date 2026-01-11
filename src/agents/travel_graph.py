"""
LangGraph Travel Planning Workflow
Defines the complete graph structure for the agentic travel planner.
"""
from langgraph.graph import StateGraph, END
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from src.agents.state import TravelPlanState
from src.agents.graph_nodes import (
    flight_search_node,
    hotel_search_node,
    activity_search_node,
    budget_analysis_node,
    generate_summary_node,
    should_optimize_route,
)


def create_travel_planning_graph():
    """
    Create and compile the LangGraph workflow for travel planning.
    
    Graph Structure:
    
        START
          ↓
    [Flight Search] ← (optimization loop)
          ↓              ↑
    [Hotel Search]       |
          ↓              |
    [Activity Search]    |
          ↓              |
    [Budget Analysis] ---+
          ↓
      (conditional)
          ↓
    [Generate Summary]
          ↓
         END
    
    Returns:
        Compiled LangGraph application ready for execution
    """
    
    # Initialize the graph with our state
    workflow = StateGraph(TravelPlanState)
    
    # ============================================
    # ADD NODES
    # ============================================
    print("Building LangGraph workflow...")
    
    workflow.add_node("search_flights", flight_search_node)
    workflow.add_node("search_hotels", hotel_search_node)
    workflow.add_node("search_activities", activity_search_node)
    workflow.add_node("analyze_budget", budget_analysis_node)
    workflow.add_node("generate_summary", generate_summary_node)
    
    print("✓ Added 5 nodes to the graph")
    
    # ============================================
    # ADD EDGES - Define the workflow
    # ============================================
    
    # Set entry point
    workflow.set_entry_point("search_flights")
    print("✓ Set entry point: search_flights")
    
    # Sequential flow for searches
    workflow.add_edge("search_flights", "search_hotels")
    workflow.add_edge("search_hotels", "search_activities")
    workflow.add_edge("search_activities", "analyze_budget")
    print("✓ Added sequential edges")
    
    # Conditional routing after budget analysis
    workflow.add_conditional_edges(
        "analyze_budget",
        should_optimize_route,
        {
            "optimize": "search_flights",  # Loop back to try cheaper options
            "generate_summary": "generate_summary"  # Proceed to summary
        }
    )
    print("✓ Added conditional routing")
    
    # Summary leads to END
    workflow.add_edge("generate_summary", END)
    print("✓ Connected to END")
    
    # ============================================
    # COMPILE THE GRAPH
    # ============================================
    app = workflow.compile()
    print("✓ Graph compiled successfully!")
    
    return app


# ============================================
# VISUALIZATION
# ============================================

def visualize_graph(app):
    """
    Generate a visual representation of the graph.
    Requires graphviz to be installed.
    """
    try:
        from IPython.display import Image, display
        display(Image(app.get_graph().draw_mermaid_png()))
    except:
        print("Graph visualization requires IPython and graphviz")
        print("\nGraph structure (text):")
        print("""
        START
          ↓
    ┌─→ [Flight Search]
    │     ↓
    │   [Hotel Search]
    │     ↓
    │   [Activity Search]
    │     ↓
    │   [Budget Analysis]
    │     ↓
    │   Is within budget?
    │     ├─ No → (loop back) ─┘
    │     └─ Yes ↓
    │   [Generate Summary]
    │     ↓
    └──  END
        """)


# ============================================
# CREATE THE COMPILED GRAPH (singleton)
# ============================================
travel_planning_app = create_travel_planning_graph()


# ============================================
# CONVENIENCE FUNCTION
# ============================================

async def plan_trip(input_data: dict) -> dict:
    """
    Convenience function to execute the travel planning graph.
    
    Args:
        input_data: Dictionary with travel request data
        
    Returns:
        Complete state after graph execution
    """
    from src.agents.state import create_initial_state
    
    print("\n" + "=" * 70)
    print("🌍 EXECUTING LANGGRAPH TRAVEL PLANNER")
    print("=" * 70)
    
    # Create initial state
    initial_state = create_initial_state(input_data)
    
    # Execute the graph!
    final_state = await travel_planning_app.ainvoke(initial_state)
    
    print("\n" + "=" * 70)
    print("✓ GRAPH EXECUTION COMPLETE")
    print("=" * 70)
    
    return final_state


# ============================================
# TESTING
# ============================================

if __name__ == "__main__":
    import asyncio
    from datetime import date
    
    async def test_graph():
        print("\n" + "=" * 70)
        print("TESTING COMPLETE LANGGRAPH WORKFLOW")
        print("=" * 70)
        
        # Test input
        test_input = {
            "origin": "New York",
            "destination": "Tokyo",
            "departure_date": date(2026, 4, 15),
            "return_date": date(2026, 4, 20),
            "budget": 3000.0,
            "travelers": 2,
            "interests": ["food", "technology", "culture"],
            "hotel_preferences": "close to city center",
            "flight_preferences": "prefer direct flights"
        }
        
        # Execute the graph
        result = await plan_trip(test_input)
        
        # Display results
        print("\n" + "=" * 70)
        print("FINAL RESULTS")
        print("=" * 70)
        
        print(f"\n📍 Destination: {result['destination']}")
        print(f"📅 Duration: {result['days']} days")
        print(f"👥 Travelers: {result['travelers']}")
        
        print("\n💰 BUDGET BREAKDOWN:")
        if result['budget_analysis']:
            breakdown = result['budget_analysis']['breakdown']
            print(f"  Flights:      ${breakdown['flights']:>10,.2f}")
            print(f"  Hotels:       ${breakdown['hotels']:>10,.2f}")
            print(f"  Activities:   ${breakdown['activities']:>10,.2f}")
            print(f"  Meals & Misc: ${breakdown['meals_and_misc']:>10,.2f}")
            print("  " + "-" * 40)
            print(f"  TOTAL:        ${breakdown['total']:>10,.2f}")
            print(f"  BUDGET:       ${breakdown['budget']:>10,.2f}")
            print(f"  REMAINING:    ${breakdown['remaining']:>10,.2f}")
        
        print("\n📋 TRIP SUMMARY:")
        print(result['trip_summary'])
        
        print("\n🔄 GRAPH METRICS:")
        print(f"  Optimization iterations: {result['optimization_iteration']}")
        print(f"  Within budget: {result['within_budget']}")
        print(f"  Errors encountered: {len(result['errors'])}")
        
        if result['errors']:
            print("\n⚠️  ERRORS:")
            for error in result['errors']:
                print(f"  - {error}")
        
        print("\n" + "=" * 70)
        print("✓ LANGGRAPH TEST COMPLETE!")
        print("=" * 70)
        
        # Show graph structure
        print("\n")
        visualize_graph(travel_planning_app)
    
    # Run the test
    asyncio.run(test_graph())
