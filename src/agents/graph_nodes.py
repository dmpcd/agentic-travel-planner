"""
LangGraph Node Functions
Each function is a node in the travel planning workflow graph.
Nodes receive state, execute their task, and return updated state.

This file contains ALL the agent logic directly in the node functions,
eliminating the need for separate agent class files.
"""
from typing import Dict, Any, List

from src.agents.state import TravelPlanState
from src.agents.llm_utils import get_llm, think  # Import shared LLM utilities
from src.tools.flight_search import FlightSearchTool
from src.tools.hotel_search import HotelSearchTool
from src.tools.activity_search import ActivitySearchTool
from src.models.flight import Flight
from src.models.hotel import Hotel
from src.models.activity import Activity


# ============================================
# SYSTEM PROMPTS - Define agent behaviors
# ============================================

FLIGHT_SYSTEM_PROMPT = """You are a flight search expert agent. Your job is to:

1. Analyze flight options considering:
   - Price (lower is better, but consider value)
   - Duration (shorter is better)
   - Number of stops (direct is strongly preferred)
   - Departure/arrival times (reasonable hours preferred)
   - Airline reputation

2. Recommend the BEST option with clear reasoning

3. Consider trade-offs intelligently:
   - A slightly more expensive direct flight is usually better than a cheap flight with 2 stops
   - Very early morning or late night flights should be noted
   - Long layovers should be mentioned

4. Keep your response concise and actionable (3-5 sentences max)

5. Format: 
   - State your recommendation clearly
   - Give 2-3 key reasons
   - Mention any important considerations"""

HOTEL_SYSTEM_PROMPT = """You are a hotel recommendation expert. Analyze hotel options considering:

1. Location (closer to city center is better)
2. Rating (user reviews are important)
3. Value for money (balance price with quality)
4. Amenities (what's included)
5. Star rating (hotel class)

Recommend the BEST hotel with clear reasoning. Consider:
- Budget travelers prefer good value
- Luxury travelers want premium experience
- Location is crucial for tourism

Keep response concise (3-5 sentences). State your recommendation and key reasons."""

ACTIVITY_SYSTEM_PROMPT = """You are an activity recommendation expert. Consider:

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

BUDGET_SYSTEM_PROMPT = """You are a budget optimization expert. Your job is to:

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

SUMMARY_SYSTEM_PROMPT = """You are the master travel planning orchestrator. Your job is to:

1. Combine all recommendations into a cohesive travel plan

2. Create a compelling summary that includes:
   - Overview of the trip
   - Key highlights
   - Why this plan is perfect for the traveler

Keep your summary engaging and concise (5-7 sentences)."""


# ============================================
# HELPER FUNCTIONS - Format data for AI
# ============================================

def format_flights(flights: List[Flight]) -> str:
    """Format flights for AI analysis"""
    if not flights:
        return "No flights found"
    
    result = []
    for i, flight in enumerate(flights[:5], 1):
        airline = flight.segments[0].airline
        result.append(
            f"Option {i}: {flight.id}\n"
            f"  - Price: {flight.formatted_price}\n"
            f"  - Duration: {flight.formatted_duration}\n"
            f"  - Stops: {flight.stops} ({'Direct' if flight.is_direct else 'Connecting'})\n"
            f"  - Airline: {airline}"
        )
    return "\n\n".join(result)


def format_hotels(hotels: List[Hotel]) -> str:
    """Format hotels for AI analysis"""
    if not hotels:
        return "No hotels found"
    
    result = []
    for i, hotel in enumerate(hotels[:5], 1):
        result.append(
            f"Hotel {i}: {hotel.name}\n"
            f"  - Rating: {hotel.user_rating}/10 ({hotel.rating_category})\n"
            f"  - Price: {hotel.formatted_price}\n"
            f"  - Stars: {hotel.star_rating}⭐\n"
            f"  - Distance: {hotel.distance_to_center_km}km from center\n"
            f"  - Amenities: {', '.join(hotel.amenities[:4])}"
        )
    return "\n\n".join(result)


def format_activities(activities: List[Activity]) -> str:
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


# ============================================
# SEARCH NODES
# ============================================

