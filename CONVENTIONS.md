# Secret Shopper Development Guidelines

## Commands
- Start server: `source venv/bin/activate && python manage.py runserver`
- Run tests: `source venv/bin/activate && python manage.py test`
- Run single test: `source venv/bin/activate && python manage.py test app_name.tests.TestClass.test_method`
- Create migrations: `source venv/bin/activate && python manage.py makemigrations`
- Apply migrations: `source venv/bin/activate && python manage.py migrate`
- Lint code: `flake8`
- Check types: `source venv/bin/activate && mypy re-secret-shop`

## Code Style
- **Imports**: Group in order: standard lib, Django, third-party, local apps
- **Formatting**: 4 spaces indentation, 88 char line length
- **Naming**: snake_case for variables/functions, CamelCase for classes
- **Types**: Use type hints in function signatures
- **Error Handling**: Use try/except with specific exceptions
- **Django Models**: Define `__str__` for all models
- **Views**: Class-based views preferred, document with docstrings
- **AI Integration**: Isolate AI functionality in dedicated services
- **CSV Processing**: Use Python's csv module with explicit error handling
- **Testing**: Write tests for all new functionality
- **Modularity**: Keep apps small and focused on specific functionality
- **Re-usability**: Write code with a minimal amount of duplication
- **Small Files**: No single file should exceed 800 line. Break up large files into smaller modules.

Always write test for new functionality. Commit early and often.
