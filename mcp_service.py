#!/usr/bin/env python
"""
FastAPI service for handling MCP operations outside of Celery.

This service runs MCPServerStdio operations in a clean environment
without Celery's logging proxy interference.
"""

import os
import sys
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
import django
django.setup()

from utils.ai_integration.agents import FloorPlanSpecialistAgent
from utils.ai_integration.schemas import FloorPlanExtractionResult

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="MCP Service", description="Handles MCP operations for secret shopping")


class FloorPlanRequest(BaseModel):
    website_url: str


class FloorPlanResponse(BaseModel):
    success: bool
    data: Optional[dict] = None
    error: Optional[str] = None


@app.post("/extract-floor-plans", response_model=FloorPlanResponse)
async def extract_floor_plans(request: FloorPlanRequest):
    """Extract floor plans from a rental community website using MCP tools."""
    try:
        logger.info(f"Starting floor plan extraction for {request.website_url}")
        
        agent = FloorPlanSpecialistAgent(use_mcp_service=False)  # Use direct MCP in the service
        result = await agent.extract_floor_plans(request.website_url)
        
        logger.info(f"Successfully extracted {len(result.floor_plans_found)} floor plans")
        
        return FloorPlanResponse(
            success=True,
            data=result.model_dump()
        )
        
    except Exception as e:
        logger.error(f"Floor plan extraction failed: {str(e)}")
        return FloorPlanResponse(
            success=False,
            error=str(e)
        )


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "mcp-service"}


@app.get("/")
async def root():
    """Root endpoint with service info."""
    return {
        "service": "MCP Service",
        "version": "1.0.0",
        "description": "Handles MCP operations for secret shopping",
        "endpoints": [
            "/extract-floor-plans",
            "/health",
            "/docs"
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "mcp_service:app",
        host="127.0.0.1",
        port=8001,
        reload=True,
        log_level="info"
    )