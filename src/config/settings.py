"""
Configuration settings for the SEO Agent application.

This module handles loading and validating environment variables, providing
type-safe access to configuration values throughout the application.
"""

import os
from pydantic import BaseSettings, Field, validator
from typing import Dict, List, Optional, Union


class LLMSettings(BaseSettings):
    """Settings for LLM API connections."""
    OPENAI_API_KEY: str = Field(..., env="OPENAI_API_KEY")
    ANTHROPIC_API_KEY: str = Field(..., env="ANTHROPIC_API_KEY")
    DEEPSEEK_API_KEY: str = Field(..., env="DEEPSEEK_API_KEY")
    GROK_API_KEY: str = Field(..., env="GROK_API_KEY")
    
    MODEL_CONFIG: Dict[str, Dict[str, Union[str, int, float, Dict]]] = {
        "research": {
            "provider": "openai",
            "model": "o3-mini",
            "temperature": 0.2,
            "max_tokens": 4000,
        },
        "brief": {
            "provider": "deepseek",
            "model": "deepseek-large",
            "temperature": 0.3,
            "max_tokens": 2000,
        },
        "facts": {
            "provider": "grok",
            "model": "grok-3",
            "temperature": 0.1,
            "max_tokens": 2000,
        },
        "content": {
            "provider": "anthropic",
            "model": "claude-3-7-sonnet",
            "temperature": 0.5,
            "max_tokens": 8000,
        }
    }
    
    @validator("OPENAI_API_KEY", "ANTHROPIC_API_KEY", "DEEPSEEK_API_KEY", "GROK_API_KEY")
    def validate_api_keys(cls, v: str) -> str:
        """Validate that API keys are not empty and have valid format."""
        if not v:
            raise ValueError("API key cannot be empty")
        if len(v) < 20:  # Simple length validation
            raise ValueError("API key seems too short to be valid")
        return v


class APISettings(BaseSettings):
    """Settings for the FastAPI application."""
    APP_NAME: str = "SEO Agent API"
    APP_VERSION: str = "0.1.0"
    APP_DESCRIPTION: str = "Multi-LLM Agentic Content Creation System"
    DEBUG: bool = Field(False, env="DEBUG")
    HOST: str = Field("0.0.0.0", env="HOST")
    PORT: int = Field(8000, env="PORT")
    LOG_LEVEL: str = Field("INFO", env="LOG_LEVEL")
    CORS_ORIGINS: List[str] = Field(["*"], env="CORS_ORIGINS")
    API_PREFIX: str = "/api/v1"
    
    # Authentication settings
    AUTH_REQUIRED: bool = Field(True, env="AUTH_REQUIRED")
    API_KEY_HEADER: str = "X-API-Key"
    API_KEYS: List[str] = Field([], env="API_KEYS")
    
    @validator("API_KEYS", pre=True)
    def validate_api_keys(cls, v: Union[str, List[str]]) -> List[str]:
        """Parse API_KEYS from comma-separated string if needed."""
        if isinstance(v, str):
            return [x.strip() for x in v.split(",") if x.strip()]
        return v


class DatabaseSettings(BaseSettings):
    """Settings for database connections."""
    POSTGRES_USER: str = Field("postgres", env="POSTGRES_USER")
    POSTGRES_PASSWORD: str = Field("postgres", env="POSTGRES_PASSWORD")
    POSTGRES_DB: str = Field("seo_agent", env="POSTGRES_DB")
    POSTGRES_HOST: str = Field("localhost", env="POSTGRES_HOST")
    POSTGRES_PORT: int = Field(5432, env="POSTGRES_PORT")
    
    @property
    def POSTGRES_URL(self) -> str:
        """Get the PostgreSQL connection URL."""
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"


class AgentSettings(BaseSettings):
    """Settings for agent execution and workflow."""
    MAX_RETRIES: int = Field(3, env="MAX_RETRIES")
    TIMEOUT_SECONDS: int = Field(300, env="TIMEOUT_SECONDS")
    CONCURRENT_WORKFLOWS: int = Field(5, env="CONCURRENT_WORKFLOWS")
    CACHE_RESULTS: bool = Field(True, env="CACHE_RESULTS")
    CACHE_TTL_HOURS: int = Field(24, env="CACHE_TTL_HOURS")

    # Agent-specific settings
    RESEARCH_MAX_SOURCES: int = Field(20, env="RESEARCH_MAX_SOURCES")
    RESEARCH_MAX_TOKENS: int = Field(50000, env="RESEARCH_MAX_TOKENS")
    FACTS_MAX_SEARCHES: int = Field(10, env="FACTS_MAX_SEARCHES")
    BRIEF_MIN_TOPICS: int = Field(5, env="BRIEF_MIN_TOPICS")
    CONTENT_MAX_LENGTH: int = Field(5000, env="CONTENT_MAX_LENGTH")


class NotificationSettings(BaseSettings):
    """Settings for notification services."""
    SLACK_WEBHOOK_URL: Optional[str] = Field(None, env="SLACK_WEBHOOK_URL")
    SLACK_CHANNEL: Optional[str] = Field(None, env="SLACK_CHANNEL")
    EMAIL_NOTIFICATIONS: bool = Field(False, env="EMAIL_NOTIFICATIONS")
    EMAIL_SERVER: Optional[str] = Field(None, env="EMAIL_SERVER")
    EMAIL_PORT: Optional[int] = Field(None, env="EMAIL_PORT")
    EMAIL_USERNAME: Optional[str] = Field(None, env="EMAIL_USERNAME")
    EMAIL_PASSWORD: Optional[str] = Field(None, env="EMAIL_PASSWORD")
    EMAIL_FROM: Optional[str] = Field(None, env="EMAIL_FROM")
    EMAIL_TO: Optional[List[str]] = Field(None, env="EMAIL_TO")


class AgnoSettings(BaseSettings):
    """Settings for Agno framework configuration."""
    # Agno storage settings
    USE_POSTGRES_STORAGE: bool = Field(True, env="USE_POSTGRES_STORAGE")
    PGVECTOR_ENABLED: bool = Field(False, env="PGVECTOR_ENABLED")
    
    # Agno team settings
    TEAM_ORCHESTRATION: str = Field("sequential", env="TEAM_ORCHESTRATION")
    
    # Agno knowledge settings
    KNOWLEDGE_PROVIDER: str = Field("pg_vector", env="KNOWLEDGE_PROVIDER")
    KNOWLEDGE_COLLECTION: str = Field("seo_agent_knowledge", env="KNOWLEDGE_COLLECTION")


class Settings(BaseSettings):
    """Main application settings combining all subsettings."""
    ENVIRONMENT: str = Field("development", env="ENVIRONMENT")
    
    llm: LLMSettings = LLMSettings()
    api: APISettings = APISettings()
    db: DatabaseSettings = DatabaseSettings()
    agent: AgentSettings = AgentSettings()
    notifications: NotificationSettings = NotificationSettings()
    agno: AgnoSettings = AgnoSettings()

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Create global settings instance
settings = Settings()
