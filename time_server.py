#!/usr/bin/env python3
"""
Simple HTTP Time Server

A FastAPI-based HTTP server that provides a GET /time endpoint
returning the current UTC time in ISO format.

Usage:
    python time_server.py

API Endpoints:
    GET /time - Returns current UTC time in ISO format

Example Response:
    {
        "current_time": "2024-01-15T10:30:45.123456Z",
        "timezone": "UTC",
        "timestamp": 1705316245.123456
    }
"""

import logging
from datetime import datetime, timezone
from typing import Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="Simple Time Server",
    description="A simple HTTP server that returns the current UTC time",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


@app.get("/time", response_model=Dict[str, Any])
async def get_current_time() -> JSONResponse:
    """
    Get the current UTC time in ISO format.
    
    Returns:
        JSONResponse: A JSON object containing:
            - current_time: ISO formatted UTC time string
            - timezone: Always "UTC"
            - timestamp: Unix timestamp as float
            
    Raises:
        HTTPException: 500 if there's an error getting the current time
        
    Example:
        GET /time
        
        Response:
        {
            "current_time": "2024-01-15T10:30:45.123456Z",
            "timezone": "UTC", 
            "timestamp": 1705316245.123456
        }
    """
    try:
        # Get current UTC time
        now_utc = datetime.now(timezone.utc)
        
        # Format as ISO string with timezone info
        iso_time = now_utc.isoformat().replace("+00:00", "Z")
        
        # Get Unix timestamp
        timestamp = now_utc.timestamp()
        
        response_data = {
            "current_time": iso_time,
            "timezone": "UTC",
            "timestamp": timestamp
        }
        
        logger.info(f"Time request served: {iso_time}")
        return JSONResponse(content=response_data)
        
    except Exception as e:
        logger.error(f"Error getting current time: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error while getting current time: {str(e)}"
        )


@app.get("/")
async def root() -> JSONResponse:
    """
    Root endpoint providing API information.
    
    Returns:
        JSONResponse: Basic API information
    """
    return JSONResponse(content={
        "message": "Simple Time Server API",
        "version": "1.0.0",
        "endpoints": {
            "/time": "GET - Returns current UTC time",
            "/docs": "GET - Interactive API documentation",
            "/redoc": "GET - Alternative API documentation"
        }
    })


@app.get("/health")
async def health_check() -> JSONResponse:
    """
    Health check endpoint.
    
    Returns:
        JSONResponse: Health status
    """
    return JSONResponse(content={
        "status": "healthy",
        "service": "time-server"
    })


if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting Simple Time Server...")
    logger.info("API Documentation available at: http://localhost:8000/docs")
    logger.info("Time endpoint available at: http://localhost:8000/time")
    
    # Run the server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )