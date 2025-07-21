"""PydanticAI agents for secret shopping tasks."""
import logging
from typing import Dict, Any, List, Optional
from pydantic_ai import Agent
from pydantic_ai.models import Model

from .schemas import (
    CommunityInformation,
    PersonaDetails,
    ConversationAnalysis,
    EmailContent
)
from .agent_config import get_agent_config, get_model_for_agent

logger = logging.getLogger(__name__)


class InformationGatheringAgent:
    """Agent for gathering information from real estate websites."""
    
    def __init__(self):
        """Initialize the information gathering agent."""
        self.config = get_agent_config('information_gathering')
        self.model = get_model_for_agent('information_gathering')
        
        # Create the PydanticAI agent
        self.agent = Agent(
            model=self.model,
            result_type=CommunityInformation,
            system_prompt=self.config['system_prompt']
        )
    
    async def extract_community_info(self, website_url: str) -> CommunityInformation:
        """Extract community information from a website.
        
        Args:
            website_url: The URL of the community website to analyze
            
        Returns:
            CommunityInformation object with extracted data
            
        Raises:
            Exception: If the analysis fails
        """
        try:
            prompt = f"""
            Please analyze this rental community website and extract comprehensive information: {website_url}
            
            For the community overview, describe the type of community, target market, website feel, and overall execution.
            
            For pages, use links from the main navigation and provide careful descriptions of each page.
            
            For floor plan data, be extra thorough - double check that no floor plans are missed and all information is accurate.
            
            Use the target website as your source of truth.
            """
            
            result = await self.agent.run(prompt)
            logger.info(f"Successfully extracted community info for {website_url}")
            return result.data
            
        except Exception as e:
            logger.error(f"Failed to extract community info for {website_url}: {str(e)}")
            raise
    
    async def gather_additional_info(self, website_url: str, initial_result: CommunityInformation) -> CommunityInformation:
        """Perform a follow-up pass to gather any missing information.
        
        Args:
            website_url: The website URL
            initial_result: The initial extraction result
            
        Returns:
            Updated CommunityInformation with additional data
        """
        try:
            prompt = f"""
            You previously analyzed this rental community website: {website_url}
            
            Here's what you found in your initial analysis:
            - Community: {initial_result.name}
            - Floor plans found: {len(initial_result.floor_plans)}
            - Pages found: {len(initial_result.community_pages)}
            
            Please search again and add any floor plans or fees that you missed in the initial pass.
            Focus on completeness and accuracy. Double-check all pricing information and floor plan details.
            """
            
            result = await self.agent.run(prompt)
            logger.info(f"Successfully completed follow-up analysis for {website_url}")
            return result.data
            
        except Exception as e:
            logger.error(f"Failed to complete follow-up analysis for {website_url}: {str(e)}")
            raise


class PersonaGenerationAgent:
    """Agent for generating realistic personas for secret shopping."""
    
    def __init__(self):
        """Initialize the persona generation agent."""
        self.config = get_agent_config('persona_generation')
        self.model = get_model_for_agent('persona_generation')
        
        self.agent = Agent(
            model=self.model,
            result_type=PersonaDetails,
            system_prompt=self.config['system_prompt']
        )
    
    async def generate_persona(self, 
                             target_demographics: Optional[str] = None,
                             budget_range: Optional[str] = None,
                             special_requirements: Optional[List[str]] = None) -> PersonaDetails:
        """Generate a realistic persona for secret shopping.
        
        Args:
            target_demographics: Optional demographics to target
            budget_range: Optional budget constraints
            special_requirements: Optional list of special requirements
            
        Returns:
            PersonaDetails object with generated persona
        """
        try:
            prompt = f"""
            Generate a realistic persona for apartment hunting secret shopping.
            
            The persona should be believable and detailed, including:
            - Personal background and occupation
            - Communication style and preferences
            - Housing priorities and requirements
            - Timeline and budget considerations
            - Specific questions they would ask
            
            {"Target demographics: " + target_demographics if target_demographics else ""}
            {"Budget range: " + budget_range if budget_range else ""}
            {"Special requirements: " + ", ".join(special_requirements) if special_requirements else ""}
            
            Make the persona authentic and varied to avoid detection as a secret shopper.
            """
            
            result = await self.agent.run(prompt)
            logger.info("Successfully generated persona")
            return result.data
            
        except Exception as e:
            logger.error(f"Failed to generate persona: {str(e)}")
            raise


