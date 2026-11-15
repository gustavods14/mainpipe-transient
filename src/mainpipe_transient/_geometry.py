"""Computational mesh (plan 01 M4, U-07, U-08).

Phase 1: horizontal pipe, stations = computational nodes only. Profile vertices
(M14) are added in phase 3.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

__all__ = [
    "MAX_STEPS",
    "N_REACHES_MIN",
    "N_REACHES_MAX",
    "Mesh",
    "build_horizontal_mesh",
    "time_step_s",
    "count_steps",
    "default_duration_s",
    "max_even_reaches",
]

MAX_STEPS = 10_000  # U-09, D-57
N_REACHES_MIN = 10  # U-09, HU-1.7
N_REACHES_MAX = 200

# U-08: absorbs binary noise in T/dt. Example: L = 1000 m, a = 1000 m/s, N = 26 gives
# dt = 0.0384615..., and 1.0 / dt = 26.000000000000004; without the tolerance a 1 s
# simulation would take 27 steps instead of 26.
_STEP_TOLERANCE = 1e-9


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


def time_step_s(length_m: float, n_reaches: int, wave_speed_ms: float) -> float:
    """dt = (L/N)/a, evaluated exactly as the mesh does (Courant = 1)."""
    return (length_m / n_reaches) / wave_speed_ms


def build_horizontal_mesh(
    length_m: float, n_reaches: int, wave_speed_ms: float, pipe_elevation_m: float
) -> Mesh:
    dx = length_m / n_reaches
    dt = time_step_s(length_m, n_reaches, wave_speed_ms)
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


def max_even_reaches(duration_s: float, length_m: float, wave_speed_ms: float) -> int | None:
    """Largest even N in [10, 200] whose step count for ``duration_s`` fits MAX_STEPS."""
    for n in range(N_REACHES_MAX, N_REACHES_MIN - 1, -2):
        if count_steps(duration_s, time_step_s(length_m, n, wave_speed_ms)) <= MAX_STEPS:
            return n
    return None
