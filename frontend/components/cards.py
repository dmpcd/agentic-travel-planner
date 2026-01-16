"""
Card Components
Display cards for flights, hotels, and activities.
"""
import streamlit as st
from typing import Dict, Any, Optional

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Icons, Colors


def render_flight_card(flight: Dict[str, Any], is_recommended: bool = False) -> None:
    """
    Render a flight option card.
    
    Args:
        flight: Flight data dictionary
        is_recommended: Whether this is the recommended option
    """
    with st.container():
        if is_recommended:
            st.markdown("⭐ **Recommended**")
        
        # Extract flight details - handle both flat and nested structures
        segments = flight.get("segments", [])
        
        if segments:
            # Nested structure (from Flight model)
            first_segment = segments[0] if segments else {}
            last_segment = segments[-1] if segments else {}
            departure = first_segment.get("departure_airport", "N/A")
            arrival = last_segment.get("arrival_airport", "N/A")
            airline = first_segment.get("airline", "Unknown Airline")
        else:
            # Flat structure fallback
            departure = flight.get("departure_airport", flight.get("origin", "N/A"))
            arrival = flight.get("arrival_airport", flight.get("destination", "N/A"))
            airline = flight.get("airline", "Unknown Airline")
        
        price = flight.get("total_price", flight.get("price", 0))
        stops = flight.get("stops", 0)
        duration = flight.get("total_duration_minutes", flight.get("duration", 0))
        cabin = flight.get("cabin_class", "economy")
        
        # Format duration
        if isinstance(duration, int) and duration > 0:
            hours = duration // 60
            mins = duration % 60
            duration_str = f"{hours}h {mins}m"
        else:
            duration_str = str(duration) if duration else "N/A"
        
        # Stops text
        stops_text = "Direct ✨" if stops == 0 else f"{stops} stop{'s' if stops > 1 else ''}"
        
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            st.markdown(f"**{Icons.FLIGHT} {departure} → {arrival}**")
            st.caption(f"{airline} • {cabin.title()}")
        
        with col2:
            st.markdown(f"⏱️ {duration_str}")
            st.caption(stops_text)
        
        with col3:
            st.markdown(f"**${price:,.0f}**" if isinstance(price, (int, float)) else f"**{price}**")
        
        st.divider()


def render_hotel_card(hotel: Dict[str, Any], is_recommended: bool = False) -> None:
    """
    Render a hotel option card.
    
    Args:
        hotel: Hotel data dictionary
        is_recommended: Whether this is the recommended option
    """
    with st.container():
        if is_recommended:
            st.markdown("⭐ **Recommended**")
        
        # Extract hotel details
        name = hotel.get("name", "Unknown Hotel")
        address = hotel.get("address", hotel.get("location", ""))
        price = hotel.get("price_per_night", 0)
        rating = hotel.get("star_rating", hotel.get("user_rating", 0))
        amenities = hotel.get("amenities", [])
        distance = hotel.get("distance_to_center_km", hotel.get("distance_km", None))
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown(f"**{Icons.HOTEL} {name}**")
            
            # Rating stars
            if rating:
                stars = "⭐" * int(min(rating, 5))
                st.caption(f"{stars} ({rating:.1f})")
            
            # Address
            if address:
                st.caption(f"📍 {address[:60]}{'...' if len(address) > 60 else ''}")
            
            # Distance
            if distance:
                st.caption(f"📏 {distance:.1f} km from center")
            
            # Amenities
            if amenities and isinstance(amenities, list):
                amenities_str = " • ".join(amenities[:5])
                st.caption(f"🏷️ {amenities_str}")
        
        with col2:
            st.markdown(f"**${price:,.0f}**" if isinstance(price, (int, float)) else f"**{price}**")
            st.caption("per night")
        
        st.divider()


def render_activity_card(activity: Dict[str, Any], is_recommended: bool = False) -> None:
    """
    Render an activity card.
    
    Args:
        activity: Activity data dictionary
        is_recommended: Whether this is the recommended option
    """
    with st.container():
        if is_recommended:
            st.markdown("⭐ **Recommended**")
        
        # Extract activity details
        name = activity.get("name", "Unknown Activity")
        category = activity.get("category", "other")
        description = activity.get("description", "")
        location = activity.get("location", activity.get("address", ""))
        price = activity.get("price", 0)
        duration = activity.get("duration_hours", None)
        rating = activity.get("rating", None)
        
        # Handle enum category
        if hasattr(category, "value"):
            category = category.value
        
        # Get category icon
        category_icon = Icons.CATEGORY_ICONS.get(category.lower(), "🎯")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown(f"**{category_icon} {name}**")
            
            # Category badge
            category_color = Colors.ACTIVITY_COLORS.get(category.lower(), "#666")
            st.caption(f"🏷️ {category.title()}")
            
            # Description
            if description:
                desc_preview = description[:100] + "..." if len(description) > 100 else description
                st.caption(desc_preview)
            
            # Location
            if location:
                loc_preview = location[:50] + "..." if len(location) > 50 else location
                st.caption(f"📍 {loc_preview}")
            
            # Duration and rating
            info_parts = []
            if duration:
                info_parts.append(f"⏱️ {duration}h")
            if rating:
                info_parts.append(f"⭐ {rating:.1f}")
            if info_parts:
                st.caption(" • ".join(info_parts))
        
        with col2:
            if price == 0:
                st.markdown("**Free**")
            elif isinstance(price, (int, float)):
                st.markdown(f"**${price:,.0f}**")
            else:
                st.markdown(f"**{price}**")
        
        st.divider()


def render_budget_card(budget_analysis: Dict[str, Any], within_budget: bool) -> None:
    """
    Render a budget summary card.
    
    Args:
        budget_analysis: Budget analysis data
        within_budget: Whether the trip is within budget
    """
    with st.container():
        st.markdown(f"### {Icons.BUDGET} Budget Summary")
        
        # Status indicator
        if within_budget:
            st.success(f"{Icons.SUCCESS} Within Budget!")
        else:
            st.warning(f"{Icons.WARNING} Over Budget")
        
        # Cost breakdown
        flights_cost = budget_analysis.get("flights_cost", 0)
        hotels_cost = budget_analysis.get("hotels_cost", 0)
        activities_cost = budget_analysis.get("activities_cost", 0)
        total_cost = budget_analysis.get("total_cost", flights_cost + hotels_cost + activities_cost)
        budget = budget_analysis.get("budget", 0)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Flights", f"${flights_cost:,.0f}")
        with col2:
            st.metric("Hotels", f"${hotels_cost:,.0f}")
        with col3:
            st.metric("Activities", f"${activities_cost:,.0f}")
        with col4:
            delta = budget - total_cost if budget else None
            st.metric(
                "Total",
                f"${total_cost:,.0f}",
                delta=f"${delta:,.0f} remaining" if delta and delta > 0 else None,
                delta_color="normal" if delta and delta > 0 else "inverse"
            )
