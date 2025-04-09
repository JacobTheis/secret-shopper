"""
Settings package initialization.

This package contains different settings configurations:
- base.py: Common settings shared by all environments
- development.py: Settings for local development
- production.py: Settings for production deployment

The actual settings used are determined by the DJANGO_SETTINGS_MODULE
environment variable, which should point to one of these modules.
"""