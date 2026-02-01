# human-behavior/models.py
"""
Behavioral models: Fatigue, Fitts's Law, Context Awareness, Multi-Input
"""

import math
import numpy as np
from datetime import datetime, timedelta
from typing import Tuple, Optional
from dataclasses import dataclass
from bs4 import BeautifulSoup

from .noise_generators import PinkNoiseGenerator
from .cognitive_states import CognitiveState, STATE_CONFIGS


# ============================================================================
# FATIGUE MODEL
# ============================================================================


class FatigueModel:
    """Simulates realistic human performance degradation"""

    def __init__(self):
        self.session_start = datetime.now()
        self.total_actions = 0
        self.actions_since_break = 0

        self.max_fatigue = 0.4
        self.fatigue_rate = 0.0001
        self.recovery_rate = 0.5

        self.peak_hours = (10, 16)  # 10 AM - 4 PM

        # Individual variance (some people tire faster)
        self.personal_fatigue_rate = np.random.uniform(0.8, 1.2)

    def get_fatigue_multiplier(self) -> float:
        """
        Returns multiplier for delays (1.0 = fresh, 1.4 = 40% slower)
        """
        # Action-based fatigue
        action_fatigue = min(
            self.max_fatigue,
            self.actions_since_break * self.fatigue_rate * self.personal_fatigue_rate,
        )

        # Circadian rhythm
        current_hour = datetime.now().hour

        if self.peak_hours[0] <= current_hour <= self.peak_hours[1]:
            circadian_factor = 0.0
        elif 6 <= current_hour < self.peak_hours[0]:
            circadian_factor = 0.1
        elif self.peak_hours[1] < current_hour <= 22:
            circadian_factor = 0.15
        else:
            circadian_factor = 0.3

        # Session duration
        session_duration = (datetime.now() - self.session_start).total_seconds()
        session_fatigue = min(0.2, session_duration / 36000)

        total_fatigue = action_fatigue + circadian_factor + session_fatigue

        return 1.0 + min(self.max_fatigue, total_fatigue)

    def get_error_probability(self) -> float:
        """Tired humans make more mistakes"""
        base_error = 0.15
        fatigue_mult = self.get_fatigue_multiplier()
        return min(0.6, base_error * fatigue_mult)

    def record_action(self):
        """Call after each action"""
        self.total_actions += 1
        self.actions_since_break += 1

    def take_break(self, duration_seconds: float):
        """Recover from fatigue"""
        recovery = duration_seconds * self.recovery_rate
        self.actions_since_break = max(0, self.actions_since_break - int(recovery))

    def should_take_break(self) -> bool:
        """Natural break points"""
        # Every 45-90 minutes
        if self.actions_since_break > np.random.uniform(2000, 4000):
            return True

        # Random distraction (0.1% per action)
        if np.random.random() < 0.001:
            return True

        return False

    def get_break_duration(self) -> float:
        """How long to break for"""
        # Short breaks (30s-2min) vs long breaks (5-15min)
        if np.random.random() < 0.7:
            return np.random.uniform(30, 120)
        else:
            return np.random.uniform(300, 900)


# ============================================================================
# FITTS'S LAW MODEL
# ============================================================================


class FittsLawModel:
    """Implements Fitts's Law for realistic targeting"""

    @staticmethod
    def calculate_movement_time(distance: float, target_width: float) -> float:
        """
        Fitts's Law: MT = a + b × log₂(2D/W)

        Returns:
            Movement time in seconds
        """
        a = 0.05
        b = 0.15

        ID = math.log2((2 * distance) / max(target_width, 1))
        movement_time = a + b * ID

        return max(0.1, movement_time)

    @staticmethod
    def calculate_overshoot_probability(
        distance: float, target_width: float, fatigue_mult: float = 1.0
    ) -> float:
        """Dynamic overshoot based on difficulty"""
        difficulty = distance / max(target_width, 10)

        base_prob = 0.05 + (difficulty * 0.01)
        base_prob = min(0.6, base_prob)

        return min(0.8, base_prob * fatigue_mult)

    @staticmethod
    def calculate_overshoot_distance(target_width: float) -> float:
        """Smaller targets = larger relative overshoot"""
        overshoot_ratio = max(0.1, min(0.5, 100 / target_width))
        return np.random.uniform(5, 20) * overshoot_ratio


# ============================================================================
# CONTEXT-AWARE SCROLLING
# ============================================================================


@dataclass
class PageContext:
    """What's currently visible on page"""

    has_video: bool = False
    has_form: bool = False
    text_density: float = 0.0
    has_large_image: bool = False
    estimated_read_time: float = 0.0
    has_interactive_element: bool = False
    is_login_page: bool = False


