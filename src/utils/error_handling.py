"""
Error handling utilities.

This module provides error handling utilities for managing and standardizing
error handling across the application, particularly for LLM API calls.
"""

import logging
import time
import asyncio
from typing import Any, Callable, Dict, List, Optional, TypeVar, Awaitable, cast
from functools import wraps

# Set up logger
logger = logging.getLogger(__name__)

# Type variables for generic functions
T = TypeVar('T')


class LLMError(Exception):
    """Base exception for LLM-related errors."""
    
    def __init__(self, message: str, model: str, status_code: Optional[int] = None):
        """Initialize LLM error.
        
        Args:
            message: Error message
            model: Model that raised the error
            status_code: Optional status code
        """
        self.model = model
        self.status_code = status_code
        super().__init__(f"Error with model {model}: {message}")


class RateLimitError(LLMError):
    """Exception for rate limit errors from LLM providers."""
    pass


class ContextLengthError(LLMError):
    """Exception for context length errors from LLM providers."""
    pass


class AuthenticationError(LLMError):
    """Exception for authentication errors with LLM providers."""
    pass


class ServiceUnavailableError(LLMError):
    """Exception for service unavailability with LLM providers."""
    pass


class InvalidResponseError(LLMError):
    """Exception for invalid or unexpected responses from LLM providers."""
    pass


def classify_llm_error(error: Exception, model: str) -> LLMError:
    """Classify a generic exception into a specific LLM error type.
    
    Args:
        error: Original exception
        model: Model that raised the error
        
    Returns:
        Classified LLM error
    """
    error_str = str(error).lower()
    
    if "rate limit" in error_str or "too many requests" in error_str or "429" in error_str:
        return RateLimitError("Rate limit exceeded", model, 429)
    
    elif "context length" in error_str or "too long" in error_str or "maximum token" in error_str:
        return ContextLengthError("Context length exceeded", model, 413)
    
    elif "auth" in error_str or "api key" in error_str or "401" in error_str or "403" in error_str:
        return AuthenticationError("Authentication failed", model, 401)
    
    elif "unavailable" in error_str or "down" in error_str or "500" in error_str or "503" in error_str:
        return ServiceUnavailableError("Service unavailable", model, 503)
    
    else:
        return LLMError(str(error), model)


async def retry_async_with_exponential_backoff(
    func: Callable[..., Awaitable[T]],
    *args: Any,
    max_retries: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    backoff_factor: float = 2.0,
    retry_on: List[type] = None,
    **kwargs: Any
) -> T:
    """Retry an async function with exponential backoff.
    
    Args:
        func: Async function to retry
        *args: Positional arguments to pass to func
        max_retries: Maximum number of retries
        initial_delay: Initial delay between retries in seconds
        max_delay: Maximum delay between retries in seconds
        backoff_factor: Factor to increase delay by after each retry
        retry_on: List of exception types to retry on
        **kwargs: Keyword arguments to pass to func
        
    Returns:
        Result of the function call
        
    Raises:
        Exception: If max retries are exceeded
    """
    if retry_on is None:
        retry_on = [LLMError, RateLimitError]
    
    retries = 0
    delay = initial_delay
    
    while True:
        try:
            return await func(*args, **kwargs)
        
        except tuple(retry_on) as e:
            retries += 1
            
            if retries > max_retries:
                logger.warning(f"Max retries ({max_retries}) exceeded for {func.__name__}")
                raise
            
            # Calculate next delay with exponential backoff
            delay = min(delay * backoff_factor, max_delay)
            
            # Log retry attempt
            logger.info(f"Retry {retries}/{max_retries} for {func.__name__} after error: {str(e)}. Waiting {delay:.2f}s")
            
            # Wait before retrying
            await asyncio.sleep(delay)
        
        except Exception as e:
            # Don't retry on other exceptions
            logger.error(f"Non-retryable error in {func.__name__}: {str(e)}")
            raise


def async_retry_decorator(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    backoff_factor: float = 2.0,
    retry_on: List[type] = None
):
    """Decorator to retry an async function with exponential backoff.
    
    Args:
        max_retries: Maximum number of retries
        initial_delay: Initial delay between retries in seconds
        max_delay: Maximum delay between retries in seconds
        backoff_factor: Factor to increase delay by after each retry
        retry_on: List of exception types to retry on
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            return await retry_async_with_exponential_backoff(
                func, *args,
                max_retries=max_retries,
                initial_delay=initial_delay,
                max_delay=max_delay,
                backoff_factor=backoff_factor,
                retry_on=retry_on,
                **kwargs
            )
        return wrapper
    return decorator
