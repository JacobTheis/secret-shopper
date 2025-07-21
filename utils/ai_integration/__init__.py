"""PydanticAI integration for secret shopping operations.

This package provides AI-powered agents for:
- Information gathering from real estate websites
- Persona generation for secret shopping
- Email conversation generation and analysis

Usage:
    from utils.ai_integration.service import (
        create_information_gathering_service,
        create_persona_generation_service,
        create_conversation_service
    )
    
    # Create services
    info_service = create_information_gathering_service()
    persona_service = create_persona_generation_service()
    email_service = create_conversation_service('initial')
    
    # Use services
    community_data = await info_service.run("https://example.com")
    persona = await persona_service.run("Generate a young professional persona")
    email = await email_service.run("Write an inquiry email")
"""

from .service import (
    create_information_gathering_service,
    create_persona_generation_service,
    create_conversation_service,
    MultiProviderAIService,
    AIServiceError,
    AIServiceUnavailableError
)

from .schemas import (
    CommunityInformation,
    PersonaDetails,
    EmailContent,
    ConversationAnalysis,
    FloorPlan,
    CommunityPage,
    FloorPlanAmenity,
    CommunityAmenity
)

from .agent_config import (
    AgentConfig,
    get_agent_config,
    get_model_for_agent,
    RETRY_CONFIG
)

__all__ = [
    # Service layer
    'create_information_gathering_service',
    'create_persona_generation_service',
    'create_conversation_service',
    'MultiProviderAIService',
    'AIServiceError',
    'AIServiceUnavailableError',
    
    # Schemas
    'CommunityInformation',
    'PersonaDetails',
    'EmailContent',
    'ConversationAnalysis',
    'FloorPlan',
    'CommunityPage',
    'FloorPlanAmenity',
    'CommunityAmenity',
    
    # Configuration
    'AgentConfig',
    'get_agent_config',
    'get_model_for_agent',
    'RETRY_CONFIG',
]