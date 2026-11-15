"""Steady state and MOC time loop with in-loop accumulators (plan 01 M1-M10, M12, U-02, U-19).

Scheme (identical to the Excel sheet ``2_Malla_MOC``, U-02)::

    C+_i = H_{i-1} + B*Q_{i-1} - R*Q_{i-1}*|Q_{i-1}|
    C-_i = H_{i+1} - B*Q_{i+1} + R*Q_{i+1}*|Q_{i+1}|
    interior:  H = (C+ + C-)/2,  Q = (C+ - C-)/(2B)
    reservoir: H = H_dep,        Q = (H_dep - C-)/B
    valve:     Q = Q_law(t_{k+1}), H = C+ - B*Q

with B = a/(g*A) and R = f*dx/(2*g*D*A^2). The elevation never enters H or Q (M13);
it only gives the pressure head p/gamma = H - z. Envelopes and extremes are accumulated
over every step on the output stations (nodes plus profile vertices, M14, U-07); the full
H/Q history is never stored (U-19).

All quantities are SI (m, s, m3/s).
"""

from __future__ import annotations

import math
from collections.abc import Callable
from dataclasses import dataclass

import numpy as np

from ._closure import ClosureLaw
from ._geometry import Mesh

__all__ = ["PipeData", "Derived", "MocResult", "Extreme", "derive", "simulate"]

StepObserver = Callable[[int, np.ndarray, np.ndarray], None]


@dataclass(frozen=True)
class PipeData:
    """Physical data of the reservoir-pipe-valve system, SI units."""

    diameter_m: float
    wave_speed_ms: float
    friction_factor: float
    initial_flow_m3s: float
    reservoir_level_m: float
    gravity_ms2: float


@dataclass(frozen=True)
class Derived:
    """Derived steady-state quantities and scheme constants (M1, M2, M5)."""

    area_m2: float
    velocity_initial_ms: float
    head_loss_m: float
    wave_constant: float  # B = a/(g*A), s/m2
    friction_constant: float  # R = f*dx/(2*g*D*A^2), s2/m5
    friction_number: float  # phi = f*dx*V0/(2*D*a) (U-03)
    reflection_time_s: float  # 2L/a
    wave_period_s: float  # 4L/a


def derive(pipe: PipeData, mesh: Mesh) -> Derived:
    d, a, f, g = pipe.diameter_m, pipe.wave_speed_ms, pipe.friction_factor, pipe.gravity_ms2
    area = math.pi * d**2 / 4.0
    v0 = pipe.initial_flow_m3s / area
    return Derived(
        area_m2=area,
        velocity_initial_ms=v0,
        head_loss_m=f * mesh.length_m * v0**2 / (2.0 * g * d),
        wave_constant=a / (g * area),
        friction_constant=f * mesh.dx_m / (2.0 * g * d * area**2),
        friction_number=f * mesh.dx_m * v0 / (2.0 * d * a),
        reflection_time_s=2.0 * mesh.length_m / a,
        wave_period_s=4.0 * mesh.length_m / a,
    )


@dataclass(frozen=True)
class Extreme:
    """An extreme value with its location and instant (U-25 tie-break applied)."""

    value_m: float
    x_m: float
    time_s: float


@dataclass(frozen=True)
class MocResult:
    """Output of :func:`simulate`. Envelope arrays follow ``mesh.station_x_m``."""

    mesh: Mesh
    derived: Derived
    n_steps: int
    # time series, length n_steps + 1
    time_s: np.ndarray
    head_valve_m: np.ndarray
    head_midpoint_m: np.ndarray
    flow_reservoir_m3s: np.ndarray
    flow_valve_m3s: np.ndarray
    # envelopes per output station (mesh.station_x_m)
    head_initial_m: np.ndarray
    head_max_m: np.ndarray
    head_min_m: np.ndarray
    head_max_step: np.ndarray  # first step reaching the station maximum
    head_min_step: np.ndarray  # first step reaching the station minimum

    @property
    def duration_s(self) -> float:
        """Effective duration n_steps * dt (U-08)."""
        return self.n_steps * self.mesh.dt_s

    @property
    def pressure_head_valve_m(self) -> np.ndarray:
        return self.head_valve_m - self.mesh.elevation_m[-1]

    @property
    def pressure_head_midpoint_m(self) -> np.ndarray:
        return self.head_midpoint_m - self.mesh.elevation_m[self.mesh.midpoint_index]

    @property
    def pressure_head_initial_m(self) -> np.ndarray:
        return self.head_initial_m - self.mesh.station_elevation_m

    @property
    def pressure_head_max_m(self) -> np.ndarray:
        return self.head_max_m - self.mesh.station_elevation_m

    @property
    def pressure_head_min_m(self) -> np.ndarray:
        return self.head_min_m - self.mesh.station_elevation_m

    def head_valve_max(self) -> tuple[float, float]:
        """(value, first instant) of the valve head maximum."""
        k = int(np.argmax(self.head_valve_m))
        return float(self.head_valve_m[k]), float(self.time_s[k])

    def head_valve_min(self) -> tuple[float, float]:
        """(value, first instant) of the valve head minimum."""
        k = int(np.argmin(self.head_valve_m))
        return float(self.head_valve_m[k]), float(self.time_s[k])

    def pressure_head_max_global(self) -> Extreme:
        return self._global_extreme(self.pressure_head_max_m, self.head_max_step, np.max)

    def pressure_head_min_global(self) -> Extreme:
        return self._global_extreme(self.pressure_head_min_m, self.head_min_step, np.min)

    def _global_extreme(self, envelope: np.ndarray, steps: np.ndarray, pick) -> Extreme:
        # Pressure = H - z with z fixed in time, so the station extreme of p happens
        # when H reaches its station extreme. Tie-break (U-25): first instant, then lower x.
        value = pick(envelope)
        candidates = np.flatnonzero(envelope == value)
        x = self.mesh.station_x_m
        j = min(candidates, key=lambda i: (steps[i], x[i]))
        return Extreme(
            value_m=float(value),
            x_m=float(x[j]),
            time_s=float(self.time_s[steps[j]]),
        )


