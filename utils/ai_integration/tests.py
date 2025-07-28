"""Tests for PydanticAI agents and services."""
import unittest
import pytest
from unittest.mock import Mock, patch, AsyncMock
from pydantic_ai.models import Model
from pydantic_ai import Agent

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
from .service import MultiProviderAIService, AIServiceError, AIServiceUnavailableError
from .agent_config import AgentConfig, get_agent_config, get_model_for_agent
from .agents import PersonaGenerationAgent, ConversationAgent


class TestAgentConfig:
    """Tests for agent configuration functionality."""
    
    @patch.dict('os.environ', {'OPENAI_API_KEY': 'test-openai-key'})
    def test_get_api_key_openai_from_env(self):
        """Test getting OpenAI API key from environment variable."""
        assert AgentConfig.get_api_key('openai') == 'test-openai-key'
    
    @patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-anthropic-key'})
    def test_get_api_key_anthropic_from_env(self):
        """Test getting Anthropic API key from environment variable."""
        assert AgentConfig.get_api_key('anthropic') == 'test-anthropic-key'
    
    def test_get_api_key_unknown_service(self):
        """Test getting API key for unknown service returns None."""
        assert AgentConfig.get_api_key('unknown') is None
    
    def test_get_agent_config_valid_type(self):
        """Test getting configuration for a valid agent type."""
        config = get_agent_config('persona_generation')
        assert 'primary_service' in config
        assert 'system_prompt' in config
    
    def test_get_agent_config_invalid_type(self):
        """Test getting configuration for invalid agent type raises KeyError."""
        with pytest.raises(KeyError):
            get_agent_config('invalid_agent_type')
    
    @patch.object(AgentConfig, 'get_api_key')
    @patch('utils.ai_integration.agent_config.OpenAIModel')
    def test_get_model_openai(self, mock_openai_model, mock_get_api_key):
        """Test getting OpenAI model instance."""
        mock_get_api_key.return_value = 'test-key'
        mock_model_instance = Mock()
        mock_openai_model.return_value = mock_model_instance
        
        result = AgentConfig.get_model('openai', 'gpt-4')
        
        mock_get_api_key.assert_called_once_with('openai')
        mock_openai_model.assert_called_once_with('gpt-4', api_key='test-key')
        assert result == mock_model_instance
    
    @patch.object(AgentConfig, 'get_api_key')
    def test_get_model_no_api_key(self, mock_get_api_key):
        """Test getting model with no API key raises ValueError."""
        mock_get_api_key.return_value = None
        
        with pytest.raises(ValueError, match="API key for openai not found"):
            AgentConfig.get_model('openai', 'gpt-4')


class TestSchemas:
    """Tests for Pydantic schema validation."""
    
    def test_community_information_minimal(self):
        """Test CommunityInformation with minimal required fields."""
        data = {
            'name': 'Test Community',
            'overview': 'A test community',
            'url': 'https://example.com'
        }
        community = CommunityInformation(**data)
        assert community.name == 'Test Community'
        assert community.overview == 'A test community'
        assert community.url == 'https://example.com'
    
    def test_community_information_with_floor_plans(self):
        """Test CommunityInformation with floor plans."""
        data = {
            'name': 'Test Community',
            'overview': 'A test community',
            'url': 'https://example.com',
            'floor_plans': [
                {
                    'name': '1BR',
                    'beds': 1,
                    'baths': 1,
                    'url': 'https://example.com/1br',
                    'type': 'apartment',
                    'floor_plan_amenities': [
                        {'amenity': 'Air Conditioning'}
                    ]
                }
            ]
        }
        community = CommunityInformation(**data)
        assert len(community.floor_plans) == 1
        assert community.floor_plans[0].name == '1BR'
        assert len(community.floor_plans[0].floor_plan_amenities) == 1
    
    def test_persona_details_validation(self):
        """Test PersonaDetails schema validation."""
        data = {
            'name': 'John Doe',
            'age': 30,
            'occupation': 'Software Engineer',
            'email': 'john@example.com',
            'phone': '555-0123',
            'timeline': 'Within 2 months',
            'key_question': 'Pet policy questions',
            'interest_point': 'Amenities',
            'communication_style': 'Professional',
            'budget_range': '$2000-$2500',
            'background_story': 'Recently relocated for work',
            'priorities': ['Pet-friendly', 'Close to work']
        }
        persona = PersonaDetails(**data)
        assert persona.name == 'John Doe'
        assert persona.age == 30
        assert len(persona.priorities) == 2
    
    def test_email_content_schema(self):
        """Test EmailContent schema validation."""
        data = {
            'subject': 'Apartment Inquiry',
            'body': 'I am interested in your apartment.',
            'tone': 'Professional'
        }
        email = EmailContent(**data)
        assert email.subject == 'Apartment Inquiry'
        assert email.tone == 'Professional'


