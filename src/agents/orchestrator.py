"""
Orchestrator Agent
The master coordinator that manages the entire trip planning process.
"""
from typing import Any, Dict
from datetime import datetime
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from src.agents.base_agent import BaseAgent
from src.agents.flight_agent import FlightAgent
from src.agents.hotel_agent import HotelAgent
from src.agents.activity_agent import ActivityAgent
from src.agents.budget_agent import BudgetAgent
from src.models.travel_request import TravelRequest


class OrchestratorAgent(BaseAgent):
    """
    The master coordinator agent that manages the entire trip planning process.
    
    Responsibilities:
    1. Parse and understand user requests
    2. Delegate tasks to specialized agents
    3. Collect and combine results
    4. Resolve conflicts between agent outputs
    5. Generate final travel plan
    """
    
    def __init__(self):
        super().__init__(
            name="Travel Orchestrator",
            description="Coordinates all agents to plan the perfect trip"
        )
        
        # Initialize all specialized agents
        self.flight_agent = FlightAgent()
        self.hotel_agent = HotelAgent()
        self.activity_agent = ActivityAgent()
        self.budget_agent = BudgetAgent()
    
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
        Execute the full trip planning workflow.
        
        Input: TravelRequest data
        Output: Complete trip plan with all recommendations
        """
        print("\n" + "=" * 70)
        print("STARTING TRIP PLANNING PROCESS")
        print("=" * 70)
        
        # Parse the request
        request = TravelRequest(**input_data)
        days = (request.return_date - request.departure_date).days
        
        print(f"\nTrip Details:")
        print(f"   From: {request.origin}")
        print(f"   To: {request.destination}")
        print(f"   Dates: {request.departure_date} to {request.return_date} ({days} days)")
        print(f"   Travelers: {request.travelers}")
        print(f"   Budget: ${request.budget:,.2f}" if request.budget else "   Budget: Flexible")
        print(f"   Interests: {', '.join(request.interests)}" if request.interests else "")
        
        # Step 1: Search for flights
        print("\n" + "-" * 70)
        print("STEP 1: Searching for flights...")
        print("-" * 70)
        flight_results = await self.flight_agent.execute({
            "origin": request.origin,
            "destination": request.destination,
            "departure_date": str(request.departure_date),
            "return_date": str(request.return_date),
            "travelers": request.travelers,
            "max_price": request.budget * 0.4 / request.travelers if request.budget else None,
            "preferences": request.flight_preferences
        })
        print(f"Found {flight_results['total_flights_found']} flight options")
        
        # Step 2: Search for hotels
        print("\n" + "-" * 70)
        print("STEP 2: Searching for hotels...")
        print("-" * 70)
        hotel_results = await self.hotel_agent.execute({
            "destination": request.destination,
            "check_in": str(request.departure_date),
            "check_out": str(request.return_date),
            "guests": request.travelers,
            "max_price_per_night": (request.budget * 0.35 / days) if request.budget else None,
            "preferences": request.hotel_preferences
        })
        print(f"Found {hotel_results['total_found']} hotel options")
        
        # Step 3: Find activities
        print("\n" + "-" * 70)
        print("STEP 3: Finding activities...")
        print("-" * 70)
        activity_results = await self.activity_agent.execute({
            "destination": request.destination,
            "interests": request.interests,
            "days": days,
            "budget": request.budget * 0.15 if request.budget else None
        })
        print(f"Found {activity_results['total_found']} activity options")
        
        # Step 4: Budget optimization
        print("\n" + "-" * 70)
        print("STEP 4: Optimizing budget...")
        print("-" * 70)
        budget_results = await self.budget_agent.execute({
            "flights": flight_results,
            "hotels": hotel_results,
            "activities": activity_results,
            "total_budget": request.budget,
            "travelers": request.travelers,
            "days": days
        })
        print(f"Total cost: ${budget_results['total_cost']:,.2f}")
        if request.budget:
            status = "Within budget" if budget_results['within_budget'] else "Over budget"
            print(f"   {status}")
        
        # Step 5: Generate final summary
        print("\n" + "-" * 70)
        print("STEP 5: Generating travel plan summary...")
        print("-" * 70)
        
        summary_prompt = f"""Create an engaging trip summary for this travel plan:

DESTINATION: {request.destination}
DURATION: {days} days
TRAVELERS: {request.travelers}

SELECTED OPTIONS:
Flights: ${budget_results['breakdown']['flights']:,.2f}
Hotel: {hotel_results['recommended']['name']} - ${hotel_results['recommended']['price_per_night']}/night
Activities: {len(activity_results['recommended'])} curated experiences
Total: ${budget_results['total_cost']:,.2f}

USER INTERESTS: {', '.join(request.interests) if request.interests else 'General tourism'}

Create an exciting 5-7 sentence summary that highlights why this is a perfect trip plan."""
        
        final_summary = await self.think(summary_prompt)
        
        print("\n" + "=" * 70)
        print("TRIP PLANNING COMPLETE!")
        print("=" * 70)
        
        return {
            "trip_summary": final_summary,
            "destination": request.destination,
            "dates": {
                "departure": str(request.departure_date),
                "return": str(request.return_date),
                "duration_days": days
            },
            "travelers": request.travelers,
            "flights": flight_results,
            "hotels": hotel_results,
            "activities": activity_results,
            "budget": budget_results,
            "created_at": datetime.now().isoformat()
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
