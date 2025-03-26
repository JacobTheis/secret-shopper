"""
ASGI config for config project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os
import dotenv # Add this import
from django.core.asgi import get_asgi_application

# Load .env file
dotenv.load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')) # Add this line, adjust path if needed

# Use DJANGO_SETTINGS_MODULE from .env or default to development (or production in a real ASGI server setup)
settings_module = os.environ.get("DJANGO_SETTINGS_MODULE", "config.settings.development")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings_module)

application = get_asgi_application()
