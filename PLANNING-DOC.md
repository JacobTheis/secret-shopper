> [!info] Summary
> The purpose of the Secret Shop project is to save businesses man hours by using advancements in Ai to reach out and show interested in rental units. They will then converse with the agents, inquire, and collect information about the property. That information will then be organized and presented in a useful/impactful report. 


# Project Requirements Outline

## Pages

- Login
- Dashboard
- Targets (Secret Shop Targets)
	- Target Details Page
	- Create New Target page
- Persona Templates

## Functionality

### Emails

| Name               | Description                                                                                                                |
| ------------------ | -------------------------------------------------------------------------------------------------------------------------- |
| New Email Address Creation | Integration with an email service or...something that allows us to create new inboxes where we can send and recieve emails |
| Email Send         | Compose and send an email                                                                                                  |
| Recieve Email      | When we get a reply to an inquiry, we need to be aware and parse the email                                                 |


### Persona Temples and Generation

| Name               | Description                                                                                                                |
| ------------------ | -------------------------------------------------------------------------------------------------------------------------- |
| Persona Templates  | Create a template for the persona that will be used to gather information about the property                               |
| Persona Generation | Generate a persona based on the template                                                                                   |
| Persona Storage    | Store the persona in a database or file                                                                                    |
| Persona Retrieval  | Retrieve the persona from the database or file                                                                             |

#### Persona Model

The persona will be created by the user. It will consist of the following information:
- First Name
- Last Name
- Rental Budget
- Desired bedrooms
- Desired Bathrooms
- Additional Rental Preferences (text description)
- Pets (text description)
- Credit Score
- Monthly Income
- Additional Occupants (text description)
- Rental History (text description)

### Target Definition

| Name               | Description                                                                                                                |
| ------------------ | -------------------------------------------------------------------------------------------------------------------------- |
| Define Secret Shop Target | Define the target of the secret shop, the property that will be inquired about                                  |
| Target Storage     | Store the target in a database or file                                                                                     |
| Target Retrieval   | Retrieve the target from the database or file                                                                              |
| Targets Gathering  | Gather information about the target automatically                                                                           |

#### Target Model

The target will be created by the user. It will consist of the following information:
- Name
- Street Address
- City
- State
- Zip
- Phone Number
- Email Address
- Website
- Owner(s)
- Property Manager

### Secret Shop Communication and Data Gathering

| Name               | Description                                                                                                                |
| ------------------ | -------------------------------------------------------------------------------------------------------------------------- |
| Inquirey           | Send an inquiry to the target property                                                                                     |
| Data Gathering     | Gather information about the property from the agent                                                                       |
| Data Storage       | Store the data in a database or file                                                                                       |
| Data Retrieval     | Retrieve the data from the database or file                                                                                |
| Parse response     | Parse the response from the agent                                                                                          |
| Follow up          | Follow up with the agent to gather more information if data is missing                                                     |

#### Shop Model

The shop will consist of the following information:
- target_id (Foreign Key to the target)
- start_time
- end_time
- status (in progress, completed, failed)

##### Secret Shop Summary Results Model

This will be a summary of the results of the shop. It will consist of the following:

- secret_shop_id (Foreign Key to the shop)
- community_names
- community_overview
- community_url
- application_fee
- administration_fee
- membership_fee
- pet_policy
- community_pages              # List of all community pages on the site being scraped
  - page_name
  - page_overview
  - page_url
- floor_plans                  # List of all floor plans available in the community    
  - floor_plan_name
  - floor_plan_beds
  - floor_plan_baths
  - floor_plan_url
  - floor_plan_sqft
  - floor_plan_type
  - floor_plan_min_rental_price
  - floor_plan_max_rental_price
  - floor_plan_security_deposit
  - floor_plan_amenities
- community_amenities         # List of all community amenities available in the community
  - amenity_name
  - amenity_description


