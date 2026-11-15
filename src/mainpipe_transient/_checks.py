"""Checks, global status and user-facing messages (plan 01 §1.5, HU-3.1 ... HU-3.5).

A non-conforming result is not an exception (kit 01 §5): every check here comes with a
computed response. Messages are Spanish, with units and decimal points (kit 01 §5, U-26).
The comparison with Joukowsky / Michaud never produces a check (HU-3.4, U-17).
"""

from __future__ import annotations

from typing import Literal

from ._format import fmt_head, fmt_pn, fmt_pressure, fmt_time, fmt_x
from ._moc import Extreme
from .schemas import Check, CheckCode

__all__ = ["PN_NEAR_LIMIT_PCT", "build_checks", "status_of"]

PN_NEAR_LIMIT_PCT = 80.0  # U-16: fixed threshold, not an input

# Errors first, then warnings; within a severity, the order of the plan table (§1.5).
_ORDER: tuple[CheckCode, ...] = (
    "PN_EXCEEDED",
    "PN_NEAR_LIMIT",
    "COLUMN_SEPARATION_RISK",
    "SUBATMOSPHERIC_PRESSURE",
    "STEADY_NEGATIVE_PRESSURE",
)
_SEVERITY_RANK = {"warning": 1, "error": 2}


def build_checks(
    *,
    pressure_max: Extreme,
    pressure_min: Extreme,
    steady_min: Extreme,
    first_below_limit: Extreme | None,
    pn_bar: float,
    pn_head_m: float,
    pn_ratio_pct: float,
    min_allowed_m: float,
) -> list[Check]:
    """All checks of one result, sorted as the plan requires (§1.5).

    ``pressure_max`` / ``pressure_min`` are the global extremes of the pressure head
    envelopes; ``steady_min`` the lowest steady-state pressure head; ``first_below_limit``
    the first crossing below ``min_allowed_m`` recorded in the MOC loop (U-25).
    """
    checks: list[Check] = []

    # Timbraje (HU-3.1). Strict ">" as the per-chainage predicate of D-60 (U-36).
    if pressure_max.value_m > pn_head_m:
        checks.append(_pn_exceeded(pressure_max, pn_bar, pn_head_m))
    elif pn_ratio_pct > PN_NEAR_LIMIT_PCT:
        checks.append(_pn_near_limit(pressure_max, pn_bar, pn_head_m, pn_ratio_pct))

    # Minimum pressure (HU-3.2). Strict "<" as the per-chainage predicate of D-60 (U-36).
    if pressure_min.value_m < min_allowed_m:
        if first_below_limit is None:  # pragma: no cover - guaranteed by simulate()
            raise RuntimeError("pressure below the limit without a recorded first crossing")
        checks.append(_column_separation(pressure_min, first_below_limit, min_allowed_m))
    elif pressure_min.value_m < 0.0:
        checks.append(_subatmospheric(pressure_min, min_allowed_m))

    # Steady state (HU-3.3)
    if steady_min.value_m < 0.0:
        checks.append(_steady_negative(steady_min, min_allowed_m))

    checks.sort(key=lambda c: (-_SEVERITY_RANK[c.severity], _ORDER.index(c.code)))
    return checks


def status_of(checks: list[Check]) -> Literal["ok", "warning", "error"]:
    """Most severe severity among the checks; ``ok`` when there are none (HU-3.5)."""
    if not checks:
        return "ok"
    return max((c.severity for c in checks), key=_SEVERITY_RANK.__getitem__)


# ------------------------------------------------------------------ one builder per code
def _where_when(e: Extreme) -> str:
    return f"x = {fmt_x(e.x_m)} m, t = {fmt_time(e.time_s)} s"