class ContextAwareScrolling:
    """Adjusts behavior based on page content"""

    def __init__(self):
        self.noise_gen = PinkNoiseGenerator()

    def analyze_viewport(self, viewport_html: str) -> PageContext:
        """Analyze visible content"""
        try:
            soup = BeautifulSoup(viewport_html, "html.parser")
        except:
            return PageContext()

        # Video detection
        has_video = bool(soup.find_all(["video", "iframe"]))

        # Form detection
        forms = soup.find_all("form")
        has_form = bool(forms)
        is_login_page = any(
            "login" in form.get("class", []) or "login" in form.get("id", "")
            for form in forms
        )

        # Text analysis
        text = soup.get_text()
        text_length = len(text.strip())
        text_density = min(1.0, text_length / 1000)

        # Image detection
        images = soup.find_all("img")
        has_large_image = any(
            int(img.get("width", 0)) > 400 or int(img.get("height", 0)) > 300
            for img in images
        )

        # Interactive elements
        has_interactive = bool(soup.find_all(["button", "input", "select", "textarea"]))

        # Reading time estimate
        word_count = len(text.split())
        estimated_read_time = (word_count / 200) * 60

        return PageContext(
            has_video=has_video,
            has_form=has_form,
            text_density=text_density,
            has_large_image=has_large_image,
            estimated_read_time=estimated_read_time,
            has_interactive_element=has_interactive,
            is_login_page=is_login_page,
        )

    def get_contextual_scroll_params(
        self, context: PageContext, base_state: CognitiveState
    ) -> Tuple[float, float]:
        """Adjust scrolling based on content"""
        base_config = STATE_CONFIGS[base_state]

        scroll_amount = self.noise_gen.generate(*base_config.scroll_speed_range)
        wait_time = self.noise_gen.generate(*base_config.scroll_interval_range)

        # Video → stop
        if context.has_video:
            scroll_amount = 0
            wait_time = self.noise_gen.generate(3, 15)

        # High text density → slow down
        elif context.text_density > 0.7:
            scroll_amount *= 0.3
            wait_time *= 2.0

            if context.estimated_read_time > 0:
                wait_time += context.estimated_read_time * 0.6

        # Form → very careful
        elif context.has_form or context.is_login_page:
            scroll_amount *= 0.4
            wait_time *= 1.8

        # Image → pause
        elif context.has_large_image:
            scroll_amount *= 0.7
            wait_time += self.noise_gen.generate(1, 3)

        return scroll_amount, wait_time


# ============================================================================
# MULTI-INPUT CONTROLLER
# ============================================================================

from enum import Enum


class InputDevice(Enum):
    MOUSE = "mouse"
    KEYBOARD = "keyboard"
    SCROLL_WHEEL = "scroll_wheel"
    TRACKPAD = "trackpad"


class MultiInputController:
    """Mixes different input methods like real humans"""

    def __init__(self):
        self.last_input_device = InputDevice.MOUSE
        self.keyboard_usage_rate = np.random.uniform(0.15, 0.35)

    def choose_scroll_method(self) -> InputDevice:
        """Humans alternate between scroll methods"""
        if self.last_input_device == InputDevice.MOUSE:
            choice = np.random.choice(
                [InputDevice.SCROLL_WHEEL, InputDevice.MOUSE, InputDevice.KEYBOARD],
                p=[0.6, 0.3, 0.1],
            )
        else:
            choice = np.random.choice(
                [InputDevice.SCROLL_WHEEL, InputDevice.MOUSE, InputDevice.KEYBOARD],
                p=[0.4, 0.5, 0.1],
            )

        self.last_input_device = choice
        return choice

    def execute_scroll(self, amount: float, method: InputDevice) -> dict:
        """Different methods have different characteristics"""
        if method == InputDevice.SCROLL_WHEEL:
            # Discrete 120-unit steps
            notches = int(amount / 120)
            actual_scroll = notches * 120
            time_per_notch = np.random.uniform(0.05, 0.1)

            return {
                "method": "wheel",
                "amount": actual_scroll,
                "duration": notches * time_per_notch,
                "steps": notches,
            }

        elif method == InputDevice.KEYBOARD:
            return {
                "method": "keyboard",
                "key": np.random.choice(
                    ["PageDown", "ArrowDown", "Space"], p=[0.5, 0.3, 0.2]
                ),
                "amount": amount,
                "duration": np.random.uniform(0.1, 0.2),
            }

        else:
            return {
                "method": "mouse_drag",
                "amount": amount,
                "duration": np.random.uniform(0.3, 0.8),
            }

    def should_use_keyboard_shortcut(self) -> bool:
        """Sometimes use Ctrl+F, Ctrl+C, etc."""
        return np.random.random() < self.keyboard_usage_rate
