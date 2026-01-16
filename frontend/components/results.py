"""
Results Display Components
Renders the complete trip planning results.
"""
import streamlit as st
from typing import Dict, Any, List

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Icons
from .cards import (
    render_flight_card,
    render_hotel_card,
    render_activity_card,
    render_budget_card
)


def render_summary(summary: str, total_cost: float, within_budget: bool) -> None:
    """
    Render the trip summary section.
    
    Args:
        summary: AI-generated trip summary
        total_cost: Total trip cost
        within_budget: Whether within budget
    """
    st.markdown(f"## {Icons.SUMMARY} Your Trip Summary")
    
    # Status banner
    col1, col2 = st.columns([3, 1])
    with col1:
        if within_budget:
            st.success(f"{Icons.SUCCESS} Great news! Your trip is within budget.")
        else:
            st.warning(f"{Icons.WARNING} This trip exceeds your budget. Consider adjusting preferences.")
    
    with col2:
        st.metric("Total Cost", f"${total_cost:,.0f}")
    
    # AI Summary
    if summary:
        with st.expander("📝 AI Trip Analysis", expanded=True):
            st.markdown(summary)


def render_flights_section(flights: List[Dict[str, Any]], title: str = "Flights") -> None:
    """
    Render the flights results section.
    
    Args:
        flights: List of flight options
        title: Section title
    """
    st.markdown(f"### {Icons.FLIGHT} {title}")
    
    if not flights:
        st.info("No flights found. Try adjusting your dates or destinations.")
        return
    
    # Show top 5 flights
    for i, flight in enumerate(flights[:5]):
        render_flight_card(flight, is_recommended=(i == 0))


def render_hotels_section(hotels: List[Dict[str, Any]]) -> None:
    """
    Render the hotels results section.
    
    Args:
        hotels: List of hotel options
    """
    st.markdown(f"### {Icons.HOTEL} Hotels")
    
    if not hotels:
        st.info("No hotels found. Try adjusting your preferences or dates.")
        return
    
    # Show top 5 hotels
    for i, hotel in enumerate(hotels[:5]):
        render_hotel_card(hotel, is_recommended=(i == 0))


def render_activities_section(activities: List[Dict[str, Any]]) -> None:
    """
    Render the activities results section.
    
    Args:
        activities: List of activity options
    """
    st.markdown(f"### {Icons.ACTIVITY} Activities & Things To Do")
    
    if not activities:
        st.info("No activities found. Try adjusting your interests.")
        return
    
    # Group by category
    by_category: Dict[str, List] = {}
    for activity in activities:
        category = activity.get("category", "other")
        if hasattr(category, "value"):
            category = category.value
        if category not in by_category:
            by_category[category] = []
        by_category[category].append(activity)
    
    # Create tabs for categories if multiple
    if len(by_category) > 1:
        category_names = list(by_category.keys())
        tabs = st.tabs([cat.title() for cat in category_names])
        
        for tab, category in zip(tabs, category_names):
            with tab:
                for i, activity in enumerate(by_category[category][:5]):
                    render_activity_card(activity, is_recommended=(i == 0))
    else:
        # Single category - show directly
        for i, activity in enumerate(activities[:10]):
            render_activity_card(activity, is_recommended=(i == 0))


def render_results_section(results) -> None:
    """
    Render the complete results section.
    
    Args:
        results: TripResults object from the API client
    """
    # Summary section
    render_summary(
        summary=results.summary,
        total_cost=results.total_cost,
        within_budget=results.within_budget
    )
    
    st.divider()
    
    # Create tabs for different sections
    tab_flights, tab_hotels, tab_activities, tab_budget = st.tabs([
        f"{Icons.FLIGHT} Flights",
        f"{Icons.HOTEL} Hotels", 
        f"{Icons.ACTIVITY} Activities",
        f"{Icons.BUDGET} Budget"
    ])
    
    with tab_flights:
        # Use separate outbound and return flights
        col1, col2 = st.columns(2)
        with col1:
            render_flights_section(results.outbound_flights, "Outbound Flights")
        with col2:
            render_flights_section(results.return_flights, "Return Flights")
    
    with tab_hotels:
        render_hotels_section(results.hotels)
    
    with tab_activities:
        render_activities_section(results.activities)
    
    with tab_budget:
        render_budget_card(results.budget_analysis, results.within_budget)


def render_errors(errors: List[str]) -> None:
    """
    Render any errors that occurred.
    
    Args:
        errors: List of error messages
    """
    if errors:
        st.error(f"{Icons.ERROR} Some issues occurred during planning:")
        for error in errors:
            st.warning(error)


def render_loading_state(step: str = "Planning your trip...") -> None:
    """
    Render a loading state.
    
    Args:
        step: Current step description
    """
    with st.spinner(f"{Icons.LOADING} {step}"):
        st.empty()
