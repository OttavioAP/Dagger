from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from app.config.config import app_settings


class DatabaseConfig(BaseModel):
    connection_string: str
    options: Optional[Dict[str, Any]] = Field(default_factory=dict)


def create_database_config() -> DatabaseConfig:
    """Create database configuration for local Postgres instance."""
    connection_string = app_settings._database_url
    if not connection_string:
        raise ValueError("PostgreSQL connection URL is required")

    # Options relevant for asyncpg/Postgres
    options = {
        "echo": True,
        "pool_size": 5,
        "max_overflow": 10,
        "connect_args": {"ssl": "disable"},
    }

    return DatabaseConfig(connection_string=connection_string, options=options)
