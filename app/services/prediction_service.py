"""
Prediction service for ML model inference
Async-based with proper error handling
"""

import pickle
import numpy as np
import asyncio
from typing import Dict, Any, Optional
import logging
from pathlib import Path

from app.utils.error_handlers import PredictionError

logger = logging.getLogger(__name__)

class PredictionService:
    """Service for handling ML model predictions"""

    def __init__(self):
        self.model = None
        self.model_path = Path("pickle/model.pkl")
        self.is_initialized = False

    async def initialize(self) -> None:
        """Initialize the prediction service"""
        try:
            await self._load_model_async()
            self.is_initialized = True
            logger.info("Prediction service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize prediction service: {e}")
            raise PredictionError(f"Model loading failed: {e}")

    async def _load_model_async(self) -> None:
        """Load ML model in a separate thread to avoid blocking"""
        loop = asyncio.get_event_loop()

        def load_model():
            try:
                with open(self.model_path, "rb") as f:
                    return pickle.load(f)
            except FileNotFoundError:
                raise PredictionError(f"Model file not found: {self.model_path}")
            except Exception as e:
                raise PredictionError(f"Failed to load model: {e}")

        self.model = await loop.run_in_executor(None, load_model)

        if not self.model:
            raise PredictionError("Model loaded but is None")

    async def predict_async(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make prediction asynchronously

        Args:
            features: Dictionary of extracted features

        Returns:
            Dict containing prediction and confidence

        Raises:
            PredictionError: If prediction fails
        """
        if not self.is_initialized:
            raise PredictionError("Service not initialized")

        if not self.model:
            raise PredictionError("Model not loaded")

        try:
            # Convert features to model input format
            feature_vector = self._prepare_features(features)

            # Make prediction in executor to avoid blocking
            loop = asyncio.get_event_loop()
            prediction = await loop.run_in_executor(
                None,
                self._make_prediction,
                feature_vector
            )

            return {
                "prediction": prediction["prediction"],
                "confidence": prediction["confidence"],
                "features_processed": len(feature_vector)
            }

        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            raise PredictionError(f"Prediction failed: {e}")

    def _prepare_features(self, features: Dict[str, Any]) -> np.ndarray:
        """Convert feature dictionary to numpy array"""
        try:
            # Extract feature values in expected order
            # This should match the original feature extraction order
            feature_order = [
                'UsingIp', 'longUrl', 'shortUrl', 'symbol', 'having_symbol',
                'redirecting', 'prefix_suffix', 'sub_domain', 'SSL_state',
                'domain_registration', 'favicon', 'port', 'https_token',
                'request_url', 'anchor_url', 'links_in_tags', 'sfh', 'email',
                'abnormal_url', 'iframe', 'age_domain', 'dns_record', 'web_traffic',
                'page_rank', 'google_index', 'links_pointing', 'statistical_report',
                'Extra_Feature_1', 'Extra_Feature_2', 'Extra_Feature_3'
            ]

            feature_vector = []
            for feature_name in feature_order:
                value = features.get(feature_name, 0)
                if isinstance(value, str):
                    # Convert string features to numeric
                    value = 1 if value.lower() in ['yes', 'true', '1'] else 0
                feature_vector.append(float(value))

            return np.array(feature_vector).reshape(1, -1)

        except Exception as e:
            raise PredictionError(f"Feature preparation failed: {e}")

    def _make_prediction(self, features: np.ndarray) -> Dict[str, Any]:
        """Make prediction using loaded model"""
        try:
            # Get prediction probabilities
            if hasattr(self.model, 'predict_proba'):
                probabilities = self.model.predict_proba(features)
                prediction = self.model.predict(features)[0]
                confidence = float(max(probabilities[0]))
            else:
                # Fallback for models without predict_proba
                prediction = self.model.predict(features)[0]
                confidence = 1.0

            return {
                "prediction": int(prediction),
                "confidence": confidence
            }

        except Exception as e:
            raise PredictionError(f"Model prediction failed: {e}")

    async def cleanup(self) -> None:
        """Cleanup resources"""
        self.model = None
        self.is_initialized = False
        logger.info("Prediction service cleaned up")

    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        if not self.model:
            return {"status": "not_loaded"}

        return {
            "status": "loaded",
            "model_type": type(self.model).__name__,
            "model_path": str(self.model_path),
            "is_initialized": self.is_initialized
        }