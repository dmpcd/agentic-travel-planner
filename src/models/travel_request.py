"""
Travel Request Model
Defines what information users provide when planning a trip.
"""
from pydantic import BaseModel, Field
from datetime import date
from typing import Optional, List


class TravelRequest(BaseModel):
    """What the user wants for their trip"""
    
    # Required fields
    origin: str = Field(..., description="Departure city", example="New York")
    destination: str = Field(..., description="Destination city", example="Tokyo")
    departure_date: date = Field(..., description="When to leave")
    return_date: date = Field(..., description="When to come back")
    
    # Optional preferences
    budget: Optional[float] = Field(None, description="Maximum budget in USD")
    travelers: int = Field(1, description="Number of travelers")
    interests: List[str] = Field(default_factory=list, description="User interests")
    hotel_preferences: Optional[str] = Field(None, description="Hotel preferences")
    flight_preferences: Optional[str] = Field(None, description="Flight preferences")
    
    class Config:
        json_schema_extra = {
            "example": {
                "origin": "New York",
                "destination": "Tokyo",
                "departure_date": "2026-04-15",
                "return_date": "2026-04-20",
                "budget": 3000,
                "travelers": 2,
                "interests": ["food", "technology", "culture"],
                "hotel_preferences": "close to city center",
                "flight_preferences": "direct flight preferred"
            }
        }


# Test the model if run directly
if __name__ == "__main__":
    # Create a sample travel request
    request = TravelRequest(
        origin="New York",
        destination="Tokyo",
        departure_date=date(2026, 4, 15),
        return_date=date(2026, 4, 20),
        budget=3000,
        travelers=2,
        interests=["food", "technology", "culture"]
    )
    
    print("Travel Request Model Created Successfully!")
    print("\n--- Sample Travel Request ---")
    print(f"From: {request.origin}")
    print(f"To: {request.destination}")
    print(f"Dates: {request.departure_date} to {request.return_date}")
    print(f"Budget: ${request.budget}")
    print(f"Travelers: {request.travelers}")
    print(f"Interests: {', '.join(request.interests)}")
    
    print("\n--- JSON Output ---")
    print(request.model_dump_json(indent=2))
