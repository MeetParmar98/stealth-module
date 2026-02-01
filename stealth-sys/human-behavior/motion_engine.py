# human-behavior/motion_engine.py
"""
Mouse motion generation with biological realism
"""

import math
import numpy as np
from typing import List, Tuple


class MotionProfile:
    """Generates human-like mouse movement profiles"""

    @staticmethod
    def bezier_curve(
        start: Tuple[float, float],
        end: Tuple[float, float],
        control_points: int = 2,
        curvature: float = 1.0,
    ) -> List[Tuple[float, float]]:
        """
        Generate Bézier curve with random control points

        Args:
            curvature: How curved the path is (0.5=subtle, 2.0=exaggerated)
        """
        points = [start]

        for i in range(control_points):
            t = (i + 1) / (control_points + 1)
            x = start[0] + (end[0] - start[0]) * t
            y = start[1] + (end[1] - start[1]) * t

            # Perpendicular offset
            offset = np.random.uniform(-100, 100) * curvature
            angle = math.atan2(end[1] - start[1], end[0] - start[0])
            x += offset * math.sin(angle)
            y += offset * -math.cos(angle)

            points.append((x, y))

        points.append(end)

        return MotionProfile._generate_bezier(points, num_points=50)

    @staticmethod
    def _generate_bezier(
        control_points: List[Tuple[float, float]], num_points: int = 50
    ) -> List[Tuple[float, float]]:
        """Generate points along Bézier curve"""
        n = len(control_points) - 1
        curve_points = []

        for i in range(num_points):
            t = i / (num_points - 1)
            x, y = 0, 0

            for j, (px, py) in enumerate(control_points):
                coef = math.comb(n, j) * (t**j) * ((1 - t) ** (n - j))
                x += coef * px
                y += coef * py

            curve_points.append((x, y))

        return curve_points

    @staticmethod
    def lognormal_velocity_profile(
        num_points: int, peak_position: float = 0.4
    ) -> np.ndarray:
        """
        Log-normal velocity: fast acceleration → peak → slow deceleration

        Args:
            peak_position: Where peak velocity occurs (0.0-1.0)
        """
        t = np.linspace(0, 1, num_points)

        mu = np.log(peak_position + 0.01)
        sigma = 0.7

        velocity = np.exp(-((np.log(t + 0.01) - mu) ** 2) / (2 * sigma**2))
        velocity = velocity / np.max(velocity)

        return velocity

    @staticmethod
    def power_law_velocity(num_points: int, power: float = 0.5) -> np.ndarray:
        """
        Power law velocity profile (alternative to log-normal)
        Common in human reaching movements
        """
        t = np.linspace(0, 1, num_points)

        # Bell curve using power law
        velocity = (t**power) * ((1 - t) ** power)
        velocity = velocity / np.max(velocity)

        return velocity


class PathCorrection:
    """Add realistic imperfections to mouse paths"""

    @staticmethod
    def add_micro_corrections(
        path: List[Tuple[float, float, float]],
        correction_probability: float = 0.2,
        intensity: float = 1.0,
    ) -> List[Tuple[float, float, float]]:
        """
        Add involuntary micro-corrections

        Args:
            intensity: How large corrections are (0.5=subtle, 2.0=pronounced)
        """
        corrected_path = []

        for i, (x, y, delay) in enumerate(path):
            corrected_path.append((x, y, delay))

            if np.random.random() < correction_probability:
                jerk_x = np.random.uniform(-8, 8) * intensity
                jerk_y = np.random.uniform(-8, 8) * intensity

                corrected_path.append(
                    (x + jerk_x, y + jerk_y, np.random.uniform(0.008, 0.015))
                )

        return corrected_path

    @staticmethod
    def add_hesitation(
        path: List[Tuple[float, float, float]], hesitation_points: int = 1
    ) -> List[Tuple[float, float, float]]:
        """Add brief pauses mid-movement"""
        if len(path) < 10:
            return path

        path_with_hesitation = list(path)

        for _ in range(hesitation_points):
            idx = np.random.randint(len(path) // 4, 3 * len(path) // 4)
            x, y, delay = path_with_hesitation[idx]

            hesitation_duration = np.random.uniform(0.05, 0.15)
            path_with_hesitation[idx] = (x, y, delay + hesitation_duration)

        return path_with_hesitation

    @staticmethod
    def add_momentum_overshoot(
        path: List[Tuple[float, float, float]],
        final_target: Tuple[float, float],
        overshoot_distance: float = 10.0,
    ) -> List[Tuple[float, float, float]]:
        """Simulate hand momentum carrying past target"""
        if len(path) < 2:
            return path

        final_x, final_y, final_delay = path[-1]
        target_x, target_y = final_target

        # Calculate movement direction
        prev_x, prev_y, _ = path[-2]
        dx = final_x - prev_x
        dy = final_y - prev_y
        magnitude = math.sqrt(dx**2 + dy**2) or 1

        # Overshoot
        overshoot_x = final_x + (dx / magnitude) * overshoot_distance
        overshoot_y = final_y + (dy / magnitude) * overshoot_distance

        path.append((overshoot_x, overshoot_y, 0.02))
        path.append((target_x, target_y, np.random.uniform(0.04, 0.08)))

        return path

    @staticmethod
    def add_hand_tremor(
        x: float, y: float, intensity: float = 1.0
    ) -> Tuple[float, float]:
        """
        Add subtle hand tremor (1-2px jitter)

        Args:
            intensity: Tremor strength (higher = more shaky)
        """
        jitter_x = np.random.uniform(-1.5, 1.5) * intensity
        jitter_y = np.random.uniform(-1.5, 1.5) * intensity

        return (x + jitter_x, y + jitter_y)
