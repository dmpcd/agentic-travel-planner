"""
Activity Model
Defines the structure for activities and things to do.
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class ActivityCategory(str, Enum):
    """Categories of activities"""
    SIGHTSEEING = "sightseeing"
    FOOD = "food"
    CULTURE = "culture"
    NATURE = "nature"
    ADVENTURE = "adventure"
    SHOPPING = "shopping"
    RELAXATION = "relaxation"
    NIGHTLIFE = "nightlife"
    ENTERTAINMENT = "entertainment"


class Activity(BaseModel):
    """Thing to do at destination"""
    id: str = Field(..., description="Unique activity identifier")
    name: str = Field(..., description="Activity name")
    description: str = Field(..., description="Activity description")
    category: ActivityCategory = Field(..., description="Activity category")
    location: str = Field(..., description="Activity location")
    duration_hours: float = Field(..., description="Estimated duration in hours")
    price: float = Field(0, description="Price in USD (0 = free)")
    currency: str = Field("USD", description="Currency code")
    rating: float = Field(..., ge=0, le=5, description="Rating (0-5)")
    best_time: Optional[str] = Field(None, description="Best time to visit")
    tags: List[str] = Field(default_factory=list, description="Activity tags")
    
    @property
    def is_free(self) -> bool:
        """Check if activity is free"""
        return self.price == 0
    
    @property
    def formatted_price(self) -> str:
        """Get formatted price"""
        if self.is_free:
            return "Free"
        return f"${self.price:,.2f}"
    
    @property
    def formatted_duration(self) -> str:
        """Get formatted duration"""
        if self.duration_hours < 1:
            return f"{int(self.duration_hours * 60)} minutes"
        elif self.duration_hours == 1:
            return "1 hour"
        else:
            return f"{self.duration_hours} hours"


# Test the model if run directly
if __name__ == "__main__":
    activity = Activity(
        id="ACT001",
        name="Visit Senso-ji Temple",
        description="Tokyo's oldest and most significant temple",
        category=ActivityCategory.CULTURE,
        location="Asakusa, Tokyo",
        duration_hours=2.0,
        price=0,
        rating=4.7,
        best_time="morning",
        tags=["historic", "spiritual", "photography"]
    )
    
    print("Activity Model Created Successfully!")
    print(f"\nActivity: {activity.name}")
    print(f"Category: {activity.category.value}")
    print(f"Duration: {activity.formatted_duration}")
    print(f"Price: {activity.formatted_price}")
    print(f"Rating: {activity.rating}⭐")
    print(f"Best time: {activity.best_time}")
    print(f"Tags: {', '.join(activity.tags)}")
