"""
Form Components
Reusable input forms for the travel planner.
"""
import streamlit as st
from datetime import date, timedelta
from typing import Tuple, List, Optional

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import CONFIG, Icons


def render_travel_form() -> Optional[Tuple]:
    """
    Render the main travel planning form with improved layout.
    
    Returns:
        Tuple of form values if submitted, None otherwise
    """
    
    with st.form("travel_form"):
        # Section 1: Flight Details
        st.markdown("### ✈️ Flight Details")
        
        col1, col2, col3, col4 = st.columns([1.5, 1.5, 1, 1])
        
        with col1:
            origin = st.text_input(
                "From (Origin)",
                placeholder="Sydney, Australia",
                help="Enter your departure city"
            )
        
        with col2:
            # Option to use popular or custom destination
            use_custom = st.checkbox("✏️ Custom destination", key="custom_dest")
            
            if use_custom:
                destination = st.text_input(
                    "To (Destination)",
                    placeholder="Paris, France",
                    help="Type your destination"
                )
            else:
                destination = st.selectbox(
                    "To (Destination)",
                    options=[""] + list(CONFIG.POPULAR_DESTINATIONS),
                    format_func=lambda x: "-- Select --" if x == "" else x,
                    help="Choose a popular destination"
                )
        
        with col3:
            min_date = date.today() + timedelta(days=1)
            departure_date = st.date_input(
                "Departure",
                value=min_date + timedelta(days=30),
                min_value=min_date,
                help="Departure date"
            )
        
        with col4:
            return_date = st.date_input(
                "Return",
                value=departure_date + timedelta(days=7),
                min_value=departure_date + timedelta(days=1),
                help="Return date"
            )
        
        col5, col6, col7 = st.columns([1, 1, 2])
        
        with col5:
            travelers = st.number_input(
                "Travelers",
                min_value=1,
                max_value=10,
                value=CONFIG.DEFAULT_TRAVELERS,
                help="Number of travelers"
            )
        
        with col6:
            flight_pref = st.selectbox(
                "Flight Class",
                options=["economy", "premium economy", "business", "first class"],
                help="Preferred cabin class"
            )
        
        with col7:
            budget = st.slider(
                "💰 Total Budget (USD)",
                min_value=int(CONFIG.MIN_BUDGET),
                max_value=int(CONFIG.MAX_BUDGET),
                value=int(CONFIG.DEFAULT_BUDGET),
                step=int(CONFIG.BUDGET_STEP),
                format="$%d",
                help="Total budget for the entire trip including flights, hotels, and activities"
            )
        
        st.markdown("---")
        
        # Section 2: Hotel Details
        st.markdown("### 🏨 Hotel Details")
        
        col1, col2 = st.columns(2)
        
        with col1:
            hotel_location = st.text_input(
                "Hotel Location/Area",
                placeholder="e.g., Galle, Colombo Downtown, Near Eiffel Tower",
                help="Where would you like to stay? Enter a city, neighborhood, or landmark"
            )
        
        with col2:
            hotel_pref = st.text_input(
                "Hotel Preferences (Optional)",
                placeholder="e.g., beachfront, pool, spa, luxury, budget-friendly",
                help="Any specific amenities or style you prefer?"
            )
        
        st.markdown("---")
        
        # Section 3: Activities & Interests
        st.markdown("### 🎭 Activities & Interests")
        
        interests = st.multiselect(
            "What do you want to do?",
            options=list(CONFIG.INTEREST_OPTIONS),
            default=["culture", "food"],
            help="Select activities you'd enjoy during your trip"
        )
        
        st.markdown("---")
        
        # Section 4: Additional Notes
        st.markdown("### 📝 Additional Requirements")
        
        additional_notes = st.text_area(
            "Any special requests or notes?",
            placeholder="e.g., We're celebrating a honeymoon, prefer quiet areas, need wheelchair accessibility, traveling with kids, interested in local cuisine...",
            help="Share any specific requirements or preferences. Our AI will consider these when planning your trip.",
            height=100
        )
        
        st.markdown("---")
        
        # Submit button
        submitted = st.form_submit_button(
            "🚀 Plan My Trip",
            use_container_width=True,
            type="primary"
        )
        
        if submitted:
            # Validation
            if not origin:
                st.error("⚠️ Please enter your departure city")
                return None
            if not destination:
                st.error("⚠️ Please select or enter a destination")
                return None
            if not hotel_location:
                st.error("⚠️ Please enter a hotel location/area")
                return None
            if return_date <= departure_date:
                st.error("⚠️ Return date must be after departure date")
                return None
            
            return (
                origin,
                destination,
                departure_date,
                return_date,
                travelers,
                budget,
                interests,
                hotel_location,
                hotel_pref if hotel_pref else "",
                flight_pref,
                additional_notes if additional_notes else ""
            )
    
    return None


def render_quick_search() -> Optional[str]:
    """
    Render a quick search bar for simple queries.
    
    Returns:
        Search query if submitted, None otherwise
    """
    with st.container():
        query = st.text_input(
            "Quick Search",
            placeholder="e.g., Beach vacation in Bali for 2 people...",
            label_visibility="collapsed"
        )
        if query:
            return query
    return None
