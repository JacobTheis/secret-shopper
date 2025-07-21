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
    overview: str = Field(description="A brief overview or description of the page and user experience")
    url: str = Field(description="The URL for the page")


class FloorPlan(BaseModel):
    """Represents a floor plan in the community."""
    name: str = Field(description="The name of the floor plan")
    beds: float = Field(description="The number of bedrooms in the floor plan")
    baths: float = Field(description="The number of bathrooms in the floor plan")
    url: str = Field(description="The URL for the floor plan")
    sqft: Optional[float] = Field(None, description="The square footage of the floor plan")
    type: str = Field(description="The type of unit (e.g. apartment, townhome, etc.)")
    min_rental_price: Optional[float] = Field(None, description="The minimum rental price of the floor plan")
    max_rental_price: Optional[float] = Field(None, description="The maximum rental price of the floor plan")
    security_deposit: Optional[float] = Field(None, description="The security deposit required for the floor plan")
    num_available_units: Optional[int] = Field(None, description="The number of available units for the floor plan")
    floor_plan_amenities: List[FloorPlanAmenity] = Field(
        default_factory=list,
        description="A list of amenities available in the floor plan"
    )


class CommunityInformation(BaseModel):
    """Schema for community information gathered by AI."""
    name: str = Field(description="The name of the community")
    overview: str = Field(description="A brief summary or description of the community")
    url: str = Field(description="The link to the community's homepage or relevant page")
    application_fee: Optional[float] = Field(None, description="The fee charged to prospects for applying to live in the community")
    application_fee_source: Optional[str] = Field(None, description="The source url of the application fee. This is usually a link to the payment processor")
    administration_fee: Optional[float] = Field(None, description="The one time fee charged to prospects for administrative purposes")
    administration_fee_source: Optional[str] = Field(None, description="The source url of the administration fee. This is usually a link to the payment processor")
    membership_fee: Optional[str] = Field(None, description="The recurring fee charged to residents for membership in the community or renting a property in the community. Sometimes called a resident benefits package or amenity package")
    membership_fee_source: Optional[str] = Field(None, description="The source url of the membership fee. This is usually a link to the payment processor")
    pet_policy: Optional[str] = Field(None, description="The community's policy and fees on pets")
    pet_policy_source: Optional[str] = Field(None, description="The source url of the pet policy. This is usually a link to the community's pet policy page")
    self_showings: Optional[bool] = Field(None, description="Whether the community offers self-showings")
    self_showings_source: Optional[str] = Field(None, description="The source url of the self-showings. This is usually a link to the community's self-showing page")
    office_hours: Optional[str] = Field(None, description="The office hours of the community")
    resident_portal_software_provider: Optional[str] = Field(None, description="The software provider for the resident portal")
    street_address: Optional[str] = Field(None, description="The street address of the community or primary office")
    city: Optional[str] = Field(None, description="The city where the community or primary office is located")
    state: Optional[str] = Field(None, description="The state where the community or primary office is located")
    zip_code: Optional[str] = Field(None, description="The zip code of the community or primary office")
    special_offers: Optional[str] = Field(None, description="Any special offers or promotions currently available")
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
    interest_point: str = Field(description="Main point of interest for the persona")
    communication_style: str = Field(description="Communication style of the persona")
    budget_range: str = Field(description="Budget range for the persona")
    background_story: str = Field(description="Brief background story")
    priorities: List[str] = Field(description="List of priorities when choosing housing")


class ConversationAnalysis(BaseModel):
    """Schema for analyzing conversation responses."""
    extracted_data: dict = Field(description="Key data points extracted from the message")
    agent_responsiveness: int = Field(ge=1, le=5, description="Agent responsiveness score (1-5)")
    question_coverage: int = Field(ge=1, le=5, description="Question coverage score (1-5)")
    professionalism: int = Field(ge=1, le=5, description="Professionalism score (1-5)")
    overall_helpfulness: int = Field(ge=1, le=5, description="Overall helpfulness score (1-5)")
    missing_information: List[str] = Field(description="List of information not provided")
    follow_up_needed: bool = Field(description="Whether a follow-up is needed")
    summary: str = Field(description="Summary of the analysis")


class EmailContent(BaseModel):
    """Schema for generated email content."""
    subject: str = Field(description="Email subject line")
    body: str = Field(description="Email body content")
    tone: str = Field(description="Tone of the email")
    follow_up_type: Optional[str] = Field(None, description="Type of follow-up if applicable")