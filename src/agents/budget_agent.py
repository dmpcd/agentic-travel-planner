"""
Budget Agent
AI agent responsible for budget optimization and cost tracking.
"""
from typing import Any, Dict, List
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from src.agents.base_agent import BaseAgent


class BudgetAgent(BaseAgent):
    """Agent responsible for budget optimization"""
    
    def __init__(self):
        super().__init__(
            name="Budget Agent",
            description="Optimizes budget and tracks costs"
        )
    
    @property
    def system_prompt(self) -> str:
        return """You are a budget optimization expert. Your job is to:

1. Calculate total trip costs accurately
2. Ensure everything fits within budget
3. Suggest cost-saving alternatives when needed
4. Provide clear budget breakdown

When analyzing costs:
- Be realistic about hidden costs (meals, transport, tips)
- Suggest where to save if over budget
- Highlight good value options
- Consider the full trip cost

Keep response concise and actionable."""

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze and optimize budget"""
        
        # Extract data
        flights = input_data.get("flights", {})
        hotels = input_data.get("hotels", {})
        activities = input_data.get("activities", {})
        total_budget = input_data.get("total_budget")
        travelers = input_data.get("travelers", 1)
        
        # Calculate costs
        flight_cost = self._calculate_flight_cost(flights, travelers)
        hotel_cost = self._calculate_hotel_cost(hotels)
        activity_cost = self._calculate_activity_cost(activities)
        
        # Estimate additional costs (meals, local transport, etc.)
        estimated_daily_expenses = 100  # $100 per day for meals, transport, misc
        days = input_data.get("days", 5)
        misc_cost = estimated_daily_expenses * days * travelers
        
        total_cost = flight_cost + hotel_cost + activity_cost + misc_cost
        
        # Create breakdown
        breakdown = {
            "flights": flight_cost,
            "hotels": hotel_cost,
            "activities": activity_cost,
            "meals_and_misc": misc_cost,
            "total": total_cost,
            "budget": total_budget,
            "remaining": (total_budget - total_cost) if total_budget else None,
            "within_budget": total_cost <= total_budget if total_budget else True
        }
        
        # AI analysis
        budget_text = f"${total_budget:,.2f}" if total_budget else "No limit"
        status_text = ""
        if total_budget:
            if total_cost > total_budget:
                status_text = f"OVER BUDGET by ${total_cost - total_budget:,.2f}"
            else:
                status_text = "WITHIN BUDGET ✓"
        
        analysis_prompt = f"""Analyze this trip budget:

COST BREAKDOWN:
- Flights: ${flight_cost:,.2f} ({travelers} travelers)
- Hotels: ${hotel_cost:,.2f} ({days} nights)
- Activities: ${activity_cost:,.2f}
- Meals & Misc: ${misc_cost:,.2f} (estimated)
- TOTAL: ${total_cost:,.2f}

TARGET BUDGET: {budget_text}
{status_text}

Provide brief analysis: Is this good value? Any suggestions to optimize?"""
        
        reasoning = await self.think(analysis_prompt)
        
        return {
            "breakdown": breakdown,
            "reasoning": reasoning,
            "within_budget": breakdown["within_budget"],
            "total_cost": total_cost,
            "budget_status": "over" if not breakdown["within_budget"] else "within"
        }
    
    def _calculate_flight_cost(self, flights_data: Dict, travelers: int) -> float:
        """Calculate total flight costs"""
        if not flights_data:
            return 0
        
        outbound = flights_data.get("recommended_outbound")
        return_flight = flights_data.get("recommended_return")
        
        if not outbound or not return_flight:
            return 0
        
        outbound_price = outbound.get("total_price", 0)
        return_price = return_flight.get("total_price", 0)
        
        return (outbound_price + return_price) * travelers
    
    def _calculate_hotel_cost(self, hotels_data: Dict) -> float:
        """Calculate total hotel costs"""
        if not hotels_data:
            return 0
            
        hotel = hotels_data.get("recommended")
        if not hotel:
            return 0
            
        price_per_night = hotel.get("price_per_night", 0)
        
        # Assuming check-in/check-out dates in parent call
        # For now, use a default
        nights = 5  # This should come from date calculation
        
        return price_per_night * nights
    
    def _calculate_activity_cost(self, activities_data: Dict) -> float:
        """Calculate total activity costs"""
        recommended = activities_data.get("recommended", [])
        
        total = 0
        for activity in recommended:
            total += activity.get("price", 0)
        
        return total


if __name__ == "__main__":
    import asyncio
    
    async def test():
        print("=" * 70)
        print("TESTING BUDGET AGENT")
        print("=" * 70)
        
        agent = BudgetAgent()
        
        # Mock data
        result = await agent.execute({
            "flights": {
                "recommended_outbound": {"total_price": 1250},
                "recommended_return": {"total_price": 1250}
            },
            "hotels": {
                "recommended": {"price_per_night": 220}
            },
            "activities": {
                "recommended": [
                    {"price": 28},
                    {"price": 85},
                    {"price": 32},
                    {"price": 0},
                    {"price": 55}
                ]
            },
            "total_budget": 3000,
            "travelers": 2,
            "days": 5
        })
        
        breakdown = result["breakdown"]
        
        print("\n" + "-" * 70)
        print("COST BREAKDOWN:")
        print("-" * 70)
        print(f"Flights:      ${breakdown['flights']:>10,.2f}")
        print(f"Hotels:       ${breakdown['hotels']:>10,.2f}")
        print(f"Activities:   ${breakdown['activities']:>10,.2f}")
        print(f"Meals & Misc: ${breakdown['meals_and_misc']:>10,.2f}")
        print("-" * 70)
        print(f"TOTAL:        ${breakdown['total']:>10,.2f}")
        print(f"BUDGET:       ${breakdown['budget']:>10,.2f}")
        print(f"REMAINING:    ${breakdown['remaining']:>10,.2f}")
        print("-" * 70)
        print(f"Status: {result['budget_status'].upper()}")
        
        print("\n" + "-" * 70)
        print("AI ANALYSIS:")
        print("-" * 70)
        print(result['reasoning'])
        
        print("\n" + "=" * 70)
        print("✅ BUDGET AGENT TEST COMPLETE!")
        print("=" * 70)
    
    asyncio.run(test())
