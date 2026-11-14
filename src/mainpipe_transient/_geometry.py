"""Computational mesh (plan 01 M4, U-07, U-08).

Phase 1: horizontal pipe, stations = computational nodes only. Profile vertices
(M14) are added in phase 3.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

__all__ = ["Mesh", "build_horizontal_mesh", "count_steps", "default_duration_s"]

_STEP_TOLERANCE = 1e-9  # U-08: 20 / 0.05 is 400.000...1 in floating point


@dataclass(frozen=True)
class Mesh:
    """Courant-1 mesh: dx = L/N, dt = dx/a, nodes x_i = L*i/N."""

    length_m: float
    n_reaches: int
    dx_m: float
    dt_s: float
    x_m: np.ndarray  # node positions, length N + 1
    elevation_m: np.ndarray  # z at each node

    @property
    def midpoint_index(self) -> int:
        """Node at x = L/2 (N is even)."""
        return self.n_reaches // 2


def build_horizontal_mesh(
    length_m: float, n_reaches: int, wave_speed_ms: float, pipe_elevation_m: float
) -> Mesh:
    dx = length_m / n_reaches
    dt = dx / wave_speed_ms
    x = length_m * np.arange(n_reaches + 1, dtype=float) / n_reaches
    x[-1] = length_m  # last node is L exactly (U-07)
    z = np.full(n_reaches + 1, float(pipe_elevation_m))
    x.setflags(write=False)
    z.setflags(write=False)
    return Mesh(length_m=length_m, n_reaches=n_reaches, dx_m=dx, dt_s=dt, x_m=x, elevation_m=z)


def count_steps(duration_s: float, dt_s: float) -> int:
    """n_steps = ceil(T/dt - 1e-9) (U-08)."""
    return math.ceil(duration_s / dt_s - _STEP_TOLERANCE)


def default_duration_s(closure_duration_s: float, length_m: float, wave_speed_ms: float) -> float:
    """Tc + 5 * (4L/a) (plan 01 §1.3)."""
    return closure_duration_s + 5.0 * (4.0 * length_m / wave_speed_ms)
