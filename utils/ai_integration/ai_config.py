"""Configuration settings for AI services used in the application."""
import os
from typing import Dict, Any
from django.conf import settings

# Structured Outout for Information Gathering
STRUCTURED_OUTPUT_INFORMATION_GATHERING = {
    "format": {
        "type": "json_schema",
        "name": "community",
        "strict": True,
        "schema": {
            "type": "object",
            "community": {
                "name": {
                    "type": "string",
                    "description": "The name of the community"
                },
                "overview": {
                    "type": "string",
                    "description": "A brief summary or description of the community."
                },
                "url": {
                    "type": "string",
                    "description": "The link to the community's homepage or relevant page."
                },
                "application_fee": {
                    "type": "number",
                    "description": "The fee charged to prospects for applying to live in the community."
                },
                "application_fee_source": {
                    "type": "string",
                    "description": "The source url of the application fee. This is usually a link to the payment processor."
                },
                "administration_fee": {
                    "type": "number",
                    "description": "The one time fee charged to prospects for administrative purposes."
                },
                "administration_fee_source": {
                    "type": "string",
                    "description": "The source url of the administration fee. This is usually a link to the payment processor."
                },
                "membership_fee": {
                    "type": "number",
                    "description": "The recurring fee charged to residents for membership in the community. Sometimes called a resident benefits package or amenity package."
                },
                "membership_fee_source": {
                    "type": "string",
                    "description": "The source url of the membership fee. This is usually a link to the payment processor."
                },
                "pet_policy": {
                    "type": "string",
                    "description": "The community's policy and fees on pets."
                },
                "pet_policy_source": {
                    "type": "string",
                    "description": "The source url of the pet policy. This is usually a link to the community's pet policy page."
                },
                "self_showings": {
                    "type": "boolean",
                    "description": "Whether the community offers self-showings."
                },
                "self_showings_source": {
                    "type": "string",
                    "description": "The source url of the self-showings. This is usually a link to the community's self-showing page."
                },
                "office_hours": {
                    "type": "string",
                    "description": "The office hours of the community."
                },
                "resident_portal_sofware_provider": {
                    "type": "string",
                    "description": "The software provider for the resident portal."
                },
                "community_pages": {
                    "type": "array",
                    "description": "A list of pages associated with the community.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "The name of the page."
                            },
                            "overview": {
                                "type": "string",
                                "description": "A brief overview or description of the page and user experience."
                            },
                            "url": {
                                "type": "string",
                                "description": "The URL for the page."
                            }
                        },
                        "required": [
                            "name",
                            "overview",
                            "url"
                        ],
                        "additionalProperties": False
                    }
                },
                "floor_plans": {
                    "type": "array",
                    "description": "A list of all floor plans available in the community.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "The name of the floor plan."
                            },
                            "beds": {
                                "type": "number",
                                "description": "The number of bedrooms in the floor plan."
                            },
                            "baths": {
                                "type": "number",
                                "description": "The number of bathrooms in the floor plan."
                            },
                            "url": {
                                "type": "string",
                                "description": "The URL for the floor plan."
                            },
                            "sqft": {
                                "type": "number",
                                "description": "The square footage of the floor plan."
                            },
                            "type": {
                                "type": "string",
                                "description": "The type of unit (e.g. apartment, townhome, etc.)."
                            },
                            "min_rental_price": {
                                "type": "number",
                                "description": "The minimum rental price of the floor plan."
                            },
                            "max_rental_price": {
                                "type": "number",
                                "description": "The maximum rental price of the floor plan."
                            },
                            "security_deposit": {
                                "type": "number",
                                "description": "The security deposit required for the floor plan."
                            },
                            "floor_plan_amenities": {
                                "type": "array",
                                "description": "A list of amenities available in the floor plan.",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "amenity": {
                                            "type": "string",
                                            "description": "The name or description of the amenity."
                                        }
                                    },
                                    "required": [
                                        "amenity"
                                    ],
                                    "additionalProperties": False
                                }
                            }
                        },
                        "required": [
                            "name",
                            "beds",
                            "baths",
                            "url",
                            "sqft",
                            "type",
                            "min_rental_price",
                            "max_rental_price",
                            "security_deposit",
                            "floor_plan_amenities"
                        ],
                        "additionalProperties": False
                    }
                },
                "community_amenities": {
                    "type": "array",
                    "description": "A list of amenities available in the community.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "amenity": {
                                "type": "string",
                                "description": "The name or description of the amenity."
                            }
                        },
                        "required": [
                            "amenity"
                        ],
                        "additionalProperties": False
                    }
                }
            },
            "required": [
                "name",
                "overview",
                "url",
                "application_fee",
                "administration_fee",
                "membership_fee",
                "pet_policy",
                "community_pages",
                "community_amenities",
                "floor_plans"
            ],
            "additionalProperties": False
        }
    }
}

# Secret shop specific configurations
SECRET_SHOP_AI_CONFIG = {
    'information_gathering': {
        'service': 'openai',
        'model': 'gpt-4o',
        'temperature': 1,
        'max_output_tokens': 10000,
        'tools': [
            {
                'type': 'web_search_preview',
                'user_location': {
                    'type': 'approximate',
                    'country': 'US'
                },
                'search_context_size': 'medium'
            }
        ],
        'tool_choice': {
            'type': 'web_search_preview',
        },
        'text': STRUCTURED_OUTPUT_INFORMATION_GATHERING,
    },
    'persona_generation': {
        'service': 'openai',
        'model': 'gpt-4o-mini',
        'temperature': 1,
        'max_output_tokens': 1000,
        'tools': [],
    },
    'initial_inquiry': {
        'service': 'openai',
        'model': 'gpt-4o-mini',
        'temperature': 1,
        'max_output_tokens': 1000,
        'tools': [],
    },
    'response_analysis': {
        'service': 'openai',
        'model': 'gpt-4o-mini',
        'temperature': 1,
        'max_output_tokens': 1000,
        'tools': [],
    },
    'followup_generation': {
        'service': 'openai',
        'model': 'gpt-4o-mini',
        'temperature': 1,
        'max_output_tokens': 1000,
        'tools': [],
    },
}

# Property data extraction configuration
DATA_EXTRACTION_CONFIG = {
    'required_data_points': [
        'price',
        'deposit',
        'lease_terms',
        'available_date',
        'square_footage',
        'pet_policy',
        'parking',
        'utilities_included',
        'application_fee',
        'amenities',
    ],
    # If less than 60% of data points are found, generate follow-up
    'follow_up_threshold': 0.6,
}

# Retry configuration for API calls
API_RETRY_CONFIG = {
    'max_retries': 3,
    'retry_delay': 2,  # seconds
    'backoff_factor': 2,
}


def get_api_key(service: str) -> str:
    """Get the API key for the specified service.

    Args:
        service: The service name ('openai' or 'anthropic')

    Returns:
        The API key as a string
    """
    if service.lower() == 'openai':
        return os.environ.get('OPENAI_API_KEY', settings.OPENAI_API_KEY)
    else:
        raise ValueError(f"Unknown service: {service}")


def get_model_config(task_type: str) -> Dict[str, Any]:
    """Get the model configuration for a specific task.

    Args:
        task_type: The type of task (e.g., 'persona_generation')

    Returns:
        A dictionary with the model configuration
    """
    if task_type in SECRET_SHOP_AI_CONFIG:
        return SECRET_SHOP_AI_CONFIG[task_type]
    else:
        # Return a default configuration
        return {
            'service': 'openai',
            'model': 'gpt-4o-mini',
            'temperature': 1,
            'max_output_tokens': 1000,
            'tools': [],
        }
