"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os
import dotenv # Add this import
from django.core.wsgi import get_wsgi_application

# Load .env file
dotenv.load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')) # Add this line, adjust path if needed

# Use DJANGO_SETTINGS_MODULE from .env or default to development (or production in a real WSGI server setup)
settings_module = os.environ.get("DJANGO_SETTINGS_MODULE", "config.settings.development")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings_module)

application = get_wsgi_application()
