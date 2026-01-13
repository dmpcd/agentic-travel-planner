"""
API Package
FastAPI-based REST API for the Agentic Travel Planner.
"""

from .main import app
from .routes import travel_router

__all__ = ['app', 'travel_router']
