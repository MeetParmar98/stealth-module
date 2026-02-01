"""
Profile Generator
=================
Generates realistic stealth profiles combining fingerprints and behavior.
"""

import sys
import os
import random
import uuid
from typing import Dict, Any, Optional
from datetime import datetime

# Add parent directories to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from .models import StealthProfile


class ProfileGenerator:
    """Generates realistic human-like profiles"""

    def __init__(self):
        """Initialize profile generator"""
        self.generated_profiles = []

    def generate_profile(
        self, profile_type: str = "random", seed: Optional[int] = None
    ) -> StealthProfile:
        """
        Generate a complete stealth profile

        Args:
            profile_type: Type of profile ('random', 'conservative', 'aggressive')
            seed: Random seed for reproducibility

        Returns:
            StealthProfile with fingerprint and behavior config
        """
        if seed:
            random.seed(seed)

        profile_id = str(uuid.uuid4())

        # Generate fingerprint
        fingerprint = self._generate_fingerprint(profile_type)

        # Generate behavior configuration
        behavior_config = self._generate_behavior_config(profile_type)

        profile = StealthProfile(
            profile_id=profile_id,
            fingerprint=fingerprint,
            behavior_config=behavior_config,
            created_at=datetime.now(),
        )

        self.generated_profiles.append(profile)
        return profile

    def _generate_fingerprint(self, profile_type: str) -> Dict[str, Any]:
        """Generate browser fingerprint data"""
        try:
            # Import fingerprinting modules - use relative imports
            import sys
            import os

            # Get the parent directory (stealth-sys)
            parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            fingerprint_dir = os.path.join(parent_dir, "browser-fingerprinting")

            # Add to path if not already there
            if fingerprint_dir not in sys.path:
                sys.path.insert(0, fingerprint_dir)

            import user_agents
            import screen_sizes
            import languages
            import timezones
            import fonts
            import plugins
            import hardware_concurrency
            import webgl_canvas

            # Select user agent
            user_agent = random.choice(user_agents.USER_AGENTS)

            # Select screen size (it's a tuple)
            screen_width, screen_height = random.choice(screen_sizes.SCREEN_SIZES)

            # Select language
            language = random.choice(languages.LANGUAGES)

            # Select timezone
            timezone = random.choice(timezones.TIMEZONES)

            # Select fonts - just use the FONTS list
            num_fonts = random.randint(20, 40)
            font_list = random.sample(fonts.FONTS, min(num_fonts, len(fonts.FONTS)))

            # Select plugins based on browser type
            browser_type = "chrome"  # Default to chrome
            if "firefox" in user_agent.lower():
                browser_type = "firefox"
            elif "safari" in user_agent.lower():
                browser_type = "safari"
            elif "edge" in user_agent.lower():
                browser_type = "edge"

            plugin_list = plugins.PLUGIN_SETS.get(browser_type, [])

            # Select hardware concurrency
            device_type = "desktop"  # Default
            if "mobile" in user_agent.lower() or "android" in user_agent.lower():
                device_type = "mobile"
            elif "macbook" in user_agent.lower() or "laptop" in user_agent.lower():
                device_type = "laptop"

            cores = random.choice(
                hardware_concurrency.HARDWARE_CONCURRENCY.get(device_type, [4, 8])
            )

            # Select WebGL/Canvas fingerprint
            webgl_vendor = random.choice(webgl_canvas.GPU_VENDORS)
            webgl_renderer = random.choice(webgl_canvas.GPU_RENDERERS)

            fingerprint = {
                "user_agent": user_agent,
                "screen_width": screen_width,
                "screen_height": screen_height,
                "color_depth": 24,
                "language": language,
                "timezone": timezone,
                "fonts": font_list,
                "plugins": plugin_list,
                "hardware_concurrency": cores,
                "webgl_vendor": webgl_vendor,
                "webgl_renderer": webgl_renderer,
                "platform": self._extract_platform(user_agent),
                "do_not_track": random.choice([None, "1"]),
                "canvas_fingerprint": self._generate_canvas_hash(),
            }

        except ImportError:
            # Fallback if fingerprinting modules not available
            fingerprint = self._generate_fallback_fingerprint()

        return fingerprint

    def _generate_behavior_config(self, profile_type: str) -> Dict[str, Any]:
        """Generate human behavior configuration"""
        # Base configuration
        if profile_type == "conservative":
            config = {
                "mouse_dpi": random.choice([400, 800]),
                "polling_rate": random.choice([125, 250]),
                "typing_speed_wpm": random.randint(30, 50),
                "error_rate": random.uniform(0.01, 0.03),
                "scroll_speed": random.uniform(0.5, 0.8),
                "pause_frequency": random.uniform(0.3, 0.5),
                "enable_context_aware": True,
            }
        elif profile_type == "aggressive":
            config = {
                "mouse_dpi": random.choice([1600, 3200]),
                "polling_rate": random.choice([500, 1000]),
                "typing_speed_wpm": random.randint(70, 100),
                "error_rate": random.uniform(0.005, 0.015),
                "scroll_speed": random.uniform(1.2, 1.8),
                "pause_frequency": random.uniform(0.1, 0.2),
                "enable_context_aware": True,
            }
        else:  # random/balanced
            config = {
                "mouse_dpi": random.choice([800, 1200, 1600]),
                "polling_rate": random.choice([250, 500]),
                "typing_speed_wpm": random.randint(50, 70),
                "error_rate": random.uniform(0.015, 0.025),
                "scroll_speed": random.uniform(0.8, 1.2),
                "pause_frequency": random.uniform(0.2, 0.4),
                "enable_context_aware": True,
            }

        return config

    def _extract_platform(self, user_agent: str) -> str:
        """Extract platform from user agent"""
        ua_lower = user_agent.lower()
        if "windows" in ua_lower:
            return "Win32"
        elif "mac" in ua_lower:
            return "MacIntel"
        elif "linux" in ua_lower:
            return "Linux x86_64"
        else:
            return "Win32"

    def _generate_canvas_hash(self) -> str:
        """Generate a realistic canvas fingerprint hash"""
        return "".join(random.choices("0123456789abcdef", k=32))

    def _generate_fallback_fingerprint(self) -> Dict[str, Any]:
        """Generate fallback fingerprint if modules unavailable"""
        return {
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "screen_width": 1920,
            "screen_height": 1080,
            "color_depth": 24,
            "language": "en-US",
            "timezone": "America/New_York",
            "fonts": ["Arial", "Times New Roman", "Courier New"],
            "plugins": [],
            "hardware_concurrency": 4,
            "webgl_vendor": "Google Inc.",
            "webgl_renderer": "ANGLE",
            "platform": "Win32",
            "do_not_track": None,
            "canvas_fingerprint": self._generate_canvas_hash(),
        }

    def get_best_profile(self) -> Optional[StealthProfile]:
        """Get the profile with highest success rate"""
        if not self.generated_profiles:
            return None

        return max(
            self.generated_profiles, key=lambda p: (p.success_rate, p.success_count)
        )

    def remove_failed_profiles(self, threshold: float = 0.3):
        """Remove profiles with success rate below threshold"""
        self.generated_profiles = [
            p
            for p in self.generated_profiles
            if p.success_rate >= threshold or (p.success_count + p.failure_count) < 5
        ]
