"""Internal-API cases for the MOC core (phase 1, no Pydantic yet).

«Caso Excel» and «caso sin fricción» as defined in plan 01 §6 and HU-1.1.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace

import numpy as np

from mainpipe_transient._closure import build_closure_law
from mainpipe_transient._geometry import build_horizontal_mesh, count_steps, default_duration_s
from mainpipe_transient._moc import MocResult, PipeData, simulate

EXCEL_LAW_T = [0.0, 0.5, 1.0, 1.5, 2.0, 5.0, 10.0, 20.0]
EXCEL_LAW_Q_LPS = [100.0, 50.0, 20.0, 0.0, 0.0, 0.0, 0.0, 0.0]


@dataclass(frozen=True)
class Case:
    """Inputs in contract units (L/s, mm), converted to SI by :func:`run`."""

    length_m: float = 1000.0
    inner_diameter_mm: float = 300.0
    wave_speed_ms: float = 1000.0
    darcy_friction_factor: float = 0.02
    initial_flow_lps: float = 100.0
    reservoir_level_m: float = 100.0
    pipe_elevation_m: float = 0.0
    gravity_ms2: float = 9.81
    n_reaches: int = 20
    duration_s: float | None = 20.0
    closure_time_s: list[float] = field(default_factory=lambda: list(EXCEL_LAW_T))
    closure_flow_lps: list[float] = field(default_factory=lambda: list(EXCEL_LAW_Q_LPS))

    def with_(self, **changes) -> "Case":
        return replace(self, **changes)


EXCEL = Case()
FRICTIONLESS = Case(
    darcy_friction_factor=0.0,
    duration_s=5.0,
    closure_time_s=[0.0, 0.05],
    closure_flow_lps=[100.0, 0.0],
)


class Recorder:
    """Observer that keeps the full H/Q history (tests only)."""

    def __init__(self) -> None:
        self.head: list[np.ndarray] = []
        self.flow: list[np.ndarray] = []

    def __call__(self, k: int, head: np.ndarray, flow: np.ndarray) -> None:
        assert k == len(self.head)
        self.head.append(head.copy())
        self.flow.append(flow.copy())

    @property
    def head_m(self) -> np.ndarray:
        return np.array(self.head)

    @property
    def flow_lps(self) -> np.ndarray:
        return 1000.0 * np.array(self.flow)


def run(case: Case, recorder: Recorder | None = None) -> MocResult:
    q0 = case.initial_flow_lps / 1000.0
    law = build_closure_law(
        case.closure_time_s, [q / 1000.0 for q in case.closure_flow_lps], q0
    )
    mesh = build_horizontal_mesh(
        case.length_m, case.n_reaches, case.wave_speed_ms, case.pipe_elevation_m
    )
    duration = case.duration_s
    if duration is None:
        duration = default_duration_s(law.closure_duration_s, case.length_m, case.wave_speed_ms)
    pipe = PipeData(
        diameter_m=case.inner_diameter_mm / 1000.0,
        wave_speed_ms=case.wave_speed_ms,
        friction_factor=case.darcy_friction_factor,
        initial_flow_m3s=q0,
        reservoir_level_m=case.reservoir_level_m,
        gravity_ms2=case.gravity_ms2,
    )
    return simulate(pipe, mesh, law, count_steps(duration, mesh.dt_s), observer=recorder)
