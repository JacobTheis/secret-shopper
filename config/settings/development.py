
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

import os

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME", "secret_shop_dev"),
        "USER": os.getenv("DB_USER", "secret_shop_user"),
        "PASSWORD": os.getenv("DB_PASSWORD", "dev_password"),
        "HOST": os.getenv("DB_HOST", "db"),
        "PORT": os.getenv("DB_PORT", "5432"),
    }
}