*This is the result schema for the AI info gathering*
```
STRUCTURED_OUTPUT_INFORMATION_GATHERING = {
    'format': {
        'type': 'json_schema',
        'name': 'community',
        'strict': True,
        'schema': {
            'type': 'object',
            'community': {
                'name': {
                    'type': 'string',
                    'description': 'The name of the community'
                },
                'overview': {
                    'type': 'string',
                    'description': 'A brief summary or description of the community.'
                },
                'url': {
                    'type': 'string',
                    'description': 'The link to the community homepage or relevant page.'
                },
                'application_fee': {
                    'type': 'number',
                    'description': 'The fee charged to prospects for applying to live in the community.'
                },
                'administration_fee': {
                    'type': 'number',
                    'description': 'The one time fee charged to prospects for administrative purposes.'
                },
                'membership_fee': {
                    'type': 'number',
                    'description': 'The recurring fee charged to residents for membership in the community. Sometimes called a resident benefits package or amenity package.'
                },
                'pet_policy': {
                    'type': 'number',
                    'description': 'The community policy and fees on pets.'
                },
                'community_pages': {
                    'type': 'array',
                    'description': 'A list of pages associated with the community.',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'name': {
                                'type': 'string',
                                'description': 'The name of the page.'
                            },
                            'overview': {
                                'type': 'string',
                                'description': 'A brief overview or description of the page and user experience.'
                            },
                            'url': {
                                'type': 'string',
                                'description': 'The URL for the page.'
                            }
                        },
                        'required': [
                            'name',
                            'overview',
                            'url'
                        ],
                        'additionalProperties': False
                    }
                },
                'floor_plans': {
                    'type': 'array',
                    'description': 'A list of all floor plans available in the community.',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'name': {
                                'type': 'string',
                                'description': 'The name of the floor plan.'
                            },
                            'beds': {
                                'type': 'number',
                                'description': 'The number of bedrooms in the floor plan.'
                            },
                            'baths': {
                                'type': 'number',
                                'description': 'The number of bathrooms in the floor plan.'
                            },
                            'url': {
                                'type': 'string',
                                'description': 'The URL for the floor plan.'
                            },
                            'sqft': {
                                'type': 'number',
                                'description': 'The square footage of the floor plan.'
                            },
                            'type': {
                                'type': 'string',
                                'description': 'The type of unit (e.g. apartment, townhome, etc.).'
                            },
                            'min_rental_price': {
                                'type': 'number',
                                'description': 'The minimum rental price of the floor plan.'
                            },
                            'max_rental_price': {
                                'type': 'number',
                                'description': 'The maximum rental price of the floor plan.'
                            },
                            'security_deposit': {
                                'type': 'number',
                                'description': 'The security deposit required for the floor plan.'
                            },
                            'floor_plan_amenities': {
                                'type': 'array',
                                'description': 'A list of amenities available in the floor plan.',
                                'items': {
                                    'type': 'object',
                                    'properties': {
                                        'amenity': {
                                            'type': 'string',
                                            'description': 'The name or description of the amenity.'
                                        }
                                    },
                                    'required': [
                                        'amenity'
                                    ],
                                    'additionalProperties': False
                                }
                            }
                        },
                        'required': [
                            'name',
                            'beds',
                            'baths',
                            'url',
                            'sqft',
                            'type',
                            'min_rental_price',
                            'max_rental_price',
                            'security_deposit',
                            'floor_plan_amenities'
                        ],
                        'additionalProperties': False
                    }
                },
                'community_amenities': {
                    'type': 'array',
                    'description': 'A list of amenities available in the community.',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'amenity': {
                                'type': 'string',
                                'description': 'The name or description of the amenity.'
                            }
                        },
                        'required': [
                            'amenity'
                        ],
                        'additionalProperties': False
                    }
                }
            },
            'required': [
                'name',
                'overview',
                'url',
                'application_fee',
                'administration_fee',
                'membership_fee',
                'pet_policy',
                'community_pages',
                'community_amenities',
                'floor_plans'
            ],
            'additionalProperties': False
        }
    }
}



```

##### Secret Shop Email Communications Model


This will be how the email communications are stored. It will consist of the following:
- secret_shop_id (Foreign Key to the shop)
- persona_id (Foreign Key to the persona)
- email_id (Foreign Key to the email)
- email_type (inquiry, followup, response)
- email_body
- email_subject
- email_from
- email_to

### Data processing and assessment

| Name               | Description                                                                                                                |
| ------------------ | -------------------------------------------------------------------------------------------------------------------------- |
| Define data to be collected | Define the data that will be collected from the agent and the property                                          |
| Apply Communication Response to Data | Apply the response from the agent to the data that was collected from the property                       |
| Read Communications and Grade agent | Read the communications and grade the agent based on the data collected and the response from the agent |



### Reporting



# Implementation

## Project Structure