async def flight_search_node(state: TravelPlanState) -> Dict[str, Any]:
    """
    Node: Search for flights
    
    Searches for flights and uses AI to recommend the best options.
    """
    print("\n" + "=" * 70)
    print("🛫 GRAPH NODE: Searching for flights...")
    print("=" * 70)
    
    try:
        flight_tool = FlightSearchTool()
        
        # Calculate max price based on budget allocation (40% for flights)
        max_price = None
        if state.get("budget"):
            max_price = state["budget"] * 0.4 / state["travelers"]
        
        # Search for outbound flights
        outbound_flights = await flight_tool.search(
            origin=state["origin"],
            destination=state["destination"],
            date=state["departure_date"],
            travelers=state["travelers"],
            max_price=max_price
        )
        
        # Search for return flights
        return_flights = await flight_tool.search(
            origin=state["destination"],
            destination=state["origin"],
            date=state["return_date"],
            travelers=state["travelers"],
            max_price=max_price
        )
        
        # Use AI to analyze and recommend
        analysis_prompt = f"""Analyze these flight options and recommend the best choice:

OUTBOUND FLIGHTS ({state["origin"]} → {state["destination"]}):
{format_flights(outbound_flights)}

RETURN FLIGHTS ({state["destination"]} → {state["origin"]}):
{format_flights(return_flights)}

USER PREFERENCES:
- Budget: ${max_price or 'flexible'} per person
- Travelers: {state["travelers"]}
- Preferences: {state.get('flight_preferences', 'none specified')}

Recommend the BEST outbound and return flight combination. Be specific and concise."""
        
        reasoning = await think(FLIGHT_SYSTEM_PROMPT, analysis_prompt)
        
        results = {
            "outbound_flights": [f.model_dump() for f in outbound_flights],
            "return_flights": [f.model_dump() for f in return_flights],
            "recommended_outbound": outbound_flights[0].model_dump() if outbound_flights else None,
            "recommended_return": return_flights[0].model_dump() if return_flights else None,
            "reasoning": reasoning,
            "total_flights_found": len(outbound_flights) + len(return_flights)
        }
        
        print(f"✓ Found {results['total_flights_found']} flight options")
        
        return {"flights": results}
        
    except Exception as e:
        print(f"✗ Error in flight search: {str(e)}")
        return {
            "flights": {},
            "errors": [f"Flight search failed: {str(e)}"]
        }


async def hotel_search_node(state: TravelPlanState) -> Dict[str, Any]:
    """
    Node: Search for hotels
    
    Searches for hotels and uses AI to recommend the best option.
    """
    print("\n" + "=" * 70)
    print("🏨 GRAPH NODE: Searching for hotels...")
    print("=" * 70)
    
    try:
        hotel_tool = HotelSearchTool()
        
        # Calculate max price based on budget allocation (35% for hotels)
        max_price_per_night = None
        if state.get("budget"):
            max_price_per_night = state["budget"] * 0.35 / state["days"]
        
        # Determine hotel search location
        hotel_location = state["destination"]
        hotel_prefs = state.get('hotel_preferences', '')
        
        # Words that should NOT be treated as city names
        non_city_words = {
            'beach', 'beaches', 'center', 'centre', 'downtown', 'airport', 
            'station', 'ocean', 'sea', 'mountain', 'lake', 'river', 'pool',
            'spa', 'resort', 'city', 'town', 'area', 'zone', 'district',
            'market', 'mall', 'park', 'garden', 'temple', 'church', 'mosque'
        }
        
        if hotel_prefs:
            # Extract city names from preferences like "close to Galle", "near Kandy"
            import re
            location_patterns = [
                r'close to (\w+)',
                r'near (\w+)',
                r'in (\w+)',
                r'around (\w+)',
                r'by (\w+)',
            ]
            for pattern in location_patterns:
                match = re.search(pattern, hotel_prefs, re.IGNORECASE)
                if match:
                    potential_city = match.group(1).strip()
                    # Only use if it's not a generic word and is likely a city name
                    if (potential_city.lower() not in non_city_words 
                        and len(potential_city) > 2 
                        and potential_city[0].isupper()):
                        hotel_location = potential_city
                        print(f"📍 Using hotel preference location: {hotel_location}")
                        break
        
        # Search for hotels
        hotels = await hotel_tool.search(
            destination=hotel_location,
            check_in=state["departure_date"],
            check_out=state["return_date"],
            guests=state["travelers"],
            max_price_per_night=max_price_per_night
        )
        
        # AI analysis
        analysis_prompt = f"""Analyze these hotel options in {state["destination"]}:

{format_hotels(hotels)}

USER REQUIREMENTS:
- Guests: {state["travelers"]}
- Budget: ${max_price_per_night or 'flexible'} per night
- Preferences: {state.get('hotel_preferences', 'none specified')}

Recommend the BEST hotel. Be specific and concise."""
        
        reasoning = await think(HOTEL_SYSTEM_PROMPT, analysis_prompt)
        
        results = {
            "hotels": [h.model_dump() for h in hotels],
            "recommended": hotels[0].model_dump() if hotels else None,
            "reasoning": reasoning,
            "total_found": len(hotels)
        }
        
        print(f"✓ Found {results['total_found']} hotel options")
        
        return {"hotels": results}
        
    except Exception as e:
        print(f"✗ Error in hotel search: {str(e)}")
        return {
            "hotels": {},
            "errors": [f"Hotel search failed: {str(e)}"]
        }


