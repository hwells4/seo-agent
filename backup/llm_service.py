"""
LLM Service for connecting to various model providers.

This service abstracts the details of connecting to different LLM providers
through Agno's model-agnostic framework, handling authentication, retries,
and error management.
"""

import logging
from typing import Dict, Any, Optional, List, Union

import agno
from agno.models.openai import OpenAIChat
from agno.models.anthropic import Claude
from agno.models.base import Model
from agno.models.custom import Custom
from agno.exceptions import AgnoModelException, AgnoTimeoutException

from src.config.settings import settings
from src.utils.error_handling import async_retry_decorator, classify_llm_error

# Set up logger
logger = logging.getLogger(__name__)


class LLMService:
    """Service for interacting with various LLM providers through Agno."""
    
    def __init__(self):
        """Initialize LLM service with configured providers."""
        self.models: Dict[str, Model] = {}
        self._initialize_models()
    
    def _initialize_models(self) -> None:
        """Initialize all supported LLM models using Agno's model wrappers."""
        try:
            # Map provider to model class initialization functions
            provider_map = {
                "openai": self._create_openai_model,
                "anthropic": self._create_anthropic_model,
                "deepseek": self._create_deepseek_model,
                "grok": self._create_grok_model
            }
            
            # Initialize models for each agent type based on settings
            for agent_type, config in settings.llm.MODEL_CONFIG.items():
                provider = config.get("provider", "").lower()
                model_name = config.get("model", "")
                
                if not provider or not model_name:
                    logger.warning(f"Missing provider or model name for {agent_type}")
                    continue
                    
                if provider not in provider_map:
                    logger.warning(f"Unsupported provider {provider} for {agent_type}")
                    continue
                    
                # Get the initialization function
                init_fn = provider_map[provider]
                
                # Create model params
                model_params = {
                    "temperature": config.get("temperature", 0.5),
                    "max_tokens": config.get("max_tokens", 2000),
                    "timeout": settings.agent.TIMEOUT_SECONDS,
                }
                
                # Add any additional params from config
                for key, value in config.items():
                    if key not in ["provider", "model", "temperature", "max_tokens"]:
                        model_params[key] = value
                
                # Initialize the model
                try:
                    model = init_fn(
                        model_name=model_name,
                        default_params=model_params
                    )
                    
                    # Store for each agent type and model name for flexibility
                    self.models[agent_type] = model
                    self.models[model_name] = model
                    
                    logger.info(f"Initialized {provider} model {model_name} for {agent_type}")
                except Exception as e:
                    logger.error(f"Failed to initialize {provider} model {model_name}: {str(e)}")
            
            logger.info(f"Successfully initialized {len(self.models)} LLM models")
        
        except Exception as e:
            logger.error(f"Error initializing LLM models: {str(e)}")
            raise
    
    def _create_openai_model(self, model_name: str, default_params: Dict[str, Any]) -> Model:
        """Create an OpenAI model instance.
        
        Args:
            model_name: Model name to use
            default_params: Default parameters for model calls
            
        Returns:
            Configured model instance
        """
        return OpenAIChat(
            id=model_name,
            config={
                "api_key": settings.llm.OPENAI_API_KEY,
                **default_params
            }
        )
    
    def _create_anthropic_model(self, model_name: str, default_params: Dict[str, Any]) -> Model:
        """Create an Anthropic model instance.
        
        Args:
            model_name: Model name to use
            default_params: Default parameters for model calls
            
        Returns:
            Configured model instance
        """
        return Claude(
            id=model_name,
            config={
                "api_key": settings.llm.ANTHROPIC_API_KEY,
                **default_params
            }
        )
    
    def _create_deepseek_model(self, model_name: str, default_params: Dict[str, Any]) -> Model:
        """Create a DeepSeek model instance using Agno's Custom model.
        
        Args:
            model_name: Model name to use
            default_params: Default parameters for model calls
            
        Returns:
            Configured model instance
        """
        return Custom(
            id=model_name,
            config={
                "base_url": "https://api.deepseek.com/v1",
                "api_key": settings.llm.DEEPSEEK_API_KEY,
                "headers": {"Authorization": f"Bearer {settings.llm.DEEPSEEK_API_KEY}"},
                "request_mapping": {
                    "path": "/chat/completions",
                    "method": "POST",
                    "request_schema": {
                        "model": "${model}",
                        "messages": [{"role": "user", "content": "${prompt}"}],
                        "temperature": "${temperature}",
                        "max_tokens": "${max_tokens}",
                    },
                    "response_mapping": {
                        "text": "choices[0].message.content",
                    }
                },
                **default_params
            }
        )
    
    def _create_grok_model(self, model_name: str, default_params: Dict[str, Any]) -> Model:
        """Create a Grok model instance using Agno's Custom model.
        
        Args:
            model_name: Model name to use
            default_params: Default parameters for model calls
            
        Returns:
            Configured model instance
        """
        return Custom(
            id=model_name,
            config={
                "base_url": "https://api.grok.ai/v1",
                "api_key": settings.llm.GROK_API_KEY,
                "headers": {"Authorization": f"Bearer {settings.llm.GROK_API_KEY}"},
                "request_mapping": {
                    "path": "/chat/completions",
                    "method": "POST",
                    "request_schema": {
                        "model": "${model}",
                        "messages": [{"role": "user", "content": "${prompt}"}],
                        "temperature": "${temperature}",
                        "max_tokens": "${max_tokens}",
                    },
                    "response_mapping": {
                        "text": "choices[0].message.content",
                    }
                },
                **default_params
            }
        )
    
    @async_retry_decorator(max_retries=settings.agent.MAX_RETRIES)
    async def generate_text(
        self, 
        model_name: str, 
        prompt: str, 
        params: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate text using the specified model through Agno.
        
        Args:
            model_name: Name of the model to use
            prompt: Text prompt to send to the model
            params: Additional parameters to pass to the model
            
        Returns:
            Generated text response
            
        Raises:
            ValueError: If model not configured or response is empty
        """
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not configured")
        
        model = self.models[model_name]
        
        try:
            # Using the Agno Agent's run method
            response = await model.run(user_message=prompt, params=params or {})
            
            # Validate response
            if not response or not isinstance(response, str):
                raise ValueError(f"Invalid response from model {model_name}")
            
            return response
            
        except AgnoTimeoutException as e:
            logger.error(f"Timeout error with model {model_name}: {str(e)}")
            raise classify_llm_error(e, model_name)
            
        except AgnoModelException as e:
            logger.error(f"Model error with {model_name}: {str(e)}")
            raise classify_llm_error(e, model_name)
            
        except Exception as e:
            logger.error(f"Unexpected error with model {model_name}: {str(e)}")
            raise classify_llm_error(e, model_name)
    
    @async_retry_decorator(max_retries=settings.agent.MAX_RETRIES)
    async def generate_structured_output(
        self, 
        model_name: str, 
        prompt: str, 
        output_schema: Dict[str, Any],
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate structured output using the specified model through Agno.
        
        Args:
            model_name: Name of the model to use
            prompt: Text prompt to send to the model
            output_schema: JSON schema for structured output
            params: Additional parameters to pass to the model
            
        Returns:
            Structured output as a dictionary
            
        Raises:
            ValueError: If model not configured or response is empty
        """
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not configured")
        
        model = self.models[model_name]
        
        # Merge parameters
        combined_params = {
            "use_json_mode": True,
            **(params or {})
        }
        
        try:
            # Call the model with JSON schema
            response = await model.run(
                user_message=prompt,
                response_model=output_schema,
                params=combined_params
            )
            
            # Validate response
            if not response or not isinstance(response, dict):
                raise ValueError(f"Invalid structured response from model {model_name}")
            
            return response
            
        except AgnoTimeoutException as e:
            logger.error(f"Timeout error with model {model_name}: {str(e)}")
            raise classify_llm_error(e, model_name)
            
        except AgnoModelException as e:
            logger.error(f"Model error with {model_name}: {str(e)}")
            raise classify_llm_error(e, model_name)
            
        except Exception as e:
            logger.error(f"Unexpected error with model {model_name}: {str(e)}")
            raise classify_llm_error(e, model_name)
    
    async def check_model_availability(self) -> Dict[str, bool]:
        """Check the availability of all configured models.
        
        Returns:
            Dictionary mapping model names to availability status
        """
        availability = {}
        
        for model_name, model in self.models.items():
            try:
                # Simple prompt to test model availability
                response = await model.generate(
                    "Hello, are you available?", 
                    {"max_tokens": 10, "timeout": 10}
                )
                availability[model_name] = bool(response and response.text)
            except Exception as e:
                logger.warning(f"Model {model_name} availability check failed: {str(e)}")
                availability[model_name] = False
        
        return availability


# Create global service instance
llm_service = LLMService()