```
secret_shop_project/
│
├── config/                          # Django project settings
│   ├── __init__.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py                  # Common settings
│   │   ├── development.py           # Development specific settings
│   │   └── production.py            # Production specific settings
│   ├── urls.py                      # Main URL routing
│   ├── wsgi.py                      # WSGI application for production
│   └── asgi.py                      # ASGI application for async capabilities
│
├── manage.py                        # Django management script
│
├── apps/                            # Application modules directory
│   │
│   ├── accounts/                    # User account management
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── forms.py
│   │   ├── managers.py              # Custom user managers
│   │   ├── models.py                # User model and related models
│   │   ├── urls.py
│   │   ├── views.py
│   │   ├── migrations/
│   │   └── templates/
│   │
│   ├── dashboard/                   # Dashboard functionality
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py                # Dashboard models (if needed)
│   │   ├── urls.py
│   │   ├── views.py                 # Dashboard views
│   │   ├── services/                # Business logic
│   │   │   ├── __init__.py
│   │   │   └── stats_service.py     # Statistics for dashboard
│   │   ├── migrations/
│   │   ├── templates/
│   │   └── tests/
│   │
│   ├── personas/                    # Persona template & generation
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py                # Persona models
│   │   ├── forms.py                 # Persona forms
│   │   ├── services/                # Business logic
│   │   │   ├── __init__.py
│   │   │   ├── persona_generator.py # AI-driven persona generation
│   │   │   └── persona_manager.py   # Persona management services
│   │   ├── urls.py
│   │   ├── views.py
│   │   ├── migrations/
│   │   ├── templates/
│   │   └── tests/
│   │
│   ├── targets/                     # Target property management
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py                # Target property models
│   │   ├── forms.py
│   │   ├── services/                # Business logic
│   │   │   ├── __init__.py
│   │   │   ├── property_crawler.py  # Automated property information gathering
│   │   │   └── target_manager.py    # Target management services
│   │   ├── urls.py
│   │   ├── views.py
│   │   ├── migrations/
│   │   ├── templates/
│   │   └── tests/
│   │
│   ├── communications/              # Email and message management
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py                # Email/communication models
│   │   ├── forms.py
│   │   ├── services/                # Business logic
│   │   │   ├── __init__.py
│   │   │   ├── email_service.py     # Email creation and management
│   │   │   ├── message_parser.py    # Parse incoming messages
│   │   │   └── followup_manager.py  # Handle follow-up communications
│   │   ├── urls.py
│   │   ├── views.py
│   │   ├── migrations/
│   │   ├── templates/
│   │   └── tests/
│   │
│   ├── shops/                       # Secret shop operation management
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py                # Secret shop models
│   │   ├── forms.py
│   │   ├── services/                # Business logic
│   │   │   ├── __init__.py
│   │   │   ├── shop_orchestrator.py # Orchestrate the shop process
│   │   │   ├── data_collector.py    # Collect and process shop data
│   │   │   └── ai_conversation.py   # AI-driven conversation management
│   │   ├── urls.py
│   │   ├── views.py
│   │   ├── migrations/
│   │   ├── templates/
│   │   └── tests/
│   │
│   └── reports/                     # Reporting functionality
│       ├── __init__.py
│       ├── admin.py
│       ├── apps.py
│       ├── models.py                # Report models
│       ├── forms.py
│       ├── services/                # Business logic
│       │   ├── __init__.py
│       │   ├── report_generator.py  # Generate reports
│       │   └── analytics.py         # Analytical services
│       ├── urls.py
│       ├── views.py
│       ├── migrations/
│       ├── templates/
│       └── tests/
│
├── static/                          # Static files (CSS, JS, images)
│   ├── css/
│   ├── js/
│   ├── images/
│   └── vendors/                     # Third-party libraries
│
├── templates/                       # Global templates
│   ├── base.html                    # Base template
│   ├── partials/                    # Reusable template parts
│   ├── emails/                      # Email templates
│   └── errors/                      # Error pages (404, 500, etc.)
│
├── media/                           # User-uploaded content
│
├── utils/                           # Common utilities
│   ├── __init__.py
│   ├── ai_integration/              # AI service integrations
│   │   ├── __init__.py
│   │   ├── openai_client.py
│   │   └── anthropic_client.py
│   ├── email/                       # Email utilities
│   │   ├── __init__.py
│   │   └── mailboxes.py
│   └── validators.py                # Custom validators
│
├── requirements/
│   ├── base.txt                     # Common dependencies
│   ├── development.txt              # Development dependencies
│   └── production.txt               # Production dependencies
│
├── .env.example                     # Example environment variables
├── .gitignore                       # Git ignore file
├── README.md                        # Project documentation
└── docker-compose.yml               # Docker configuration
```


## Technical

### Tasks

> [!info] Issue Summary
> This application involved long running processes that may take awhile. This includes the initial evaluation of the target which will take several passes with the AI to get correct, but most importantly, the communications back and fourth. 

To handle this, we're going to use Celery.  This will allow us to handle all that pesky async stuff. 

### Database

We will run this on a Postgres database. On the local test environment this will be run in a docket container.
