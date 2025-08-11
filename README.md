# Secret Shopper Project

A Django-based web application for managing secret shopping operations, including persona generation, target property management, automated communications, and comprehensive reporting.

## Features

- **User Account Management**: Custom user authentication and profile management
- **Dashboard**: Comprehensive overview of secret shopping operations and statistics
- **Persona Management**: AI-driven persona generation and template management
- **Target Properties**: Property information gathering and target management
- **Communications**: Automated email and message management with follow-up capabilities
- **Secret Shopping Operations**: Orchestrated shop processes with AI-driven conversations
- **Reporting**: Analytics and report generation for shop operations

## Quick Start

### Prerequisites

- Python 3.8+
- pip
- virtualenv

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd re-secret-shop
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements/development.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

6. Create superuser:
```bash
python manage.py createsuperuser
```

7. Start the development server:
```bash
python manage.py runserver
```

## Development Commands

All commands should be run within the activated virtual environment:

```bash
source venv/bin/activate
```

### Server Management
- **Start server**: `python manage.py runserver`
- **Run migrations**: `python manage.py makemigrations && python manage.py migrate`

### Testing
- **Run all tests**: `python manage.py test`
- **Run specific test**: `python manage.py test app_name.tests.TestClass.test_method`

### Code Quality
- **Lint code**: `flake8`
- **Type checking**: `mypy re-secret-shop`
- **Format code**: `black .`

## Project Structure

The project follows Django best practices with a modular app-based architecture:

- **config/**: Django project settings and configuration
- **apps/**: Application modules (accounts, dashboard, personas, targets, communications, shops, reports)
- **utils/**: Common utilities and AI integrations
- **static/**: Static assets (CSS, JS, images)
- **templates/**: Django templates
- **media/**: User-uploaded content

## Style Guide

- **Imports**: Standard library → Django → third-party → local apps
- **Formatting**: 4 spaces indentation, 88 character line limit
- **Naming**: snake_case for variables/functions, CamelCase for classes
- **Type Hints**: Required for all function signatures
- **Testing**: Required for all new functionality
- **File Size**: Maximum 800 lines per file

## Contributing

1. Follow the established code style and conventions
2. Write tests for new functionality
3. Use specific exceptions in try/except blocks
4. Document all models with `__str__` methods
5. Use class-based views with docstrings
6. Keep apps small and focused with minimal duplication

## Environment Configuration

Copy `.env.example` to `.env` and configure the following variables:

- Database settings
- API keys for AI services
- Email configuration
- Debug settings

## License

[Add your license information here]