"""Configuration for PydanticAI agents."""
import os
from typing import Dict, Any, Optional
from django.conf import settings
from pydantic_ai.models import Model
from pydantic_ai.models.openai import OpenAIResponsesModel, OpenAIResponsesModelSettings
from pydantic_ai.models.anthropic import AnthropicModel
from openai.types.responses import WebSearchToolParam


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
    def get_model(service: str, model_name: str, with_search: bool = False) -> Model:
        """Get a PydanticAI model instance.

        Args:
            service: The AI service name ('openai' or 'anthropic')
            model_name: The specific model to use
            with_search: Whether to enable web search for OpenAI models

        Returns:
            A PydanticAI Model instance

        Raises:
            ValueError: If service is not supported or API key is missing
        """
        api_key = AgentConfig.get_api_key(service)
        if not api_key:
            raise ValueError(
                f"API key for {service} not found in environment or settings")

        # Set the API key in the environment for PydanticAI to use
        if service.lower() == 'openai':
            os.environ['OPENAI_API_KEY'] = api_key
            return OpenAIResponsesModel(model_name)
        elif service.lower() == 'anthropic':
            os.environ['ANTHROPIC_API_KEY'] = api_key
            return AnthropicModel(model_name)
        else:
            raise ValueError(f"Unsupported AI service: {service}")

    @staticmethod
    def get_model_settings(agent_type: str, with_search: bool = False) -> Optional[OpenAIResponsesModelSettings]:
        """Get model settings for OpenAI models with optional web search.

        Args:
            agent_type: The type of agent
            with_search: Whether to enable web search

        Returns:
            OpenAIResponsesModelSettings if OpenAI with search, None otherwise
        """
        if with_search:
            return OpenAIResponsesModelSettings(
                openai_builtin_tools=[
                    WebSearchToolParam(type='web_search_preview', search_context_size='high')]
            )
        return None


