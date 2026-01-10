"""
Activity Agent
AI agent responsible for recommending activities and attractions.
"""
from typing import Any, Dict, List
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from src.agents.base_agent import BaseAgent
from src.models.activity import Activity
from src.tools.activity_search import ActivitySearchTool


class ActivityAgent(BaseAgent):
    """Agent responsible for finding and recommending activities"""
    
    def __init__(self):
        super().__init__(
            name="Activity Agent",
            description="Recommends activities and attractions"
        )
        self.activity_tool = ActivitySearchTool()
        self.add_tool(self.activity_tool)
    
    @property
    def system_prompt(self) -> str:
        return """You are an activity recommendation expert. Consider:

1. User interests (match activities to what they love)
2. Mix of free and paid activities
3. Variety (culture, food, sightseeing, entertainment)
4. Timing (group by location/area)
5. Value for money

Recommend a diverse mix of activities. For a multi-day trip:
- Include must-see attractions
- Mix famous spots with hidden gems
- Consider pacing (not too rushed)
- Group nearby activities together

Keep response concise but exciting. Highlight why each activity is special."""

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Search and recommend activities"""
        
        # Search for activities
        activities = await self.activity_tool.search(
            destination=input_data["destination"],
            interests=input_data.get("interests", []),
            max_price=input_data.get("budget")
        )
        
        # AI analysis
        days = input_data.get("days", 3)
        analysis_prompt = f"""Recommend activities for a {days}-day trip to {input_data["destination"]}:

AVAILABLE ACTIVITIES:
{self._format_activities(activities)}

USER INTERESTS: {', '.join(input_data.get('interests', ['general tourism']))}
BUDGET: ${input_data.get('budget', 'flexible')} total for activities

Recommend the TOP {min(days * 3, 12)} activities. Create a diverse itinerary."""
        
        reasoning = await self.think(analysis_prompt)
        
        # Select top activities (3 per day)
        top_activities = activities[:min(days * 3, 12)]
        
        return {
            "activities": [a.model_dump() for a in activities],
            "recommended": [a.model_dump() for a in top_activities],
            "reasoning": reasoning,
            "total_found": len(activities)
        }
    
    def _format_activities(self, activities: List[Activity]) -> str:
        """Format activities for AI analysis"""
        if not activities:
            return "No activities found"
        
        result = []
        for i, activity in enumerate(activities[:15], 1):
            result.append(
                f"{i}. {activity.name}\n"
                f"   - Category: {activity.category.value}\n"
                f"   - Price: {activity.formatted_price}\n"
                f"   - Duration: {activity.formatted_duration}\n"
                f"   - Rating: {activity.rating}⭐"
            )
        return "\n\n".join(result)


if __name__ == "__main__":
    import asyncio
    
    async def test():
        print("=" * 70)
        print("TESTING ACTIVITY AGENT WITH AI")
        print("=" * 70)
        
        agent = ActivityAgent()
        
        result = await agent.execute({
            "destination": "Tokyo",
            "interests": ["food", "technology", "culture"],
            "days": 5,
            "budget": 300
        })
        
        print(f"\nFound {result['total_found']} activities")
        print(f"   Recommended: {len(result['recommended'])}")
        
        print("\n" + "-" * 70)
        print("AI RECOMMENDATION:")
        print("-" * 70)
        print(result['reasoning'])
        
        print("\n" + "-" * 70)
        print("TOP RECOMMENDED ACTIVITIES:")
        print("-" * 70)
        for i, activity in enumerate(result['recommended'][:5], 1):
            print(f"{i}. {activity['name']} ({activity['category']})")
            print(f"   Price: ${activity['price']}, Rating: {activity['rating']}⭐")
        
        print("\n" + "=" * 70)
        print("ACTIVITY AGENT TEST COMPLETE!")
        print("=" * 70)
    
    asyncio.run(test())
