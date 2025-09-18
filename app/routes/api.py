"""
General API routes
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from datetime import datetime

router = APIRouter()

class APIInfo(BaseModel):
    """API information model"""
    name: str
    version: str
    description: str
    endpoints: List[str]
    documentation_url: str

@router.get("/info", response_model=APIInfo)
async def get_api_info():
    """Get API information and available endpoints"""
    return APIInfo(
        name="Phishing URL Detection API",
        version="2.0.0",
        description="Modern API for detecting phishing websites with machine learning",
        endpoints=[
            "POST /api/v1/analyze - Analyze URL for phishing",
            "GET /api/v1/analysis/{request_id} - Get analysis result",
            "GET /api/v1/info - Get API information",
            "GET /api/v1/health - Health check",
            "GET /docs - API documentation"
        ],
        documentation_url="/docs"
    )

@router.get("/stats")
async def get_api_stats():
    """Get API usage statistics"""
    # TODO: Implement statistics tracking
    return {
        "total_requests": 0,
        "successful_predictions": 0,
        "average_response_time": 0.0,
        "uptime_seconds": 0,
        "timestamp": datetime.now()
    }

@router.get("/health")
async def api_health():
    """API health check"""
    return {
        "status": "healthy",
        "service": "api",
        "timestamp": datetime.now()
    }