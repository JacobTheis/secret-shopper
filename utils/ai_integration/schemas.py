"""Pydantic schemas for AI service inputs and outputs."""
from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl


class FloorPlanAmenity(BaseModel):
    """Represents an amenity for a floor plan."""
    amenity: str = Field(description="The name or description of the amenity")


class CommunityAmenity(BaseModel):
    """Represents an amenity for the community."""
    amenity: str = Field(description="The name or description of the amenity")


class CommunityPage(BaseModel):
    """Represents a page associated with the community."""
    name: str = Field(description="The name of the page")
    overview: str = Field(
        description="A brief overview or description of the page and user experience")
    url: str = Field(description="The URL for the page")


class FeeDetails(BaseModel):
    """Schema for detailed fee information."""
    fee_name: str = Field(description="Name or title of the fee")
    amount: Optional[float] = Field(None, description="Dollar amount of the fee")
    description: str = Field(description="Description of what the fee covers")
    refundable: bool = Field(default=False, description="Whether this fee is refundable")
    frequency: str = Field(description="Frequency (one-time, monthly, annual, conditional)")
    source_url: str = Field(description="URL where this fee information was found")
    conditions: Optional[str] = Field(None, description="Any conditions that apply to this fee")
    fee_category: str = Field(description="Category (application, pet, amenity, etc.)")


class FloorPlan(BaseModel):
    """Represents a floor plan in the community."""
    name: str = Field(description="The name of the floor plan")
    beds: float = Field(description="The number of bedrooms in the floor plan")
    baths: float = Field(
        description="The number of bathrooms in the floor plan")
    url: str = Field(description="The URL for the floor plan")
    sqft: Optional[float] = Field(
        None, description="The square footage of the floor plan")
    type: str = Field(
        description="The type of unit (e.g. apartment, townhome, etc.)")
    min_rental_price: Optional[float] = Field(
        None, description="The minimum rental price of the floor plan")
    max_rental_price: Optional[float] = Field(
        None, description="The maximum rental price of the floor plan")
    security_deposit: Optional[float] = Field(
        None, description="The security deposit required for the floor plan")
    image: Optional[str] = Field(
        None, description="URL to the floor plan image if available")
    num_available: Optional[int] = Field(
        None, description="The number of available units for the floor plan")
    floor_plan_amenities: List[FloorPlanAmenity] = Field(
        default_factory=list,
        description="A list of amenities available in the floor plan"
    )


class CommunityInformation(BaseModel):
    """Schema for community information gathered by AI."""
    name: str = Field(description="The name of the community")
    overview: str = Field(
        description="A brief summary or description of the community")
    url: str = Field(
        description="The link to the community's homepage or relevant page")
    fees: List[FeeDetails] = Field(
        default_factory=list,
        description="List of all fees associated with the community")
    pet_policy: Optional[str] = Field(
        None, description="The community's policy and fees on pets")
    pet_policy_source: Optional[str] = Field(
        None, description="The source url of the pet policy. This is usually a link to the community's pet policy page")
    self_showings: Optional[bool] = Field(
        None, description="Whether the community offers self-showings")
    self_showings_source: Optional[str] = Field(
        None, description="The source url of the self-showings. This is usually a link to the community's self-showing page")
    office_hours: Optional[str] = Field(
        None, description="The office hours of the community")
    resident_portal_software_provider: Optional[str] = Field(
        None, description="The software provider for the resident portal")
    street_address: Optional[str] = Field(
        None, description="The street address of the community or primary office")
    city: Optional[str] = Field(
        None, description="The city where the community or primary office is located")
    state: Optional[str] = Field(
        None, description="The state where the community or primary office is located")
    zip_code: Optional[str] = Field(
        None, description="The zip code of the community or primary office")
    special_offers: Optional[str] = Field(
        None, description="Any special offers or promotions currently available")
    community_pages: List[CommunityPage] = Field(
        default_factory=list,
        description="A list of pages associated with the community"
    )
    floor_plans: List[FloorPlan] = Field(
        default_factory=list,
        description="A list of all floor plans available in the community"
    )
    community_amenities: List[CommunityAmenity] = Field(
        default_factory=list,
        description="A list of amenities available in the community"
    )


class PersonaDetails(BaseModel):
    """Schema for generated persona details."""
    name: str = Field(description="Full name of the persona")
    age: int = Field(description="Age of the persona")
    occupation: str = Field(description="Job/occupation of the persona")
    email: str = Field(description="Email address for the persona")
    phone: str = Field(description="Phone number for the persona")
    timeline: str = Field(description="Timeline for moving")
    key_question: str = Field(description="Key question the persona would ask")
    interest_point: str = Field(
        description="Main point of interest for the persona")
    communication_style: str = Field(
        description="Communication style of the persona")
    budget_range: str = Field(description="Budget range for the persona")
    background_story: str = Field(description="Brief background story")
    priorities: List[str] = Field(
        description="List of priorities when choosing housing")


