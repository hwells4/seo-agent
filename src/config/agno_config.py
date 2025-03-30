"""
Agno framework configuration.

This module initializes and configures the Agno agent framework,
including storage providers, logging, and global settings.
"""

import logging
from typing import Optional

from agno import Config
from agno.storage import PostgresStorage, MemoryStorage, StorageProvider
from agno.knowledge import PGVectorKnowledge

from src.config.settings import settings

# Set up logger
logger = logging.getLogger(__name__)


def configure_agno() -> None:
    """Configure the Agno framework with appropriate settings."""
    try:
        # Create storage provider
        storage_provider = _get_storage_provider()
        
        # Configure Agno
        Config.configure(
            default_storage=storage_provider,
            log_level=settings.api.LOG_LEVEL,
            default_model_params={
                "timeout": settings.agent.TIMEOUT_SECONDS,
            },
        )
        
        logger.info("Agno framework configured successfully")
    
    except Exception as e:
        logger.error(f"Error configuring Agno framework: {str(e)}")
        # Fall back to memory storage if configuration fails
        Config.configure(
            default_storage=MemoryStorage(),
            log_level="INFO",
        )
        logger.warning("Falling back to memory storage")


def _get_storage_provider() -> StorageProvider:
    """Get the appropriate storage provider based on configuration.
    
    Returns:
        Configured storage provider
    """
    # Use PostgreSQL if enabled in settings
    if settings.agno.USE_POSTGRES_STORAGE:
        try:
            return PostgresStorage(
                connection_url=settings.db.POSTGRES_URL,
                table_prefix="agno_",
            )
        except Exception as e:
            logger.error(f"Failed to initialize PostgreSQL storage: {str(e)}")
    
    # Use memory storage as fallback
    return MemoryStorage()


def get_knowledge_provider():
    """Get the appropriate knowledge provider based on configuration.
    
    Returns:
        Configured knowledge provider
    """
    # Use PGVector if enabled in settings
    if settings.agno.PGVECTOR_ENABLED:
        try:
            return PGVectorKnowledge(
                connection_url=settings.db.POSTGRES_URL,
                collection_name=settings.agno.KNOWLEDGE_COLLECTION,
            )
        except Exception as e:
            logger.error(f"Failed to initialize PGVector knowledge: {str(e)}")
            return None
    
    return None


# Initialize Agno configuration (can be called from main.py)
def init_agno() -> None:
    """Initialize Agno framework with default configuration."""
    configure_agno() 