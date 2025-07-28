#!/usr/bin/env python3
"""
Simple HTTP Time Server

A FastAPI-based HTTP server that provides current UTC time through a REST API endpoint.
This server returns the current UTC time in ISO 8601 format.

Endpoints:
    GET /time - Returns current UTC time in ISO format

Usage:
    python time_server.py

Or run with uvicorn directly:
    uvicorn time_server:app --host 0.0.0.0 --port 8000

Author: GitHub MCP Client Project
"""

import logging
from datetime import datetime, timezone
from typing import Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import uvicorn


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI application
app = FastAPI(
    title="Time Server API",
    description="A simple HTTP server that returns current UTC time",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


@app.get("/", response_model=Dict[str, str])
async def root() -> Dict[str, str]:
    """
    Root endpoint providing basic API information.
    
    Returns:
        Dict[str, str]: Basic API information including name and available endpoints
    """
    return {
        "name": "Time Server API",
        "description": "A simple HTTP server that returns current UTC time",
        "endpoints": "/time - Get current UTC time"
    }


@app.get("/time", response_model=Dict[str, Any])
async def get_current_time() -> Dict[str, Any]:
    """
    Get current UTC time endpoint.
    
    Returns the current UTC time in ISO 8601 format along with metadata.
    
    Returns:
        Dict[str, Any]: JSON response containing:
            - utc_time: Current UTC time in ISO 8601 format
            - timezone: Timezone information (UTC)
            - timestamp: Unix timestamp
            - format: Format description
    
    Raises:
        HTTPException: 500 error if time retrieval fails
        
    Example:
        GET /time
        
        Response:
        {
            "utc_time": "2024-07-28T22:15:30.123456Z",
            "timezone": "UTC",
            "timestamp": 1722207330.123456,
            "format": "ISO 8601"
        }
    """
    try:
        # Get current UTC time
        now_utc = datetime.now(timezone.utc)
        
        # Format as ISO 8601 string
        iso_time = now_utc.isoformat()
        
        # Get Unix timestamp
        timestamp = now_utc.timestamp()
        
        logger.info(f"Time request served: {iso_time}")
        
        return {
            "utc_time": iso_time,
            "timezone": "UTC", 
            "timestamp": timestamp,
            "format": "ISO 8601"
        }
        
    except Exception as e:
        logger.error(f"Error getting current time: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve current time: {str(e)}"
        )


@app.get("/health", response_model=Dict[str, str])
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint.
    
    Returns:
        Dict[str, str]: Health status of the service
    """
    return {
        "status": "healthy",
        "service": "time-server"
    }


# Exception handler for general errors
@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception) -> JSONResponse:
    """
    Global exception handler for unhandled errors.
    
    Args:
        request: The request that caused the exception
        exc: The exception that was raised
        
    Returns:
        JSONResponse: Error response with details
    """
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": "An unexpected error occurred"
        }
    )


def main():
    """
    Main function to run the server.
    
    Starts the FastAPI application using uvicorn server on localhost:8000.
    """
    logger.info("Starting Time Server...")
    logger.info("API documentation available at: http://localhost:8000/docs")
    logger.info("Time endpoint available at: http://localhost:8000/time")
    
    try:
        uvicorn.run(
            "time_server:app",
            host="0.0.0.0",
            port=8000,
            log_level="info",
            reload=False
        )
    except KeyboardInterrupt:
        logger.info("Server shutdown requested by user")
    except Exception as e:
        logger.error(f"Server failed to start: {str(e)}")
        raise


if __name__ == "__main__":
    main()