class ConversationAgent:
    """Agent for managing email conversations and analysis."""
    
    def __init__(self, agent_type: str):
        """Initialize the conversation agent.
        
        Args:
            agent_type: Type of conversation agent ('conversation_initial', 'conversation_followup', 'conversation_analysis')
        """
        self.agent_type = agent_type
        self.config = get_agent_config(agent_type)
        self.model = get_model_for_agent(agent_type)
        
        # Set result type based on agent type
        result_type = EmailContent if agent_type in ['conversation_initial', 'conversation_followup'] else ConversationAnalysis
        
        self.agent = Agent(
            model=self.model,
            result_type=result_type,
            system_prompt=self.config['system_prompt']
        )
    
    async def generate_initial_inquiry(self, 
                                     persona: PersonaDetails,
                                     community_info: CommunityInformation) -> EmailContent:
        """Generate an initial inquiry email.
        
        Args:
            persona: The persona making the inquiry
            community_info: Information about the community
            
        Returns:
            EmailContent with the generated email
        """
        if self.agent_type != 'conversation_initial':
            raise ValueError("This agent is not configured for initial inquiries")
        
        try:
            prompt = f"""
            You are {persona.name}, a {persona.age} year old {persona.occupation} looking for a new place to live.
            
            Write an initial inquiry email about this community:
            Community: {community_info.name}
            Website: {community_info.url}
            
            Your persona details:
            - Age: {persona.age}
            - Occupation: {persona.occupation}
            - Timeline: {persona.timeline}
            - Key question: {persona.key_question}
            - Interest point: {persona.interest_point}
            - Communication style: {persona.communication_style}
            - Budget range: {persona.budget_range}
            - Background: {persona.background_story}
            
            Your priorities: {', '.join(persona.priorities)}
            
            Your email should:
            1. Express interest in the property
            2. Ask about availability for viewing
            3. Inquire about your key question: {persona.key_question}
            4. Mention your timeline: {persona.timeline}
            5. Request more information about {persona.interest_point}
            
            Sign as {persona.name} and include contact: {persona.email} and {persona.phone}
            """
            
            result = await self.agent.run(prompt)
            logger.info(f"Generated initial inquiry for persona {persona.name}")
            return result.data
            
        except Exception as e:
            logger.error(f"Failed to generate initial inquiry: {str(e)}")
            raise
    
    async def generate_followup(self,
                              persona: PersonaDetails,
                              previous_conversation: List[Dict[str, str]],
                              missing_info: List[str]) -> EmailContent:
        """Generate a follow-up email.
        
        Args:
            persona: The persona making the inquiry
            previous_conversation: History of the conversation
            missing_info: Information still needed
            
        Returns:
            EmailContent with the generated follow-up email
        """
        if self.agent_type != 'conversation_followup':
            raise ValueError("This agent is not configured for follow-ups")
        
        try:
            conversation_str = ""
            for message in previous_conversation:
                sender = message.get("sender", "Unknown")
                content = message.get("content", "")
                conversation_str += f"{sender}: {content}\n\n"
            
            missing_info_str = "\n".join([f"- {info}" for info in missing_info])
            
            prompt = f"""
            You are {persona.name} following up on a property inquiry.
            
            Previous conversation:
            {conversation_str}
            
            You still need to find out about:
            {missing_info_str}
            
            Write a polite follow-up email that:
            1. Thanks the agent for their previous response
            2. Asks specifically about the missing information
            3. Reiterates your interest in the property
            4. Maintains your communication style: {persona.communication_style}
            
            Sign as {persona.name}.
            """
            
            result = await self.agent.run(prompt)
            logger.info(f"Generated follow-up for persona {persona.name}")
            return result.data
            
        except Exception as e:
            logger.error(f"Failed to generate follow-up: {str(e)}")
            raise
    
    async def analyze_response(self,
                             community_info: CommunityInformation,
                             agent_message: str,
                             data_points: List[str]) -> ConversationAnalysis:
        """Analyze an agent's response.
        
        Args:
            community_info: Information about the property
            agent_message: The agent's response message
            data_points: Key data points to extract
            
        Returns:
            ConversationAnalysis with the analysis results
        """
        if self.agent_type != 'conversation_analysis':
            raise ValueError("This agent is not configured for analysis")
        
        try:
            data_points_str = "\n".join([f"- {point}" for point in data_points])
            
            prompt = f"""
            Analyze this property agent's response to extract key information.
            
            Property details:
            Name: {community_info.name}
            URL: {community_info.url}
            
            Agent's message:
            {agent_message}
            
            Extract these data points:
            {data_points_str}
            
            For each data point:
            1. Provide exact information if found
            2. Mark as "Not provided" if not found
            3. Note any vague or misleading statements
            
            Evaluate:
            - Agent responsiveness (1-5 scale)
            - Question coverage (1-5 scale)  
            - Professionalism (1-5 scale)
            - Overall helpfulness (1-5 scale)
            
            Identify missing information and whether follow-up is needed.
            """
            
            result = await self.agent.run(prompt)
            logger.info("Successfully analyzed agent response")
            return result.data
            
        except Exception as e:
            logger.error(f"Failed to analyze response: {str(e)}")
            raise