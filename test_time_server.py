#!/usr/bin/env python3
"""
Test script for the Simple Time Server.

This script validates that the time server works correctly and meets the requirements.
"""

import asyncio
import json
import subprocess
import sys
import time
from datetime import datetime, timezone

import httpx
from fastapi.testclient import TestClient

# Import our time server app
from time_server import app


def test_time_endpoint_format():
    """Test that the /time endpoint returns correctly formatted data."""
    print("🧪 Testing /time endpoint format...")
    
    client = TestClient(app)
    response = client.get("/time")
    
    # Check status code
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    # Parse JSON
    data = response.json()
    
    # Check required fields
    required_fields = ["current_time", "timezone", "timestamp"]
    for field in required_fields:
        assert field in data, f"Missing required field: {field}"
    
    # Check timezone is UTC
    assert data["timezone"] == "UTC", f"Expected timezone UTC, got {data['timezone']}"
    
    # Check ISO format - should end with Z and be parseable
    time_str = data["current_time"]
    assert time_str.endswith("Z"), f"Time should end with Z, got: {time_str}"
    
    # Parse the ISO time to validate format
    try:
        parsed_time = datetime.fromisoformat(time_str.replace("Z", "+00:00"))
        assert parsed_time.tzinfo is not None, "Parsed time should have timezone info"
    except ValueError as e:
        assert False, f"Invalid ISO format: {e}"
    
    # Check timestamp is a number and reasonable
    timestamp = data["timestamp"]
    assert isinstance(timestamp, (int, float)), f"Timestamp should be number, got {type(timestamp)}"
    assert timestamp > 0, f"Timestamp should be positive, got {timestamp}"
    
    print("✅ /time endpoint format test passed")


def test_time_accuracy():
    """Test that the returned time is reasonably accurate."""
    print("🧪 Testing time accuracy...")
    
    client = TestClient(app)
    
    # Get current time before request
    before = datetime.now(timezone.utc)
    response = client.get("/time")
    after = datetime.now(timezone.utc)
    
    data = response.json()
    time_str = data["current_time"]
    
    # Parse the returned time
    returned_time = datetime.fromisoformat(time_str.replace("Z", "+00:00"))
    
    # Check that returned time is between before and after (allowing 1 second margin)
    before_margin = before.timestamp() - 1
    after_margin = after.timestamp() + 1
    returned_timestamp = returned_time.timestamp()
    
    assert before_margin <= returned_timestamp <= after_margin, \
        f"Time {returned_timestamp} not between {before_margin} and {after_margin}"
    
    print("✅ Time accuracy test passed")


def test_other_endpoints():
    """Test other endpoints for basic functionality."""
    print("🧪 Testing other endpoints...")
    
    client = TestClient(app)
    
    # Test root endpoint
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "endpoints" in data
    
    # Test health endpoint
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "time-server"
    
    print("✅ Other endpoints test passed")


def test_error_handling():
    """Test error handling for invalid requests."""
    print("🧪 Testing error handling...")
    
    client = TestClient(app)
    
    # Test POST to /time (should return 405 Method Not Allowed)
    response = client.post("/time")
    assert response.status_code == 405
    
    # Test invalid endpoint (should return 404)
    response = client.get("/invalid-endpoint")
    assert response.status_code == 404
    
    print("✅ Error handling test passed")


def test_openapi_docs():
    """Test that OpenAPI documentation is available."""
    print("🧪 Testing OpenAPI documentation...")
    
    client = TestClient(app)
    
    # Test docs endpoint
    response = client.get("/docs")
    assert response.status_code == 200
    assert "swagger" in response.text.lower()
    
    # Test OpenAPI spec
    response = client.get("/openapi.json")
    assert response.status_code == 200
    spec = response.json()
    assert "openapi" in spec
    assert "paths" in spec
    assert "/time" in spec["paths"]
    
    print("✅ OpenAPI documentation test passed")


def main():
    """Run all tests."""
    print("Simple Time Server - Test Suite")
    print("===============================")
    print()
    
    try:
        test_time_endpoint_format()
        test_time_accuracy()
        test_other_endpoints()
        test_error_handling()
        test_openapi_docs()
        
        print()
        print("🎉 All tests passed!")
        print()
        print("The time server meets all requirements:")
        print("✅ Provides GET /time endpoint")
        print("✅ Returns current UTC time in ISO format")
        print("✅ Includes proper error handling")
        print("✅ Has comprehensive documentation")
        print("✅ Uses FastAPI framework")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)