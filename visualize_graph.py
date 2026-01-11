"""
LangGraph Workflow Visualization
Run this to see the graph structure in text format.
"""

def print_workflow_diagram():
    """Print a detailed diagram of the LangGraph workflow"""
    
    print("\n" + "=" * 80)
    print("🗺️  LANGGRAPH TRAVEL PLANNER WORKFLOW")
    print("=" * 80)
    
    print("""
    
    ┌─────────────────────────────────────────────────────────────────────┐
    │                          USER INPUT                                 │
    │  {origin, destination, dates, budget, travelers, interests}        │
    └────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 ↓
                        [CREATE INITIAL STATE]
                         TravelPlanState
                                 │
                                 ↓
                        ┌────────────────┐
                        │  START GRAPH   │
                        └────────┬───────┘
                                 │
                                 ↓
    ┌────────────────────────────────────────────────────────────────────┐
    │                    NODE: flight_search_node                        │
    │  • Executes FlightAgent                                           │
    │  • Searches outbound and return flights                           │
    │  • Updates state: flights = {...}                                 │
    └────────────────────┬───────────────────────────────────────────────┘
                         │
                         ↓
    ┌────────────────────────────────────────────────────────────────────┐
    │                    NODE: hotel_search_node                         │
    │  • Executes HotelAgent                                            │
    │  • Searches hotels for stay duration                              │
    │  • Updates state: hotels = {...}                                  │
    └────────────────────┬───────────────────────────────────────────────┘
                         │
                         ↓
    ┌────────────────────────────────────────────────────────────────────┐
    │                  NODE: activity_search_node                        │
    │  • Executes ActivityAgent                                         │
    │  • Finds activities based on interests                            │
    │  • Updates state: activities = {...}                              │
    └────────────────────┬───────────────────────────────────────────────┘
                         │
                         ↓
    ┌────────────────────────────────────────────────────────────────────┐
    │                  NODE: budget_analysis_node                        │
    │  • Executes BudgetAgent                                           │
    │  • Calculates total cost                                          │
    │  • Checks if within budget                                        │
    │  • Updates state:                                                 │
    │    - budget_analysis = {...}                                      │
    │    - within_budget = True/False                                   │
    │    - needs_optimization = True/False                              │
    └────────────────────┬───────────────────────────────────────────────┘
                         │
                         ↓
                 ┌───────────────┐
                 │  CONDITIONAL  │
                 │    ROUTING    │
                 └───┬───────┬───┘
                     │       │
        within_budget?       │
                     │       │
        ┌────────────┴─┐   ┌─┴─────────────┐
        │ NO           │   │ YES           │
        ↓              │   ↓               │
    needs_optimization │ within_budget     │
    AND iteration < 3  │ OR iteration >= 3 │
        │              │   │               │
        ↓              │   ↓               │
    ┌────────┐         │ ┌──────────────────────────────────────────┐
    │  LOOP  │         │ │  NODE: generate_summary_node             │
    │  BACK  │◄────────┘ │  • Uses AI to create trip summary        │
    │        │           │  • Updates state: trip_summary = "..."   │
    └────┬───┘           └──────────────┬───────────────────────────┘
         │                              │
         │ (Try cheaper options)        │
         │                              │
         └──────────────────┐           │
                            │           │
                            ↓           ↓
                    [search_flights]  [END]
                                       │
                                       ↓
                            ┌──────────────────┐
                            │  RETURN RESULT   │
                            │  Complete state  │
                            │  with all data   │
                            └──────────────────┘
    
    """)
    
    print("=" * 80)
    print("🔄 OPTIMIZATION LOOP DETAILS")
    print("=" * 80)
    print("""
    When budget is exceeded:
    
    Iteration 1: Search with original criteria → Over budget
                 ↓
                 Loop back to Flight Search
                 ↓
    Iteration 2: Search with tighter constraints → Still over?
                 ↓
                 Loop back again
                 ↓
    Iteration 3: Final attempt with minimum budget → Still over?
                 ↓
                 Give up, proceed to summary (max iterations reached)
    
    Max iterations: 3
    Each iteration increments: state['optimization_iteration']
    """)
    
    print("=" * 80)
    print("📊 STATE FLOW")
    print("=" * 80)
    print("""
    TravelPlanState flows through each node:
    
    Initial State:
    {
        origin: "NYC",
        destination: "Tokyo",
        budget: 3000,
        flights: {},           ← Empty initially
        hotels: {},            ← Empty initially
        activities: {},        ← Empty initially
        budget_analysis: {},   ← Empty initially
        within_budget: True,
        optimization_iteration: 0,
        ...
    }
    
    After flight_search_node:
    {
        ...
        flights: {
            outbound_flights: [...],
            return_flights: [...],
            recommended_outbound: {...},
            recommended_return: {...}
        },
        ...
    }
    
    After budget_analysis_node:
    {
        ...
        budget_analysis: {
            breakdown: {...},
            total_cost: 2850,
            within_budget: True
        },
        within_budget: True,
        needs_optimization: False,
        total_cost: 2850,
        ...
    }
    
    After generate_summary_node:
    {
        ...
        trip_summary: "Embark on an unforgettable 5-day journey..."
    }
    
    Final state returned to user!
    """)
    
    print("=" * 80)
    print("🎯 KEY FEATURES")
    print("=" * 80)
    print("""
    ✅ Automatic State Management
       - No manual dict passing between agents
       - LangGraph handles state updates
    
    ✅ Conditional Routing
       - Dynamic path based on budget status
       - Intelligent decision-making
    
    ✅ Optimization Loops
       - Automatic retry with cheaper options
       - Max 3 attempts to stay within budget
    
    ✅ Error Handling
       - Errors accumulated in state['errors']
       - Graph continues even if one node fails
    
    ✅ Extensible
       - Easy to add new nodes
       - Simple to modify routing logic
       - Can add parallel execution
    """)


if __name__ == "__main__":
    print_workflow_diagram()
