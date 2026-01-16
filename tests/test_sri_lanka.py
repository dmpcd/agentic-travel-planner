"""Test the India -> Sri Lanka route"""
import asyncio
import sys
sys.path.insert(0, '.')

async def test_india_sri_lanka():
    print('='*60)
    print('TESTING: India -> Sri Lanka Route')
    print('='*60)
    
    from src.tools.flight_search import FlightSearchTool
    from src.tools.hotel_search import HotelSearchTool
    from src.tools.location_resolver import get_airport_code, get_city_code
    
    # Test location resolution
    print('\n📍 Location Resolution:')
    print(f'   India -> Airport: {get_airport_code("India")} (Delhi)')
    print(f'   Sri Lanka -> Airport: {get_airport_code("Sri Lanka")} (Colombo)')
    
    # Test flight search
    print('\n✈️  Flight Search (Delhi -> Colombo):')
    flight_tool = FlightSearchTool()
    flights = await flight_tool.search(
        origin='India',
        destination='Sri Lanka',
        date='2026-04-20',
        travelers=3
    )
    print(f'   Found {len(flights)} flights')
    if flights:
        f = flights[0]
        print(f'   First: {f.segments[0].departure_airport} -> {f.segments[-1].arrival_airport}')
        print(f'   Price: {f.formatted_price}')
    
    # Test hotel search  
    print('\n🏨 Hotel Search (Colombo):')
    hotel_tool = HotelSearchTool()
    hotels = await hotel_tool.search(
        destination='Sri Lanka',
        check_in='2026-04-20',
        check_out='2026-04-25',
        guests=3
    )
    print(f'   Found {len(hotels)} hotels')
    if hotels:
        h = hotels[0]
        print(f'   First: {h.name}')
        print(f'   Price: {h.formatted_price}')
    
    print('\n' + '='*60)
    print('✅ India -> Sri Lanka route test complete!')
    print('='*60)

if __name__ == "__main__":
    asyncio.run(test_india_sri_lanka())
