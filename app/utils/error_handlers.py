"""
Custom error handlers for the application
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class FeatureExtractionError(Exception):
    """Custom exception for feature extraction errors"""
    pass

class PredictionError(Exception):
    """Custom exception for prediction errors"""
    pass

class ServiceUnavailableError(Exception):
    """Custom exception for service unavailable errors"""
    pass

class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass

def setup_error_handlers(app: FastAPI) -> None:
    """Setup custom error handlers for the application"""

    @app.exception_handler(FeatureExtractionError)
    async def feature_extraction_error_handler(request: Request, exc: FeatureExtractionError):
        """Handle feature extraction errors"""
        logger.error(f"Feature extraction error: {exc}")
        return JSONResponse(
            status_code=400,
            content={
                "error": "FeatureExtractionError",
                "message": str(exc),
                "type": "feature_extraction_error"
            }
        )

    @app.exception_handler(PredictionError)
    async def prediction_error_handler(request: Request, exc: PredictionError):
        """Handle prediction errors"""
        logger.error(f"Prediction error: {exc}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "PredictionError",
                "message": str(exc),
                "type": "prediction_error"
            }
        )

    @app.exception_handler(ServiceUnavailableError)
    async def service_unavailable_error_handler(request: Request, exc: ServiceUnavailableError):
        """Handle service unavailable errors"""
        logger.error(f"Service unavailable error: {exc}")
        return JSONResponse(
            status_code=503,
            content={
                "error": "ServiceUnavailableError",
                "message": str(exc),
                "type": "service_unavailable_error"
            }
        )

    @app.exception_handler(ValidationError)
    async def validation_error_handler(request: Request, exc: ValidationError):
        """Handle validation errors"""
        logger.error(f"Validation error: {exc}")
        return JSONResponse(
            status_code=422,
            content={
                "error": "ValidationError",
                "message": str(exc),
                "type": "validation_error"
            }
        )

    @app.exception_handler(RequestValidationError)
    async def request_validation_error_handler(request: Request, exc: RequestValidationError):
        """Handle FastAPI request validation errors"""
        logger.error(f"Request validation error: {exc}")
        return JSONResponse(
            status_code=422,
            content={
                "error": "RequestValidationError",
                "message": "Invalid request parameters",
                "details": exc.errors(),
                "type": "request_validation_error"
            }
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        """Handle HTTP exceptions"""
        logger.error(f"HTTP error: {exc.status_code} - {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": "HTTPError",
                "message": exc.detail,
                "type": "http_error"
            }
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle all other exceptions"""
        logger.error(f"Unexpected error: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": "InternalServerError",
                "message": "An unexpected error occurred",
                "type": "internal_server_error"
            }
        )

def create_error_response(
    status_code: int,
    error_type: str,
    message: str,
    details: Dict[str, Any] = None
) -> JSONResponse:
    """Create a standardized error response"""
    response = {
        "error": error_type,
        "message": message,
        "type": error_type.lower()
    }

    if details:
        response["details"] = details

    return JSONResponse(status_code=status_code, content=response)

class ErrorResponse:
    """Standardized error response format"""

    @staticmethod
    def bad_request(message: str, details: Dict[str, Any] = None) -> JSONResponse:
        return create_error_response(400, "BadRequest", message, details)

    @staticmethod
    def unauthorized(message: str = "Unauthorized") -> JSONResponse:
        return create_error_response(401, "Unauthorized", message)

    @staticmethod
    def forbidden(message: str = "Forbidden") -> JSONResponse:
        return create_error_response(403, "Forbidden", message)

    @staticmethod
    def not_found(message: str = "Resource not found") -> JSONResponse:
        return create_error_response(404, "NotFound", message)

    @staticmethod
    def validation_error(message: str, details: Dict[str, Any] = None) -> JSONResponse:
        return create_error_response(422, "ValidationError", message, details)

    @staticmethod
    def server_error(message: str = "Internal server error") -> JSONResponse:
        return create_error_response(500, "InternalServerError", message)

    @staticmethod
    def service_unavailable(message: str = "Service unavailable") -> JSONResponse:
        return create_error_response(503, "ServiceUnavailable", message)