def simulate(
    pipe: PipeData,
    mesh: Mesh,
    law: ClosureLaw,
    n_steps: int,
    observer: StepObserver | None = None,
) -> MocResult:
    """Run the MOC from the steady state for ``n_steps`` time steps.

    ``observer(k, H, Q)``, if given, is called for k = 0 .. n_steps with the node
    arrays of step k. The arrays are reused buffers: copy them to keep them.
    Envelopes are taken on ``mesh.station_x_m`` (M14).
    """
    der = derive(pipe, mesh)
    b, r = der.wave_constant, der.friction_constant
    n = mesh.n_reaches
    mid = mesh.midpoint_index
    h_dep = pipe.reservoir_level_m
    q0 = pipe.initial_flow_m3s
    dt = mesh.dt_s

    # Steady state (M3, U-04)
    head = h_dep - der.head_loss_m * mesh.x_m / mesh.length_m
    flow = np.full(n + 1, q0)
    head_initial = mesh.station_head(head).copy()

    time_s = np.arange(n_steps + 1, dtype=float) * dt  # k*dt, not a running sum (U-08)
    head_valve = np.empty(n_steps + 1)
    head_mid = np.empty(n_steps + 1)
    flow_res = np.empty(n_steps + 1)
    flow_valve = np.empty(n_steps + 1)

    n_stations = mesh.station_x_m.size
    head_max = head_initial.copy()
    head_min = head_initial.copy()
    head_max_step = np.zeros(n_stations, dtype=np.int64)
    head_min_step = np.zeros(n_stations, dtype=np.int64)

    head_valve[0] = head[n]
    head_mid[0] = head[mid]
    flow_res[0] = flow[0]
    flow_valve[0] = flow[n]
    if observer is not None:
        observer(0, head, flow)

    new_head = np.empty(n + 1)
    new_flow = np.empty(n + 1)
    two_b = 2.0 * b
    for k in range(1, n_steps + 1):
        u = b * flow - r * flow * np.abs(flow)
        cp = head[:-1] + u[:-1]  # C+ at nodes 1..N
        cm = head[1:] - u[1:]  # C- at nodes 0..N-1

        new_head[1:n] = 0.5 * (cp[:-1] + cm[1:])
        new_flow[1:n] = (cp[:-1] - cm[1:]) / two_b

        new_head[0] = h_dep
        new_flow[0] = (h_dep - cm[0]) / b

        q_valve = law.flow_at(time_s[k])
        new_flow[n] = q_valve
        new_head[n] = cp[-1] - b * q_valve

        head, new_head = new_head, head
        flow, new_flow = new_flow, flow

        st_head = mesh.station_head(head)
        higher = st_head > head_max
        if higher.any():
            head_max[higher] = st_head[higher]
            head_max_step[higher] = k
        lower = st_head < head_min
        if lower.any():
            head_min[lower] = st_head[lower]
            head_min_step[lower] = k

        head_valve[k] = head[n]
        head_mid[k] = head[mid]
        flow_res[k] = flow[0]
        flow_valve[k] = flow[n]
        if observer is not None:
            observer(k, head, flow)

    return MocResult(
        mesh=mesh,
        derived=der,
        n_steps=n_steps,
        time_s=time_s,
        head_valve_m=head_valve,
        head_midpoint_m=head_mid,
        flow_reservoir_m3s=flow_res,
        flow_valve_m3s=flow_valve,
        head_initial_m=head_initial,
        head_max_m=head_max,
        head_min_m=head_min,
        head_max_step=head_max_step,
        head_min_step=head_min_step,
    )
