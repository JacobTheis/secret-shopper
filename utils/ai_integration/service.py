"""Service layer for PydanticAI agents with multi-provider fallback support."""
import logging
from typing import Any, Optional, Type, TypeVar
from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.exceptions import ModelRetry, UserError

from .agent_config import get_agent_config, get_model_for_agent, RETRY_CONFIG

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=BaseModel)


class AIServiceError(Exception):
    """Base exception for AI service errors."""
    pass


class AIServiceUnavailableError(AIServiceError):
    """Exception raised when all AI services are unavailable."""
    pass


class MultiProviderAIService:
    """Service that handles AI operations with automatic fallback between providers."""
    
    def __init__(self, agent_type: str, result_type: Type[T]):
        """Initialize the multi-provider service.
        
        Args:
            agent_type: The type of agent (from AGENT_CONFIGS)
            result_type: Pydantic model type for the expected result
        """
        self.agent_type = agent_type
        self.result_type = result_type
        self.config = get_agent_config(agent_type)
        
        # Initialize primary and fallback agents
        try:
            primary_model = get_model_for_agent(agent_type, prefer_fallback=False)
            self.primary_agent = Agent(
                model=primary_model,
                result_type=result_type,
                system_prompt=self.config['system_prompt']
            )
            logger.info(f"Initialized primary agent for {agent_type} using {self.config['primary_service']}")
        except Exception as e:
            logger.warning(f"Failed to initialize primary agent for {agent_type}: {str(e)}")
            self.primary_agent = None
        
        try:
            fallback_model = get_model_for_agent(agent_type, prefer_fallback=True)
            self.fallback_agent = Agent(
                model=fallback_model,
                result_type=result_type,
                system_prompt=self.config['system_prompt']
            )
            logger.info(f"Initialized fallback agent for {agent_type} using {self.config['fallback_service']}")
        except Exception as e:
            logger.warning(f"Failed to initialize fallback agent for {agent_type}: {str(e)}")
            self.fallback_agent = None
        
        if not self.primary_agent and not self.fallback_agent:
            raise AIServiceUnavailableError(f"No agents available for {agent_type}")
    
    async def run(self, prompt: str, **kwargs) -> T:
        """Run the agent with automatic fallback.
        
        Args:
            prompt: The prompt to send to the agent
            **kwargs: Additional arguments for the agent
            
        Returns:
            The result from the agent
            
        Raises:
            AIServiceError: If both primary and fallback agents fail
        """
        # Try primary agent first
        if self.primary_agent:
            try:
                logger.debug(f"Attempting {self.agent_type} with primary service ({self.config['primary_service']})")
                result = await self.primary_agent.run(prompt, **kwargs)
                logger.info(f"Successfully completed {self.agent_type} with primary service")
                return result.data
            except Exception as e:
                logger.warning(f"Primary agent failed for {self.agent_type}: {str(e)}")
                
                # Check if this is a retryable error
                if self._is_retryable_error(e):
                    logger.info(f"Error is retryable, attempting fallback for {self.agent_type}")
                else:
                    # For non-retryable errors (like validation), re-raise immediately
                    logger.error(f"Non-retryable error in {self.agent_type}: {str(e)}")
                    raise AIServiceError(f"Primary agent failed with non-retryable error: {str(e)}")
        
        # Try fallback agent
        if self.fallback_agent:
            try:
                logger.info(f"Attempting {self.agent_type} with fallback service ({self.config['fallback_service']})")
                result = await self.fallback_agent.run(prompt, **kwargs)
                logger.info(f"Successfully completed {self.agent_type} with fallback service")
                return result.data
            except Exception as e:
                logger.error(f"Fallback agent also failed for {self.agent_type}: {str(e)}")
                raise AIServiceError(f"Both primary and fallback agents failed: {str(e)}")
        
        raise AIServiceUnavailableError(f"No agents available for {self.agent_type}")
    
    def _is_retryable_error(self, error: Exception) -> bool:
        """Check if an error is retryable.
        
        Args:
            error: The exception to check
            
        Returns:
            True if the error is retryable, False otherwise
        """
        # Convert to string to check error messages
        error_str = str(error).lower()
        
        # Check for known retryable error patterns
        retryable_patterns = [
            'rate limit',
            'timeout',
            'connection error',
            'server error',
            'service unavailable',
            'internal server error',
            'bad gateway',
            'gateway timeout',
            'too many requests'
        ]
        
        for pattern in retryable_patterns:
            if pattern in error_str:
                return True
        
        # PydanticAI specific retry exceptions
        if isinstance(error, ModelRetry):
            return True
        
        # User errors (validation, etc.) are generally not retryable
        if isinstance(error, UserError):
            return False
        
        # Default to retryable for unknown errors
        return True


# Convenience functions for creating service instances
def create_information_gathering_service():
    """Create an information gathering service instance."""
    from .agents import InformationGatheringAgent
    return InformationGatheringAgent()


def create_persona_generation_service():
    """Create a persona generation service instance."""
    from .schemas import PersonaDetails
    return MultiProviderAIService('persona_generation', PersonaDetails)


def create_conversation_service(conversation_type: str):
    """Create a conversation service instance.
    
    Args:
        conversation_type: Either 'initial', 'followup', or 'analysis'
    """
    from .schemas import EmailContent, ConversationAnalysis
    
    agent_type = f'conversation_{conversation_type}'
    
    if conversation_type in ['initial', 'followup']:
        return MultiProviderAIService(agent_type, EmailContent)
    elif conversation_type == 'analysis':
        return MultiProviderAIService(agent_type, ConversationAnalysis)
    else:
        raise ValueError(f"Unknown conversation type: {conversation_type}")