class TestMultiProviderAIService:
    """Tests for MultiProviderAIService."""
    
    @pytest.fixture
    def mock_agent(self):
        """Create a mock agent."""
        agent = Mock(spec=Agent)
        mock_result = Mock()
        mock_result.data = PersonaDetails(
            name="John Doe",
            age=30,
            occupation="Software Engineer",
            email="john@example.com",
            phone="555-0123",
            timeline="Within 2 months",
            key_question="Pet policy questions",
            interest_point="Amenities",
            communication_style="Professional",
            budget_range="$2000-$2500",
            background_story="Recently relocated for work",
            priorities=["Pet-friendly", "Close to work"]
        )
        agent.run = AsyncMock(return_value=mock_result)
        return agent
    
    @pytest.fixture
    def mock_service(self, mock_agent):
        """Create a MultiProviderAIService with mock agents."""
        with patch('utils.ai_integration.service.get_agent_config') as mock_config, \
             patch('utils.ai_integration.service.get_model_for_agent') as mock_model:
            
            mock_config.return_value = {
                'primary_service': 'openai',
                'fallback_service': 'anthropic',
                'system_prompt': 'Test prompt'
            }
            
            service = MultiProviderAIService('persona_generation', PersonaDetails)
            service.primary_agent = mock_agent
            service.fallback_agent = mock_agent
            return service
    
    @pytest.mark.asyncio
    async def test_run_success_primary(self, mock_service):
        """Test successful run with primary agent."""
        result = await mock_service.run("Test prompt")
        
        assert isinstance(result, PersonaDetails)
        assert result.name == "John Doe"
        mock_service.primary_agent.run.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_run_fallback_on_error(self, mock_service):
        """Test fallback to secondary agent on error."""
        # Make primary agent fail
        mock_service.primary_agent.run.side_effect = Exception("Rate limit exceeded")
        
        result = await mock_service.run("Test prompt")
        
        assert isinstance(result, PersonaDetails)
        mock_service.primary_agent.run.assert_called_once()
        mock_service.fallback_agent.run.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_run_both_agents_fail(self, mock_service):
        """Test when both agents fail."""
        mock_service.primary_agent.run.side_effect = Exception("Primary failed")
        mock_service.fallback_agent.run.side_effect = Exception("Fallback failed")
        
        with pytest.raises(AIServiceError):
            await mock_service.run("Test prompt")
    
    def test_is_retryable_error_rate_limit(self, mock_service):
        """Test rate limit errors are retryable."""
        error = Exception("Rate limit exceeded")
        assert mock_service._is_retryable_error(error) is True
    
    def test_is_retryable_error_validation(self, mock_service):
        """Test validation errors are not retryable."""
        from pydantic_ai.exceptions import UserError
        error = UserError("Invalid input")
        assert mock_service._is_retryable_error(error) is False


class TestAgents:
    """Tests for individual agent classes."""
    
    @pytest.fixture
    def mock_model(self):
        """Create a mock model."""
        return Mock(spec=Model)
    
    @pytest.fixture 
    def mock_agent_result(self):
        """Create a mock agent result."""
        mock_result = Mock()
        mock_result.data = PersonaDetails(
            name="John Doe",
            age=30,
            occupation="Software Engineer",
            email="john@example.com",
            phone="555-0123",
            timeline="Within 2 months",
            key_question="Pet policy questions",
            interest_point="Amenities",
            communication_style="Professional",
            budget_range="$2000-$2500",
            background_story="Recently relocated for work",
            priorities=["Pet-friendly", "Close to work"]
        )
        return mock_result
    
    
    @patch('utils.ai_integration.agents.get_model_for_agent')
    @patch('utils.ai_integration.agents.get_agent_config')
    def test_persona_generation_agent_init(self, mock_config, mock_get_model):
        """Test PersonaGenerationAgent initialization."""
        mock_config.return_value = {'system_prompt': 'Test prompt'}
        mock_get_model.return_value = Mock(spec=Model)
        
        agent = PersonaGenerationAgent()
        
        mock_config.assert_called_once_with('persona_generation')
        assert agent.agent is not None
    
    @patch('utils.ai_integration.agents.get_model_for_agent')
    @patch('utils.ai_integration.agents.get_agent_config')
    def test_conversation_agent_init(self, mock_config, mock_get_model):
        """Test ConversationAgent initialization."""
        mock_config.return_value = {'system_prompt': 'Test prompt'}
        mock_get_model.return_value = Mock(spec=Model)
        
        agent = ConversationAgent('conversation_initial')
        
        mock_config.assert_called_once_with('conversation_initial')
        assert agent.agent_type == 'conversation_initial'
        assert agent.agent is not None
    
    def test_conversation_agent_invalid_type(self):
        """Test ConversationAgent with invalid agent type."""
        with patch('utils.ai_integration.agents.get_agent_config', side_effect=KeyError):
            with pytest.raises(KeyError):
                ConversationAgent('invalid_type')


class TestServiceCreators:
    """Tests for service creator functions."""
    
    
    @patch('utils.ai_integration.service.MultiProviderAIService')
    def test_create_persona_generation_service(self, mock_service_class):
        """Test persona generation service creation."""
        from .service import create_persona_generation_service
        
        create_persona_generation_service()
        
        mock_service_class.assert_called_once()
        args = mock_service_class.call_args[0]
        assert args[0] == 'persona_generation'
        assert args[1] == PersonaDetails
    
    @patch('utils.ai_integration.service.MultiProviderAIService')
    def test_create_conversation_service_initial(self, mock_service_class):
        """Test conversation service creation for initial emails."""
        from .service import create_conversation_service
        
        create_conversation_service('initial')
        
        mock_service_class.assert_called_once()
        args = mock_service_class.call_args[0]
        assert args[0] == 'conversation_initial'
        assert args[1] == EmailContent
    
    @patch('utils.ai_integration.service.MultiProviderAIService')
    def test_create_conversation_service_analysis(self, mock_service_class):
        """Test conversation service creation for analysis."""
        from .service import create_conversation_service
        
        create_conversation_service('analysis')
        
        mock_service_class.assert_called_once()
        args = mock_service_class.call_args[0]
        assert args[0] == 'conversation_analysis'
        assert args[1] == ConversationAnalysis
    
    def test_create_conversation_service_invalid_type(self):
        """Test conversation service creation with invalid type."""
        from .service import create_conversation_service
        
        with pytest.raises(ValueError, match="Unknown conversation type"):
            create_conversation_service('invalid')