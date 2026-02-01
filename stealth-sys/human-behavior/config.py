# human-behavior/config.py
"""
Configuration presets for different user profiles
"""

from typing import Dict, Any


class BehaviorProfile:
    """Predefined behavior profiles"""

    CAUTIOUS_USER = {
        "mouse_dpi": 800,
        "polling_rate": 500,
        "typing_speed_wpm": 35,
        "error_rate": 0.03,
        "fatigue_rate": 1.2,  # Tires faster
        "scroll_preference": "wheel",
        "state_durations": "long",  # Stays in states longer
    }

    AVERAGE_USER = {
        "mouse_dpi": 800,
        "polling_rate": 500,
        "typing_speed_wpm": 50,
        "error_rate": 0.02,
        "fatigue_rate": 1.0,
        "scroll_preference": "mixed",
        "state_durations": "medium",
    }

    POWER_USER = {
        "mouse_dpi": 1600,
        "polling_rate": 1000,
        "typing_speed_wpm": 70,
        "error_rate": 0.01,
        "fatigue_rate": 0.8,  # Tires slower
        "scroll_preference": "keyboard",
        "state_durations": "short",  # Quick state switches
    }

    MOBILE_USER = {
        "mouse_dpi": 400,
        "polling_rate": 125,
        "typing_speed_wpm": 25,
        "error_rate": 0.05,
        "fatigue_rate": 1.3,
        "scroll_preference": "trackpad",
        "state_durations": "medium",
    }


def get_profile_config(profile_name: str) -> Dict[str, Any]:
    """Get configuration for a named profile"""
    profiles = {
        "cautious": BehaviorProfile.CAUTIOUS_USER,
        "average": BehaviorProfile.AVERAGE_USER,
        "power": BehaviorProfile.POWER_USER,
        "mobile": BehaviorProfile.MOBILE_USER,
    }

    return profiles.get(profile_name.lower(), BehaviorProfile.AVERAGE_USER)