class ConversationAnalysis(BaseModel):
    """Schema for analyzing conversation responses."""
    extracted_data: dict = Field(
        description="Key data points extracted from the message")
    agent_responsiveness: int = Field(
        ge=1, le=5, description="Agent responsiveness score (1-5)")
    question_coverage: int = Field(
        ge=1, le=5, description="Question coverage score (1-5)")
    professionalism: int = Field(
        ge=1, le=5, description="Professionalism score (1-5)")
    overall_helpfulness: int = Field(
        ge=1, le=5, description="Overall helpfulness score (1-5)")
    missing_information: List[str] = Field(
        description="List of information not provided")
    follow_up_needed: bool = Field(description="Whether a follow-up is needed")
    summary: str = Field(description="Summary of the analysis")


class EmailContent(BaseModel):
    """Schema for generated email content."""
    subject: str = Field(description="Email subject line")
    body: str = Field(description="Email body content")
    tone: str = Field(description="Tone of the email")
    follow_up_type: Optional[str] = Field(
        None, description="Type of follow-up if applicable")


# Multi-Agent Communication Schemas

class ValidationReport(BaseModel):
    """Schema for validation agent reports on data completeness."""
    completeness_score: float = Field(
        ge=0, le=100, description="Overall completeness score (0-100%)")
    critical_fields_missing: List[str] = Field(
        default_factory=list, description="List of critical missing fields")
    incomplete_fields: List[str] = Field(
        default_factory=list, description="List of fields with incomplete data")
    quality_issues: List[str] = Field(
        default_factory=list, description="List of identified quality issues")
    specific_feedback: List[str] = Field(
        default_factory=list, description="Specific actionable feedback items")
    retry_recommendations: List[str] = Field(
        default_factory=list, description="Specific areas that need re-extraction")
    validation_passed: bool = Field(description="Whether validation criteria are met")
    validation_summary: str = Field(description="Summary of validation results")


class ExtractionStatus(BaseModel):
    """Schema for tracking extraction task status."""
    agent_name: str = Field(description="Name of the agent performing extraction")
    status: str = Field(description="Current status (pending, running, completed, failed)")
    success: bool = Field(description="Whether the extraction was successful")
    error_message: Optional[str] = Field(None, description="Error message if extraction failed")
    retry_count: int = Field(default=0, description="Number of retry attempts")
    extraction_time: float = Field(description="Time taken for extraction in seconds")
    data_points_found: int = Field(description="Number of data points successfully extracted")


class FloorPlanExtractionResult(BaseModel):
    """Schema for floor plan specialist extraction results."""
    floor_plans_found: List[FloorPlan] = Field(
        default_factory=list, description="List of extracted floor plans")
    extraction_method: str = Field(description="Method used for extraction")
    pages_searched: List[str] = Field(
        default_factory=list, description="URLs of pages searched for floor plans")
    search_strategies_used: List[str] = Field(
        default_factory=list, description="List of search strategies employed")
    extraction_confidence: float = Field(
        ge=0, le=100, description="Confidence level in extraction completeness")
    missing_data_areas: List[str] = Field(
        default_factory=list, description="Areas where data could not be found")
    extraction_notes: str = Field(description="Additional notes about the extraction process")


class CommunityOverviewExtractionResult(BaseModel):
    """Schema for community overview agent extraction results."""
    community_info: CommunityInformation = Field(description="Extracted community information")
    extraction_confidence: float = Field(
        ge=0, le=100, description="Confidence level in extraction completeness")
    pages_analyzed: List[str] = Field(
        default_factory=list, description="URLs of pages analyzed")
    fee_sources_found: List[str] = Field(
        default_factory=list, description="Sources where fee information was located")
    policy_sources_found: List[str] = Field(
        default_factory=list, description="Sources where policy information was located")
    extraction_notes: str = Field(description="Additional notes about the extraction process")


class FeeExtractionResult(BaseModel):
    """Schema for fee specialist extraction results."""
    fees_found: List[FeeDetails] = Field(
        default_factory=list, description="List of extracted fees")
    extraction_method: str = Field(description="Method used for extraction")
    pages_searched: List[str] = Field(
        default_factory=list, description="URLs of pages searched for fees")
    search_strategies_used: List[str] = Field(
        default_factory=list, description="List of search strategies employed")
    extraction_confidence: float = Field(
        ge=0, le=100, description="Confidence level in extraction completeness")
    missing_fee_areas: List[str] = Field(
        default_factory=list, description="Areas where fees might exist but couldn't be found")
    extraction_notes: str = Field(description="Additional notes about the extraction process")


class OrchestrationResult(BaseModel):
    """Schema for master orchestrator results."""
    final_community_info: CommunityInformation = Field(description="Final compiled community information")
    extraction_summary: str = Field(description="Summary of the orchestration process")
    agents_used: List[str] = Field(description="List of agents that were utilized")
    total_retry_count: int = Field(description="Total number of retries across all agents")
    final_validation_score: float = Field(
        ge=0, le=100, description="Final validation score for the extracted data")
    orchestration_time: float = Field(description="Total time for orchestration in seconds")
    quality_assessment: str = Field(description="Assessment of the final data quality")
    areas_needing_improvement: List[str] = Field(
        default_factory=list, description="Areas where data quality could be improved")
