"""
FastAPI main application entry point
Modern async-based architecture with proper error handling
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
import logging
from contextlib import asynccontextmanager
import uvicorn

# Import routes
from app.routes import analysis, api
from app.services.prediction_service import PredictionService
from app.utils.error_handlers import setup_error_handlers
from app.utils.logger import setup_logging

# Global service instance
prediction_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    global prediction_service
    prediction_service = PredictionService()
    await prediction_service.initialize()

    logging.info("Application started successfully")

    yield

    # Shutdown
    if prediction_service:
        await prediction_service.cleanup()
    logging.info("Application shutdown complete")

# Create FastAPI app
app = FastAPI(
    title="Phishing URL Detection API",
    description="Modern API for detecting phishing websites with machine learning",
    version="2.0.0",
    lifespan=lifespan
)

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup logging
setup_logging()

# Setup error handlers
setup_error_handlers(app)

# Include routers
app.include_router(analysis.router, prefix="/api/v1", tags=["analysis"])
app.include_router(api.router, prefix="/api/v1", tags=["api"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Phishing URL Detection API",
        "version": "2.0.0",
        "status": "healthy"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "service": "phishing-detector"
    }

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )