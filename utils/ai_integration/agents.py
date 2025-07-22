"""PydanticAI agents for secret shopping tasks."""
import logging
import time
from typing import Dict, List, Optional
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio

from .schemas import (
    CommunityInformation,
    PersonaDetails,
    ConversationAnalysis,
    EmailContent,
    FloorPlanExtractionResult,
    CommunityOverviewExtractionResult,
    FeeExtractionResult,
    ValidationReport,
    OrchestrationResult
)
from .agent_config import get_agent_config, get_model_for_agent, get_model_settings_for_agent

logger = logging.getLogger(__name__)


class InformationGatheringAgent:
    """Agent for gathering information from real estate websites."""

    def __init__(self):
        """Initialize the information gathering agent."""
        self.config = get_agent_config('information_gathering')
        self.model = get_model_for_agent('information_gathering')
        self.model_settings = get_model_settings_for_agent(
            'information_gathering')

        # Create the PydanticAI agent
        self.agent = Agent(
            model=self.model,
            result_type=CommunityInformation,
            system_prompt=self.config['system_prompt'],
            model_settings=self.model_settings
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
            prompt = self.config['prompts']['initial_analysis'].format(
                website_url=website_url
            )

            result = await self.agent.run(prompt)
            logger.info(
                f"Successfully extracted community info for {website_url}")
            return result.data

        except Exception as e:
            logger.error(f"Failed to extract community info for {
                         website_url}: {str(e)}")
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
            # Format community pages details
            community_pages_details = []
            for page in initial_result.community_pages:
                community_pages_details.append(
                    f"  • {page.name}: {page.overview} ({page.url})"
                )

            # Format floor plans details
            floor_plans_details = []
            for fp in initial_result.floor_plans:
                amenities = [a.amenity for a in fp.floor_plan_amenities]
                floor_plans_details.append(
                    f"  • {fp.name}: {
                        fp.beds}BR/{fp.baths}BA, {fp.sqft or 'N/A'} sqft, "
                    f"${fp.min_rental_price or 'N/A'}-${fp.max_rental_price or 'N/A'}, "
                    f"Deposit: ${
                        fp.security_deposit or 'N/A'}, Type: {fp.type}, "
                    f"Amenities: {
                        ', '.join(amenities) if amenities else 'None listed'} ({fp.url})"
                )

            # Format community amenities details
            community_amenities_details = []
            for amenity in initial_result.community_amenities:
                community_amenities_details.append(f"  • {amenity.amenity}")

            prompt = self.config['prompts']['follow_up_analysis'].format(
                website_url=website_url,
                community_name=initial_result.name or 'Not found',
                community_overview=initial_result.overview or 'Not found',
                community_url=initial_result.url or 'Not found',
                application_fee=initial_result.application_fee or 'Not found',
                administration_fee=initial_result.administration_fee or 'Not found',
                membership_fee=initial_result.membership_fee or 'Not found',
                pet_policy=initial_result.pet_policy or 'Not found',
                self_showings=initial_result.self_showings or 'Not found',
                office_hours=initial_result.office_hours or 'Not found',
                street_address=initial_result.street_address or 'Not found',
                city=initial_result.city or 'Not found',
                state=initial_result.state or 'Not found',
                zip_code=initial_result.zip_code or 'Not found',
                resident_portal_provider=initial_result.resident_portal_software_provider or 'Not found',
                special_offers=initial_result.special_offers or 'Not found',
                pages_count=len(initial_result.community_pages),
                community_pages_details='\n'.join(
                    community_pages_details) if community_pages_details else '  No pages found',
                floor_plans_count=len(initial_result.floor_plans),
                floor_plans_details='\n'.join(
                    floor_plans_details) if floor_plans_details else '  No floor plans found',
                community_amenities_count=len(
                    initial_result.community_amenities),
                community_amenities_details='\n'.join(
                    community_amenities_details) if community_amenities_details else '  No amenities found'
            )

            result = await self.agent.run(prompt)
            logger.info(
                f"Successfully completed follow-up analysis for {website_url}")
            return result.data

        except Exception as e:
            logger.error(
                f"Failed to complete follow-up analysis for {website_url}: {str(e)}")
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
            # Build conditional text for the prompt
            target_demographics_text = f"Target demographics: {
                target_demographics}" if target_demographics else ""
            budget_range_text = f"Budget range: {
                budget_range}" if budget_range else ""
            special_requirements_text = f"Special requirements: {
                ', '.join(special_requirements)}" if special_requirements else ""

            prompt = self.config['prompts']['generate_persona'].format(
                target_demographics_text=target_demographics_text,
                budget_range_text=budget_range_text,
                special_requirements_text=special_requirements_text
            )

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
        result_type = EmailContent if agent_type in [
            'conversation_initial', 'conversation_followup'] else ConversationAnalysis

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
            raise ValueError(
                "This agent is not configured for initial inquiries")

        try:
            prompt = self.config['prompts']['generate_initial_inquiry'].format(
                persona_name=persona.name,
                persona_age=persona.age,
                persona_occupation=persona.occupation,
                community_name=community_info.name,
                community_url=community_info.url,
                persona_timeline=persona.timeline,
                persona_key_question=persona.key_question,
                persona_interest_point=persona.interest_point,
                persona_communication_style=persona.communication_style,
                persona_budget_range=persona.budget_range,
                persona_background_story=persona.background_story,
                persona_priorities=', '.join(persona.priorities),
                persona_email=persona.email,
                persona_phone=persona.phone
            )

            result = await self.agent.run(prompt)
            logger.info(f"Generated initial inquiry for persona {
                        persona.name}")
            # Type assertion for mypy - PydanticAI result.data should match result_type
            return result.data  # type: ignore

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

            missing_info_str = "\n".join(
                [f"- {info}" for info in missing_info])

            prompt = self.config['prompts']['generate_followup'].format(
                persona_name=persona.name,
                conversation_history=conversation_str,
                missing_info=missing_info_str,
                persona_communication_style=persona.communication_style
            )

            result = await self.agent.run(prompt)
            logger.info(f"Generated follow-up for persona {persona.name}")
            return result.data  # type: ignore

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
            data_points_str = "\n".join(
                [f"- {point}" for point in data_points])

            prompt = self.config['prompts']['analyze_response'].format(
                community_name=community_info.name,
                community_url=community_info.url,
                agent_message=agent_message,
                data_points=data_points_str
            )

            result = await self.agent.run(prompt)
            logger.info("Successfully analyzed agent response")
            return result.data  # type: ignore

        except Exception as e:
            logger.error(f"Failed to analyze response: {str(e)}")
            raise


