"""
Agentic Travel Planner - Agents Package

This package contains the LangGraph-based travel planning workflow.
All agent logic is consolidated in graph_nodes.py for simplicity.
"""

# Core LangGraph components
from .state import TravelPlanState, create_initial_state
from .travel_graph import travel_planning_app, create_travel_planning_graph
from .orchestrator import plan_trip

# Graph nodes (contain all agent logic)
from .graph_nodes import (
    flight_search_node,
    hotel_search_node,
    activity_search_node,
    budget_analysis_node,
    generate_summary_node,
    should_optimize_route,
    think,
    get_llm,
)

# LLM utilities
from .llm_utils import get_llm, think

__all__ = [
    # Main entry point
    'plan_trip',
    
    # State management
    'TravelPlanState',
    'create_initial_state',
    
    # Graph
    'travel_planning_app',
    'create_travel_planning_graph',
    
    # Node functions
    'flight_search_node',
    'hotel_search_node',
    'activity_search_node',
    'budget_analysis_node',
    'generate_summary_node',
    'should_optimize_route',
    
    # LLM utilities
    'get_llm',
    'think',
]
