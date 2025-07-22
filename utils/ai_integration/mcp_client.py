"""
Client for communicating with the MCP service.

This module provides a client interface for making requests to the 
separate MCP service that handles MCPServerStdio operations.
"""

import logging
import httpx
from typing import Optional
from .schemas import FloorPlanExtractionResult

logger = logging.getLogger(__name__)


class MCPServiceClient:
    """Client for the MCP service."""
    
    def __init__(self, base_url: str = "http://127.0.0.1:8001"):
        """Initialize the MCP service client.
        
        Args:
            base_url: Base URL of the MCP service
        """
        self.base_url = base_url
        self.timeout = 300  # 5 minutes for MCP operations
    
    async def extract_floor_plans(self, website_url: str) -> FloorPlanExtractionResult:
        """Extract floor plans using the MCP service.
        
        Args:
            website_url: The URL of the community website to analyze
            
        Returns:
            FloorPlanExtractionResult with extracted data
            
        Raises:
            Exception: If the MCP service call fails
        """
        try:
            logger.info(f"Calling MCP service for floor plan extraction: {website_url}")
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/extract-floor-plans",
                    json={"website_url": website_url}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get("success"):
                        # Convert response back to FloorPlanExtractionResult
                        result_data = data.get("data", {})
                        return FloorPlanExtractionResult(**result_data)
                    else:
                        error_msg = data.get("error", "Unknown error from MCP service")
                        logger.error(f"MCP service returned error: {error_msg}")
                        raise Exception(f"MCP service error: {error_msg}")
                else:
                    logger.error(f"MCP service returned {response.status_code}: {response.text}")
                    raise Exception(f"MCP service HTTP {response.status_code}: {response.text}")
                    
        except httpx.TimeoutException:
            logger.error(f"MCP service timeout for {website_url}")
            raise Exception("MCP service timeout")
        except httpx.RequestError as e:
            logger.error(f"MCP service request error: {str(e)}")
            raise Exception(f"MCP service connection error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error calling MCP service: {str(e)}")
            raise
    
    async def health_check(self) -> bool:
        """Check if the MCP service is healthy.
        
        Returns:
            True if service is healthy, False otherwise
        """
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(f"{self.base_url}/health")
                return response.status_code == 200
        except Exception as e:
            logger.warning(f"MCP service health check failed: {str(e)}")
            return False