# human-behavior/utils.py
"""
Utility functions for human behavior simulation
"""

import numpy as np
from typing import Tuple, List
import time


def distance_between(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    """Calculate Euclidean distance between two points"""
    return np.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)


def angle_between(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    """Calculate angle between two points in radians"""
    return np.arctan2(p2[1] - p1[1], p2[0] - p1[0])


def interpolate_points(
    p1: Tuple[float, float], p2: Tuple[float, float], num_points: int
) -> List[Tuple[float, float]]:
    """Linear interpolation between two points"""
    x_vals = np.linspace(p1[0], p2[0], num_points)
    y_vals = np.linspace(p1[1], p2[1], num_points)
    return list(zip(x_vals, y_vals))


def smooth_path(
    points: List[Tuple[float, float]], window_size: int = 3
) -> List[Tuple[float, float]]:
    """Apply moving average smoothing to path"""
    if len(points) < window_size:
        return points

    smoothed = []
    for i in range(len(points)):
        start = max(0, i - window_size // 2)
        end = min(len(points), i + window_size // 2 + 1)

        window = points[start:end]
        avg_x = sum(p[0] for p in window) / len(window)
        avg_y = sum(p[1] for p in window) / len(window)

        smoothed.append((avg_x, avg_y))

    return smoothed


def timing_decorator(func):
    """Decorator to time function execution"""

    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        print(f"{func.__name__} took {elapsed:.4f}s")
        return result

    return wrapper


class PerformanceMonitor:
    """Monitor behavior engine performance"""

    def __init__(self):
        self.timings = {}

    def record(self, operation: str, duration: float):
        if operation not in self.timings:
            self.timings[operation] = []
        self.timings[operation].append(duration)

    def get_stats(self, operation: str) -> dict:
        if operation not in self.timings:
            return {}

        times = self.timings[operation]
        return {
            "mean": np.mean(times),
            "std": np.std(times),
            "min": np.min(times),
            "max": np.max(times),
            "count": len(times),
        }

    def print_report(self):
        print("\n=== Performance Report ===")
        for op in self.timings:
            stats = self.get_stats(op)
            print(f"\n{op}:")
            print(f"  Mean: {stats['mean']:.4f}s")
            print(f"  Std:  {stats['std']:.4f}s")
            print(f"  Min:  {stats['min']:.4f}s")
            print(f"  Max:  {stats['max']:.4f}s")
            print(f"  Count: {stats['count']}")
