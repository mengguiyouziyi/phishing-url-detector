#!/usr/bin/env python3
"""
Test suite for the new FastAPI application
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.main import app

class TestFastAPIApp:
    """Test cases for the FastAPI application"""

    def setup_method(self):
        """Setup test client"""
        self.client = TestClient(app)

    def test_root_endpoint(self):
        """Test the root endpoint"""
        response = self.client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "status" in data

    def test_health_check(self):
        """Test the health check endpoint"""
        response = self.client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data

    def test_api_info(self):
        """Test the API info endpoint"""
        response = self.client.get("/api/v1/info")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Phishing URL Detection API"
        assert data["version"] == "2.0.0"
        assert "endpoints" in data

    def test_analysis_health(self):
        """Test the analysis health endpoint"""
        response = self.client.get("/api/v1/analyze/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_analyze_endpoint_invalid_url(self):
        """Test analyze endpoint with invalid URL"""
        response = self.client.post(
            "/api/v1/analyze",
            json={"url": "not-a-valid-url"}
        )
        assert response.status_code == 422  # Validation error

    @patch('app.services.feature_extraction_service.FeatureExtractionService.extract_features_async')
    @patch('app.services.prediction_service.PredictionService.predict_async')
    def test_analyze_endpoint_mocked(self, mock_predict, mock_extract):
        """Test analyze endpoint with mocked services"""
        # Mock feature extraction
        mock_extract.return_value = {
            'UsingIp': 0, 'longUrl': 0, 'shortUrl': 0, 'symbol': 0,
            'having_symbol': 0, 'redirecting': 0, 'prefix_suffix': 0,
            'sub_domain': 0, 'SSL_state': 0, 'domain_registration': 0,
            'favicon': 0, 'port': 0, 'https_token': 0, 'request_url': 0,
            'anchor_url': 0, 'links_in_tags': 0, 'sfh': 0, 'email': 0,
            'abnormal_url': 0, 'iframe': 0, 'age_domain': 0, 'dns_record': 0,
            'web_traffic': 0, 'page_rank': 0, 'google_index': 0,
            'links_pointing': 0, 'statistical_report': 0
        }

        # Mock prediction
        mock_predict.return_value = {
            "prediction": 0,
            "confidence": 0.95
        }

        # Test valid URL
        response = self.client.post(
            "/api/v1/analyze",
            json={"url": "https://example.com"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "url" in data
        assert "is_phishing" in data
        assert "confidence" in data
        assert "prediction_time" in data
        assert "request_id" in data

    def test_cors_headers(self):
        """Test that CORS headers are properly set"""
        response = self.client.get("/")
        assert "access-control-allow-origin" in response.headers

    def test_api_docs_accessible(self):
        """Test that API documentation is accessible"""
        response = self.client.get("/docs")
        assert response.status_code == 200

    def test_openapi_spec(self):
        """Test that OpenAPI specification is accessible"""
        response = self.client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert "info" in data

if __name__ == "__main__":
    # Run tests manually
    import unittest
    unittest.main()