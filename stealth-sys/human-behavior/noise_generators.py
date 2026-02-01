# human-behavior/noise_generators.py
"""
Biologically-inspired noise generators for natural timing
"""

import numpy as np
from typing import Optional


class PinkNoiseGenerator:
    """
    1/f (pink) noise generator for natural timing variations
    More realistic than uniform random
    """

    def __init__(self, seed: Optional[int] = None):
        if seed:
            np.random.seed(seed)
        self.state = np.random.randn(10)
        self.last_value = 0.5

    def generate(self, min_val: float, max_val: float) -> float:
        """Generate pink noise value in range"""
        white = np.random.randn()
        self.state[1:] = self.state[:-1]
        self.state[0] = white
        pink = np.sum(self.state) / 10

        # Normalize to 0-1
        normalized = (pink + 3) / 6
        normalized = max(0, min(1, normalized))

        # Add autocorrelation (current value depends on last)
        alpha = 0.3
        normalized = alpha * self.last_value + (1 - alpha) * normalized
        self.last_value = normalized

        return min_val + (max_val - min_val) * normalized

    def generate_array(self, min_val: float, max_val: float, size: int) -> np.ndarray:
        """Generate array of pink noise values"""
        return np.array([self.generate(min_val, max_val) for _ in range(size)])


class PerlinNoiseGenerator:
    """
    Perlin noise for smooth, natural variations
    Good for tremor and micro-movements
    """

    def __init__(self):
        self.permutation = np.random.permutation(256)
        self.p = np.concatenate([self.permutation, self.permutation])

    def fade(self, t):
        """Smoothstep function"""
        return t * t * t * (t * (t * 6 - 15) + 10)

    def lerp(self, t, a, b):
        """Linear interpolation"""
        return a + t * (b - a)

    def grad(self, hash_val, x):
        """Gradient function"""
        h = hash_val & 15
        return x if (h & 1) == 0 else -x

    def noise(self, x):
        """1D Perlin noise"""
        X = int(np.floor(x)) & 255
        x -= np.floor(x)
        u = self.fade(x)

        return self.lerp(u, self.grad(self.p[X], x), self.grad(self.p[X + 1], x - 1))

    def generate(self, min_val: float, max_val: float, t: float = None) -> float:
        """Generate Perlin noise value"""
        if t is None:
            t = np.random.uniform(0, 100)

        noise_val = self.noise(t)
        # Normalize from [-1, 1] to [0, 1]
        normalized = (noise_val + 1) / 2

        return min_val + (max_val - min_val) * normalized
