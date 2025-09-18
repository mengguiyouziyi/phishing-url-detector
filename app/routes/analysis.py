"""
Analysis routes for phishing URL detection
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, HttpUrl
from typing import Optional, Dict, Any
import asyncio
from datetime import datetime

from app.services.prediction_service import PredictionService
from app.services.feature_extraction_service import FeatureExtractionService
from app.utils.error_handlers import FeatureExtractionError, PredictionError

router = APIRouter()

class URLRequest(BaseModel):
    """URL analysis request model"""
    url: HttpUrl
    timeout: Optional[int] = 30
    include_features: Optional[bool] = False

class AnalysisResponse(BaseModel):
    """Analysis response model"""
    url: str
    is_phishing: bool
    confidence: float
    prediction_time: float
    features: Optional[Dict[str, Any]] = None
    timestamp: datetime
    request_id: str

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_url(
    request: URLRequest,
    background_tasks: BackgroundTasks
):
    """
    Analyze a URL for phishing characteristics

    Args:
        request: URL analysis request

    Returns:
        AnalysisResponse: Analysis results

    Raises:
        HTTPException: If analysis fails
    """
    try:
        # Get global service instance
        from app.main import prediction_service

        if not prediction_service:
            raise HTTPException(status_code=503, detail="Service not initialized")

        # Generate unique request ID
        request_id = f"req_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(request.url) % 10000:04d}"

        # Start timing
        start_time = asyncio.get_event_loop().time()

        # Extract features
        feature_service = FeatureExtractionService()
        features = await feature_service.extract_features_async(
            str(request.url),
            timeout=request.timeout
        )

        # Make prediction
        result = await prediction_service.predict_async(features)

        # Calculate prediction time
        prediction_time = asyncio.get_event_loop().time() - start_time

        # Prepare response
        response_data = {
            "url": str(request.url),
            "is_phishing": bool(result["prediction"]),
            "confidence": float(result["confidence"]),
            "prediction_time": prediction_time,
            "timestamp": datetime.now(),
            "request_id": request_id
        }

        # Include features if requested
        if request.include_features:
            response_data["features"] = features

        return AnalysisResponse(**response_data)

    except FeatureExtractionError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PredictionError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.get("/analysis/{request_id}")
async def get_analysis_result(request_id: str):
    """
    Get analysis result by request ID

    Args:
        request_id: Unique request identifier

    Returns:
        Analysis result or 404 if not found
    """
    # TODO: Implement result caching and retrieval
    raise HTTPException(status_code=501, detail="Not implemented yet")

@router.get("/health")
async def analysis_health():
    """Analysis service health check"""
    return {
        "status": "healthy",
        "service": "analysis",
        "timestamp": datetime.now()
    }