"""
Streamlit Frontend Configuration
Centralized configuration and constants.
"""
from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class AppConfig:
    """Application configuration constants."""
    APP_TITLE: str = "🌍 AI Travel Planner"
    APP_ICON: str = "✈️"
    PAGE_LAYOUT: str = "wide"
    
    # Default values
    DEFAULT_TRAVELERS: int = 2
    DEFAULT_BUDGET: float = 5000.0
    MIN_BUDGET: float = 500.0
    MAX_BUDGET: float = 50000.0
    BUDGET_STEP: float = 500.0
    
    # Interest options
    INTEREST_OPTIONS: tuple = (
        "beach", "surfing", "diving", "snorkeling",
        "culture", "history", "art", "architecture",
        "food", "nightlife", "shopping",
        "nature", "hiking", "wildlife", "adventure",
        "relaxation", "spa"
    )
    
    # Popular destinations
    POPULAR_DESTINATIONS: tuple = (
        "Tokyo, Japan",
        "Paris, France", 
        "Bali, Indonesia",
        "Sri Lanka",
        "New York, USA",
        "Barcelona, Spain",
        "Sydney, Australia",
        "Rome, Italy",
        "Maldives",
        "Thailand"
    )


# Color scheme for consistent styling
class Colors:
    PRIMARY = "#FF4B4B"
    SECONDARY = "#0068C9"
    SUCCESS = "#09AB3B"
    WARNING = "#FACA2B"
    ERROR = "#FF4B4B"
    INFO = "#0068C9"
    
    # Category colors for activities
    ACTIVITY_COLORS = {
        "sightseeing": "#0068C9",
        "food": "#FF6B35",
        "culture": "#9B59B6",
        "nature": "#27AE60",
        "adventure": "#E74C3C",
        "shopping": "#F39C12",
        "relaxation": "#1ABC9C",
        "nightlife": "#8E44AD",
        "entertainment": "#3498DB"
    }


# Emoji icons for UI elements
class Icons:
    FLIGHT = "✈️"
    HOTEL = "🏨"
    ACTIVITY = "🎭"
    BUDGET = "💰"
    CALENDAR = "📅"
    TRAVELERS = "👥"
    LOCATION = "📍"
    STAR = "⭐"
    SUCCESS = "✅"
    WARNING = "⚠️"
    ERROR = "❌"
    LOADING = "⏳"
    SUMMARY = "📋"
    
    # Category icons
    CATEGORY_ICONS = {
        "sightseeing": "🏛️",
        "food": "🍽️",
        "culture": "🎭",
        "nature": "🌿",
        "adventure": "🏔️",
        "shopping": "🛍️",
        "relaxation": "🧘",
        "nightlife": "🌙",
        "entertainment": "🎬"
    }


CONFIG = AppConfig()
