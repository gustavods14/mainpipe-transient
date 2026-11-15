"""Theoretical reference: Joukowsky, Michaud and full-pulse length (plan 01 M15-M17, U-17).

Informative only: never produces a check nor changes ``status`` (HU-3.4).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

__all__ = ["Theory", "theory"]


@dataclass(frozen=True)
class Theory:
    maneuver_type: Literal["rapid", "slow"]
    joukowsky_head_rise_m: float
    michaud_head_rise_m: float | None
    full_pulse_length_m: float | None
    theoretical_head_rise_m: float
    moc_head_rise_valve_m: float
    theory_deviation_pct: float


def theory(
    *,
    length_m: float,
    wave_speed_ms: float,
    gravity_ms2: float,
    velocity_initial_ms: float,
    closure_duration_s: float,
    head_valve_initial_m: float,
    head_valve_max_m: float,
) -> Theory:
    a, g, v0, tc, L = wave_speed_ms, gravity_ms2, velocity_initial_ms, closure_duration_s, length_m
    rapid = tc <= 2.0 * L / a
    joukowsky = a * v0 / g
    michaud = None if rapid else 2.0 * L * v0 / (g * tc)
    pulse = L - a * tc / 2.0 if rapid else None
    theoretical = joukowsky if rapid else michaud
    assert theoretical is not None
    moc_rise = head_valve_max_m - head_valve_initial_m
    return Theory(
        maneuver_type="rapid" if rapid else "slow",
        joukowsky_head_rise_m=joukowsky,
        michaud_head_rise_m=michaud,
        full_pulse_length_m=pulse,
        theoretical_head_rise_m=theoretical,
        moc_head_rise_valve_m=moc_rise,
        theory_deviation_pct=100.0 * (moc_rise - theoretical) / theoretical,
    )
