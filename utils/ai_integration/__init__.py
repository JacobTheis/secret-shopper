"""PydanticAI integration for secret shopping operations.

This package provides AI-powered agents for:
- Information gathering from real estate websites
- Persona generation for secret shopping
- Email conversation generation and analysis

Usage:
    from utils.ai_integration.agents import (
        PersonaGenerationAgent,
        ConversationAgent,
        FloorPlanSpecialistAgent
    )
    
    # Create agents
    persona_agent = PersonaGenerationAgent()
    email_agent = ConversationAgent('conversation_initial')
    
    # Use agents
    persona = await persona_agent.generate_persona()
    email = await email_agent.generate_initial_inquiry(persona, community_info)
"""

from .schemas import (
    CommunityInformation,
    PersonaDetails,
    EmailContent,
    ConversationAnalysis,
    FloorPlan,
    CommunityPage,
    FloorPlanAmenity,
    CommunityAmenity,
    FloorPlanExtractionResult,
    CommunityOverviewExtractionResult,
    FeeExtractionResult,
    ValidationReport,
    OrchestrationResult
)

from .agents import (
    PersonaGenerationAgent,
    ConversationAgent,
    FloorPlanSpecialistAgent,
    CommunityOverviewAgent,
    FeeSpecialistAgent,
    ValidationAgent,
    MasterOrchestratorAgent
)

from .agent_config import (
    AgentConfig,
    get_agent_config,
    get_model_for_agent,
    get_model_settings_for_agent,
    RETRY_CONFIG
)

__all__ = [
    # Agents
    'PersonaGenerationAgent',
    'ConversationAgent',
    'FloorPlanSpecialistAgent',
    'CommunityOverviewAgent', 
    'FeeSpecialistAgent',
    'ValidationAgent',
    'MasterOrchestratorAgent',
    
    # Schemas
    'CommunityInformation',
    'PersonaDetails',
    'EmailContent',
    'ConversationAnalysis',
    'FloorPlan',
    'CommunityPage',
    'FloorPlanAmenity',
    'CommunityAmenity',
    'FloorPlanExtractionResult',
    'CommunityOverviewExtractionResult',
    'FeeExtractionResult',
    'ValidationReport',
    'OrchestrationResult',
    
    # Configuration
    'AgentConfig',
    'get_agent_config',
    'get_model_for_agent',
    'get_model_settings_for_agent',
    'RETRY_CONFIG',
]