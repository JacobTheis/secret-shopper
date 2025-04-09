"""
Django settings for re-secret-shop project.

This module imports the appropriate settings based on the DJANGO_SETTINGS_MODULE 
environment variable. By default, it will load development settings.

If DJANGO_SETTINGS_MODULE is not set, it defaults to 'config.settings.development'.

Available settings:
    - config.settings.development: For local development
    - config.settings.production: For production deployment
"""

import os
import sys
from pathlib import Path

# Get the settings module from environment variable
settings_module = os.environ.get(
    'DJANGO_SETTINGS_MODULE', 'config.settings.development')

# If DJANGO_SETTINGS_MODULE is not explicitly set, set it to the default
if 'DJANGO_SETTINGS_MODULE' not in os.environ:
    os.environ['DJANGO_SETTINGS_MODULE'] = settings_module

# Import appropriate settings based on DJANGO_SETTINGS_MODULE
if settings_module == 'config.settings.development':
    from .settings.development import *  # noqa
elif settings_module == 'config.settings.production':
    from .settings.production import *  # noqa
else:
    # If trying to import from a custom location, simply try to import from that location
    exec(f"from {settings_module} import *")  # noqa
