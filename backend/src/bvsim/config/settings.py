"""Application configuration settings."""

import os
from functools import lru_cache
from typing import List, Optional

from pydantic import BaseModel


class Settings(BaseModel):
    """Application settings loaded from environment variables."""
    
    # Application settings
    DEBUG: bool = False
    SECRET_KEY: str = "dev-secret-key"
    
    # Database settings
    DATABASE_URL: str = "postgresql://bvsim_user:bvsim_pass@localhost:5432/bvsim"
    
    # Redis settings
    REDIS_URL: str = "redis://localhost:6379"
    
    # Security settings
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1", "0.0.0.0"]
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # Simulation settings
    MAX_SIMULATION_POINTS: int = 1000000
    DEFAULT_SIMULATION_POINTS: int = 10000
    MAX_PARALLEL_WORKERS: int = 8
    
    # Analytics settings
    ENABLE_SHAP_ANALYSIS: bool = True
    SHAP_SAMPLE_SIZE: int = 1000
    
    # Logging settings
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"  # json or console
    
    def __init__(self, **kwargs):
        """Initialize settings with environment variable overrides."""
        # Override with environment variables
        env_overrides = {
            'DEBUG': os.getenv('DEBUG', 'false').lower() == 'true',
            'SECRET_KEY': os.getenv('SECRET_KEY', 'dev-secret-key'),
            'DATABASE_URL': os.getenv('DATABASE_URL', 'postgresql://bvsim_user:bvsim_pass@localhost:5432/bvsim'),
            'REDIS_URL': os.getenv('REDIS_URL', 'redis://localhost:6379'),
            'LOG_LEVEL': os.getenv('LOG_LEVEL', 'INFO'),
            'LOG_FORMAT': os.getenv('LOG_FORMAT', 'json'),
        }
        
        # Update with environment overrides
        for key, value in env_overrides.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
        super().__init__(**kwargs)


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
