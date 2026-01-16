"""
AI Travel Planner - Streamlit Frontend
Main entry point for the Streamlit application.

Run with: streamlit run frontend/app.py
"""
import streamlit as st
import sys
import os

# Add project paths
FRONTEND_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(FRONTEND_DIR)
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, FRONTEND_DIR)

from config import CONFIG, Icons
from components.forms import render_travel_form
from components.results import render_results_section, render_errors
from utils.api_client import TravelPlannerClient, TripRequest


# ============================================
# PAGE CONFIGURATION
# ============================================

st.set_page_config(
    page_title=CONFIG.APP_TITLE,
    page_icon=CONFIG.APP_ICON,
    layout=CONFIG.PAGE_LAYOUT,
    initial_sidebar_state="collapsed"
)


# ============================================
# CUSTOM CSS
# ============================================

st.markdown("""
<style>
    /* Main container - full width */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
        max-width: 100%;
        padding-left: 3rem;
        padding-right: 3rem;
    }
    
    /* Form container styling */
    [data-testid="stForm"] {
        background: linear-gradient(135deg, #1a2a3a 0%, #243b53 100%);
        padding: 30px;
        border-radius: 15px;
        border: 1px solid #3d5a80;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    }
    
    /* Section headers in form */
    [data-testid="stForm"] h3 {
        color: #ffffff !important;
        margin-bottom: 15px !important;
        padding-bottom: 8px;
        border-bottom: 2px solid #3d7ab5;
    }
    
    /* All labels should be white and visible */
    .stTextInput label, .stSelectbox label, .stDateInput label,
    .stNumberInput label, .stSlider label, .stMultiSelect label,
    .stCheckbox label, .stTextArea label {
        color: #ffffff !important;
        font-weight: 600 !important;
        font-size: 14px !important;
    }
    
    /* Input fields styling */
    .stTextInput input, .stSelectbox select, .stNumberInput input,
    .stTextArea textarea {
        background-color: #ffffff !important;
        color: #1a1a2e !important;
        border-radius: 8px !important;
    }
    
    /* Text area specific */
    .stTextArea textarea {
        min-height: 80px !important;
    }
    
    /* Placeholder text */
    .stTextInput input::placeholder, .stTextArea textarea::placeholder {
        color: #666666 !important;
        opacity: 1 !important;
    }
    
    /* Make markdown text visible in forms */
    [data-testid="stForm"] .stMarkdown {
        color: #ffffff !important;
    }

    [data-testid="stForm"] p, [data-testid="stForm"] span {
        color: #e0e0e0 !important;
    }
    
    /* Checkbox styling */
    .stCheckbox span {
        color: #ffffff !important;
    }
    
    /* Multiselect styling */
    .stMultiSelect > div > div {
        background-color: #ffffff !important;
    }
    
    /* Metric styling */
    div[data-testid="metric-container"] {
        background-color: #1e3a5f;
        border-radius: 10px;
        padding: 15px;
        border: 1px solid #3d7ab5;
    }
    
    div[data-testid="metric-container"] label {
        color: #a0c4e8 !important;
    }
    
    div[data-testid="metric-container"] [data-testid="stMetricValue"] {
        color: #ffffff !important;
    }
    
    /* Button styling */
    .stButton > button {
        border-radius: 25px;
        font-weight: 600;
        padding: 12px 30px;
        font-size: 16px;
        background: linear-gradient(90deg, #ff6b6b 0%, #ff8e53 100%);
        border: none;
        color: white;
    }
    
    .stButton > button:hover {
        background: linear-gradient(90deg, #ff8e53 0%, #ff6b6b 100%);
        transform: translateY(-2px);
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #1a1a2e;
        padding: 5px;
        border-radius: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 10px 20px;
        color: #ffffff;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #3d7ab5 !important;
    }
    
    /* Cards and containers */
    .stExpander {
        background-color: #1e3a5f;
        border-radius: 10px;
        border: 1px solid #3d7ab5;
    }
    
    /* Divider */
    hr {
        margin: 1rem 0;
        border-color: #3d7ab5;
    }
    
    /* Success/Warning messages */
    .stSuccess {
        background-color: #1b4332 !important;
        color: #95d5b2 !important;
    }
    
    .stWarning {
        background-color: #5c4813 !important;
        color: #ffd166 !important;
    }
    
    /* Result cards */
    .result-card {
        background: linear-gradient(135deg, #1e3a5f 0%, #2d4a6f 100%);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
        border: 1px solid #3d7ab5;
    }
    
    /* Page title */
    h1 {
        color: #ffffff !important;
    }
    
    /* Help tooltips */
    .stTooltipIcon svg {
        fill: #a0c4e8 !important;
    }
    
    /* Multiselect tags */
    .stMultiSelect [data-baseweb="tag"] {
        background-color: #3d7ab5 !important;
    }
    
    /* Slider */
    .stSlider [data-baseweb="slider"] {
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)


# ============================================
# SESSION STATE INITIALIZATION
# ============================================

if "trip_results" not in st.session_state:
    st.session_state.trip_results = None

if "is_planning" not in st.session_state:
    st.session_state.is_planning = False

if "last_request" not in st.session_state:
    st.session_state.last_request = None


# ============================================
# MAIN APP
# ============================================

def main():
    """Main application entry point."""
    
    # Header
    col_header1, col_header2 = st.columns([3, 1])
    with col_header1:
        st.markdown(f"# {CONFIG.APP_TITLE}")
        st.markdown("*Powered by AI agents using LangGraph, Amadeus & Geoapify APIs*")
    
    st.divider()
    
    # Full-width form at the top, results below
    # Render the travel form
    form_data = render_travel_form()
    
    if form_data:
        # Unpack form data (now includes hotel_location and notes)
        (origin, destination, departure_date, return_date,
         travelers, budget, interests, hotel_location, hotel_pref, 
         flight_pref, additional_notes) = form_data
        
        # Create request object
        request = TripRequest(
            origin=origin,
            destination=destination,
            departure_date=departure_date,
            return_date=return_date,
            travelers=travelers,
            budget=float(budget),
            interests=interests,
            hotel_preferences=f"{hotel_location}; {hotel_pref}" if hotel_pref else hotel_location,
            flight_preferences=flight_pref,
            additional_notes=additional_notes
        )
        
        # Store request
        st.session_state.last_request = request
        st.session_state.is_planning = True
    
    st.divider()
    
    # Results section (full width)
    if st.session_state.is_planning and st.session_state.last_request:
        with st.spinner(f"{Icons.LOADING} Planning your perfect trip... This may take a minute."):
            try:
                # Execute the planning
                client = TravelPlannerClient()
                results = client.plan_trip(st.session_state.last_request)
                
                # Store results
                st.session_state.trip_results = results
                st.session_state.is_planning = False
                
                # Force rerun to display results
                st.rerun()
                
            except Exception as e:
                st.error(f"{Icons.ERROR} An error occurred: {str(e)}")
                st.session_state.is_planning = False
    
    elif st.session_state.trip_results:
        # Display results
        results = st.session_state.trip_results
        
        # Show any errors first
        if results.errors:
            render_errors(results.errors)
        
        # Render results
        render_results_section(results)
        
        # Reset button
        st.markdown("---")
        if st.button("🔄 Plan Another Trip", use_container_width=True):
            st.session_state.trip_results = None
            st.session_state.last_request = None
            st.rerun()
    
    else:
        # Welcome message when no results
        st.markdown("""
        <div style="text-align: center; padding: 40px 20px;">
            <h2>👆 Fill out the form above to start planning!</h2>
            <p style="color: #888; font-size: 18px;">
                Our AI agents will find the best flights, hotels, and activities for your trip.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Feature highlights
        col1, col2, col3, col4, col5 = st.columns(5)
        features = [
            ("✈️", "Flights", "Real Amadeus API"),
            ("🏨", "Hotels", "Best prices"),
            ("🎭", "Activities", "Local experiences"),
            ("💰", "Budget", "AI optimization"),
            ("📋", "Summary", "Complete itinerary")
        ]
        for col, (icon, title, desc) in zip([col1, col2, col3, col4, col5], features):
            with col:
                st.markdown(f"### {icon}")
                st.markdown(f"**{title}**")
                st.caption(desc)


# ============================================
# RUN APP
# ============================================

if __name__ == "__main__":
    main()
