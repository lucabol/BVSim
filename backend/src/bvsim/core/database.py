"""Database configuration and connection management."""

import os
from typing import Optional, Generator
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

# Load .env file if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Environment variables with defaults
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "sqlite:///./dev_bvsim.db"  # Changed default to SQLite
)

# For testing, we might want to use SQLite
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL", 
    "sqlite:///./test_bvsim.db"
)

# Redis configuration
REDIS_URL = os.getenv(
    "REDIS_URL",
    "redis://localhost:6379/0"
)

# Create SQLAlchemy engine
if DATABASE_URL.startswith("sqlite"):
    # SQLite configuration for development/testing
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False  # Set to True for SQL query logging
    )
else:
    # PostgreSQL configuration for production
    engine = create_engine(
        DATABASE_URL,
        pool_size=20,
        max_overflow=0,
        pool_pre_ping=True,
        echo=False  # Set to True for SQL query logging
    )

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()


def get_database_url() -> str:
    """Get the database URL for the current environment."""
    return DATABASE_URL


def get_db() -> Generator[Session, None, None]:
    """
    Dependency that provides a database session.
    
    Yields:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)


def drop_tables():
    """Drop all database tables."""
    Base.metadata.drop_all(bind=engine)


async def check_database_connection() -> bool:
    """
    Check if database connection is working.
    
    Returns:
        bool: True if connection is successful, False otherwise
    """
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


# Database configuration for different environments
class DatabaseConfig:
    """Database configuration class."""
    
    def __init__(self, environment: str = "development"):
        self.environment = environment
        
    @property
    def database_url(self) -> str:
        """Get database URL based on environment."""
        if self.environment == "testing":
            return TEST_DATABASE_URL
        elif self.environment == "production":
            return os.getenv("DATABASE_URL", DATABASE_URL)
        else:
            return DATABASE_URL
    
    @property
    def echo_queries(self) -> bool:
        """Whether to echo SQL queries."""
        return self.environment == "development"
    
    @property
    def pool_size(self) -> int:
        """Database connection pool size."""
        if self.environment == "production":
            return 20
        elif self.environment == "testing":
            return 1
        else:
            return 5
    
    @property
    def max_overflow(self) -> int:
        """Maximum overflow connections."""
        if self.environment == "production":
            return 10
        else:
            return 0