async def activity_search_node(state: TravelPlanState) -> Dict[str, Any]:
    """
    Node: Search for activities
    
    Searches for activities and uses AI to recommend a diverse itinerary.
    Uses hotel_preferences location for more accurate results.
    """
    print("\n" + "=" * 70)
    print("🎯 GRAPH NODE: Finding activities...")
    print("=" * 70)
    
    try:
        activity_tool = ActivitySearchTool()
        
        # Calculate activity budget (15% of total)
        activity_budget = None
        if state.get("budget"):
            activity_budget = state["budget"] * 0.15
        
        # Extract specific location from hotel_preferences for beach/activity-focused trips
        activity_location = state["destination"]
        hotel_prefs = state.get("hotel_preferences", "")
        interests = state.get("interests", [])
        
        # Words that should NOT be treated as city names
        non_city_words = {
            'beach', 'beaches', 'center', 'centre', 'downtown', 'airport', 
            'station', 'ocean', 'sea', 'mountain', 'lake', 'river', 'pool',
            'spa', 'resort', 'city', 'town', 'area', 'zone', 'district',
            'market', 'mall', 'park', 'garden', 'temple', 'church', 'mosque'
        }
        
        # For beach/water activities, use the hotel preference location if available
        beach_interests = ['beach', 'beaches', 'surfing', 'surf', 'diving', 'snorkeling', 
                          'corals', 'ocean', 'water sports', 'swimming']
        has_beach_interests = any(i.lower() in beach_interests for i in interests)
        
        if hotel_prefs and has_beach_interests:
            # Extract city name from hotel preferences
            import re
            location_patterns = [
                r'close to (\w+)',
                r'near (\w+)',
                r'in (\w+)',
                r'around (\w+)',
                r'(\w+) area',
            ]
            for pattern in location_patterns:
                match = re.search(pattern, hotel_prefs, re.IGNORECASE)
                if match:
                    potential_city = match.group(1).strip()
                    # Only use if it's a real city name (capitalized, not a generic word)
                    if (potential_city.lower() not in non_city_words 
                        and len(potential_city) > 2
                        and potential_city[0].isupper()):
                        activity_location = f"{potential_city}, {state['destination']}"
                        print(f"📍 Using activity location from preferences: {activity_location}")
                        break
        
        # Search for activities
        activities = await activity_tool.search(
            destination=activity_location,
            interests=interests,
            max_price=activity_budget
        )
        
        # AI analysis
        days = state["days"]
        analysis_prompt = f"""Recommend activities for a {days}-day trip to {state["destination"]}:

AVAILABLE ACTIVITIES:
{format_activities(activities)}

USER INTERESTS: {', '.join(state.get('interests', ['general tourism']))}
BUDGET: ${activity_budget or 'flexible'} total for activities

Recommend the TOP {min(days * 3, 12)} activities. Create a diverse itinerary."""
        
        reasoning = await think(ACTIVITY_SYSTEM_PROMPT, analysis_prompt)
        
        # Select top activities (3 per day)
        top_activities = activities[:min(days * 3, 12)]
        
        results = {
            "activities": [a.model_dump() for a in activities],
            "recommended": [a.model_dump() for a in top_activities],
            "reasoning": reasoning,
            "total_found": len(activities)
        }
        
        print(f"✓ Found {results['total_found']} activity options")
        
        return {"activities": results}
        
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
    
    Calculates costs and checks budget constraints.
    Determines if optimization is needed.
    """
    print("\n" + "=" * 70)
    print("💰 GRAPH NODE: Analyzing budget...")
    print("=" * 70)
    
    try:
        flights_data = state.get("flights", {})
        hotels_data = state.get("hotels", {})
        activities_data = state.get("activities", {})
        total_budget = state.get("budget")
        travelers = state["travelers"]
        days = state["days"]
        
        # Calculate flight costs
        flight_cost = 0
        if flights_data:
            outbound = flights_data.get("recommended_outbound")
            return_flight = flights_data.get("recommended_return")
            if outbound and return_flight:
                outbound_price = outbound.get("total_price", 0)
                return_price = return_flight.get("total_price", 0)
                flight_cost = (outbound_price + return_price) * travelers
        
        # Calculate hotel costs
        hotel_cost = 0
        if hotels_data:
            hotel = hotels_data.get("recommended")
            if hotel:
                hotel_cost = hotel.get("price_per_night", 0) * days
        
        # Calculate activity costs
        activity_cost = 0
        recommended_activities = activities_data.get("recommended", [])
        for activity in recommended_activities:
            activity_cost += activity.get("price", 0)
        
        # Estimate additional costs
        estimated_daily_expenses = 100  # $100 per day for meals, transport, misc
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
        
        within_budget = breakdown["within_budget"]
        
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
        
        reasoning = await think(BUDGET_SYSTEM_PROMPT, analysis_prompt)
        
        results = {
            "breakdown": breakdown,
            "reasoning": reasoning,
            "within_budget": within_budget,
            "total_cost": total_cost,
            "budget_status": "over" if not within_budget else "within"
        }
        
        print(f"✓ Total cost: ${total_cost:,.2f}")
        if total_budget:
            status = "Within budget ✓" if within_budget else "Over budget ✗"
            print(f"  {status}")
        
        # Determine if we need optimization
        needs_optimization = False
        if total_budget and not within_budget:
            if state["optimization_iteration"] < 3:
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
        # Get recommended options
        hotel = state["hotels"].get("recommended", {})
        hotel_name = hotel.get("name", "Unknown Hotel")
        hotel_price = hotel.get("price_per_night", 0)
        
        num_activities = len(state["activities"].get("recommended", []))
        
        budget_analysis = state.get("budget_analysis", {})
        breakdown = budget_analysis.get("breakdown", {})
        
        # Include additional user notes if provided
        additional_notes = state.get("additional_notes", "")
        notes_section = f"\nSPECIAL REQUIREMENTS/NOTES: {additional_notes}" if additional_notes else ""
        
        summary_prompt = f"""Create an engaging trip summary for this travel plan:

DESTINATION: {state['destination']}
DURATION: {state['days']} days
TRAVELERS: {state['travelers']}

SELECTED OPTIONS:
- Flights: ${breakdown.get('flights', 0):,.2f}
- Hotel: {hotel_name} - ${hotel_price}/night
- Activities: {num_activities} curated experiences
- Total Cost: ${state['total_cost']:,.2f}

USER INTERESTS: {', '.join(state['interests']) if state['interests'] else 'General tourism'}{notes_section}

Create an exciting 5-7 sentence summary that highlights why this is a perfect trip plan.
Make it engaging and mention specific highlights. If there are special requirements/notes, address how this plan meets them."""
        
        summary = await think(SUMMARY_SYSTEM_PROMPT, summary_prompt)
        
        print("✓ Trip summary generated")
        
        return {"trip_summary": summary}
        
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
