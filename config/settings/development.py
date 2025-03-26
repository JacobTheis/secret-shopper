
from .base import *  # noqa: F403 F401

# Development-specific settings
DEBUG = True

ALLOWED_HOSTS = []

# Add any development-specific apps here if needed later
# INSTALLED_APPS += [
#     'debug_toolbar',
# ]

# Add development-specific middleware if needed later
# MIDDLEWARE += [
#     'debug_toolbar.middleware.DebugToolbarMiddleware',
# ]

# Development database (default is SQLite in base.py)
# DATABASES = { ... }

print("DEBUG:", DEBUG)
print("Loading development settings")
