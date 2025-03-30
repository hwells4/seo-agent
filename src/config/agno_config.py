"""
Agno framework configuration.

This module initializes and configures the Agno agent framework,
including storage providers, logging, and global settings.
"""

import logging
import os
from typing import Optional

from agno.storage.postgres import PostgresStorage
from agno.storage.json import JsonStorage as MemoryStorage
from agno.storage.base import Storage as StorageProvider
from agno.knowledge import AgentKnowledge

from src.config.settings import settings

# Set up logger
logger = logging.getLogger(__name__)

# Global storage provider for agents to use
_storage_provider = None

def configure_agno() -> None:
    """Configure the Agno framework with appropriate settings.
    
    For Agno 1.2.6+, we don't use agno.configure() anymore.
    Instead, we set up a global storage provider that will be
    used by individual Agent instances.
    """
    global _storage_provider
    
    try:
        # Create storage provider
        _storage_provider = _get_storage_provider()
        
        # Set up environment variables for API keys used by Agno models
        os.environ["OPENAI_API_KEY"] = settings.llm.OPENAI_API_KEY
        os.environ["ANTHROPIC_API_KEY"] = settings.llm.ANTHROPIC_API_KEY
        
        # These might be used by custom model implementations
        os.environ["DEEPSEEK_API_KEY"] = settings.llm.DEEPSEEK_API_KEY
        os.environ["GROK_API_KEY"] = settings.llm.GROK_API_KEY
        
        logger.info("Agno framework configured successfully")
    
    except Exception as e:
        logger.error(f"Error configuring Agno framework: {str(e)}")
        # Fall back to memory storage if configuration fails
        _storage_provider = MemoryStorage(dir_path="./agno_storage")
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
    
    # Use memory storage as fallback with a temporary directory path
    return MemoryStorage(dir_path="./agno_storage")


def get_knowledge_provider():
    """Get the appropriate knowledge provider based on configuration.
    
    Returns:
        Configured knowledge provider
    """
    # Use PGVector if enabled in settings
    if settings.agno.PGVECTOR_ENABLED:
        try:
            # Use default AgentKnowledge for now
            return AgentKnowledge()
        except Exception as e:
            logger.error(f"Failed to initialize knowledge provider: {str(e)}")
            return None
    
    return None


def get_storage():
    """Get the configured storage provider.
    
    Returns:
        Configured storage provider
    """
    global _storage_provider
    if _storage_provider is None:
        configure_agno()
    return _storage_provider


# Initialize Agno configuration (can be called from main.py)
def init_agno() -> None:
    """Initialize Agno framework with default configuration."""
    configure_agno() 