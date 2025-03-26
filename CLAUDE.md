# Secret Shopper Project Guidelines for Claude

## Commands
- Server: `source venv/bin/activate && python manage.py runserver`
- Tests: `source venv/bin/activate && python manage.py test`
- Single test: `source venv/bin/activate && python manage.py test app_name.tests.TestClass.test_method`
- Migrations: `source venv/bin/activate && python manage.py makemigrations && python manage.py migrate`
- Lint: `flake8`
- Type check: `source venv/bin/activate && mypy re-secret-shop`

## Style Guide
- Imports: Standard lib → Django → third-party → local apps
- Formatting: 4 spaces, 88 char line limit, use black
- Naming: snake_case (vars/funcs), CamelCase (classes)
- Types: Use type hints in all function signatures
- Error handling: Specific exceptions in try/except
- Models: Define __str__ method for all models
- Views: Class-based, documented with docstrings
- Testing: Required for all new functionality
- Architecture: Small, focused apps with minimal duplication
- File size: Maximum 800 lines per file

Always run in virtual environment with `source venv/bin/activate && [command]`


## Basic Project Structure

```
re-secret-shop/
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