class FloorPlanSpecialistAgent:
    """Agent specialized in finding and extracting floor plan information."""

    def __init__(self):
        """Initialize the floor plan specialist agent."""
        self.config = get_agent_config('floor_plan_specialist')
        self.model = get_model_for_agent('floor_plan_specialist')
        self.model_settings = get_model_settings_for_agent(
            'floor_plan_specialist')

        # Initialize Firecrawl API key
        self.firecrawl_api_key = "fc-f2f7e90a38db44f595408139874ef6bb"

        # Create the PydanticAI agent without MCP toolset
        self.agent = Agent(
            model=self.model,
            result_type=FloorPlanExtractionResult,
            system_prompt=self.config['system_prompt'],
            model_settings=self.model_settings
        )

    async def _scrape_website(self, url: str) -> str:
        """Scrape website content using Firecrawl API directly.
        
        Args:
            url: The URL to scrape
            
        Returns:
            Scraped content as text
        """
        import httpx
        import asyncio

        headers = {
            'Authorization': f'Bearer {self.firecrawl_api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'url': url,
            'formats': ['markdown', 'html'],
            'includeTags': ['a', 'div', 'section', 'h1', 'h2', 'h3', 'p', 'span', 'table'],
            'onlyMainContent': True,
            'waitFor': 5000  # Wait 5 seconds for page to load
        }

        try:
            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.post(
                    'https://api.firecrawl.dev/v1/scrape',
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success'):
                        content = data.get('data', {})
                        return content.get('markdown', content.get('html', ''))
                    else:
                        logger.error(f"Firecrawl API error: {data.get('error')}")
                        return ""
                else:
                    logger.error(f"Firecrawl API returned {response.status_code}: {response.text}")
                    return ""
                    
        except Exception as e:
            logger.error(f"Error scraping {url} with Firecrawl: {str(e)}")
            return ""

    async def extract_floor_plans(self, website_url: str) -> FloorPlanExtractionResult:
        """Extract all floor plans from a rental community website.

        Args:
            website_url: The URL of the community website to analyze

        Returns:
            FloorPlanExtractionResult with all discovered floor plans

        Raises:
            Exception: If the extraction fails
        """
        try:
            # First scrape the website content
            logger.info(f"Scraping website content for {website_url}")
            website_content = await self._scrape_website(website_url)
            
            if not website_content:
                logger.warning(f"No content scraped from {website_url}, using fallback")
                return FloorPlanExtractionResult(
                    floor_plans_found=[],
                    extraction_method="scraping_failed",
                    pages_searched=[website_url],
                    search_strategies_used=["direct_api_scrape"],
                    extraction_confidence=0.0,
                    missing_data_areas=["floor_plans"],
                    extraction_notes=f"Failed to scrape content from {website_url}"
                )

            # Create enhanced prompt with scraped content
            prompt = f"""
            Website URL: {website_url}
            
            Website Content:
            {website_content[:15000]}  # Limit content to prevent token overflow
            
            Based on the above website content, extract all floor plan information following the requirements in your system prompt.
            Look for floor plan names, bedroom/bathroom counts, square footage, pricing, and amenities.
            """

            result = await self.agent.run(prompt)
            logger.info(f"FloorPlan specialist found {len(result.data.floor_plans_found)} floor plans for {website_url}")
            return result.data

        except Exception as e:
            logger.error(f"Floor plan extraction failed for {website_url}: {str(e)}")
            # Return fallback result instead of raising
            return FloorPlanExtractionResult(
                floor_plans_found=[],
                extraction_method="extraction_error",
                pages_searched=[website_url],
                search_strategies_used=["direct_api_scrape"],
                extraction_confidence=0.0,
                missing_data_areas=["floor_plans"],
                extraction_notes=f"Extraction failed: {str(e)}"
            )


class CommunityOverviewAgent:
    """Agent specialized in extracting general community information (excluding floor plans)."""

    def __init__(self):
        """Initialize the community overview agent."""
        self.config = get_agent_config('community_overview_agent')
        self.model = get_model_for_agent('community_overview_agent')
        self.model_settings = get_model_settings_for_agent(
            'community_overview_agent')

        # Create the PydanticAI agent
        self.agent = Agent(
            model=self.model,
            result_type=CommunityOverviewExtractionResult,
            system_prompt=self.config['system_prompt'],
            model_settings=self.model_settings
        )

    async def extract_community_info(self, website_url: str) -> CommunityOverviewExtractionResult:
        """Extract general community information from a website.

        Args:
            website_url: The URL of the community website to analyze

        Returns:
            CommunityOverviewExtractionResult with extracted community data

        Raises:
            Exception: If the extraction fails
        """
        try:
            prompt = self.config['prompts']['extract_community_info'].format(
                website_url=website_url
            )

            result = await self.agent.run(prompt)
            logger.info(
                f"Community overview agent successfully analyzed {website_url}")
            return result.data

        except Exception as e:
            logger.error(f"Community overview extraction failed for {
                         website_url}: {str(e)}")
            raise


class FeeSpecialistAgent:
    """Agent specialized in finding and extracting fee information."""

    def __init__(self):
        """Initialize the fee specialist agent."""
        self.config = get_agent_config('fee_specialist')
        self.model = get_model_for_agent('fee_specialist')
        self.model_settings = get_model_settings_for_agent('fee_specialist')

        # Create the PydanticAI agent
        self.agent = Agent(
            model=self.model,
            result_type=FeeExtractionResult,
            system_prompt=self.config['system_prompt'],
            model_settings=self.model_settings
        )

    async def extract_fees(self, website_url: str) -> FeeExtractionResult:
        """Extract all fees from a rental community website.

        Args:
            website_url: The URL of the community website to analyze

        Returns:
            FeeExtractionResult with all discovered fees

        Raises:
            Exception: If the extraction fails
        """
        try:
            prompt = self.config['prompts']['extract_fees'].format(
                website_url=website_url
            )

            result = await self.agent.run(prompt)
            logger.info(f"Fee specialist found {
                        len(result.data.fees_found)} fees for {website_url}")
            return result.data

        except Exception as e:
            logger.error(f"Fee extraction failed for {website_url}: {str(e)}")
            raise


class ValidationAgent:
    """Agent specialized in validating extracted data for completeness and quality."""

    def __init__(self):
        """Initialize the validation agent."""
        self.config = get_agent_config('validation_agent')
        self.model = get_model_for_agent('validation_agent')

        # Create the PydanticAI agent
        self.agent = Agent(
            model=self.model,
            result_type=ValidationReport,
            system_prompt=self.config['system_prompt']
        )

    async def validate_extraction(self, community_data: CommunityInformation) -> ValidationReport:
        """Validate extracted community data for completeness.

        Args:
            community_data: The extracted community information to validate

        Returns:
            ValidationReport with detailed validation results

        Raises:
            Exception: If the validation fails
        """
        try:
            # Convert community data to dict for validation
            extracted_data_str = community_data.model_dump_json(indent=2)

            prompt = self.config['prompts']['validate_extraction'].format(
                extracted_data=extracted_data_str
            )

            result = await self.agent.run(prompt)
            logger.info(f"Validation completed with {
                        result.data.completeness_score}% completeness score")
            return result.data

        except Exception as e:
            logger.error(f"Data validation failed: {str(e)}")
            raise


class MasterOrchestratorAgent:
    """Master orchestrator agent that coordinates specialized agents using agents-as-tools."""

    def __init__(self):
        """Initialize the master orchestrator agent."""
        self.config = get_agent_config('master_orchestrator')
        self.model = get_model_for_agent('master_orchestrator')

        # Initialize specialized agents
        self.floor_plan_specialist = FloorPlanSpecialistAgent()
        self.community_overview_agent = CommunityOverviewAgent()
        self.fee_specialist = FeeSpecialistAgent()
        self.validation_agent = ValidationAgent()

        # Create the PydanticAI agent
        self.agent = Agent(
            model=self.model,
            result_type=CommunityInformation,
            system_prompt=self.config['system_prompt']
        )

        # Add agent tools using the decorator pattern
        self._setup_agent_tools()

        logger.info(
            "MasterOrchestratorAgent initialized with all specialist agents and tools")

    def _setup_agent_tools(self):
        """Setup agent tools using PydanticAI's tool decorator pattern."""

        @self.agent.tool_plain
        async def extract_floor_plans(website_url: str) -> FloorPlanExtractionResult:
            """Extract all floor plans and their details from a rental community website.

            This tool specializes in finding comprehensive floor plan information 
            including pricing, amenities, and availability.

            Args:
                website_url: The URL of the community website to analyze

            Returns:
                FloorPlanExtractionResult with extracted floor plans
            """
            logger.info(
                f"Tool: Starting floor plan extraction for {website_url}")
            result = await self.floor_plan_specialist.extract_floor_plans(website_url)
            logger.info(f"Tool: Floor plan extraction completed, found {
                        len(result.floor_plans_found)} floor plans")
            return result

        @self.agent.tool_plain
        async def extract_community_overview(website_url: str) -> CommunityOverviewExtractionResult:
            """Extract general community information including fees, policies, contact details.

            This tool focuses on community-wide information excluding floor plan specific details.

            Args:
                website_url: The URL of the community website to analyze

            Returns:
                CommunityOverviewExtractionResult with extracted community information
            """
            logger.info(
                f"Tool: Starting community overview extraction for {website_url}")
            result = await self.community_overview_agent.extract_community_info(website_url)
            logger.info("Tool: Community overview extraction completed")
            return result

        @self.agent.tool_plain
        async def extract_fees(website_url: str) -> FeeExtractionResult:
            """Extract all fees and pricing information from a rental community website.

            This tool specializes in finding comprehensive fee information including
            application fees, pet fees, amenities fees, and all other charges.

            Args:
                website_url: The URL of the community website to analyze

            Returns:
                FeeExtractionResult with all discovered fees
            """
            logger.info(f"Tool: Starting fee extraction for {website_url}")
            result = await self.fee_specialist.extract_fees(website_url)
            logger.info(f"Tool: Fee extraction completed, found {
                        len(result.fees_found)} fees")
            return result

        @self.agent.tool_plain
        async def validate_extraction_data(community_data_json: str) -> ValidationReport:
            """Validate extracted community data for completeness and quality.

            This tool identifies missing information, incomplete fields, and provides 
            specific feedback for improvement.

            Args:
                community_data_json: JSON string of the community data to validate

            Returns:
                ValidationReport with validation results
            """
            logger.info("Tool: Starting data validation")
            # Parse JSON string back to CommunityInformation model
            import json
            community_data_dict = json.loads(community_data_json)
            community_data = CommunityInformation(**community_data_dict)
            result = await self.validation_agent.validate_extraction(community_data)
            logger.info(f"Tool: Data validation completed with {
                        result.completeness_score}% score")
            return result

    async def orchestrate_extraction(self, website_url: str, max_retries: int = 2) -> OrchestrationResult:
        """Orchestrate complete information extraction using specialized agents as tools.

        Args:
            website_url: The URL of the community website to analyze
            max_retries: Maximum number of retry attempts

        Returns:
            OrchestrationResult with complete extraction results

        Raises:
            Exception: If orchestration fails after all retries
        """
        start_time = time.time()
        agents_used = []
        total_retry_count = 0

        try:
            # Use the orchestrator agent with tools to coordinate extraction
            prompt = self.config['prompts']['orchestrate_extraction'].format(
                website_url=website_url
            )

            logger.info(
                f"Starting tools-based orchestrated extraction for {website_url}")
            result = await self.agent.run(prompt)

            # The agent with tools should return the final CommunityInformation
            final_community_info = result.data

            # Debug: Log the fees in the final result
            logger.info(f"Tools-based extraction completed. Final result fees: "
                        f"Application: ${
                            final_community_info.application_fee}, "
                        f"Administration: ${
                            final_community_info.administration_fee}, "
                        f"Membership: {final_community_info.membership_fee}")
            logger.info(
                f"Tools-based extraction returned {len(final_community_info.floor_plans)} floor plans")

            # Validate the final result using direct agent call
            validation_result = await self.validation_agent.validate_extraction(final_community_info)
            agents_used.append("ValidationAgent")

            # If validation fails, attempt retry with fallback method
            retry_count = 0
            while not validation_result.validation_passed and retry_count < max_retries:
                retry_count += 1
                total_retry_count += retry_count

                logger.warning(f"Tools-based extraction validation failed (score: {
                               validation_result.completeness_score}%), attempting fallback retry {retry_count}/{max_retries}")

                # Use fallback direct agent methods for retry
                retry_result = await self._handle_retry_extraction(
                    website_url, validation_result, final_community_info
                )
                agents_used.extend(retry_result['agents_used'])
                final_community_info = retry_result['updated_community_info']

                # Re-validate after retry
                validation_result = await self.validation_agent.validate_extraction(final_community_info)
                agents_used.append("ValidationAgent")

            # Prepare final orchestration result
            orchestration_time = time.time() - start_time

            quality_assessment = self._assess_data_quality(validation_result)
            areas_needing_improvement = self._identify_improvement_areas(
                validation_result)

            extraction_summary = (
                f"Successfully orchestrated extraction using tools-based agents "
                f"with {retry_count} retry(s). Final validation score: {
                    validation_result.completeness_score}%"
            )

            result = OrchestrationResult(
                final_community_info=final_community_info,
                extraction_summary=extraction_summary,
                agents_used=["MasterOrchestrator"] + agents_used,
                total_retry_count=total_retry_count,
                final_validation_score=validation_result.completeness_score,
                orchestration_time=orchestration_time,
                quality_assessment=quality_assessment,
                areas_needing_improvement=areas_needing_improvement
            )

            logger.info(f"Tools-based orchestration completed successfully in {
                        orchestration_time:.2f}s with {validation_result.completeness_score}% completeness")
            return result

        except Exception as e:
            orchestration_time = time.time() - start_time
            logger.error(
                f"Tools-based orchestration failed after {orchestration_time:.2f}s: {str(e)}")
            raise

    def _merge_extraction_results(self, community_info: CommunityInformation, floor_plans: List) -> CommunityInformation:
        """Merge floor plans into community information."""
        # Create a new community info with merged floor plans
        merged_data = community_info.model_copy()
        merged_data.floor_plans = floor_plans
        return merged_data

    async def _handle_retry_extraction(self, website_url: str, validation_result: ValidationReport,
                                       current_data: CommunityInformation) -> Dict:
        """Handle retry extraction based on validation feedback."""
        agents_used = []
        updated_community_info = current_data

        # Determine what needs to be retried based on validation feedback
        retry_floor_plans = any('floor plan' in feedback.lower()
                                for feedback in validation_result.retry_recommendations)
        retry_fees = any('fee' in feedback.lower() or 'cost' in feedback.lower(
        ) or 'price' in feedback.lower() for feedback in validation_result.retry_recommendations)
        retry_community_info = any('policy' in feedback.lower() or 'contact' in feedback.lower() or 'amenity' in feedback.lower()
                                   for feedback in validation_result.retry_recommendations)

        # Retry floor plan extraction if needed
        if retry_floor_plans:
            logger.info(
                "Retrying floor plan extraction based on validation feedback")
            floor_plan_result = await self.floor_plan_specialist.extract_floor_plans(website_url)
            agents_used.append("FloorPlanSpecialistAgent")
            updated_community_info = self._merge_extraction_results(
                updated_community_info, floor_plan_result.floor_plans_found)

        # Retry fee extraction if needed
        if retry_fees:
            logger.info("Retrying fee extraction based on validation feedback")
            fee_result = await self.fee_specialist.extract_fees(website_url)
            agents_used.append("FeeSpecialistAgent")
            # Merge fee data into community info while preserving existing data
            logger.info(
                f"Processing {len(fee_result.fees_found)} fees from FeeSpecialist")
            for fee in fee_result.fees_found:
                fee_category_lower = fee.fee_category.lower()
                logger.info(f"Processing fee: {fee.fee_name} (${
                            fee.amount}) - Category: {fee.fee_category}")

                # Map fee categories to community info fields with more flexible matching
                if fee_category_lower == 'application' and not updated_community_info.application_fee:
                    updated_community_info.application_fee = fee.amount
                    updated_community_info.application_fee_source = fee.source_url
                    logger.info(f"Updated application_fee: ${fee.amount}")
                elif fee_category_lower in ['administration', 'administrative'] and not updated_community_info.administration_fee:
                    updated_community_info.administration_fee = fee.amount
                    updated_community_info.administration_fee_source = fee.source_url
                    logger.info(f"Updated administration_fee: ${fee.amount}")
                elif fee_category_lower in ['membership', 'amenity'] and (not updated_community_info.membership_fee or updated_community_info.membership_fee.strip() == ''):
                    updated_community_info.membership_fee = f"${
                        fee.amount}" if fee.amount else fee.description
                    updated_community_info.membership_fee_source = fee.source_url
                    logger.info(f"Updated membership_fee: {
                                updated_community_info.membership_fee}")

            logger.info(f"After fee processing - Application: ${updated_community_info.application_fee}, "
                        f"Administration: ${
                            updated_community_info.administration_fee}, "
                        f"Membership: {updated_community_info.membership_fee}")

        # Retry community overview extraction if needed
        if retry_community_info:
            logger.info(
                "Retrying community overview extraction based on validation feedback")
            community_result = await self.community_overview_agent.extract_community_info(website_url)
            agents_used.append("CommunityOverviewAgent")
            # Merge community info while preserving floor plans
            floor_plans = updated_community_info.floor_plans
            updated_community_info = community_result.community_info
            updated_community_info.floor_plans = floor_plans

        return {
            'agents_used': agents_used,
            'updated_community_info': updated_community_info
        }

    def _assess_data_quality(self, validation_result: ValidationReport) -> str:
        """Assess the overall quality of extracted data."""
        score = validation_result.completeness_score

        if score >= 90:
            return "Excellent - Comprehensive data extraction with minimal gaps"
        elif score >= 80:
            return "Good - Most critical information captured with some minor omissions"
        elif score >= 70:
            return "Fair - Key information present but several data points missing"
        elif score >= 60:
            return "Poor - Significant gaps in extracted information"
        else:
            return "Very Poor - Major information missing, extraction needs significant improvement"

    def _identify_improvement_areas(self, validation_result: ValidationReport) -> List[str]:
        """Identify areas where data quality could be improved."""
        improvement_areas = []

        if validation_result.critical_fields_missing:
            improvement_areas.append(f"Critical fields missing: {
                                     ', '.join(validation_result.critical_fields_missing)}")

        if validation_result.incomplete_fields:
            improvement_areas.append(f"Incomplete fields: {
                                     ', '.join(validation_result.incomplete_fields)}")

        if validation_result.quality_issues:
            improvement_areas.extend(validation_result.quality_issues)

        return improvement_areas
