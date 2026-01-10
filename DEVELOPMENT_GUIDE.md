# 🌍 Agentic AI Travel Planner - Complete Development Guide

> **What is this project?**  
> An AI-powered travel planning application where multiple AI agents work together to automate trip planning — finding flights, booking hotels, suggesting activities, and optimizing your budget.

---

## 📖 Table of Contents

1. [What is Agentic AI?](#what-is-agentic-ai)
2. [Project Overview](#project-overview)
3. [Architecture](#architecture)
4. [Project Structure](#project-structure)
5. [Development Phases](#development-phases)
6. [Tech Stack](#tech-stack)
7. [Step-by-Step Implementation](#step-by-step-implementation)
8. [API Reference](#api-reference)
9. [Testing Strategy](#testing-strategy)
10. [Next Steps](#next-steps)

---

## 🤖 What is Agentic AI?

### Simple Explanation

Think of **Agentic AI** as giving AI the ability to **take actions**, not just answer questions.

| Traditional AI | Agentic AI |
|----------------|------------|
| You ask: "What's a good hotel in Paris?" | You say: "Plan my Paris trip" |
| AI gives you information | AI searches flights, compares hotels, books activities |
| You do all the work | AI agents collaborate and do the work for you |

### Key Concepts

| Concept | What It Means | Example in Our App |
|---------|---------------|-------------------|
| **Agent** | An AI that can make decisions and take actions | Flight Agent searches and compares flights |
| **Tool** | A capability an agent can use | API call to search flights |
| **Orchestrator** | Coordinator that manages multiple agents | Main agent that delegates tasks |
| **Memory** | Ability to remember previous interactions | Remembering user preferences |
| **Reasoning** | Thinking through problems step-by-step | Deciding best flight based on multiple factors |

---

## 🎯 Project Overview

### What We're Building

```
User: "Plan a 5-day trip to Tokyo from New York, budget $3000, 
       I love food and technology, traveling in April"

                    ↓

    ┌─────────────────────────────────────┐
    │     🤖 AI Travel Planner App        │
    │                                     │
    │  ✈️  Best flights found: $850       │
    │  🏨  Hotel recommended: $120/night  │
    │  🎯  Activities planned: 12 items   │
    │  💰  Total cost: $2,450 (under!)    │
    │                                     │
    │  📋 Complete day-by-day itinerary   │
    └─────────────────────────────────────┘
```

### Core Features

| Feature | Description |
|---------|-------------|
| ✈️ **Flight Search** | Find best flights based on dates, budget, preferences |
| 🏨 **Hotel Recommendations** | Suggest accommodations matching your needs |
| 🎯 **Activity Planning** | Recommend things to do based on interests |
| 💰 **Budget Optimization** | Keep everything within your budget |
| 📋 **Itinerary Generation** | Create day-by-day travel plan |
| 💬 **Natural Language** | Just describe what you want in plain English |

---

## 🏗️ Architecture

### High-Level Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────────────┐
│                            USER INTERFACE                                 │
│                     (Web App / CLI / REST API)                           │
│                                                                          │
│   "Plan a trip to Tokyo from NYC, 5 days, $3000 budget, love food"      │
└────────────────────────────────┬─────────────────────────────────────────┘
                                 │
                                 ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                        🧠 ORCHESTRATOR AGENT                              │
│                                                                          │
│   • Understands user request                                             │
│   • Breaks down into subtasks                                            │
│   • Delegates to specialized agents                                      │
│   • Combines results into final plan                                     │
│   • Resolves conflicts (e.g., hotel too far from activities)            │
└────┬─────────────────┬─────────────────┬─────────────────┬───────────────┘
     │                 │                 │                 │
     ▼                 ▼                 ▼                 ▼
┌─────────┐      ┌─────────┐      ┌─────────┐      ┌─────────┐
│   ✈️    │      │   🏨    │      │   🎯    │      │   💰    │
│ FLIGHT  │      │  HOTEL  │      │ACTIVITY │      │ BUDGET  │
│  AGENT  │      │  AGENT  │      │  AGENT  │      │  AGENT  │
└────┬────┘      └────┬────┘      └────┬────┘      └────┬────┘
     │                │                │                │
     ▼                ▼                ▼                ▼
┌─────────┐      ┌─────────┐      ┌─────────┐      ┌─────────┐
│ Flight  │      │  Hotel  │      │ Places  │      │  Cost   │
│  APIs   │      │  APIs   │      │  APIs   │      │ Calculator│
│         │      │         │      │         │      │         │
│Amadeus  │      │Booking  │      │Google   │      │ Internal│
│Skyscanner│     │Hotels.com│     │TripAdvisor│    │ Logic   │
└─────────┘      └─────────┘      └─────────┘      └─────────┘
```

### How Agents Communicate

```
Step 1: User Request
        │
        ▼
Step 2: Orchestrator analyzes request
        │
        ├──→ Step 3a: Flight Agent searches flights ──→ Returns top 5 options
        │
        ├──→ Step 3b: Hotel Agent searches hotels ──→ Returns top 5 options
        │
        └──→ Step 3c: Activity Agent finds activities ──→ Returns 15 activities
        │
        ▼
Step 4: Budget Agent calculates combinations within budget
        │
        ▼
Step 5: Orchestrator creates optimal itinerary
        │
        ▼
Step 6: Return complete travel plan to user
```

---

## 📁 Project Structure

```
agentic-travel-planner/
│
├── 📄 README.md                    # Project overview
├── 📄 DEVELOPMENT_GUIDE.md         # This file
├── 📄 requirements.txt             # Python dependencies
├── 📄 .env.example                 # Environment variables template
├── 📄 .env                         # Your actual environment variables (git ignored)
├── 📄 .gitignore                   # Git ignore file
│
├── 📂 src/                         # Source code
│   │
│   ├── 📂 agents/                  # All AI agents
│   │   ├── 📄 __init__.py
│   │   ├── 📄 base_agent.py        # Base class for all agents
│   │   ├── 📄 orchestrator.py      # Main coordinator agent
│   │   ├── 📄 flight_agent.py      # Flight search agent
│   │   ├── 📄 hotel_agent.py       # Hotel search agent
│   │   ├── 📄 activity_agent.py    # Activity recommendation agent
│   │   └── 📄 budget_agent.py      # Budget optimization agent
│   │
│   ├── 📂 tools/                   # Tools that agents use
│   │   ├── 📄 __init__.py
│   │   ├── 📄 flight_search.py     # Flight API integration
│   │   ├── 📄 hotel_search.py      # Hotel API integration
│   │   ├── 📄 activity_search.py   # Activity API integration
│   │   └── 📄 weather.py           # Weather API integration
│   │
│   ├── 📂 models/                  # Data models/schemas
│   │   ├── 📄 __init__.py
│   │   ├── 📄 travel_request.py    # User request schema
│   │   ├── 📄 flight.py            # Flight data schema
│   │   ├── 📄 hotel.py             # Hotel data schema
│   │   ├── 📄 activity.py          # Activity data schema
│   │   └── 📄 itinerary.py         # Complete itinerary schema
│   │
│   ├── 📂 api/                     # REST API endpoints
│   │   ├── 📄 __init__.py
│   │   ├── 📄 main.py              # FastAPI application
│   │   └── 📄 routes.py            # API route definitions
│   │
│   ├── 📂 prompts/                 # LLM prompt templates
│   │   ├── 📄 orchestrator.py      # Orchestrator prompts
│   │   ├── 📄 flight.py            # Flight agent prompts
│   │   ├── 📄 hotel.py             # Hotel agent prompts
│   │   └── 📄 activity.py          # Activity agent prompts
│   │
│   ├── 📄 config.py                # Configuration settings
│   └── 📄 utils.py                 # Utility functions
│
├── 📂 data/                        # Data files
│   └── 📂 mock/                    # Mock data for testing
│       ├── 📄 flights.json
│       ├── 📄 hotels.json
│       └── 📄 activities.json
│
├── 📂 tests/                       # Test files
│   ├── 📄 __init__.py
│   ├── 📄 test_flight_agent.py
│   ├── 📄 test_hotel_agent.py
│   └── 📄 test_orchestrator.py
│
└── 📂 docs/                        # Documentation
    ├── 📄 api_docs.md
    └── 📄 agent_design.md
```

---

## 🚀 Development Phases

### Phase 1: Foundation (Week 1)
> Set up the project and create basic structure

| Task | Description | Files to Create |
|------|-------------|-----------------|
| 1.1 | Initialize Python project | `requirements.txt` |
| 1.2 | Set up virtual environment | - |
| 1.3 | Create project folders | All directories |
| 1.4 | Define data models | `src/models/*.py` |
| 1.5 | Set up configuration | `src/config.py`, `.env` |

### Phase 2: Build Agents (Week 2-3)
> Create individual AI agents

| Task | Description | Files to Create |
|------|-------------|-----------------|
| 2.1 | Create base agent class | `src/agents/base_agent.py` |
| 2.2 | Build Flight Agent | `src/agents/flight_agent.py` |
| 2.3 | Build Hotel Agent | `src/agents/hotel_agent.py` |
| 2.4 | Build Activity Agent | `src/agents/activity_agent.py` |
| 2.5 | Build Budget Agent | `src/agents/budget_agent.py` |

### Phase 3: Tools & APIs (Week 3-4)
> Connect agents to external services

| Task | Description | Files to Create |
|------|-------------|-----------------|
| 3.1 | Create mock data | `data/mock/*.json` |
| 3.2 | Build flight search tool | `src/tools/flight_search.py` |
| 3.3 | Build hotel search tool | `src/tools/hotel_search.py` |
| 3.4 | Build activity search tool | `src/tools/activity_search.py` |

### Phase 4: Orchestration (Week 4-5)
> Connect everything together

| Task | Description | Files to Create |
|------|-------------|-----------------|
| 4.1 | Build Orchestrator Agent | `src/agents/orchestrator.py` |
| 4.2 | Implement agent communication | - |
| 4.3 | Create itinerary generator | `src/models/itinerary.py` |

### Phase 5: API & Interface (Week 5-6)
> Create user-facing interface

| Task | Description | Files to Create |
|------|-------------|-----------------|
| 5.1 | Set up FastAPI | `src/api/main.py` |
| 5.2 | Create API endpoints | `src/api/routes.py` |
| 5.3 | Add error handling | - |
| 5.4 | Create simple CLI (optional) | `src/cli.py` |

### Phase 6: Testing & Polish (Week 6+)
> Make it production-ready

| Task | Description | Files to Create |
|------|-------------|-----------------|
| 6.1 | Write unit tests | `tests/*.py` |
| 6.2 | Add logging | - |
| 6.3 | Optimize prompts | `src/prompts/*.py` |
| 6.4 | Documentation | `docs/*.md` |

---

## 🛠️ Tech Stack

### Required Technologies

| Category | Technology | Why We Use It |
|----------|------------|---------------|
| **Language** | Python 3.10+ | Best ecosystem for AI/ML |
| **Agent Framework** | LangChain | Popular, well-documented, flexible |
| **LLM** | OpenAI GPT-4 | Powerful reasoning capabilities |
| **API Framework** | FastAPI | Fast, modern, automatic docs |
| **Data Validation** | Pydantic | Type safety, validation |

### Dependencies (requirements.txt)

```txt
# Core
python-dotenv==1.0.0
pydantic==2.5.0

# AI/LLM
langchain==0.1.0
langchain-openai==0.0.5
openai==1.12.0

# API
fastapi==0.109.0
uvicorn==0.27.0

# HTTP Requests
httpx==0.26.0
aiohttp==3.9.0

# Utilities
rich==13.7.0          # Beautiful terminal output

# Testing
pytest==8.0.0
pytest-asyncio==0.23.0
```

### Optional Technologies

| Category | Technology | When to Use |
|----------|------------|-------------|
| **Database** | PostgreSQL | If you need to store trip history |
| **Caching** | Redis | For caching API responses |
| **Frontend** | Streamlit | Quick UI prototyping |
| **Monitoring** | LangSmith | Debugging agent behavior |

---

## 📝 Step-by-Step Implementation

### Step 1: Project Setup

#### 1.1 Create Virtual Environment

```bash
# Navigate to project folder
cd "d:\AI Project\agentic-travel-planner"

# Create virtual environment
python -m venv venv

# Activate it (Windows)
.\venv\Scripts\activate

# Activate it (Mac/Linux)
source venv/bin/activate
```

#### 1.2 Install Dependencies

```bash
pip install langchain langchain-openai openai fastapi uvicorn python-dotenv pydantic httpx rich pytest
```

#### 1.3 Create Environment File

Create `.env` file:
```env
# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key-here

# Optional: Azure OpenAI (if using Azure)
# AZURE_OPENAI_API_KEY=your-azure-key
# AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/

# Application Settings
DEBUG=true
LOG_LEVEL=INFO

# API Keys for Travel Services (optional - we'll use mock data first)
# AMADEUS_API_KEY=your-amadeus-key
# AMADEUS_API_SECRET=your-amadeus-secret
```

---

### Step 2: Create Data Models

#### 2.1 Travel Request Model

**File: `src/models/travel_request.py`**

```python
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
```

#### 2.2 Flight Model

**File: `src/models/flight.py`**

```python
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

class FlightSegment(BaseModel):
    """A single flight segment"""
    airline: str
    flight_number: str
    departure_airport: str
    arrival_airport: str
    departure_time: datetime
    arrival_time: datetime
    duration_minutes: int
    
class Flight(BaseModel):
    """Complete flight option (can have multiple segments)"""
    id: str
    segments: List[FlightSegment]
    total_price: float
    currency: str = "USD"
    total_duration_minutes: int
    stops: int
    cabin_class: str = "economy"
    
    @property
    def is_direct(self) -> bool:
        return self.stops == 0
    
    @property
    def formatted_duration(self) -> str:
        hours = self.total_duration_minutes // 60
        minutes = self.total_duration_minutes % 60
        return f"{hours}h {minutes}m"
```

#### 2.3 Hotel Model

**File: `src/models/hotel.py`**

```python
from pydantic import BaseModel, Field
from typing import List, Optional

class Hotel(BaseModel):
    """Hotel accommodation option"""
    id: str
    name: str
    address: str
    star_rating: float = Field(..., ge=1, le=5)
    user_rating: float = Field(..., ge=0, le=10)
    price_per_night: float
    currency: str = "USD"
    amenities: List[str] = []
    distance_to_center_km: float
    image_url: Optional[str] = None
    
    @property
    def rating_category(self) -> str:
        if self.user_rating >= 9:
            return "Excellent"
        elif self.user_rating >= 8:
            return "Very Good"
        elif self.user_rating >= 7:
            return "Good"
        else:
            return "Average"
```

#### 2.4 Activity Model

**File: `src/models/activity.py`**

```python
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class ActivityCategory(str, Enum):
    SIGHTSEEING = "sightseeing"
    FOOD = "food"
    CULTURE = "culture"
    ADVENTURE = "adventure"
    SHOPPING = "shopping"
    RELAXATION = "relaxation"
    NIGHTLIFE = "nightlife"

class Activity(BaseModel):
    """Thing to do at destination"""
    id: str
    name: str
    description: str
    category: ActivityCategory
    location: str
    duration_hours: float
    price: float = 0  # 0 means free
    currency: str = "USD"
    rating: float = Field(..., ge=0, le=5)
    best_time: Optional[str] = None  # "morning", "afternoon", "evening"
    tags: List[str] = []
```

#### 2.5 Itinerary Model

**File: `src/models/itinerary.py`**

```python
from pydantic import BaseModel, Field
from datetime import date, time
from typing import List, Optional
from .flight import Flight
from .hotel import Hotel
from .activity import Activity

class DayPlanItem(BaseModel):
    """Single item in a day's plan"""
    time: str  # e.g., "09:00"
    activity: Activity
    notes: Optional[str] = None

class DayPlan(BaseModel):
    """Plan for a single day"""
    date: date
    day_number: int
    items: List[DayPlanItem]
    meals: List[str] = []  # Restaurant recommendations

class TripItinerary(BaseModel):
    """Complete trip itinerary"""
    id: str
    origin: str
    destination: str
    
    # Selected options
    outbound_flight: Flight
    return_flight: Flight
    hotel: Hotel
    
    # Day-by-day plan
    daily_plans: List[DayPlan]
    
    # Cost breakdown
    flight_cost: float
    hotel_cost: float
    activities_cost: float
    estimated_food_cost: float
    total_cost: float
    
    # Metadata
    created_at: str
    notes: List[str] = []
```

---

### Step 3: Create Base Agent

**File: `src/agents/base_agent.py`**

```python
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

class BaseAgent(ABC):
    """
    Base class for all agents in the travel planner.
    
    Each agent has:
    - A specific role/purpose
    - Access to an LLM for reasoning
    - Tools it can use
    - A method to execute its task
    """
    
    def __init__(
        self,
        name: str,
        description: str,
        model_name: str = "gpt-4",
        temperature: float = 0.7
    ):
        self.name = name
        self.description = description
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=temperature
        )
        self.tools = []
    
    @property
    @abstractmethod
    def system_prompt(self) -> str:
        """Define the agent's personality and instructions"""
        pass
    
    @abstractmethod
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent's main task"""
        pass
    
    async def think(self, user_message: str) -> str:
        """
        Send a message to the LLM and get a response.
        This is the agent's "thinking" capability.
        """
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=user_message)
        ]
        response = await self.llm.ainvoke(messages)
        return response.content
    
    def add_tool(self, tool):
        """Add a tool that this agent can use"""
        self.tools.append(tool)
    
    def __repr__(self):
        return f"<{self.__class__.__name__}(name='{self.name}')>"
```

---

### Step 4: Create Flight Agent

**File: `src/agents/flight_agent.py`**

```python
from typing import Any, Dict, List
from .base_agent import BaseAgent
from ..models.flight import Flight
from ..tools.flight_search import FlightSearchTool

class FlightAgent(BaseAgent):
    """
    Agent responsible for searching and recommending flights.
    
    Capabilities:
    - Search flights based on criteria
    - Compare prices and durations
    - Recommend best options based on preferences
    """
    
    def __init__(self):
        super().__init__(
            name="Flight Agent",
            description="Searches and recommends the best flights"
        )
        self.flight_tool = FlightSearchTool()
        self.add_tool(self.flight_tool)
    
    @property
    def system_prompt(self) -> str:
        return """You are a flight search expert agent. Your job is to:

1. Search for flights based on user criteria
2. Analyze the options considering:
   - Price (lower is better, but consider value)
   - Duration (shorter is better)
   - Number of stops (direct is preferred)
   - Departure/arrival times (reasonable hours preferred)
   - Airline reputation

3. Recommend the TOP 3 options with clear reasoning

When analyzing flights, consider trade-offs. For example:
- A slightly more expensive direct flight might be better than a cheap flight with 2 stops
- Early morning flights are cheaper but less convenient

Always explain your recommendations clearly."""

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Search for flights and return recommendations.
        
        Input:
            {
                "origin": "NYC",
                "destination": "TYO", 
                "departure_date": "2026-04-15",
                "return_date": "2026-04-20",
                "travelers": 2,
                "max_price": 1500,
                "preferences": "direct flight preferred"
            }
        
        Output:
            {
                "outbound_flights": [...],
                "return_flights": [...],
                "recommendations": {...},
                "reasoning": "..."
            }
        """
        # Step 1: Search for flights using the tool
        outbound_flights = await self.flight_tool.search(
            origin=input_data["origin"],
            destination=input_data["destination"],
            date=input_data["departure_date"],
            travelers=input_data.get("travelers", 1)
        )
        
        return_flights = await self.flight_tool.search(
            origin=input_data["destination"],
            destination=input_data["origin"],
            date=input_data["return_date"],
            travelers=input_data.get("travelers", 1)
        )
        
        # Step 2: Use LLM to analyze and recommend
        analysis_prompt = f"""
Analyze these flight options and recommend the best choices:

OUTBOUND FLIGHTS ({input_data["origin"]} → {input_data["destination"]}):
{self._format_flights(outbound_flights)}

RETURN FLIGHTS ({input_data["destination"]} → {input_data["origin"]}):
{self._format_flights(return_flights)}

USER PREFERENCES:
- Budget: ${input_data.get("max_price", "flexible")} per person
- Travelers: {input_data.get("travelers", 1)}
- Preferences: {input_data.get("preferences", "none specified")}

Recommend the best outbound and return flight combination.
Explain your reasoning.
"""
        
        reasoning = await self.think(analysis_prompt)
        
        return {
            "outbound_flights": outbound_flights,
            "return_flights": return_flights,
            "recommended_outbound": outbound_flights[0] if outbound_flights else None,
            "recommended_return": return_flights[0] if return_flights else None,
            "reasoning": reasoning
        }
    
    def _format_flights(self, flights: List[Flight]) -> str:
        """Format flights for LLM analysis"""
        if not flights:
            return "No flights found"
        
        result = []
        for i, flight in enumerate(flights, 1):
            result.append(f"""
Flight {i}:
  - Price: ${flight.total_price}
  - Duration: {flight.formatted_duration}
  - Stops: {flight.stops} ({'Direct' if flight.is_direct else 'With stops'})
  - Airline: {flight.segments[0].airline}
""")
        return "\n".join(result)
```

---

### Step 5: Create Flight Search Tool

**File: `src/tools/flight_search.py`**

```python
import json
from typing import List, Optional
from datetime import datetime
from pathlib import Path
from ..models.flight import Flight, FlightSegment

class FlightSearchTool:
    """
    Tool for searching flights.
    
    Currently uses mock data. Can be extended to use real APIs:
    - Amadeus API
    - Skyscanner API
    - Google Flights (unofficial)
    """
    
    def __init__(self, use_mock: bool = True):
        self.use_mock = use_mock
        self.mock_data_path = Path("data/mock/flights.json")
    
    async def search(
        self,
        origin: str,
        destination: str,
        date: str,
        travelers: int = 1,
        max_price: Optional[float] = None,
        direct_only: bool = False
    ) -> List[Flight]:
        """
        Search for flights matching criteria.
        
        Args:
            origin: Departure city/airport code
            destination: Arrival city/airport code
            date: Travel date (YYYY-MM-DD)
            travelers: Number of passengers
            max_price: Maximum price per person
            direct_only: Only return direct flights
        
        Returns:
            List of Flight objects sorted by price
        """
        if self.use_mock:
            return await self._search_mock(
                origin, destination, date, travelers, max_price, direct_only
            )
        else:
            return await self._search_api(
                origin, destination, date, travelers, max_price, direct_only
            )
    
    async def _search_mock(
        self,
        origin: str,
        destination: str,
        date: str,
        travelers: int,
        max_price: Optional[float],
        direct_only: bool
    ) -> List[Flight]:
        """Search using mock data"""
        
        # Generate mock flights
        mock_flights = self._generate_mock_flights(origin, destination, date)
        
        # Apply filters
        if direct_only:
            mock_flights = [f for f in mock_flights if f.stops == 0]
        
        if max_price:
            mock_flights = [f for f in mock_flights if f.total_price <= max_price]
        
        # Sort by price
        mock_flights.sort(key=lambda f: f.total_price)
        
        return mock_flights
    
    def _generate_mock_flights(
        self,
        origin: str,
        destination: str,
        date: str
    ) -> List[Flight]:
        """Generate realistic mock flight data"""
        
        airlines = ["United", "Delta", "American", "JetBlue", "ANA", "JAL"]
        
        mock_flights = [
            # Direct flight - most expensive
            Flight(
                id="FL001",
                segments=[
                    FlightSegment(
                        airline="ANA",
                        flight_number="NH109",
                        departure_airport=origin,
                        arrival_airport=destination,
                        departure_time=datetime.fromisoformat(f"{date}T10:30:00"),
                        arrival_time=datetime.fromisoformat(f"{date}T14:30:00+09:00"),
                        duration_minutes=840  # 14 hours
                    )
                ],
                total_price=1250.00,
                total_duration_minutes=840,
                stops=0,
                cabin_class="economy"
            ),
            # One stop - medium price
            Flight(
                id="FL002",
                segments=[
                    FlightSegment(
                        airline="United",
                        flight_number="UA881",
                        departure_airport=origin,
                        arrival_airport="SFO",
                        departure_time=datetime.fromisoformat(f"{date}T08:00:00"),
                        arrival_time=datetime.fromisoformat(f"{date}T11:30:00"),
                        duration_minutes=330
                    ),
                    FlightSegment(
                        airline="United",
                        flight_number="UA837",
                        departure_airport="SFO",
                        arrival_airport=destination,
                        departure_time=datetime.fromisoformat(f"{date}T13:00:00"),
                        arrival_time=datetime.fromisoformat(f"{date}T17:00:00+09:00"),
                        duration_minutes=660
                    )
                ],
                total_price=980.00,
                total_duration_minutes=1140,  # 19 hours with layover
                stops=1,
                cabin_class="economy"
            ),
            # Two stops - cheapest
            Flight(
                id="FL003",
                segments=[
                    FlightSegment(
                        airline="Delta",
                        flight_number="DL123",
                        departure_airport=origin,
                        arrival_airport="LAX",
                        departure_time=datetime.fromisoformat(f"{date}T06:00:00"),
                        arrival_time=datetime.fromisoformat(f"{date}T09:00:00"),
                        duration_minutes=300
                    ),
                    FlightSegment(
                        airline="Delta",
                        flight_number="DL456",
                        departure_airport="LAX",
                        arrival_airport="ICN",
                        departure_time=datetime.fromisoformat(f"{date}T11:00:00"),
                        arrival_time=datetime.fromisoformat(f"{date}T16:00:00+09:00"),
                        duration_minutes=780
                    ),
                    FlightSegment(
                        airline="Korean Air",
                        flight_number="KE789",
                        departure_airport="ICN",
                        arrival_airport=destination,
                        departure_time=datetime.fromisoformat(f"{date}T18:00:00+09:00"),
                        arrival_time=datetime.fromisoformat(f"{date}T20:00:00+09:00"),
                        duration_minutes=120
                    )
                ],
                total_price=750.00,
                total_duration_minutes=1500,  # 25 hours
                stops=2,
                cabin_class="economy"
            ),
        ]
        
        return mock_flights
    
    async def _search_api(self, *args, **kwargs) -> List[Flight]:
        """
        Search using real API.
        
        TODO: Implement Amadeus or Skyscanner integration
        """
        raise NotImplementedError("Real API integration not implemented yet")
```

---

### Step 6: Create the Orchestrator

**File: `src/agents/orchestrator.py`**

```python
from typing import Any, Dict
from .base_agent import BaseAgent
from .flight_agent import FlightAgent
from .hotel_agent import HotelAgent
from .activity_agent import ActivityAgent
from .budget_agent import BudgetAgent
from ..models.travel_request import TravelRequest
from ..models.itinerary import TripItinerary

class OrchestratorAgent(BaseAgent):
    """
    The main coordinator agent that manages the entire trip planning process.
    
    Responsibilities:
    1. Parse and understand user requests
    2. Delegate tasks to specialized agents
    3. Collect and combine results
    4. Resolve conflicts between agent outputs
    5. Generate final itinerary
    """
    
    def __init__(self):
        super().__init__(
            name="Travel Orchestrator",
            description="Coordinates all agents to plan the perfect trip"
        )
        
        # Initialize all specialized agents
        self.flight_agent = FlightAgent()
        self.hotel_agent = HotelAgent()
        self.activity_agent = ActivityAgent()
        self.budget_agent = BudgetAgent()
    
    @property
    def system_prompt(self) -> str:
        return """You are the master travel planner orchestrator. Your job is to:

1. Understand what the user wants for their trip
2. Coordinate with specialized agents:
   - Flight Agent: Finds the best flights
   - Hotel Agent: Recommends accommodations
   - Activity Agent: Suggests things to do
   - Budget Agent: Ensures everything fits the budget

3. Combine all recommendations into a cohesive travel plan
4. Resolve any conflicts (e.g., hotel too far from activities)
5. Create a day-by-day itinerary

Be helpful, thorough, and always explain your recommendations.
Consider the user's preferences and constraints carefully."""

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the full trip planning workflow.
        
        Input: TravelRequest data
        Output: Complete TripItinerary
        """
        # Step 1: Parse the request
        request = TravelRequest(**input_data)
        
        # Step 2: Calculate budget allocation
        budget_allocation = await self._allocate_budget(request)
        
        # Step 3: Search for flights (parallel with hotels)
        flight_results = await self.flight_agent.execute({
            "origin": request.origin,
            "destination": request.destination,
            "departure_date": str(request.departure_date),
            "return_date": str(request.return_date),
            "travelers": request.travelers,
            "max_price": budget_allocation.get("flights"),
            "preferences": request.flight_preferences
        })
        
        # Step 4: Search for hotels
        hotel_results = await self.hotel_agent.execute({
            "destination": request.destination,
            "check_in": str(request.departure_date),
            "check_out": str(request.return_date),
            "guests": request.travelers,
            "max_price_per_night": budget_allocation.get("hotel_per_night"),
            "preferences": request.hotel_preferences
        })
        
        # Step 5: Find activities based on interests
        activity_results = await self.activity_agent.execute({
            "destination": request.destination,
            "interests": request.interests,
            "days": (request.return_date - request.departure_date).days,
            "budget": budget_allocation.get("activities")
        })
        
        # Step 6: Optimize with budget agent
        optimized = await self.budget_agent.execute({
            "flights": flight_results,
            "hotels": hotel_results,
            "activities": activity_results,
            "total_budget": request.budget,
            "travelers": request.travelers
        })
        
        # Step 7: Generate final itinerary
        itinerary = await self._create_itinerary(
            request, optimized
        )
        
        return {
            "itinerary": itinerary,
            "flight_options": flight_results,
            "hotel_options": hotel_results,
            "activity_options": activity_results,
            "budget_breakdown": optimized.get("breakdown")
        }
    
    async def _allocate_budget(self, request: TravelRequest) -> Dict[str, float]:
        """
        Intelligently allocate budget across categories.
        
        Default allocation:
        - Flights: 40%
        - Hotels: 35%
        - Activities: 15%
        - Food & Misc: 10%
        """
        if not request.budget:
            return {}
        
        total = request.budget
        nights = (request.return_date - request.departure_date).days
        
        return {
            "flights": total * 0.40 / request.travelers,  # Per person
            "hotel_total": total * 0.35,
            "hotel_per_night": (total * 0.35) / nights,
            "activities": total * 0.15,
            "food_misc": total * 0.10
        }
    
    async def _create_itinerary(
        self,
        request: TravelRequest,
        optimized_results: Dict
    ) -> TripItinerary:
        """Create the final day-by-day itinerary"""
        
        # Use LLM to create a natural itinerary
        prompt = f"""
Create a day-by-day itinerary for this trip:

TRIP DETAILS:
- Destination: {request.destination}
- Dates: {request.departure_date} to {request.return_date}
- Interests: {', '.join(request.interests)}

SELECTED OPTIONS:
- Flight: {optimized_results.get('selected_flight')}
- Hotel: {optimized_results.get('selected_hotel')}
- Activities: {optimized_results.get('selected_activities')}

Create a logical day-by-day plan that:
1. Starts with arrival and settling in
2. Groups nearby activities together
3. Includes meal recommendations
4. Accounts for travel time between locations
5. Ends with departure
"""
        
        itinerary_plan = await self.think(prompt)
        
        # TODO: Parse LLM response into structured DayPlan objects
        
        return itinerary_plan
```

---

### Step 7: Create API Endpoints

**File: `src/api/main.py`**

```python
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from datetime import date

from ..agents.orchestrator import OrchestratorAgent
from ..models.travel_request import TravelRequest

# Initialize FastAPI app
app = FastAPI(
    title="Agentic Travel Planner API",
    description="AI-powered travel planning with multiple collaborative agents",
    version="1.0.0"
)

# Add CORS middleware (for frontend access)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the orchestrator
orchestrator = OrchestratorAgent()


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Agentic Travel Planner",
        "version": "1.0.0"
    }


@app.post("/api/plan-trip")
async def plan_trip(request: TravelRequest):
    """
    Plan a complete trip based on user requirements.
    
    This endpoint:
    1. Receives travel requirements
    2. Coordinates multiple AI agents
    3. Returns a complete itinerary with recommendations
    """
    try:
        result = await orchestrator.execute(request.model_dump())
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/search/flights")
async def search_flights(
    origin: str,
    destination: str,
    departure_date: date,
    travelers: int = 1,
    max_price: Optional[float] = None
):
    """Search for flights only"""
    flight_agent = orchestrator.flight_agent
    
    result = await flight_agent.execute({
        "origin": origin,
        "destination": destination,
        "departure_date": str(departure_date),
        "return_date": str(departure_date),  # One-way
        "travelers": travelers,
        "max_price": max_price
    })
    
    return {"success": True, "data": result}


@app.get("/api/search/hotels")
async def search_hotels(
    destination: str,
    check_in: date,
    check_out: date,
    guests: int = 1,
    max_price: Optional[float] = None
):
    """Search for hotels only"""
    hotel_agent = orchestrator.hotel_agent
    
    result = await hotel_agent.execute({
        "destination": destination,
        "check_in": str(check_in),
        "check_out": str(check_out),
        "guests": guests,
        "max_price_per_night": max_price
    })
    
    return {"success": True, "data": result}


@app.get("/api/search/activities")
async def search_activities(
    destination: str,
    interests: List[str] = [],
    days: int = 1
):
    """Search for activities only"""
    activity_agent = orchestrator.activity_agent
    
    result = await activity_agent.execute({
        "destination": destination,
        "interests": interests,
        "days": days
    })
    
    return {"success": True, "data": result}


# Run with: uvicorn src.api.main:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

## 🔌 API Reference

### Endpoints Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| POST | `/api/plan-trip` | Plan complete trip |
| GET | `/api/search/flights` | Search flights only |
| GET | `/api/search/hotels` | Search hotels only |
| GET | `/api/search/activities` | Search activities only |

### Plan Trip Request

```json
POST /api/plan-trip
{
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
```

### Plan Trip Response

```json
{
    "success": true,
    "data": {
        "itinerary": {
            "id": "trip-12345",
            "destination": "Tokyo",
            "outbound_flight": {...},
            "return_flight": {...},
            "hotel": {...},
            "daily_plans": [
                {
                    "date": "2026-04-15",
                    "day_number": 1,
                    "items": [
                        {"time": "15:00", "activity": "Check into hotel"},
                        {"time": "18:00", "activity": "Explore Shibuya"}
                    ]
                }
            ],
            "total_cost": 2450
        }
    }
}
```

---

## 🧪 Testing Strategy

### Unit Tests Example

**File: `tests/test_flight_agent.py`**

```python
import pytest
from src.agents.flight_agent import FlightAgent

@pytest.fixture
def flight_agent():
    return FlightAgent()

@pytest.mark.asyncio
async def test_flight_search_returns_results(flight_agent):
    """Test that flight search returns results"""
    result = await flight_agent.execute({
        "origin": "NYC",
        "destination": "TYO",
        "departure_date": "2026-04-15",
        "return_date": "2026-04-20",
        "travelers": 1
    })
    
    assert "outbound_flights" in result
    assert len(result["outbound_flights"]) > 0

@pytest.mark.asyncio
async def test_flight_search_respects_budget(flight_agent):
    """Test that flights are filtered by max price"""
    result = await flight_agent.execute({
        "origin": "NYC",
        "destination": "TYO",
        "departure_date": "2026-04-15",
        "return_date": "2026-04-20",
        "max_price": 800
    })
    
    for flight in result["outbound_flights"]:
        assert flight.total_price <= 800
```

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_flight_agent.py -v
```

---

## 🎯 Next Steps

After completing the basic implementation:

### Immediate Improvements
1. ✅ Add Hotel Agent and Activity Agent (similar pattern to Flight Agent)
2. ✅ Add more mock data for realistic testing
3. ✅ Implement proper error handling
4. ✅ Add logging throughout the application

### Advanced Features
1. 🔄 **Real API Integration** - Connect to Amadeus, Booking.com
2. 🧠 **Memory** - Remember user preferences across sessions
3. 🔄 **Streaming** - Stream responses as agents work
4. 📊 **Analytics** - Track agent performance
5. 🌐 **Web UI** - Build a frontend with React or Streamlit

### Production Readiness
1. 🔒 **Authentication** - Add user accounts
2. 📦 **Caching** - Cache API responses
3. 🚀 **Deployment** - Docker, Kubernetes
4. 📈 **Monitoring** - Add observability with LangSmith

---

## 📚 Resources

### Learning Materials
- [LangChain Documentation](https://python.langchain.com/docs/)
- [OpenAI Function Calling](https://platform.openai.com/docs/guides/function-calling)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

### Travel APIs
- [Amadeus API](https://developers.amadeus.com/) - Flights, Hotels
- [Skyscanner API](https://developers.skyscanner.net/) - Flight search
- [Google Places API](https://developers.google.com/maps/documentation/places) - Activities

### Agent Frameworks
- [LangChain Agents](https://python.langchain.com/docs/modules/agents/)
- [AutoGen](https://microsoft.github.io/autogen/)
- [CrewAI](https://www.crewai.io/)

---

## ❓ Questions?

If you get stuck at any step, feel free to ask for help! Good luck with your Agentic AI journey! 🚀
