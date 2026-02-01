"""
Bot Detection Detector
======================
Detects various types of bot detection mechanisms.
"""

from typing import Optional, Dict, Any
import re
from .models import DetectionResult, DetectionType


class BotDetector:
    """Detects if bot detection mechanisms are active"""

    def __init__(self):
        """Initialize detector with common patterns"""
        self.captcha_patterns = [
            r"captcha",
            r"recaptcha",
            r"hcaptcha",
            r"cloudflare",
            r"challenge",
            r"verify you are human",
            r"are you a robot",
            r"security check",
        ]

        self.rate_limit_patterns = [
            r"rate limit",
            r"too many requests",
            r"429",
            r"slow down",
            r"try again later",
        ]

        self.block_patterns = [
            r"access denied",
            r"forbidden",
            r"403",
            r"blocked",
            r"banned",
        ]

    def check_response(
        self,
        html_content: Optional[str] = None,
        status_code: Optional[int] = None,
        headers: Optional[Dict[str, str]] = None,
        url: Optional[str] = None,
    ) -> DetectionResult:
        """
        Check if response indicates bot detection

        Args:
            html_content: HTML response body
            status_code: HTTP status code
            headers: Response headers
            url: Current URL

        Returns:
            DetectionResult with detection status and details
        """
        indicators = []
        detection_type = None
        confidence = 0.0

        # Check status code
        if status_code:
            if status_code == 429:
                indicators.append(f"HTTP 429 status code")
                detection_type = DetectionType.RATE_LIMIT
                confidence = 0.95
            elif status_code == 403:
                indicators.append(f"HTTP 403 status code")
                detection_type = DetectionType.IP_BLOCK
                confidence = 0.85
            elif status_code >= 400:
                indicators.append(f"HTTP {status_code} error")
                confidence = 0.5

        # Check HTML content
        if html_content:
            html_lower = html_content.lower()

            # CAPTCHA detection
            for pattern in self.captcha_patterns:
                if re.search(pattern, html_lower):
                    indicators.append(f"CAPTCHA pattern found: {pattern}")
                    detection_type = DetectionType.CAPTCHA
                    confidence = max(confidence, 0.9)

            # Rate limit detection
            for pattern in self.rate_limit_patterns:
                if re.search(pattern, html_lower):
                    indicators.append(f"Rate limit pattern found: {pattern}")
                    if not detection_type:
                        detection_type = DetectionType.RATE_LIMIT
                    confidence = max(confidence, 0.85)

            # Block detection
            for pattern in self.block_patterns:
                if re.search(pattern, html_lower):
                    indicators.append(f"Block pattern found: {pattern}")
                    if not detection_type:
                        detection_type = DetectionType.IP_BLOCK
                    confidence = max(confidence, 0.8)

        # Check headers
        if headers:
            # Cloudflare detection
            if "cf-ray" in headers or "CF-RAY" in headers:
                indicators.append("Cloudflare detected")
                if not detection_type:
                    detection_type = DetectionType.CAPTCHA
                confidence = max(confidence, 0.7)

            # Rate limit headers
            if "retry-after" in headers or "Retry-After" in headers:
                indicators.append("Retry-After header present")
                if not detection_type:
                    detection_type = DetectionType.RATE_LIMIT
                confidence = max(confidence, 0.9)

        # Check URL
        if url:
            url_lower = url.lower()
            if "captcha" in url_lower or "challenge" in url_lower:
                indicators.append("CAPTCHA/challenge in URL")
                detection_type = DetectionType.CAPTCHA
                confidence = max(confidence, 0.95)

        # Determine if detected
        detected = confidence >= 0.5

        return DetectionResult(
            detected=detected,
            detection_type=detection_type,
            confidence=confidence,
            indicators=indicators,
            raw_data={"status_code": status_code, "url": url, "headers": headers},
        )

    def check_javascript_challenges(self, page_content: str) -> DetectionResult:
        """
        Check for JavaScript-based bot detection

        Args:
            page_content: Full page content including scripts

        Returns:
            DetectionResult
        """
        indicators = []
        confidence = 0.0

        js_patterns = [
            r"navigator\.webdriver",
            r"__webdriver_",
            r"bot.*detection",
            r"antibot",
            r"datadome",
            r"perimeterx",
            r"px-captcha",
        ]

        for pattern in js_patterns:
            if re.search(pattern, page_content, re.IGNORECASE):
                indicators.append(f"JS detection pattern: {pattern}")
                confidence = max(confidence, 0.75)

        detected = confidence >= 0.5

        return DetectionResult(
            detected=detected,
            detection_type=DetectionType.FINGERPRINT_MISMATCH if detected else None,
            confidence=confidence,
            indicators=indicators,
        )
