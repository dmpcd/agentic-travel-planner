"""
API Response Schemas
Pydantic models for API responses to ensure type safety and auto-documentation.
"""
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
from datetime import datetime


# ============================================
# FLIGHT RESPONSE SCHEMAS
# ============================================

class FlightSegmentResponse(BaseModel):
    """Flight segment in API response"""
    airline: str
    flight_number: str
    departure_airport: str
    arrival_airport: str
    departure_time: str
    arrival_time: str
    duration_minutes: int


class FlightResponse(BaseModel):
    """Flight option in API response"""
    id: str
    segments: List[FlightSegmentResponse]
    total_price: float
    currency: str
    total_duration_minutes: int
    stops: int
    cabin_class: str


class FlightsResult(BaseModel):
    """Flight search results"""
    outbound_flights: List[Dict[str, Any]] = []
    return_flights: List[Dict[str, Any]] = []
    recommended_outbound: Optional[Dict[str, Any]] = None
    recommended_return: Optional[Dict[str, Any]] = None
    reasoning: str = ""
    total_flights_found: int = 0


# ============================================
# HOTEL RESPONSE SCHEMAS
# ============================================

class HotelResponse(BaseModel):
    """Hotel option in API response"""
    id: str
    name: str
    address: str
    star_rating: float
    user_rating: float
    price_per_night: float
    currency: str
    amenities: List[str]
    distance_to_center_km: float


class HotelsResult(BaseModel):
    """Hotel search results"""
    hotels: List[Dict[str, Any]] = []
    recommended: Optional[Dict[str, Any]] = None
    reasoning: str = ""
    total_found: int = 0


# ============================================
# ACTIVITY RESPONSE SCHEMAS
# ============================================

class ActivityResponse(BaseModel):
    """Activity option in API response"""
    id: str
    name: str
    description: str
    category: str
    location: str
    duration_hours: float
    price: float
    rating: float


class ActivitiesResult(BaseModel):
    """Activity search results"""
    activities: List[Dict[str, Any]] = []
    recommended: List[Dict[str, Any]] = []
    reasoning: str = ""
    total_found: int = 0


# ============================================
# BUDGET RESPONSE SCHEMAS
# ============================================

class BudgetBreakdown(BaseModel):
    """Budget breakdown details"""
    flights: float = 0
    hotels: float = 0
    activities: float = 0
    meals_and_misc: float = 0
    total: float = 0
    budget: Optional[float] = None
    remaining: Optional[float] = None
    within_budget: bool = True


class BudgetResult(BaseModel):
    """Budget analysis results"""
    breakdown: BudgetBreakdown
    reasoning: str = ""
    within_budget: bool = True
    total_cost: float = 0
    budget_status: str = "within"


# ============================================
# TRIP PLAN RESPONSE SCHEMAS
# ============================================

class TripDates(BaseModel):
    """Trip date information"""
    departure: str
    return_date: str = Field(..., alias="return")
    duration_days: int
    
    class Config:
        populate_by_name = True


class TripMetadata(BaseModel):
    """LangGraph execution metadata"""
    optimization_iterations: int = 0
    within_budget: bool = True
    total_cost: float = 0
    errors: List[str] = []


class TripPlanResponse(BaseModel):
    """Complete trip plan response"""
    trip_summary: str
    destination: str
    dates: TripDates
    travelers: int
    flights: FlightsResult
    hotels: HotelsResult
    activities: ActivitiesResult
    budget: BudgetResult
    created_at: str
    metadata: TripMetadata
    
    class Config:
        json_schema_extra = {
            "example": {
                "trip_summary": "Your perfect Tokyo adventure awaits...",
                "destination": "Tokyo",
                "dates": {
                    "departure": "2026-04-15",
                    "return": "2026-04-20",
                    "duration_days": 5
                },
                "travelers": 2,
                "flights": {
                    "total_flights_found": 10,
                    "reasoning": "Direct ANA flight recommended..."
                },
                "hotels": {
                    "total_found": 5,
                    "reasoning": "Park Hyatt Tokyo offers best value..."
                },
                "activities": {
                    "total_found": 15,
                    "reasoning": "Mix of culture and food experiences..."
                },
                "budget": {
                    "breakdown": {
                        "flights": 2500,
                        "hotels": 1100,
                        "activities": 200,
                        "meals_and_misc": 1000,
                        "total": 4800
                    }
                },
                "created_at": "2026-01-13T10:30:00",
                "metadata": {
                    "optimization_iterations": 0,
                    "within_budget": True,
                    "total_cost": 4800,
                    "errors": []
                }
            }
        }


# ============================================
# ERROR RESPONSE SCHEMAS
# ============================================

class ErrorDetail(BaseModel):
    """Error detail for API errors"""
    message: str
    code: str = "UNKNOWN_ERROR"
    details: Optional[Dict[str, Any]] = None


class ErrorResponse(BaseModel):
    """Standard error response"""
    error: ErrorDetail
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": {
                    "message": "Invalid date range: return date must be after departure date",
                    "code": "VALIDATION_ERROR"
                }
            }
        }


# ============================================
# HEALTH CHECK SCHEMAS
# ============================================

class HealthResponse(BaseModel):
    """Health check response"""
    status: str = "healthy"
    version: str = "1.0.0"
    timestamp: str
    services: Dict[str, str] = {}
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "version": "1.0.0",
                "timestamp": "2026-01-13T10:30:00Z",
                "services": {
                    "langgraph": "operational",
                    "llm": "operational"
                }
            }
        }
