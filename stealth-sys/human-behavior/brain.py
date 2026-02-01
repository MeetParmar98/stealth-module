# human-behavior/brain.py
"""
Main HumanBrain class - orchestrates all behavioral components
"""

import time
import math
import numpy as np
from typing import Tuple, List, Optional, Dict, Any

from .cognitive_states import CognitiveState, StateTransitionManager, STATE_CONFIGS
from .noise_generators import PinkNoiseGenerator, PerlinNoiseGenerator
from .motion_engine import MotionProfile, PathCorrection
from .hardware_simulation import HardwareInputSimulator, KeyboardSimulator
from .models import (
    FatigueModel,
    FittsLawModel,
    ContextAwareScrolling,
    MultiInputController,
    PageContext,
)


class HumanBrain:
    """
    Complete human behavior simulation engine
    Integrates all behavioral models for realistic automation
    """

    def __init__(
        self,
        mouse_dpi: int = 800,
        polling_rate: int = 500,
        enable_fatigue: bool = True,
        enable_context_aware: bool = True,
    ):
        """
        Args:
            mouse_dpi: Mouse DPI (400, 800, 1600, etc.)
            polling_rate: Mouse polling rate Hz (125, 500, 1000)
            enable_fatigue: Enable fatigue modeling
            enable_context_aware: Enable context-aware scrolling
        """
        # Core components
        self.noise_gen = PinkNoiseGenerator()
        self.perlin = PerlinNoiseGenerator()

        # State management
        self.current_state = CognitiveState.READING
        self.state_start_time = time.time()
        self.state_manager = StateTransitionManager()

        # Hardware simulation
        self.hardware = HardwareInputSimulator(polling_rate, mouse_dpi)
        self.keyboard = KeyboardSimulator()

        # Behavioral models
        self.fatigue = FatigueModel() if enable_fatigue else None
        self.context_aware = ContextAwareScrolling() if enable_context_aware else None
        self.multi_input = MultiInputController()

        # State tracking
        self.current_mouse_pos = (0, 0)
        self.total_clicks = 0
        self.session_start = time.time()

        # Performance metrics
        self.metrics = {"clicks": 0, "scrolls": 0, "hovers": 0, "state_switches": 0}

    def _should_switch_state(self) -> bool:
        """Check if time to switch cognitive states"""
        config = STATE_CONFIGS[self.current_state]
        duration = time.time() - self.state_start_time
        max_duration = self.noise_gen.generate(*config.duration_range)

        return duration >= max_duration

    def _switch_state(self) -> CognitiveState:
        """Switch to new cognitive state"""
        new_state = self.state_manager.get_next_state(self.current_state)
        self.current_state = new_state
        self.state_start_time = time.time()
        self.metrics["state_switches"] += 1

        return new_state

    def execute_click(
        self,
        target_pos: Tuple[float, float],
        target_size: Tuple[int, int] = (50, 30),
        click_type: str = "left",
    ) -> Dict[str, Any]:
        """
        Execute human-like click with full biological realism

        Args:
            target_pos: (x, y) target coordinates
            target_size: (width, height) of target element
            click_type: 'left', 'right', 'double'

        Returns:
            dict with 'path', 'hover_duration', 'click_duration'
        """
        # Calculate distance
        distance = math.sqrt(
            (target_pos[0] - self.current_mouse_pos[0]) ** 2
            + (target_pos[1] - self.current_mouse_pos[1]) ** 2
        )

        # Fitts's Law: calculate movement time
        target_width = min(target_size)
        movement_time = FittsLawModel.calculate_movement_time(distance, target_width)

        # Get fatigue multiplier
        fatigue_mult = self.fatigue.get_fatigue_multiplier() if self.fatigue else 1.0

        # Calculate overshoot probability
        overshoot_prob = FittsLawModel.calculate_overshoot_probability(
            distance, target_width, fatigue_mult
        )

        # Generate base path
        num_points = max(30, int(distance / 10))
        points = MotionProfile.bezier_curve(
            self.current_mouse_pos,
            target_pos,
            control_points=2,
            curvature=np.random.uniform(0.7, 1.3),
        )

        # Apply velocity profile
        velocity_profile = MotionProfile.lognormal_velocity_profile(
            len(points), peak_position=np.random.uniform(0.35, 0.45)
        )

        # Convert to timed path
        path_with_timing = []
        for i, (x, y) in enumerate(points):
            delay = (movement_time / len(points)) / (velocity_profile[i] + 0.1)
            delay *= fatigue_mult  # Slower when tired
            path_with_timing.append((x, y, delay))

        # Add imperfections
        correction_intensity = 1.0 + (fatigue_mult - 1.0) * 0.5
        path_with_timing = PathCorrection.add_micro_corrections(
            path_with_timing, correction_probability=0.2, intensity=correction_intensity
        )

        # Add hesitation (more when tired)
        if fatigue_mult > 1.2:
            path_with_timing = PathCorrection.add_hesitation(path_with_timing, 2)

        # Overshoot logic
        if np.random.random() < overshoot_prob:
            overshoot_dist = FittsLawModel.calculate_overshoot_distance(target_width)
            path_with_timing = PathCorrection.add_momentum_overshoot(
                path_with_timing, target_pos, overshoot_dist
            )

        # Apply hardware constraints
        path_with_timing = self.hardware.apply_hardware_timing(path_with_timing)

        # Apply pixel quantization and sensor noise
        final_path = []
        for x, y, delay in path_with_timing:
            x, y = self.hardware.add_sensor_noise(x, y)
            x, y = self.hardware.apply_pixel_quantization(x, y)
            final_path.append((x, y, delay))

        # Hover duration before clicking
        hover_duration = self.noise_gen.generate(0.1, 0.3) * fatigue_mult

        # Click hold duration
        click_duration = self.noise_gen.generate(0.05, 0.12)

        # Double click logic
        if click_type == "double":
            double_click_interval = self.noise_gen.generate(0.08, 0.15)
        else:
            double_click_interval = None

        # Update state
        self.current_mouse_pos = target_pos
        self.total_clicks += 1
        self.metrics["clicks"] += 1

        if self.fatigue:
            self.fatigue.record_action()

        # Check for break
        should_break = self.fatigue.should_take_break() if self.fatigue else False

        return {
            "path": final_path,
            "hover_duration": hover_duration,
            "click_duration": click_duration,
            "double_click_interval": double_click_interval,
            "fatigue_level": fatigue_mult,
            "should_take_break": should_break,
        }

    def execute_scroll(
        self, viewport_html: Optional[str] = None, force_amount: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Execute human-like scroll with context awareness

        Args:
            viewport_html: HTML of visible content (for context)
            force_amount: Override scroll amount (for testing)

        Returns:
            dict with scroll parameters
        """
        # Switch states if needed
        if self._should_switch_state():
            self._switch_state()

        # Get base scroll parameters
        base_config = STATE_CONFIGS[self.current_state]

        if self.context_aware and viewport_html:
            # Analyze page content
            context = self.context_aware.analyze_viewport(viewport_html)
            scroll_amount, wait_time = self.context_aware.get_contextual_scroll_params(
                context, self.current_state
            )
        else:
            scroll_amount = self.noise_gen.generate(*base_config.scroll_speed_range)
            wait_time = self.noise_gen.generate(*base_config.scroll_interval_range)

        # Override if specified
        if force_amount is not None:
            scroll_amount = force_amount

        # Apply fatigue
        if self.fatigue:
            fatigue_mult = self.fatigue.get_fatigue_multiplier()
            wait_time *= fatigue_mult
            self.fatigue.record_action()

        # Choose scroll method
        scroll_method = self.multi_input.choose_scroll_method()
        scroll_action = self.multi_input.execute_scroll(scroll_amount, scroll_method)
        scroll_action["wait_after"] = wait_time
        scroll_action["state"] = self.current_state.value

        self.metrics["scrolls"] += 1

        return scroll_action

    def execute_hover(
        self, position: Tuple[float, float], duration: float = 2.0
    ) -> List[Tuple[float, float, float]]:
        """
        Simulate idle hovering with micro-tremors

        Args:
            position: Where to hover
            duration: How long to hover

        Returns:
            List of (x, y, delay) tremor points
        """
        tremor_points = []
        elapsed = 0
        current_pos = position

        # Tremor intensity based on fatigue
        tremor_intensity = 1.0
        if self.fatigue:
            tremor_intensity = self.fatigue.get_fatigue_multiplier() * 0.8

        while elapsed < duration:
            wait = self.noise_gen.generate(0.2, 0.5)

            # Add tremor
            new_pos = PathCorrection.add_hand_tremor(
                *current_pos, intensity=tremor_intensity
            )

            tremor_points.append((*new_pos, wait))
            current_pos = new_pos
            elapsed += wait

        self.metrics["hovers"] += 1

        return tremor_points

    def execute_typing(self, text: str) -> List[Tuple[str, float, float]]:
        """
        Simulate realistic typing with errors and corrections

        Args:
            text: Text to type

        Returns:
            List of (character, press_duration, interval_before_next)
        """
        typing_sequence = []

        for i, char in enumerate(text):
            # Key press duration
            press_duration = self.keyboard.get_key_press_duration()

            # Interval before next key
            interval = self.keyboard.get_inter_key_interval()

            # Apply fatigue
            if self.fatigue:
                fatigue_mult = self.fatigue.get_fatigue_multiplier()
                interval *= fatigue_mult

            # Random typo
            if self.keyboard.should_make_typo() and i < len(text) - 1:
                # Add typo sequence
                typo_seq = self.keyboard.simulate_backspace_correction()
                for typo_char, typo_delay in typo_seq:
                    typing_sequence.append((typo_char, press_duration, typo_delay))

            typing_sequence.append((char, press_duration, interval))

        return typing_sequence

    def take_break(self, duration: Optional[float] = None):
        """Simulate a human break"""
        if duration is None and self.fatigue:
            duration = self.fatigue.get_break_duration()
        elif duration is None:
            duration = np.random.uniform(30, 120)

        if self.fatigue:
            self.fatigue.take_break(duration)

        return {
            "duration": duration,
            "activity": np.random.choice(
                ["tab_switch", "phone_check", "coffee_break", "bathroom", "distraction"]
            ),
        }

    def get_metrics(self) -> Dict[str, Any]:
        """Get session performance metrics"""
        session_duration = time.time() - self.session_start

        return {
            **self.metrics,
            "session_duration": session_duration,
            "current_state": self.current_state.value,
            "fatigue_level": self.fatigue.get_fatigue_multiplier()
            if self.fatigue
            else 1.0,
            "actions_per_minute": (sum(self.metrics.values()) / session_duration) * 60,
        }
