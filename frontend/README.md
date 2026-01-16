# AI Travel Planner - Streamlit Frontend

## Quick Start

### Option 1: Run directly
```bash
cd agentic-travel-planner
streamlit run frontend/app.py
```

### Option 2: Using the batch file (Windows)
```bash
cd frontend
run_app.bat
```

The app will open at: **http://localhost:8501**

## Project Structure

```
frontend/
├── app.py              # Main Streamlit app entry point
├── config.py           # Configuration and constants
├── run_app.bat         # Windows launcher script
├── components/         # Reusable UI components
│   ├── __init__.py
│   ├── forms.py       # Input forms (travel request form)
│   ├── cards.py       # Display cards (flights, hotels, activities)
│   └── results.py     # Results display components
└── utils/
    ├── __init__.py
    └── api_client.py  # Backend API wrapper
```

## Architecture

The frontend follows **DRY (Don't Repeat Yourself)** and **clean code** principles:

### Components

1. **config.py** - Centralized configuration
   - App settings (title, layout)
   - Default values (budget, travelers)
   - Interest options
   - Color scheme and icons

2. **components/forms.py** - Input components
   - `render_travel_form()` - Main travel planning form

3. **components/cards.py** - Display cards
   - `render_flight_card()` - Flight option card
   - `render_hotel_card()` - Hotel option card
   - `render_activity_card()` - Activity card
   - `render_budget_card()` - Budget summary card

4. **components/results.py** - Results sections
   - `render_summary()` - Trip summary with AI analysis
   - `render_flights_section()` - Flights tab content
   - `render_hotels_section()` - Hotels tab content
   - `render_activities_section()` - Activities tab content
   - `render_results_section()` - Complete results view

5. **utils/api_client.py** - Backend integration
   - `TripRequest` - Request data structure
   - `TripResults` - Response data structure
   - `TravelPlannerClient` - Backend wrapper

## Features

- 📝 **Intuitive Form** - Easy-to-use travel planning form
- 🎨 **Modern UI** - Clean, responsive design
- 📊 **Tabbed Results** - Organized display of flights, hotels, activities
- 💰 **Budget Tracking** - Visual budget analysis
- 🤖 **AI Summaries** - AI-generated trip analysis
- 📱 **Responsive** - Works on different screen sizes

## Environment Variables

Make sure your `.env` file contains:
```
AMADEUS_CLIENT_ID=your_amadeus_client_id
AMADEUS_CLIENT_SECRET=your_amadeus_client_secret
GEOAPIFY_API_KEY=your_geoapify_key
PERPLEXITY_API_KEY=your_perplexity_key
```

## Customization

### Adding New Interest Options
Edit `config.py`:
```python
INTEREST_OPTIONS: tuple = (
    "beach", "surfing", "diving",
    # Add more here
)
```

### Changing Colors
Edit `config.py` `Colors` class:
```python
class Colors:
    PRIMARY = "#FF4B4B"
    # Customize colors
```

### Adding New Card Types
Create a new function in `components/cards.py` following the existing pattern.
