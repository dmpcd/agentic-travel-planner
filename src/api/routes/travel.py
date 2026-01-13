"""
Travel API Routes
Endpoints for trip planning and travel-related operations.
"""
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import Dict, Any
from datetime import datetime
import uuid

from src.models.travel_request import TravelRequest
from src.api.schemas import (
    TripPlanResponse,
    ErrorResponse,
    HealthResponse,
)
from src.api.dependencies import get_trip_planner, verify_api_key


# Create router with prefix and tags for OpenAPI documentation
router = APIRouter(
    prefix="/api/v1",
    tags=["Travel Planning"],
    responses={
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)


# ============================================
# HEALTH CHECK ENDPOINTS
# ============================================

@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check",
    description="Check if the API is running and all services are operational."
)
async def health_check():
    """
    Health check endpoint for monitoring and load balancers.
    Returns status of all dependent services.
    """
    services = {}
    
    # Check LangGraph availability
    try:
        from src.agents.travel_graph import travel_planning_app
        services["langgraph"] = "operational" if travel_planning_app else "unavailable"
    except Exception:
        services["langgraph"] = "error"
    
    # Check LLM availability
    try:
        verify_api_key()
        services["llm"] = "operational"
    except Exception:
        services["llm"] = "not_configured"
    
    overall_status = "healthy" if all(
        s == "operational" for s in services.values()
    ) else "degraded"
    
    return HealthResponse(
        status=overall_status,
        version="1.0.0",
        timestamp=datetime.utcnow().isoformat() + "Z",
        services=services
    )


# ============================================
# TRIP PLANNING ENDPOINTS
# ============================================

@router.post(
    "/plan-trip",
    response_model=TripPlanResponse,
    summary="Plan a Complete Trip",
    description="""
    Plan a complete trip using AI agents. This endpoint:
    
    1. **Searches flights** - Finds best outbound and return flights
    2. **Searches hotels** - Recommends accommodations at destination
    3. **Finds activities** - Suggests things to do based on interests
    4. **Analyzes budget** - Ensures everything fits within budget
    5. **Generates summary** - Creates an engaging trip summary
    
    The planning is powered by LangGraph for intelligent workflow orchestration
    and uses AI for recommendations.
    
    **Note:** This operation may take 30-60 seconds as it involves multiple AI calls.
    """,
    responses={
        200: {"description": "Trip planned successfully"},
        400: {"model": ErrorResponse, "description": "Invalid request"},
        503: {"model": ErrorResponse, "description": "Service unavailable"}
    }
)
async def plan_trip(
    request: TravelRequest,
    plan_trip_fn = Depends(get_trip_planner)
):
    """
    Plan a complete trip based on user preferences.
    
    This is the main endpoint that orchestrates all travel planning agents.
    """
    # Validate date range
    if request.return_date <= request.departure_date:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Return date must be after departure date",
                "code": "INVALID_DATE_RANGE"
            }
        )
    
    # Validate budget if provided
    if request.budget is not None and request.budget <= 0:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Budget must be a positive number",
                "code": "INVALID_BUDGET"
            }
        )
    
    try:
        # Convert request to dict for the planner
        input_data = request.model_dump()
        
        # Execute the trip planning workflow
        result = await plan_trip_fn(input_data)
        
        return result
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "message": str(e),
                "code": "VALIDATION_ERROR"
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail={
                "message": f"Trip planning failed: {str(e)}",
                "code": "PLANNING_ERROR"
            }
        )


@router.post(
    "/plan-trip/async",
    summary="Plan Trip Asynchronously (Future)",
    description="Submit a trip planning request for async processing. Returns a job ID.",
    include_in_schema=False  # Hidden for now - future feature
)
async def plan_trip_async(
    request: TravelRequest,
    background_tasks: BackgroundTasks
):
    """
    Async trip planning for long-running requests.
    Returns immediately with a job ID that can be polled.
    
    TODO: Implement with Redis/Celery for production use.
    """
    job_id = str(uuid.uuid4())
    
    # In production, this would queue the task
    # background_tasks.add_task(process_trip_planning, job_id, request)
    
    return {
        "job_id": job_id,
        "status": "queued",
        "message": "Trip planning started. Poll /api/v1/jobs/{job_id} for status.",
        "estimated_time_seconds": 60
    }


# ============================================
# UTILITY ENDPOINTS
# ============================================

@router.get(
    "/destinations/popular",
    summary="Get Popular Destinations",
    description="Returns a list of popular travel destinations."
)
async def get_popular_destinations():
    """
    Get list of popular destinations for suggestions.
    """
    return {
        "destinations": [
            {"city": "Tokyo", "country": "Japan", "code": "TYO"},
            {"city": "Paris", "country": "France", "code": "PAR"},
            {"city": "New York", "country": "USA", "code": "NYC"},
            {"city": "London", "country": "UK", "code": "LON"},
            {"city": "Barcelona", "country": "Spain", "code": "BCN"},
            {"city": "Rome", "country": "Italy", "code": "ROM"},
            {"city": "Bangkok", "country": "Thailand", "code": "BKK"},
            {"city": "Sydney", "country": "Australia", "code": "SYD"},
            {"city": "Dubai", "country": "UAE", "code": "DXB"},
            {"city": "Singapore", "country": "Singapore", "code": "SIN"},
        ]
    }


@router.get(
    "/interests",
    summary="Get Available Interest Categories",
    description="Returns available interest categories for trip personalization."
)
async def get_interests():
    """
    Get list of available interests for trip personalization.
    """
    return {
        "interests": [
            {"id": "food", "label": "Food & Dining", "icon": "🍜"},
            {"id": "culture", "label": "Culture & History", "icon": "🏛️"},
            {"id": "adventure", "label": "Adventure & Sports", "icon": "🏔️"},
            {"id": "relaxation", "label": "Relaxation & Wellness", "icon": "🧘"},
            {"id": "nightlife", "label": "Nightlife & Entertainment", "icon": "🎉"},
            {"id": "shopping", "label": "Shopping", "icon": "🛍️"},
            {"id": "nature", "label": "Nature & Wildlife", "icon": "🌿"},
            {"id": "technology", "label": "Technology & Innovation", "icon": "🤖"},
            {"id": "art", "label": "Art & Museums", "icon": "🎨"},
            {"id": "photography", "label": "Photography", "icon": "📸"},
        ]
    }
