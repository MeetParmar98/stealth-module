# human-behavior/hardware_simulation.py
"""
Hardware-level input simulation (polling rate, USB jitter, DPI)
"""

import numpy as np
from typing import List, Tuple


class HardwareInputSimulator:
    """Simulates real mouse hardware characteristics"""

    def __init__(self, polling_rate_hz: int = 500, mouse_dpi: int = 800):
        """
        Args:
            polling_rate_hz: 125, 250, 500, 1000 (common values)
            mouse_dpi: 400, 800, 1600, 3200 (common values)
        """
        self.polling_interval = 1.0 / polling_rate_hz
        self.mouse_dpi = mouse_dpi
        self.usb_jitter_range = (0.0001, 0.0005)  # 0.1-0.5ms

        # Sensor noise characteristics
        self.sensor_noise_enabled = True
        self.lift_off_distance = 2  # mm

    def apply_hardware_timing(
        self, path_points: List[Tuple[float, float, float]]
    ) -> List[Tuple[float, float, float]]:
        """
        Convert smooth timing to hardware-realistic polling intervals

        Returns:
            Path with realistic hardware timing
        """
        hardware_path = []
        accumulated_time = 0
        last_report_time = 0

        for x, y, ideal_delay in path_points:
            accumulated_time += ideal_delay

            # Only report at polling intervals
            if accumulated_time - last_report_time >= self.polling_interval:
                # USB jitter
                jitter = np.random.uniform(*self.usb_jitter_range)
                actual_delay = self.polling_interval + jitter

                hardware_path.append((x, y, actual_delay))
                last_report_time = accumulated_time

        return hardware_path

    def apply_pixel_quantization(self, x: float, y: float) -> Tuple[int, int]:
        """
        Mice can't move by fractions of pixels
        DPI determines minimum movement granularity
        """
        quantum = max(1, int(1600 / self.mouse_dpi))

        quantized_x = round(x / quantum) * quantum
        quantized_y = round(y / quantum) * quantum

        return int(quantized_x), int(quantized_y)

    def add_sensor_noise(self, x: float, y: float) -> Tuple[float, float]:
        """
        Optical sensors have minor tracking errors
        Especially on glossy surfaces
        """
        if not self.sensor_noise_enabled:
            return (x, y)

        # Very subtle noise (±0.5px)
        noise_x = np.random.normal(0, 0.3)
        noise_y = np.random.normal(0, 0.3)

        return (x + noise_x, y + noise_y)

    def simulate_acceleration(
        self, velocity: float, os_acceleration: bool = True
    ) -> float:
        """
        Simulate OS-level mouse acceleration
        Windows/Mac apply pointer acceleration by default

        Args:
            velocity: Current mouse velocity (pixels/second)
            os_acceleration: Whether OS acceleration is enabled

        Returns:
            Adjusted velocity
        """
        if not os_acceleration:
            return velocity

        # Windows acceleration curve (simplified)
        if velocity < 100:
            return velocity  # No acceleration for slow movements
        elif velocity < 500:
            return velocity * 1.2  # Slight boost
        else:
            return velocity * 1.5  # Significant boost for fast movements


class KeyboardSimulator:
    """Simulates realistic keyboard input"""

    def __init__(self):
        self.typing_speed_wpm = np.random.uniform(35, 65)  # Words per minute
        self.error_rate = 0.02  # 2% typo rate

    def get_key_press_duration(self) -> float:
        """How long key is held down"""
        # Most people: 50-150ms
        return np.random.uniform(0.05, 0.15)

    def get_inter_key_interval(self) -> float:
        """Time between key presses"""
        # Based on typing speed
        chars_per_second = (self.typing_speed_wpm * 5) / 60  # ~5 chars per word
        base_interval = 1.0 / chars_per_second

        # Add variance (±30%)
        variance = np.random.uniform(0.7, 1.3)
        return base_interval * variance

    def should_make_typo(self) -> bool:
        """Probabilistic typo generation"""
        return np.random.random() < self.error_rate

    def simulate_backspace_correction(self) -> List[Tuple[str, float]]:
        """
        Simulate typo correction: wrong_key → backspace → correct_key

        Returns:
            [(key, delay), ...]
        """
        return [
            ("wrong_char", 0.0),
            ("Backspace", np.random.uniform(0.2, 0.5)),
            ("correct_char", np.random.uniform(0.1, 0.3)),
        ]
