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