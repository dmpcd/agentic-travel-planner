"""
Hotel Model
Defines the structure for hotel accommodation data.
"""
from pydantic import BaseModel, Field
from typing import List, Optional


class Hotel(BaseModel):
    """Hotel accommodation option"""
    id: str = Field(..., description="Unique hotel identifier")
    name: str = Field(..., description="Hotel name")
    address: str = Field(..., description="Hotel address")
    star_rating: float = Field(..., ge=1, le=5, description="Star rating (1-5)")
    user_rating: float = Field(..., ge=0, le=10, description="User rating (0-10)")
    price_per_night: float = Field(..., description="Price per night in USD")
    currency: str = Field("USD", description="Currency code")
    amenities: List[str] = Field(default_factory=list, description="Hotel amenities")
    distance_to_center_km: float = Field(..., description="Distance to city center in km")
    image_url: Optional[str] = Field(None, description="Hotel image URL")
    
    @property
    def rating_category(self) -> str:
        """Get rating category based on user rating"""
        if self.user_rating >= 9:
            return "Excellent"
        elif self.user_rating >= 8:
            return "Very Good"
        elif self.user_rating >= 7:
            return "Good"
        else:
            return "Average"
    
    @property
    def formatted_price(self) -> str:
        """Get formatted price"""
        return f"${self.price_per_night:,.2f}/night"


# Test the model if run directly
if __name__ == "__main__":
    hotel = Hotel(
        id="HTL001",
        name="Park Hyatt Tokyo",
        address="3-7-1-2 Nishi Shinjuku, Shinjuku-ku, Tokyo",
        star_rating=5.0,
        user_rating=9.2,
        price_per_night=450.00,
        amenities=["WiFi", "Pool", "Spa", "Restaurant", "Gym"],
        distance_to_center_km=2.5
    )
    
    print("Hotel Model Created Successfully!")
    print(f"\nHotel: {hotel.name}")
    print(f"Rating: {hotel.star_rating}⭐ ({hotel.rating_category})")
    print(f"Price: {hotel.formatted_price}")
    print(f"Amenities: {', '.join(hotel.amenities)}")
    print(f"Location: {hotel.distance_to_center_km}km from center")
