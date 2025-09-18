"""
Feature extraction service with async support
Simplified timeout handling using asyncio
"""

import asyncio
from typing import Dict, Any, Optional
import logging
from urllib.parse import urlparse
import signal
from contextlib import contextmanager

from app.utils.error_handlers import FeatureExtractionError
from feature import FeatureExtraction

logger = logging.getLogger(__name__)

class TimeoutError(Exception):
    """Custom timeout error"""
    pass

@contextmanager
def timeout_handler(timeout: int):
    """Context manager for timeout handling"""
    def handler(signum, frame):
        raise TimeoutError(f"Operation timed out after {timeout} seconds")

    # Set up signal handler
    old_handler = signal.signal(signal.SIGALRM, handler)
    signal.alarm(timeout)

    try:
        yield
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old_handler)

class FeatureExtractionService:
    """Service for extracting URL features"""

    def __init__(self):
        self.timeout = 30  # Default timeout

    async def extract_features_async(self, url: str, timeout: Optional[int] = None) -> Dict[str, Any]:
        """
        Extract features from URL asynchronously

        Args:
            url: URL to analyze
            timeout: Custom timeout in seconds

        Returns:
            Dictionary of extracted features

        Raises:
            FeatureExtractionError: If extraction fails
        """
        timeout = timeout or self.timeout

        try:
            # Run feature extraction in executor to avoid blocking
            loop = asyncio.get_event_loop()
            features = await asyncio.wait_for(
                loop.run_in_executor(None, self._extract_features_sync, url),
                timeout=timeout
            )

            return features

        except asyncio.TimeoutError:
            raise FeatureExtractionError(f"Feature extraction timed out after {timeout} seconds")
        except Exception as e:
            logger.error(f"Feature extraction failed for {url}: {e}")
            raise FeatureExtractionError(f"Feature extraction failed: {e}")

    def _extract_features_sync(self, url: str) -> Dict[str, Any]:
        """Synchronous feature extraction with timeout"""
        try:
            # Use timeout context manager
            with timeout_handler(30):  # 30 second timeout
                extractor = FeatureExtraction(url)
                features_list = extractor.getFeaturesList()

                # Convert list to dictionary with proper feature names
                feature_names = [
                    'UsingIp', 'longUrl', 'shortUrl', 'symbol', 'having_symbol',
                    'redirecting', 'prefix_suffix', 'sub_domain', 'SSL_state',
                    'domain_registration', 'favicon', 'port', 'https_token',
                    'request_url', 'anchor_url', 'links_in_tags', 'sfh', 'email',
                    'abnormal_url', 'iframe', 'age_domain', 'dns_record', 'web_traffic',
                    'page_rank', 'google_index', 'links_pointing', 'statistical_report'
                ]

                if len(features_list) != len(feature_names):
                    raise FeatureExtractionError(f"Feature count mismatch: got {len(features_list)}, expected {len(feature_names)}")

                return dict(zip(feature_names, features_list))

        except TimeoutError as e:
            raise FeatureExtractionError(str(e))
        except Exception as e:
            raise FeatureExtractionError(f"Feature extraction error: {e}")

    def validate_url(self, url: str) -> bool:
        """Validate URL format"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False

    def extract_basic_features(self, url: str) -> Dict[str, Any]:
        """Extract basic URL features without external requests"""
        try:
            parsed = urlparse(url)

            features = {
                'url_length': len(url),
                'domain_length': len(parsed.netloc),
                'path_length': len(parsed.path),
                'has_special_chars': any(c in url for c in ['@', '-', '_', '.']),
                'scheme': parsed.scheme,
                'netloc': parsed.netloc,
                'path': parsed.path
            }

            return features

        except Exception as e:
            raise FeatureExtractionError(f"Basic feature extraction failed: {e}")

    async def health_check(self) -> Dict[str, Any]:
        """Service health check"""
        return {
            "status": "healthy",
            "service": "feature_extraction",
            "timeout": self.timeout,
            "timestamp": asyncio.get_event_loop().time()
        }