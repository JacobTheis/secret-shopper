
import os
from .base import *  # noqa: F403 F401
# import dj_database_url # Needs dj-database-url installed

# Production-specific settings
DEBUG = False

# Get SECRET_KEY from environment variable
SECRET_KEY = os.environ.get('SECRET_KEY', 'fallback-secret-key-if-not-set') # Replace fallback or ensure it's always set

# Get ALLOWED_HOSTS from environment variable (comma-separated string)
allowed_hosts_str = os.environ.get('ALLOWED_HOSTS', '')
ALLOWED_HOSTS = [host.strip() for host in allowed_hosts_str.split(',') if host.strip()]

# Configure database from DATABASE_URL environment variable
# DATABASE_URL = os.environ.get('DATABASE_URL')
# if DATABASE_URL:
#     DATABASES = {
#         'default': dj_database_url.config(default=DATABASE_URL, conn_max_age=600)
#     }
# else:
#     # Fallback or raise error if DATABASE_URL is not set in production
#     print("WARNING: DATABASE_URL environment variable not set for production.")
#     # DATABASES = { ... } # Define a fallback if absolutely necessary

# Static files configuration for production (using WhiteNoise)
# Ensure 'whitenoise.middleware.WhiteNoiseMiddleware' is added to MIDDLEWARE
# MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware') # Insert after SecurityMiddleware
# STATIC_ROOT = BASE_DIR / 'staticfiles' # Directory where collectstatic will gather files
# STORAGES = {
#     "staticfiles": {
#         "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
#     },
# }


# Add any other production-specific settings:
# - Logging configuration
# - Email backend (e.g., SMTP)
# - Security settings (CSRF_COOKIE_SECURE, SESSION_COOKIE_SECURE, SECURE_SSL_REDIRECT, etc.)

# Production security settings
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Production AI Integration Settings - Must be provided through environment variables
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")  # Will raise error if not set in environment
OPENAI_ORG_ID = os.environ.get("OPENAI_ORG_ID", "")

# Ensure API keys are set
if not OPENAI_API_KEY:
    # Log error but don't raise exception to allow app to start
    # This gives flexibility to have components not dependent on AI still work
    print("WARNING: OPENAI_API_KEY environment variable not set for production.")

print("DEBUG:", DEBUG)
print("Loading production settings")

# Ensure sensitive information like SECRET_KEY is not printed or logged carelessly.