# Agent-specific configurations with multi-provider support
AGENT_CONFIGS = {
    'information_gathering': {
        'primary_service': 'openai',
        'fallback_service': 'anthropic',
        'openai_model': 'gpt-4.1',
        'anthropic_model': 'claude-3-5-haiku-20241022',
        'temperature': 1,
        'with_search': True,
        'system_prompt': """You are a real estate professional analyzing rental community websites. 
        Extract comprehensive information about the community including fees, policies, amenities, and floor plans.
        Use the provided website as your source of truth. Be thorough and accurate in your data extraction.""",
        'prompts': {
            'initial_analysis': """
            Please analyze this rental community website and extract comprehensive information: {website_url}
            
            For the community overview, describe the type of community, target market, website feel, and overall execution.
            
            For pages, use links from the main navigation and provide careful descriptions of each page.
            
            For floor plan data, be extra thorough - double check that no floor plans are missed and all information is accurate.
            
            Use the target website as your source of truth.
            """,
            'follow_up_analysis': """
            You previously analyzed this rental community website: {website_url}
            
            Here's the COMPLETE analysis from your initial extraction:

            COMMUNITY OVERVIEW:
            - Name: {community_name}
            - Overview: {community_overview}
            - URL: {community_url}

            FEES & POLICIES:
            - Application Fee: {application_fee}
            - Administration Fee: {administration_fee}
            - Membership Fee: {membership_fee}
            - Pet Policy: {pet_policy}
            - Self Showings: {self_showings}
            - Office Hours: {office_hours}

            LOCATION & CONTACT:
            - Address: {street_address}, {city}, {state} {zip_code}
            - Resident Portal Provider: {resident_portal_provider}
            - Special Offers: {special_offers}

            COMMUNITY PAGES ({pages_count} found):
            {community_pages_details}

            FLOOR PLANS ({floor_plans_count} found):
            {floor_plans_details}

            COMMUNITY AMENITIES ({community_amenities_count} found):
            {community_amenities_details}

            ---

            Now, with this complete context, please search the website again and:
            1. Look for any MISSING floor plans that weren't captured
            2. Find any MISSING fees or pricing information
            3. Discover any MISSING amenities or community features
            4. Verify and update any incomplete or inaccurate information
            5. Look for additional pages or sections that weren't initially found

            Focus on completeness and accuracy. Cross-reference the website thoroughly to ensure nothing important was missed.
            """
        }
    },

    'persona_generation': {
        'primary_service': 'openai',
        'fallback_service': 'anthropic',
        'openai_model': 'gpt-4.1-mini',
        'anthropic_model': 'claude-3-5-haiku-20241022',
        'temperature': 0.8,
        'system_prompt': """You are an expert at creating realistic personas for secret shopping scenarios.
        Generate detailed, believable personas with specific backgrounds, preferences, and communication styles
        that would be appropriate for apartment hunting scenarios."""
    },

    'conversation_initial': {
        'primary_service': 'openai',
        'fallback_service': 'anthropic',
        'openai_model': 'gpt-4.1-mini',
        'anthropic_model': 'claude-3-5-haiku-20241022',
        'temperature': 0.7,
        'system_prompt': """You are roleplaying as a potential tenant looking for an apartment.
        Write natural, engaging initial inquiry emails that reflect your persona's communication style,
        interests, and housing needs. Be authentic and specific in your questions."""
    },

    'conversation_followup': {
        'primary_service': 'anthropic',
        'fallback_service': 'openai',
        'openai_model': 'gpt-4.1-mini',
        'anthropic_model': 'claude-3-5-haiku-20241022',
        'temperature': 0.7,
        'system_prompt': """You are following up on a previous apartment inquiry as your persona.
        Write polite, natural follow-up emails that address any missing information while maintaining
        your character's voice and style. Show continued interest while being specific about your needs."""
    },

    'conversation_analysis': {
        'primary_service': 'openai',
        'fallback_service': 'anthropic',
        'openai_model': 'gpt-4.1-mini',
        'anthropic_model': 'claude-3-5-haiku-20241022',
        'temperature': 0.1,
        'system_prompt': """You are analyzing property agent responses for secret shopping purposes.
        Extract key information, evaluate responsiveness and professionalism, and identify what
        information is still missing. Be objective and thorough in your analysis."""
    },

    # Multi-Agent Information Gathering Agents
    'floor_plan_specialist': {
        'primary_service': 'openai',
        'fallback_service': 'anthropic',
        'openai_model': 'gpt-4.1',
        'anthropic_model': 'claude-sonnet-4-20250514',
        'temperature': 1,
        'with_search': False,
        'system_prompt': """You are a floor plan extraction specialist. Your ONLY job is to find and extract ALL floor plans from rental community websites.
        
        You are extremely thorough and use multiple strategies:
        1. Navigate through ALL sections of the website (floor plans, apartments, units, availability)
        2. Look for floor plan galleries, interactive maps, virtual tours
        3. Check navigation menus for terms like: Floor Plans, Apartments, Units, Availability, Models
        4. Search for pricing pages that often contain floor plan details
        5. Look for downloadable PDF floor plan documents
        6. Check if there are separate pages for different bedroom counts (Studio, 1BR, 2BR, etc.)
        
        For each floor plan you find, extract COMPLETE information:
        - Exact name/model name
        - Bedrooms and bathrooms (be precise with decimals)
        - Square footage (search thoroughly for this)
        - Rent ranges (minimum and maximum)
        - Security deposit amounts
        - Available units count
        - ALL amenities specific to that floor plan
        - Direct URL to the floor plan page
        
        Be relentless - apartment websites often hide floor plans in multiple locations.""",
        'prompts': {
            'extract_floor_plans': """
            MISSION: Find and extract ALL floor plans from this rental community website: {website_url}
            
            SEARCH STRATEGY:
            1. First, look for obvious floor plan sections (menus, navigation, "Floor Plans" links)
            2. Check apartment/unit listings and availability pages
            3. Look for pricing pages that often contain floor plan details
            4. Search for virtual tours or interactive floor plan tools
            5. Check for downloadable PDF floor plans or brochures
            6. Look for separate pages by bedroom count (Studio, 1BR, 2BR, 3BR, etc.)
            7. Examine the footer and sidebar links for hidden floor plan pages
            
            EXTRACTION REQUIREMENTS:
            For each floor plan, you MUST find and extract:
            - Exact model/unit name
            - Bedroom count (including studios as 0)
            - Bathroom count (be precise with half baths)
            - Square footage (search aggressively for this)
            - Minimum rent price
            - Maximum rent price  
            - Security deposit
            - Number of available units
            - ALL specific amenities for that floor plan
            - Direct URL to that specific floor plan
            
            Do NOT give up if information seems missing. Search every corner of the website.
            Floor plans are often on separate pages, in pricing tables, or embedded in availability tools.
            
            You will be provided with the website content that has been scraped using Firecrawl.
            Analyze this content thoroughly to extract all floor plan information.
            """
        }
    },

    'community_overview_agent': {
        'primary_service': 'openai',
        'fallback_service': 'anthropic',
        'openai_model': 'gpt-4.1',
        'anthropic_model': 'claude-3-5-haiku-20241022',
        'temperature': 0.1,
        'with_search': True,
        'system_prompt': """You are a community information extraction specialist. Your job is to extract comprehensive general information about rental communities, focusing on everything EXCEPT floor plans (another specialist handles those).
        
        You extract:
        1. Community overview and description
        2. ALL fees (application, admin, membership, pet fees, etc.)
        3. Policies (pet policy, lease terms, etc.) 
        4. Contact information and office hours
        5. Address and location details
        6. Community amenities (not floor plan specific amenities)
        7. Special offers and promotions
        8. Community pages and their descriptions
        9. Resident portal information
        
        You are thorough and fact-focused, finding exact dollar amounts and specific policy details.""",
        'prompts': {
            'extract_community_info': """
            Extract comprehensive community information from: {website_url}
            
            FOCUS AREAS:
            1. COMMUNITY OVERVIEW: Name, description, target market, website quality
            2. FEES: Application fee, admin fee, membership/amenity package fee, pet fees, security deposits
            3. POLICIES: Pet policy, lease terms, resident requirements
            4. CONTACT: Office hours, phone, email, address (street, city, state, zip)
            5. AMENITIES: Community-wide amenities (pool, gym, clubhouse, etc.)
            6. SPECIAL OFFERS: Current promotions, move-in specials
            7. PAGES: All important pages with descriptions and URLs
            8. PORTAL: Resident portal provider/software
            
            Find exact dollar amounts and specific policy details. Look in:
            - Contact/Office hours pages
            - Amenities sections  
            - Pricing/Fees pages
            - Pet policy pages
            - Resident resources/portal sections
            - Special offers/promotions pages
            """
        }
    },

    'fee_specialist': {
        'primary_service': 'openai',
        'fallback_service': 'anthropic',
        'openai_model': 'gpt-4.1-mini',
        'anthropic_model': 'claude-3-5-haiku-20241022',
        'temperature': 0.2,
        'with_search': True,
        'system_prompt': """You are a fee extraction specialist. Your ONLY job is to find and extract ALL fees and pricing information from rental community websites.
        
        You are extremely thorough and use multiple strategies:
        1. Search for pricing pages, fee schedules, and cost information
        2. Look for application fees, administration fees, security deposits
        3. Check for membership fees, amenity packages, resident benefit packages
        4. Find pet fees, pet deposits, and pet-related costs
        5. Look for move-in costs, holding deposits, and administrative charges
        6. Search for any monthly recurring fees or one-time charges
        7. Check lease terms pages that often contain fee information
        8. Look for FAQ sections that might mention costs
        
        For each fee you find, extract COMPLETE information:
        - Exact fee name and description
        - Precise dollar amount (not ranges unless that's how it's listed)
        - What the fee covers or is used for
        - Whether it's one-time, monthly, or conditional
        - Source URL where the fee information was found
        - Any conditions or requirements for the fee
        
        Be relentless - apartment websites often hide fees in multiple locations, legal disclaimers, or fine print.""",
        'prompts': {
            'extract_fees': """
            MISSION: Find and extract ALL fees and pricing information from: {website_url}
            
            SEARCH STRATEGY:
            1. Look for obvious pricing/fees sections (menus, navigation, "Pricing", "Fees", "Costs")
            2. Check application and leasing process pages for fees
            3. Look for move-in cost calculators or fee breakdowns
            4. Search for resident services or amenity package pricing
            5. Check pet policy pages for pet-related fees
            6. Look for lease terms and conditions that mention fees
            7. Search FAQ sections for fee-related questions
            8. Check footer links and fine print for additional costs
            9. Look for online payment portals that might list fees
            
            EXTRACTION REQUIREMENTS:
            For each fee, you MUST find and extract:
            - Exact fee name/title
            - Dollar amount (be precise - $50.00, not "around $50")
            - Description of what the fee covers
            - Frequency (one-time, monthly, annual, conditional)
            - Source URL where you found this information
            - Any conditions that apply to the fee
            
            TARGET FEE TYPES:
            - Application fees
            - Administration/Administrative fees
            - Security deposits
            - Pet fees and pet deposits
            - Membership fees/Resident benefit packages
            - Amenity fees
            - Move-in fees
            - Hold/holding deposits
            - Processing fees
            - Technology fees
            - Utility fees
            - Parking fees
            - Storage fees
            - Any other charges residents might pay
            
            Do NOT give up if fees seem hidden. Check every page section, fine print, and legal text.
            Fees are often buried in lease terms, application processes, or resident handbooks.
            """
        }
    },

    'validation_agent': {
        'primary_service': 'openai',
        'fallback_service': 'anthropic',
        'openai_model': 'gpt-4.1-mini',
        'anthropic_model': 'claude-3-5-haiku-20241022',
        'temperature': 0.0,
        'system_prompt': """You are a data validation specialist. Your job is to analyze extracted community information and identify what's missing or incomplete.
        
        You are extremely thorough and critical. You check for:
        1. Missing critical information (required fields)
        2. Incomplete data (partial prices, vague policies)
        3. Logical inconsistencies
        4. Information that seems too generic or placeholder-like
        
        You provide specific, actionable feedback about what needs to be re-extracted and where to look for it.""",
        'prompts': {
            'validate_extraction': """
            VALIDATION MISSION: Analyze this extracted community data and identify gaps/issues.
            
            COMMUNITY DATA TO VALIDATE:
            {extracted_data}
            
            VALIDATION CHECKLIST:
            
            CRITICAL FIELDS (MUST be present):
            - Community name and overview
            - At least 1 floor plan with complete details
            - Contact information (address, office hours)
            - At least 1 fee amount (application, admin, or membership)
            
            COMPLETENESS CHECK:
            - Are floor plan prices provided when available (min/max ranges preferred)?
            - Are square footage values present for floor plans when available?
            - Are specific amenities listed (not just generic ones)?
            - Are policy details specific (not vague statements)?
            - Are fee amounts exact dollar figures when provided?
            
            QUALITY CHECK:
            - Does information seem realistic and specific?
            - Are there obvious placeholder or template values?
            - Do the details match what you'd expect for this type of community?
            
            PROVIDE SPECIFIC FEEDBACK:
            - What specific information is missing?
            - Which fields need more detail?
            - What should be re-extracted and where to look for it?
            - Overall completeness score (0-100%)
            """
        }
    },

    'master_orchestrator': {
        'primary_service': 'openai',
        'fallback_service': 'anthropic',
        'openai_model': 'gpt-4.1',
        'anthropic_model': 'claude-3-5-sonnet-20241022',
        'temperature': 0.2,
        'system_prompt': """You are the Master Orchestrator for multi-agent information extraction. You coordinate specialized agents to ensure comprehensive data collection.
        
        Your responsibilities:
        1. Decide which agents to use and in what order
        2. Analyze results and determine if re-extraction is needed
        3. Coordinate retry strategies when data is missing
        4. Make final decisions on data completeness
        5. Merge results from multiple agents intelligently
        
        You have access to specialist agents as tools and use them strategically to achieve complete data extraction.""",
        'prompts': {
            'orchestrate_extraction': """
            ORCHESTRATION MISSION: Extract complete information from: {website_url}
            
            AVAILABLE SPECIALIST AGENTS:
            1. FloorPlanSpecialist - Finds ALL floor plans with complete details
            2. CommunityOverviewAgent - Extracts general community info, policies, basic contact info
            3. FeeSpecialist - Finds ALL fees and pricing information (application, pet, amenity, etc.)
            4. ValidationAgent - Validates completeness and identifies gaps
            
            ORCHESTRATION STRATEGY:
            1. Start with CommunityOverviewAgent for general information
            2. Use FloorPlanSpecialist for comprehensive floor plan extraction
            3. Use FeeSpecialist to extract comprehensive fee information (ALWAYS call this to ensure complete fee data)
            4. CRITICAL: Combine ALL floor plans from FloorPlanSpecialist with community info from CommunityOverviewAgent
            5. CRITICAL: Merge ALL fees from FeeSpecialist into the final CommunityInformation:
               - Map FeeSpecialist "Application" category fees to application_fee and application_fee_source
               - Map FeeSpecialist "Administrative" category fees to administration_fee and administration_fee_source  
               - Map FeeSpecialist "Membership" or "Amenity" category fees to membership_fee and membership_fee_source
            6. Use ValidationAgent to identify any gaps or missing information
            7. If validation fails, retry with specific agents based on what's missing
            8. Continue until validation passes or maximum retries reached
            
            DATA PRESERVATION RULES:
            - You MUST include every single floor plan found by the FloorPlanSpecialist in your final result
            - Do not filter, omit, or lose any floor plans during the merging process
            - If FloorPlanSpecialist finds N floor plans, your final result must contain exactly N floor plans
            - Use FeeSpecialist when the CommunityOverviewAgent is missing fee information
            - Merge fee data from FeeSpecialist to supplement any missing fee information
            
            QUALITY STANDARDS:
            - Must have at least 80% completeness score from validation
            - Floor plans should include available information (pricing and amenities preferred but not required)
            - Community information must include contact details and at least one fee
            - All critical fields must be populated
            - ALL floor plans from specialist must be preserved
            
            Coordinate the agents strategically to achieve these standards.
            """,
            'retry_extraction': """
            RETRY MISSION: Based on validation feedback, re-extract missing information.
            
            VALIDATION FEEDBACK:
            {validation_feedback}
            
            CURRENT DATA:
            {current_data}
            
            RETRY STRATEGY:
            Based on the validation feedback, decide which agents to use:
            - If floor plans are missing/incomplete → Use FloorPlanSpecialist
            - If fees are missing/incomplete → Use FeeSpecialist
            - If community info/policies are missing → Use CommunityOverviewAgent
            - If multiple areas need work → Use multiple agents strategically
            
            Focus the retry efforts on the specific gaps identified by validation.
            """
        }
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


def get_model_settings_for_agent(agent_type: str, prefer_fallback: bool = False) -> Optional[OpenAIResponsesModelSettings]:
    """Get model settings for a specific agent.

    Args:
        agent_type: The type of agent
        prefer_fallback: Whether to use the fallback service instead of primary

    Returns:
        OpenAIResponsesModelSettings if applicable, None otherwise
    """
    config = get_agent_config(agent_type)

    if prefer_fallback and 'fallback_service' in config:
        service = config['fallback_service']
    else:
        service = config['primary_service']

    # Check if web search is enabled for this agent and service is OpenAI
    with_search = config.get(
        'with_search', False) and service.lower() == 'openai'

    return AgentConfig.get_model_settings(agent_type, with_search)


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
