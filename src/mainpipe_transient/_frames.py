"""Frame selection for the player series (plan 01 §1.4, U-10, D-65 (1)-(2)).

The frames are the head at every output station for a subset of the time steps (since 2.0
the only frame matrix is ``frame_head_m``: the pressure head is derived by the screen as
``frame_head_m[k][j] - elevation_m[j]``, D-64). Their number is capped so that the matrix
holds at most ``FRAME_CELL_BUDGET`` cells::

    n_frames_max = min(MAX_FRAMES, floor(FRAME_CELL_BUDGET / n_stations))
    stride = 1                                   if n_steps + 1 <= n_frames_max
           = ceil(n_steps / (n_frames_max - 2))  otherwise
    frames at k = 0, stride, 2*stride, ... (< n_steps) and always k = n_steps

so there are at most ``n_frames_max - 1`` frames once subsampled. This is the 1.0 formula
unchanged (D-65 (1)); the values are rounded to 3 decimals when the response is built
(U-39), the frame instants are not.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

__all__ = ["FRAME_CELL_BUDGET", "MAX_FRAMES", "FramePlan", "max_frames", "plan_frames"]

# Cells of the single frame matrix frame_head_m (U-10, D-65 (1)-(2)). Fixed by the portal:
# it neither goes down nor up without a decision request (U-34 (6), D-65 (5)).
FRAME_CELL_BUDGET = 50_000
MAX_FRAMES = 1001  # D-57 (4), D-65 (1)


@dataclass(frozen=True)
class FramePlan:
    """Which time steps become frames."""

    stride: int
    steps: np.ndarray  # strictly increasing step indices, first 0, last n_steps

    @property
    def n_frames(self) -> int:
        return int(self.steps.size)


def max_frames(n_stations: int, cell_budget: int = FRAME_CELL_BUDGET) -> int:
    """Frame cap min(1001, floor(budget / n_stations)) (U-10, D-65 (1))."""
    return min(MAX_FRAMES, cell_budget // n_stations)


def plan_frames(n_steps: int, n_stations: int, cell_budget: int = FRAME_CELL_BUDGET) -> FramePlan:
    """Frame steps for a run of ``n_steps`` steps reported on ``n_stations`` stations."""
    cap = max_frames(n_stations, cell_budget)
    if n_steps + 1 <= cap:
        stride = 1
    else:
        # The contract bounds keep cap >= 71 (at most 699 stations); a cap below 3 would
        # leave no room between the first and the last frame.
        if cap < 3:
            raise ValueError(f"frame cap {cap} too small for {n_stations} stations")
        stride = math.ceil(n_steps / (cap - 2))
    steps = np.append(np.arange(0, n_steps, stride, dtype=np.int64), np.int64(n_steps))
    steps.setflags(write=False)
    return FramePlan(stride=stride, steps=steps)
