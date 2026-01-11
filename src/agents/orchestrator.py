"""
Orchestrator Agent
The master coordinator that manages the entire trip planning process.

NOW POWERED BY LANGGRAPH! 🎉
This orchestrator uses LangGraph for intelligent workflow management.
"""
from typing import Any, Dict
from datetime import datetime
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from src.agents.base_agent import BaseAgent
from src.agents.travel_graph import travel_planning_app, plan_trip
from src.agents.state import create_initial_state
from src.models.travel_request import TravelRequest


class OrchestratorAgent(BaseAgent):
    """
    The master coordinator agent that manages the entire trip planning process.
    
    NOW USING LANGGRAPH for workflow orchestration!
    
    Responsibilities:
    1. Parse and understand user requests
    2. Create initial state for the graph
    3. Execute the LangGraph workflow
    4. Return formatted results
    
    The actual orchestration is now handled by the LangGraph workflow,
    which provides:
    - Automatic state management
    - Conditional routing (budget optimization)
    - Better error handling
    - Visual workflow representation
    - Potential for parallel execution
    """
    
    def __init__(self):
        super().__init__(
            name="Travel Orchestrator (LangGraph)",
            description="Coordinates all agents using LangGraph workflow"
        )
        
        # Reference to the compiled LangGraph application
        self.graph = travel_planning_app
    
    @property
    def system_prompt(self) -> str:
        return """You are the master travel planning orchestrator. Your job is to:

1. Coordinate with specialized agents:
   - Flight Agent: Finds the best flights
   - Hotel Agent: Recommends accommodations
   - Activity Agent: Suggests things to do
   - Budget Agent: Ensures everything fits the budget

2. Combine all recommendations into a cohesive travel plan

3. Create a compelling summary that includes:
   - Overview of the trip
   - Key highlights
   - Why this plan is perfect for the traveler

Keep your summary engaging and concise (5-7 sentences)."""

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the full trip planning workflow using LangGraph.
        
        Input: TravelRequest data
        Output: Complete trip plan with all recommendations
        
        This now delegates to the LangGraph workflow which handles:
        - Sequential execution of search agents
        - Budget analysis and optimization
        - Conditional routing (retry with cheaper options if over budget)
        - Final summary generation
        """
        print("\n" + "=" * 70)
        print("🌍 LANGGRAPH TRAVEL ORCHESTRATOR")
        print("=" * 70)
        
        # Parse the request to show summary
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
        
        # Create initial state from input
        initial_state = create_initial_state(input_data)
        
        # Execute the graph! This is where all the magic happens
        final_state = await self.graph.ainvoke(initial_state)
        
        print("\n" + "=" * 70)
        print("✓ LANGGRAPH EXECUTION COMPLETE!")
        print("=" * 70)
        
        # Format the output to match the old orchestrator's return format
        # This ensures backward compatibility with any existing API consumers
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
            
            # Additional LangGraph-specific metadata
            "langgraph_metadata": {
                "optimization_iterations": final_state["optimization_iteration"],
                "within_budget": final_state["within_budget"],
                "total_cost": final_state["total_cost"],
                "errors": final_state["errors"]
            }
        }


if __name__ == "__main__":
    import asyncio
    from datetime import date
    
    async def test():
        print("\n" + "=" * 70)
        print("🌍 TESTING COMPLETE ORCHESTRATOR - FULL TRIP PLANNING")
        print("=" * 70)
        
        # Create orchestrator
        orchestrator = OrchestratorAgent()
        
        # Plan a complete trip
        result = await orchestrator.execute({
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
        print("RECOMMENDED FLIGHTS:")
        print("-" * 70)
        print(result['flights']['reasoning'][:200] + "...")
        
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
        print("ORCHESTRATOR TEST COMPLETE!")
        print("=" * 70)
        print("\nYour Agentic AI Travel Planner is FULLY FUNCTIONAL!")
        print("All agents working together to plan the perfect trip!")
        
    asyncio.run(test())
