"""Configuration for PydanticAI agents."""
import os
from typing import Dict, Any, Optional, Union
from django.conf import settings
from pydantic_ai.models import Model
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.models.anthropic import AnthropicModel


class AgentConfig:
    """Configuration class for PydanticAI agents."""
    
    @staticmethod
    def get_api_key(service: str) -> Optional[str]:
        """Get API key for the specified service.
        
        Args:
            service: The AI service name ('openai' or 'anthropic')
            
        Returns:
            The API key or None if not found
        """
        if service.lower() == 'openai':
            return os.environ.get('OPENAI_API_KEY') or getattr(settings, 'OPENAI_API_KEY', None)
        elif service.lower() == 'anthropic':
            return os.environ.get('ANTHROPIC_API_KEY') or getattr(settings, 'ANTHROPIC_API_KEY', None)
        return None
    
    @staticmethod
    def get_model(service: str, model_name: str) -> Model:
        """Get a PydanticAI model instance.
        
        Args:
            service: The AI service name ('openai' or 'anthropic')
            model_name: The specific model to use
            
        Returns:
            A PydanticAI Model instance
            
        Raises:
            ValueError: If service is not supported or API key is missing
        """
        api_key = AgentConfig.get_api_key(service)
        if not api_key:
            raise ValueError(f"API key for {service} not found in environment or settings")
        
        # Set the API key in the environment for PydanticAI to use
        if service.lower() == 'openai':
            os.environ['OPENAI_API_KEY'] = api_key
            return OpenAIModel(model_name)
        elif service.lower() == 'anthropic':
            os.environ['ANTHROPIC_API_KEY'] = api_key  
            return AnthropicModel(model_name)
        else:
            raise ValueError(f"Unsupported AI service: {service}")


# Agent-specific configurations with multi-provider support
AGENT_CONFIGS = {
    'information_gathering': {
        'primary_service': 'openai',
        'fallback_service': 'anthropic',
        'openai_model': 'gpt-4o-mini',
        'anthropic_model': 'claude-3-5-haiku-20241022',
        'temperature': 0.1,
        'tools': [
            {
                'type': 'web_search_preview',
                'user_location': {
                    'type': 'approximate',
                    'country': 'US'
                },
                'search_context_size': 'high',
            }
        ],
        'system_prompt': """You are a real estate professional analyzing rental community websites. 
        Extract comprehensive information about the community including fees, policies, amenities, and floor plans.
        Use the provided website as your source of truth. Be thorough and accurate in your data extraction."""
    },
    
    'persona_generation': {
        'primary_service': 'anthropic',
        'fallback_service': 'openai',
        'openai_model': 'gpt-4o-mini',
        'anthropic_model': 'claude-3-5-haiku-20241022',
        'temperature': 0.8,
        'system_prompt': """You are an expert at creating realistic personas for secret shopping scenarios.
        Generate detailed, believable personas with specific backgrounds, preferences, and communication styles
        that would be appropriate for apartment hunting scenarios."""
    },
    
    'conversation_initial': {
        'primary_service': 'anthropic',
        'fallback_service': 'openai',
        'openai_model': 'gpt-4o-mini',
        'anthropic_model': 'claude-3-5-haiku-20241022',
        'temperature': 0.7,
        'system_prompt': """You are roleplaying as a potential tenant looking for an apartment.
        Write natural, engaging initial inquiry emails that reflect your persona's communication style,
        interests, and housing needs. Be authentic and specific in your questions."""
    },
    
    'conversation_followup': {
        'primary_service': 'anthropic',
        'fallback_service': 'openai',
        'openai_model': 'gpt-4o-mini',
        'anthropic_model': 'claude-3-5-haiku-20241022',
        'temperature': 0.7,
        'system_prompt': """You are following up on a previous apartment inquiry as your persona.
        Write polite, natural follow-up emails that address any missing information while maintaining
        your character's voice and style. Show continued interest while being specific about your needs."""
    },
    
    'conversation_analysis': {
        'primary_service': 'openai',
        'fallback_service': 'anthropic',
        'openai_model': 'gpt-4o-mini',
        'anthropic_model': 'claude-3-5-haiku-20241022',
        'temperature': 0.1,
        'system_prompt': """You are analyzing property agent responses for secret shopping purposes.
        Extract key information, evaluate responsiveness and professionalism, and identify what
        information is still missing. Be objective and thorough in your analysis."""
    }
}


def get_agent_config(agent_type: str) -> Dict[str, Any]:
    """Get configuration for a specific agent type.
    
    Args:
        agent_type: The type of agent (e.g., 'information_gathering')
        
    Returns:
        Configuration dictionary for the agent
        
    Raises:
        KeyError: If agent_type is not found
    """
    if agent_type not in AGENT_CONFIGS:
        raise KeyError(f"Unknown agent type: {agent_type}")
    return AGENT_CONFIGS[agent_type].copy()


def get_model_for_agent(agent_type: str, prefer_fallback: bool = False) -> Model:
    """Get a configured model instance for a specific agent.
    
    Args:
        agent_type: The type of agent
        prefer_fallback: Whether to use the fallback service instead of primary
        
    Returns:
        A PydanticAI Model instance
    """
    config = get_agent_config(agent_type)
    
    if prefer_fallback and 'fallback_service' in config:
        service = config['fallback_service']
        model_name = config[f'{service}_model']
    else:
        service = config['primary_service']
        model_name = config[f'{service}_model']
    
    return AgentConfig.get_model(service, model_name)


def get_model_with_fallback(agent_type: str) -> tuple[Model, Model]:
    """Get both primary and fallback models for an agent.
    
    Args:
        agent_type: The type of agent
        
    Returns:
        Tuple of (primary_model, fallback_model)
    """
    primary_model = get_model_for_agent(agent_type, prefer_fallback=False)
    fallback_model = get_model_for_agent(agent_type, prefer_fallback=True)
    return primary_model, fallback_model


# Retry configuration
RETRY_CONFIG = {
    'max_retries': 3,
    'retry_delay': 2,  # seconds
    'backoff_factor': 2,
    'retriable_errors': [
        'rate_limit_exceeded',
        'timeout',
        'server_error',
        'connection_error'
    ]
}