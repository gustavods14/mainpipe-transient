"""Valve closure law Q(t) given as a table (plan 01 M11, U-18).

Linear interpolation between table points, constant after the last point. The
evaluation order mirrors the Excel workbook (``2_Malla_MOC`` column C):
``Q_j + (Q_{j+1} - Q_j) * (t - T_j) / (T_{j+1} - T_j)``.
"""

from __future__ import annotations

from bisect import bisect_right
from collections.abc import Sequence
from dataclasses import dataclass

__all__ = ["ClosureLaw", "build_closure_law"]


@dataclass(frozen=True)
class ClosureLaw:
    """Closure table in SI units. Inputs are assumed already validated."""

    time_s: tuple[float, ...]
    flow_m3s: tuple[float, ...]

    def flow_at(self, t: float) -> float:
        """Flow imposed at the valve at time ``t`` (s), in m3/s."""
        times, flows = self.time_s, self.flow_m3s
        if t >= times[-1]:
            return flows[-1]
        j = bisect_right(times, t) - 1
        if j < 0:  # t < 0 never happens in the solver; keep the law defined anyway
            return flows[0]
        return flows[j] + (flows[j + 1] - flows[j]) * (t - times[j]) / (times[j + 1] - times[j])

    @property
    def closure_duration_s(self) -> float:
        """Tc: first table instant with Q = 0 (HU-1.2 crit. 3)."""
        for t, q in zip(self.time_s, self.flow_m3s):
            if q == 0.0:
                return t
        raise ValueError("closure law never reaches Q = 0")


def build_closure_law(
    time_s: Sequence[float], flow_m3s: Sequence[float], initial_flow_m3s: float
) -> ClosureLaw:
    """Build the law, replacing the first flow by Q0 (U-18: exact consistency at t = 0)."""
    flows = [float(q) for q in flow_m3s]
    flows[0] = float(initial_flow_m3s)
    return ClosureLaw(time_s=tuple(float(t) for t in time_s), flow_m3s=tuple(flows))
