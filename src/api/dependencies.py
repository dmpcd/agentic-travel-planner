"""
API Dependencies
Shared dependencies for FastAPI routes using Dependency Injection.
"""
from typing import Optional
import os
from functools import lru_cache
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    Uses pydantic-settings for validation and type coercion.
    """
    # API Settings
    app_name: str = "Agentic Travel Planner API"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Server Settings
    host: str = "0.0.0.0"
    port: int = 8000
    
    # CORS Settings
    cors_origins: str = "*"  # Comma-separated list of origins
    
    # LLM Settings
    perplexity_api_key: Optional[str] = None
    
    # Rate Limiting (future use)
    rate_limit_requests: int = 10
    rate_limit_period: int = 60  # seconds
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"
    
    @property
    def cors_origins_list(self) -> list:
        """Parse CORS origins from comma-separated string"""
        if self.cors_origins == "*":
            return ["*"]
        return [origin.strip() for origin in self.cors_origins.split(",")]


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    Using lru_cache ensures settings are only loaded once.
    """
    return Settings()


def verify_api_key():
    """
    Verify that required API keys are configured.
    Raises ValueError if missing.
    """
    settings = get_settings()
    if not settings.perplexity_api_key:
        # Try loading directly from environment as fallback
        api_key = os.getenv("PERPLEXITY_API_KEY")
        if not api_key:
            raise ValueError(
                "PERPLEXITY_API_KEY not configured. "
                "Please set it in your .env file."
            )
    return True


async def get_trip_planner():
    """
    Dependency to get the trip planner function.
    This allows for easy mocking in tests.
    """
    from src.agents.orchestrator import plan_trip
    return plan_trip
