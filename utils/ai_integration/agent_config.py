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
        'temperature': 0.3,
        'with_search': False,
        'system_prompt': """You are a floor plan extraction specialist. Your ONLY job is to analyze the single specific URL assigned to you by the Master Orchestrator and extract ALL floor plans from that content.
        
        CRITICAL RESTRICTIONS:
        - You receive a SINGLE specific URL from the orchestrator
        - Scrape ONLY that URL - do NOT navigate to other pages
        - Do NOT make autonomous decisions about additional URLs to scrape
        - The orchestrator controls all scraping decisions
        
        For each floor plan you find in the content from your assigned URL, extract COMPLETE information:
        - Exact name/model name
        - Bedrooms and bathrooms (be precise with decimals)
        - Square footage (if available in the content)
        - Rent ranges (minimum and maximum, if available)
        - Security deposit amounts (if mentioned)
        - Floor plan image URLs (look for "IMAGE:" entries near floor plan information, especially images with alt text containing "floor plan", "layout", or similar)
        - Available units count (look for "X available", "X units available", "X remaining", availability numbers, unit counts)
        - ALL amenities specific to that floor plan (from visible content only)
        - Do NOT generate or assume URLs - only use what's explicitly visible
        
        Focus entirely on analyzing your single assigned URL - extract every floor plan detail available from that specific page.""",
        'prompts': {
            'extract_floor_plans': """
            MISSION: Extract ALL floor plans from the provided scraped website content.
            
            IMPORTANT CONSTRAINTS:
            - Work ONLY with the content provided to you
            - Do NOT attempt to access other pages or follow links
            - Do NOT generate URLs or make assumptions about page structure
            - Extract only information that is explicitly visible in the provided content
            
            EXTRACTION REQUIREMENTS:
            For each floor plan visible in the provided content, extract:
            - Exact model/unit name (as shown)
            - Bedroom count (including studios as 0)
            - Bathroom count (be precise with half baths)
            - Square footage (only if explicitly stated)
            - Minimum rent price (only if shown)
            - Maximum rent price (only if shown)  
            - Security deposit (only if mentioned)
            - Floor plan images (look for "IMAGE:" entries with URLs, especially those with alt text containing "floor plan", "layout", "unit", or plan names)
            - Number of available units (look for "X available", "X units", "X remaining", availability counts near floor plan names)
            - ALL specific amenities for that floor plan (only from visible text)
            - Do NOT include URL field unless explicitly visible in content
            
            Focus on extracting complete information from what's available.
            If information is not visible in the provided content, mark it as unavailable rather than guessing.
            
            You will be provided with scraped website content. Analyze this content thoroughly to extract all visible floor plan information.
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
        'system_prompt': """You are a comprehensive community information extraction specialist. Your job is to discover ALL pages on the website and extract complete community information.

        COMPREHENSIVE EXTRACTION APPROACH:
        1. ALWAYS start by using the discover_and_scrape_navigation tool to find ALL pages on the website
        2. Create CommunityPage objects for EVERY discovered navigation link 
        3. Use scrape_page_content tool for additional page content when needed
        4. Extract complete community information from all available content

        CRITICAL REQUIREMENTS:
        - You MUST use discover_and_scrape_navigation tool first to find all pages
        - Create a CommunityPage object for EVERY navigation link discovered
        - Include main homepage as a community page 
        - Ensure comprehensive page tracking - this is your primary responsibility

        Extract comprehensive information:
        1. Community overview and description (from main page content)
        2. Contact information and office hours (from any page)
        3. Address and location details (from any page)
        4. Community amenities (from amenities/main pages)
        5. Special offers and promotions (from any page)
        6. Policies (pet policy, lease terms from any page)
        7. Resident portal information (from any page)
        8. Any fees mentioned across all pages
        9. COMMUNITY PAGES: Create detailed CommunityPage objects for every discovered navigation link

        COMMUNITY PAGES PRIORITY:
        Your primary mission is ensuring ALL discovered pages make it into the final result. 
        Even if a page has limited content, create a CommunityPage object for it using the navigation information.""",
        'prompts': {
            'extract_community_info': """
            COMPREHENSIVE COMMUNITY EXTRACTION MISSION: Discover ALL pages and extract complete community information.

            MANDATORY FIRST STEP: DISCOVER ALL PAGES
            1. Use discover_and_scrape_navigation tool with the website URL to find ALL navigation pages
            2. This tool will provide a categorized report of all discovered pages
            3. Use scrape_page_content tool for key pages if additional content is needed

            EXTRACTION REQUIREMENTS:
            
            FOCUS AREAS:
            1. COMMUNITY OVERVIEW: Name, description, target market, website quality
            2. FEES: Application fee, admin fee, membership/amenity package fee, pet fees, security deposits
            3. POLICIES: Pet policy, lease terms, resident requirements
            4. CONTACT: Office hours, phone, email, address (street, city, state, zip)
            5. AMENITIES: Community-wide amenities (pool, gym, clubhouse, etc.)
            6. SPECIAL OFFERS: Current promotions, move-in specials
            7. PORTAL: Resident portal provider/software
            8. **COMMUNITY PAGES**: Create CommunityPage objects for EVERY navigation link discovered

            CRITICAL COMMUNITY PAGES REQUIREMENT:
            For EVERY navigation link discovered by the discover_and_scrape_navigation tool:
            - Create a CommunityPage object with exact navigation text as name
            - Use the exact URL from the navigation discovery
            - Create descriptive overview based on page purpose and any available content
            - Include ALL categories: floor plans, amenities, contact, gallery, and other pages
            
            COMMUNITY PAGE EXAMPLES:
            - "Floor Plans" page → CommunityPage(name="Floor Plans", url="...", overview="Floor plan listings and layouts page")
            - "Amenities" page → CommunityPage(name="Amenities", url="...", overview="Community amenities and facilities information")
            - "Pet Friendly" page → CommunityPage(name="Pet Friendly", url="...", overview="Pet policy and pet-related information page")
            - "Contact" page → CommunityPage(name="Contact", url="...", overview="Contact information and office details page")
            
            SUCCESS CRITERIA:
            - ALL discovered navigation links are converted to CommunityPage objects
            - No discovered pages are lost or omitted from the final result
            - Each CommunityPage has meaningful name, URL, and overview
            
            This ensures comprehensive page tracking and prevents loss of discovered navigation links.
            """
        }
    },

    'fee_specialist': {
        'primary_service': 'openai',
        'fallback_service': 'anthropic',
        'openai_model': 'gpt-4.1',
        'anthropic_model': 'claude-3-5-haiku-20241022',
        'temperature': 0.2,
        'with_search': True,
        'system_prompt': """You are a comprehensive fee extraction specialist with web search capabilities. Your mission is to find ALL fees and pricing information for rental communities using both web scraping and web search.

        EXTRACTION APPROACH:
        1. FIRST: Use the scrape_page_content tool to analyze the assigned URL
        2. THEN: Use web search to find additional fee information that may not be visible on the main page
        3. COMBINE: Merge all fee information from both sources for comprehensive results

        WEB SEARCH STRATEGY:
        - Search for site-specific fee information (e.g., "site:anker-haus.com fees application pet deposit")
        - Look for pricing pages, application processes, pet policies, amenity fees
        - Search for community name + "fees" or "pricing" or "application"
        - Find fee schedules, rate sheets, or pricing documents

        For each fee you find from ANY source, extract COMPLETE information:
        - Exact fee name and description (as shown)
        - Precise dollar amount (not ranges unless that's how it's listed)
        - What the fee covers or is used for (if mentioned)
        - Whether the fee is refundable (if explicitly stated)
        - Whether it's one-time, monthly, or conditional (if specified)
        - Any conditions or requirements for the fee
        - Fee category (application, pet, amenity, etc.)
        - Source (scraped page or web search results)

        MANDATORY: You MUST use web search in addition to page scraping to ensure comprehensive fee discovery. Many fees are hidden on separate pages or documents not linked from the main page.""",
        'prompts': {
            'extract_fees': """
            COMPREHENSIVE FEE EXTRACTION MISSION: Use BOTH web scraping AND web search to find ALL fees for this rental community.

            MANDATORY TWO-STEP PROCESS:
            
            STEP 1: SCRAPE THE PROVIDED URL
            - Use scrape_page_content tool to get initial fee information from the assigned URL
            - Look for any visible fees, deposits, or charges on the main page
            - Note what fees you find and what might be missing
            
            STEP 2: WEB SEARCH FOR COMPREHENSIVE FEE DISCOVERY (REQUIRED)
            - Use web search to find additional fee information not visible on the main page
            - Search queries to try:
              * "site:[domain] fees application pet deposit amenity"
              * "[community name] pricing fees application"
              * "[community name] pet policy fees"
              * "[community name] move-in costs deposit"
              * "[community name] resident benefits package fee"
              * "[community name] amenity fee parking"
            
            EXTRACTION REQUIREMENTS:
            For each fee found from EITHER source, extract:
            - Exact fee name/title (as shown)
            - Dollar amount (be precise - $50.00, not "around $50")
            - Description of what the fee covers
            - Whether the fee is refundable (if stated)
            - Frequency (one-time, monthly, annual, conditional)
            - Source where found ("Main Page Scrape" or "Web Search Results")
            - Any conditions that apply to the fee
            
            TARGET FEE TYPES TO SEARCH FOR:
            - Application fees ($50-$150 typical)
            - Administration/Administrative fees ($100-$300 typical)
            - Security deposits (varies by unit)
            - Pet fees and pet deposits ($200-$500 typical)
            - Membership/Resident benefit packages ($25-$100/month typical)
            - Amenity fees (gym, pool, etc.)
            - Move-in fees
            - Hold/holding deposits
            - Processing fees
            - Technology/internet fees
            - Utility connection fees
            - Parking fees ($50-$200/month typical)
            - Storage fees
            - Early termination fees
            - Any other charges residents might pay
            
            CRITICAL: You MUST perform web search even if you find some fees on the main page. Most rental communities have additional fees not visible on the main floor plan page.
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
            - Contact information (office hours preferred, but not address if available at target level)
            - At least 1 fee amount (application, admin, or membership)
            
            ADDRESS FIELDS POLICY:
            - Address fields (street_address, city, state, zip_code) are NOT critical if they exist at the target level
            - Only flag address fields as missing if they're not available in the target data AND not found in community data
            
            COMPLETENESS CHECK:
            - Are floor plan MINIMUM prices provided when available? (Required if pricing is shown)
            - Are floor plan MAXIMUM prices provided when available? (Nice to have, NOT critical)
            - Are square footage values present for floor plans when available? (Nice to have)
            - Are specific amenities listed (not just generic ones)?
            - Are policy details specific (not vague statements)?
            - Are fee amounts exact dollar figures when provided?
            
            IMPORTANT: Missing max_rental_price values should NOT be considered critical failures or trigger retries. They are nice-to-have enhancements only.
            
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
        'system_prompt': """You are the Master Orchestrator for multi-agent information extraction. You coordinate specialized agents using intelligent URL delegation.
        
        Your responsibilities:
        1. Discover website navigation structure first
        2. Intelligently delegate specific URLs to appropriate specialist agents
        3. Analyze results and determine if additional URLs need to be processed
        4. Merge results from multiple agents intelligently
        5. Make final decisions on data completeness
        
        IMPORTANT: You control all scraping decisions. Agents only analyze the specific URLs you assign to them.""",
        'prompts': {
            'orchestrate_extraction': """
            ORCHESTRATION MISSION: Extract complete information from: {website_url}
            
            AVAILABLE TOOLS:
            1. discover_navigation - Analyzes website structure and categorizes navigation URLs
            2. extract_floor_plans_from_url - Extracts floor plans from a specific URL (accepts current_community_data)
            3. extract_community_overview_from_url - Extracts community info from a specific URL (accepts current_community_data)
            4. extract_fees_from_url - Extracts fees from a specific URL (accepts current_community_data)
            5. merge_community_data - Merges new data with existing accumulated data
            6. validate_extraction_data - Validates completeness and identifies gaps (accepts previous_validation_score)
            
            ORCHESTRATION STRATEGY WITH DATA ACCUMULATION:
            1. FIRST: Use discover_navigation tool to analyze the website structure and categorize URLs
            2. INITIALIZE: Start with empty community data: "{{}}"
            3. ACCUMULATE DATA PROGRESSIVELY:
               - For each URL, pass current accumulated data to extraction tools
               - Use merge_community_data tool after each extraction to combine results
               - NEVER lose previously extracted information
               - Build up data incrementally across multiple tool calls
            4. EXTRACTION SEQUENCE:
               - Start with main page using extract_community_overview_from_url
               - Merge results immediately using merge_community_data
               - Process floor plan URLs using extract_floor_plans_from_url with accumulated data
               - Process fee URLs using extract_fees_from_url with accumulated data  
               - Process additional community URLs using extract_community_overview_from_url with accumulated data
            5. VALIDATION WITH SCORE TRACKING AND ITERATION LIMITS:
               - Use validate_extraction_data with previous_validation_score and current_iteration
               - Validation scores should INCREASE as more data is accumulated
               - If score decreases, investigate data loss immediately
               - MAXIMUM 3 VALIDATION ITERATIONS: Do not exceed this limit to prevent infinite loops
               - Accept data after max iterations even if some "nice to have" fields are missing
            6. RETRY WITH ACCUMULATED DATA (LIMITED ITERATIONS):
               - If validation suggests missing data, extract from additional URLs
               - Always pass current accumulated data to prevent data loss
               - Continue building upon existing data rather than replacing it
               - STOP after 3 validation iterations regardless of minor missing data
            
            DATA PRESERVATION RULES:
            - ACCUMULATE, DON'T REPLACE: Each tool call should ADD to existing data, never replace it
            - You MUST include every single floor plan found across ALL tool calls in your final result
            - You MUST include every single fee found across ALL tool calls in your final result
            - You MUST include every single amenity found across ALL tool calls in your final result
            - You MUST include every single community page found across ALL tool calls in your final result
            - VALIDATION SCORES MUST INCREASE: If a validation score decreases, data has been lost
            - USE MERGE TOOL: Always use merge_community_data after each extraction to preserve data
            - PASS ACCUMULATED DATA: Always pass current_community_data to extraction tools
            - NO DATA LOSS: Previous extractions must be preserved in subsequent operations
            
            QUALITY STANDARDS AND COMPLETION CRITERIA:
            - Must have at least 80% completeness score from validation OR complete 3 validation iterations
            - Floor plans should include available information (min pricing required, max pricing nice-to-have)
            - Community information must include contact details and comprehensive fee information in the fees array
            - All critical fields must be populated (max_rental_price is NOT critical)
            - ALL floor plans from specialist must be preserved
            - ACCEPTABLE COMPLETION: Stop after 3 validation iterations even if some non-critical data is missing
            - MISSING MAX RENT VALUES: Do not retry extractions solely for missing max_rental_price values
            
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