def _pn_exceeded(p_max: Extreme, pn_bar: float, pn_head_m: float) -> Check:
    # Literal of HU-3.1 crit. 4.
    message = (
        f"La presión máxima ({fmt_head(p_max.value_m)} m.c.a. en {_where_when(p_max)}) supera "
        f"el PN {fmt_pn(pn_bar)} bar ({fmt_head(pn_head_m)} m.c.a.). Aumente la clase de la "
        "tubería o alargue el cierre."
    )
    return _check("PN_EXCEEDED", "error", message, p_max, pn_head_m)


def _pn_near_limit(p_max: Extreme, pn_bar: float, pn_head_m: float, ratio_pct: float) -> Check:
    message = (
        f"La presión máxima ({fmt_head(p_max.value_m)} m.c.a. en {_where_when(p_max)}) alcanza "
        f"el {fmt_head(ratio_pct)} % del PN {fmt_pn(pn_bar)} bar ({fmt_head(pn_head_m)} m.c.a.), "
        f"por encima del umbral de aviso del {fmt_pn(PN_NEAR_LIMIT_PCT)} %. El margen es "
        "reducido: considere una clase de tubería mayor o un cierre más lento."
    )
    return _check("PN_NEAR_LIMIT", "warning", message, p_max, pn_head_m)


def _column_separation(p_min: Extreme, first: Extreme, limit_m: float) -> Check:
    # Literal of HU-3.2 crit. 4: value and limit, where, when, and that the MOC stops
    # being physical from there. The value is the pressure head at the first crossing.
    message = (
        f"La presión cae a {fmt_pressure(first.value_m)} m.c.a., por debajo del límite "
        f"admisible de {fmt_pressure(limit_m)} m.c.a., por primera vez en "
        f"x = {fmt_x(first.x_m)} m y t = {fmt_time(first.time_s)} s. A partir de ese instante "
        "puede haber separación de columna y los resultados del MOC simple dejan de ser "
        "físicos: las presiones y caudales posteriores no son fiables."
    )
    return _check(
        "COLUMN_SEPARATION_RISK",
        "error",
        message,
        p_min,
        limit_m,
        first_x_m=first.x_m,
        first_time_s=first.time_s,
        first_pressure_head_m=first.value_m,
    )


def _subatmospheric(p_min: Extreme, limit_m: float) -> Check:
    message = (
        f"La presión mínima ({fmt_pressure(p_min.value_m)} m.c.a. en {_where_when(p_min)}) es "
        "inferior a la atmosférica, aunque no baja del límite admisible de "
        f"{fmt_pressure(limit_m)} m.c.a. Revise si conviene proteger la conducción (ventosas, "
        "cierre más lento)."
    )
    return _check("SUBATMOSPHERIC_PRESSURE", "warning", message, p_min, 0.0)


def _steady_negative(steady: Extreme, limit_m: float) -> Check:
    head = (
        "La presión ya es negativa en el régimen inicial, antes de la maniobra: "
        f"{fmt_pressure(steady.value_m)} m.c.a. en x = {fmt_x(steady.x_m)} m"
    )
    if steady.value_m < limit_m:
        message = (
            f"{head}, por debajo del límite admisible de {fmt_pressure(limit_m)} m.c.a. "
            "El trazado o el caudal de diseño no son viables: revise el perfil o el caudal."
        )
        return _check("STEADY_NEGATIVE_PRESSURE", "error", message, steady, limit_m)
    message = (
        f"{head} (la piezométrica de régimen queda por debajo de la tubería). Revise el "
        "perfil o el caudal de diseño."
    )
    return _check("STEADY_NEGATIVE_PRESSURE", "warning", message, steady, 0.0)


def _check(
    code: CheckCode,
    severity: Literal["warning", "error"],
    message: str,
    at: Extreme,
    limit_m: float,
    **first: float,
) -> Check:
    return Check(
        code=code,
        severity=severity,
        message=message,
        value_m=at.value_m,
        limit_m=limit_m,
        x_m=at.x_m,
        time_s=at.time_s,
        **first,
    )
