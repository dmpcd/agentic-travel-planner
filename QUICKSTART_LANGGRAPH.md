# 🚀 Quick Start: LangGraph Travel Planner

## Run the Test
```bash
cd agentic-travel-planner
python test_langgraph.py
```

## Key Commands

### Test Individual Components
```bash
# Test state
python src/agents/state.py

# Test nodes
python src/agents/graph_nodes.py

# Test graph
python src/agents/travel_graph.py

# Test orchestrator
python src/agents/orchestrator.py
```

### Use in Your Code
```python
from src.agents.orchestrator import OrchestratorAgent
from datetime import date

# Create orchestrator (now with LangGraph!)
orchestrator = OrchestratorAgent()

# Plan a trip
result = await orchestrator.execute({
    "origin": "New York",
    "destination": "Tokyo",
    "departure_date": date(2026, 4, 15),
    "return_date": date(2026, 4, 20),
    "budget": 3000.0,
    "travelers": 2,
    "interests": ["food", "technology"]
})

# Access LangGraph metadata
print(f"Iterations: {result['langgraph_metadata']['optimization_iterations']}")
print(f"Total cost: ${result['langgraph_metadata']['total_cost']:,.2f}")
```

## What Changed?

### New Files
- `src/agents/state.py` - State definition
- `src/agents/graph_nodes.py` - Graph node functions
- `src/agents/travel_graph.py` - LangGraph workflow
- `test_langgraph.py` - Test script
- `LANGGRAPH_MIGRATION.md` - Full migration guide

### Modified Files
- `src/agents/orchestrator.py` - Now uses LangGraph

### Dependencies Added
- `langgraph`
- `langgraph-checkpoint`

## Graph Workflow

```
START → Flight Search → Hotel Search → Activity Search 
    ↓
Budget Analysis
    ↓
Over budget? → Yes → Loop back (max 3 times)
    ↓ No
Generate Summary → END
```

## Benefits

✅ Automatic state management  
✅ Conditional routing  
✅ Budget optimization loops  
✅ Better error handling  
✅ Visual workflow  
✅ Future-ready (parallel execution, streaming, etc.)

## Next Steps

1. ✅ Run `python test_langgraph.py`
2. Try different budgets to see optimization
3. Add parallel execution for flights + hotels
4. Integrate LangSmith for debugging
5. Add streaming for real-time updates

---

See **LANGGRAPH_MIGRATION.md** for complete documentation!
