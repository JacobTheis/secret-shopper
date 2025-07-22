#!/bin/bash

# Start MCP Service
# This script starts the FastAPI MCP service on port 8001

set -e

echo "Starting MCP Service..."

# Activate virtual environment
source venv/bin/activate

# Set environment variables
export DJANGO_SETTINGS_MODULE=config.settings.development

# Start the service
echo "MCP Service will be available at http://127.0.0.1:8001"
echo "API documentation at http://127.0.0.1:8001/docs"
echo ""

python mcp_service.py