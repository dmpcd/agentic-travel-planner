"""
Flight Model
Defines the structure for flight data.
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List


class FlightSegment(BaseModel):
    """A single flight segment (one takeoff and landing)"""
    airline: str = Field(..., description="Airline name", example="ANA")
    flight_number: str = Field(..., description="Flight number", example="NH109")
    departure_airport: str = Field(..., description="Departure airport code", example="JFK")
    arrival_airport: str = Field(..., description="Arrival airport code", example="NRT")
    departure_time: datetime = Field(..., description="Departure date and time")
    arrival_time: datetime = Field(..., description="Arrival date and time")
    duration_minutes: int = Field(..., description="Flight duration in minutes")


class Flight(BaseModel):
    """Complete flight option (can have multiple segments for connecting flights)"""
    id: str = Field(..., description="Unique flight identifier")
    segments: List[FlightSegment] = Field(..., description="List of flight segments")
    total_price: float = Field(..., description="Total price in USD")
    currency: str = Field("USD", description="Currency code")
    total_duration_minutes: int = Field(..., description="Total travel time including layovers")
    stops: int = Field(..., description="Number of stops (0 = direct)")
    cabin_class: str = Field("economy", description="Cabin class")
    
    @property
    def is_direct(self) -> bool:
        """Check if this is a direct flight"""
        return self.stops == 0
    
    @property
    def formatted_duration(self) -> str:
        """Get human-readable duration"""
        hours = self.total_duration_minutes // 60
        minutes = self.total_duration_minutes % 60
        return f"{hours}h {minutes}m"
    
    @property
    def formatted_price(self) -> str:
        """Get formatted price with currency"""
        return f"${self.total_price:,.2f}"


# Test the model if run directly
if __name__ == "__main__":
    # Create a sample direct flight
    direct_flight = Flight(
        id="FL001",
        segments=[
            FlightSegment(
                airline="ANA",
                flight_number="NH109",
                departure_airport="JFK",
                arrival_airport="NRT",
                departure_time=datetime(2026, 4, 15, 10, 30),
                arrival_time=datetime(2026, 4, 15, 14, 30),
                duration_minutes=840
            )
        ],
        total_price=1250.00,
        total_duration_minutes=840,
        stops=0
    )
    
    # Create a sample connecting flight
    connecting_flight = Flight(
        id="FL002",
        segments=[
            FlightSegment(
                airline="United",
                flight_number="UA881",
                departure_airport="JFK",
                arrival_airport="SFO",
                departure_time=datetime(2026, 4, 15, 8, 0),
                arrival_time=datetime(2026, 4, 15, 11, 30),
                duration_minutes=330
            ),
            FlightSegment(
                airline="United",
                flight_number="UA837",
                departure_airport="SFO",
                arrival_airport="NRT",
                departure_time=datetime(2026, 4, 15, 13, 0),
                arrival_time=datetime(2026, 4, 15, 17, 0),
                duration_minutes=660
            )
        ],
        total_price=980.00,
        total_duration_minutes=1140,
        stops=1
    )
    
    print("Flight Model Created Successfully!")
    print("\n--- Direct Flight ---")
    print(f"ID: {direct_flight.id}")
    print(f"Route: {direct_flight.segments[0].departure_airport} → {direct_flight.segments[0].arrival_airport}")
    print(f"Airline: {direct_flight.segments[0].airline}")
    print(f"Price: {direct_flight.formatted_price}")
    print(f"Duration: {direct_flight.formatted_duration}")
    print(f"Direct: {direct_flight.is_direct}")
    
    print("\n--- Connecting Flight ---")
    print(f"ID: {connecting_flight.id}")
    print(f"Route: {connecting_flight.segments[0].departure_airport} → {connecting_flight.segments[-1].arrival_airport}")
    print(f"Stops: {connecting_flight.stops}")
    print(f"Price: {connecting_flight.formatted_price}")
    print(f"Duration: {connecting_flight.formatted_duration}")
    print(f"Segments: {len(connecting_flight.segments)}")
