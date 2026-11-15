"""Orchestration of :func:`solve` and the error wrapper (plan 01 §1.1, kit 01 §3, kit 02 §1).

Plan phases 2-4: horizontal and profile geometry, checks and status. Still pending by
plan phase: the player frames (phase 5; ``frame_*`` are null until then).
"""

from __future__ import annotations

import logging
from typing import Any

import numpy as np
from pydantic import ValidationError

from ._checks import build_checks, status_of
from ._closure import build_closure_law
from ._geometry import (
    Mesh,
    build_horizontal_mesh,
    build_profile_mesh,
    count_steps,
    default_duration_s,
)
from ._moc import PipeData, simulate
from ._theory import theory
from .exceptions import (
    MainpipeTransientComputationError,
    MainpipeTransientError,
    MainpipeTransientValidationError,
)
from .schemas import SCHEMA_VERSION, SolveRequest, SolveResponse

logger = logging.getLogger("mainpipe_transient")

__all__ = ["solve"]

_LPS_PER_M3S = 1000.0
_MM_PER_M = 1000.0

_UNEXPECTED_MESSAGE = (
    "Error interno inesperado durante el cálculo del transitorio. Los datos de entrada "
    "pasaron la validación; si el problema persiste, informa del caso al equipo de la API."
)


def solve(data: dict[str, Any]) -> dict[str, Any]:
    """Compute the water-hammer transient for one reservoir-pipe-valve case.

    Validates ``data`` with :class:`SolveRequest`, runs the MOC and returns
    ``SolveResponse(...).model_dump(mode="json")``.

    Raises:
        MainpipeTransientValidationError: invalid input (HTTP 422), message in Spanish.
        MainpipeTransientComputationError: any unexpected internal failure (HTTP 500).
    """
    try:
        request = SolveRequest.model_validate(data)
    except ValidationError as exc:
        raise MainpipeTransientValidationError(_format_validation_error(exc)) from exc
    except Exception as exc:  # a validator bug must not leak a foreign exception (kit 02 §1)
        logger.exception("unexpected failure while validating the request")
        raise MainpipeTransientComputationError(_UNEXPECTED_MESSAGE) from exc

    try:
        response = _compute(request)
        return response.model_dump(mode="json")
    except MainpipeTransientError:
        raise
    except Exception as exc:
        logger.exception("unexpected failure while solving")
        raise MainpipeTransientComputationError(_UNEXPECTED_MESSAGE) from exc


def _compute(req: SolveRequest) -> SolveResponse:
    q0 = req.initial_flow_lps / _LPS_PER_M3S
    law = build_closure_law(
        req.closure_time_s, [q / _LPS_PER_M3S for q in req.closure_flow_lps], q0
    )
    mesh = _build_mesh(req)
    tc = law.closure_duration_s
    duration = req.duration_s
    if duration is None:
        duration = default_duration_s(tc, mesh.length_m, req.wave_speed_ms)
    pipe = PipeData(
        diameter_m=req.inner_diameter_mm / _MM_PER_M,
        wave_speed_ms=req.wave_speed_ms,
        friction_factor=req.darcy_friction_factor,
        initial_flow_m3s=q0,
        reservoir_level_m=req.reservoir_level_m,
        gravity_ms2=req.gravity_ms2,
    )
    res = simulate(
        pipe,
        mesh,
        law,
        count_steps(duration, mesh.dt_s),
        pressure_limit_m=req.min_allowed_pressure_head_m,
    )
    der = res.derived

    h_vmax, t_vmax = res.head_valve_max()
    h_vmin, t_vmin = res.head_valve_min()
    p_max = res.pressure_head_max_global()
    p_min = res.pressure_head_min_global()
    pn_head = req.pn_bar * 1e5 / (req.density_kgm3 * req.gravity_ms2)
    pn_ratio_pct = 100.0 * p_max.value_m / pn_head
    th = theory(
        length_m=mesh.length_m,
        wave_speed_ms=req.wave_speed_ms,
        gravity_ms2=req.gravity_ms2,
        velocity_initial_ms=der.velocity_initial_ms,
        closure_duration_s=tc,
        head_valve_initial_m=float(res.head_valve_m[0]),
        head_valve_max_m=h_vmax,
    )
    checks = build_checks(
        pressure_max=p_max,
        pressure_min=p_min,
        steady_min=res.pressure_head_initial_min(),
        first_below_limit=res.first_below_limit(),
        pn_bar=req.pn_bar,
        pn_head_m=pn_head,
        pn_ratio_pct=pn_ratio_pct,
        min_allowed_m=req.min_allowed_pressure_head_m,
    )

    return SolveResponse(
        schema_version=SCHEMA_VERSION,
        scenario=req.scenario,
        geometry=req.geometry,
        status=status_of(checks),
        checks=checks,
        length_m=mesh.length_m,
        area_m2=der.area_m2,
        velocity_initial_ms=der.velocity_initial_ms,
        head_loss_m=der.head_loss_m,
        dx_m=mesh.dx_m,
        dt_s=mesh.dt_s,
        n_reaches=mesh.n_reaches,
        n_steps=res.n_steps,
        duration_s=res.duration_s,
        reflection_time_s=der.reflection_time_s,
        wave_period_s=der.wave_period_s,
        closure_duration_s=tc,
        friction_number=der.friction_number,
        time_s=_floats(res.time_s),
        head_valve_m=_floats(res.head_valve_m),
        head_midpoint_m=_floats(res.head_midpoint_m),
        pressure_head_valve_m=_floats(res.pressure_head_valve_m),
        pressure_head_midpoint_m=_floats(res.pressure_head_midpoint_m),
        flow_reservoir_lps=_floats(_LPS_PER_M3S * res.flow_reservoir_m3s),
        flow_valve_lps=_floats(_LPS_PER_M3S * res.flow_valve_m3s),
        x_m=_floats(mesh.station_x_m),
        x_is_node=mesh.station_is_node.tolist(),
        elevation_m=_floats(mesh.station_elevation_m),
        head_initial_m=_floats(res.head_initial_m),
        pressure_head_initial_m=_floats(res.pressure_head_initial_m),
        head_max_m=_floats(res.head_max_m),
        head_min_m=_floats(res.head_min_m),
        pressure_head_max_m=_floats(res.pressure_head_max_m),
        pressure_head_min_m=_floats(res.pressure_head_min_m),
        head_valve_max_m=h_vmax,
        head_valve_max_time_s=t_vmax,
        head_valve_min_m=h_vmin,
        head_valve_min_time_s=t_vmin,
        pressure_head_max_global_m=p_max.value_m,
        pressure_head_max_global_x_m=p_max.x_m,
        pressure_head_max_global_time_s=p_max.time_s,
        pressure_head_min_global_m=p_min.value_m,
        pressure_head_min_global_x_m=p_min.x_m,
        pressure_head_min_global_time_s=p_min.time_s,
        pn_head_m=pn_head,
        pressure_max_pn_ratio_pct=pn_ratio_pct,
        min_allowed_pressure_head_m=req.min_allowed_pressure_head_m,
        maneuver_type=th.maneuver_type,
        joukowsky_head_rise_m=th.joukowsky_head_rise_m,
        michaud_head_rise_m=th.michaud_head_rise_m,
        full_pulse_length_m=th.full_pulse_length_m,
        theoretical_head_rise_m=th.theoretical_head_rise_m,
        moc_head_rise_valve_m=th.moc_head_rise_valve_m,
        theory_deviation_pct=th.theory_deviation_pct,
        # plan phase 5
        frame_stride=None,
        frame_time_s=None,
        frame_x_m=None,
        frame_head_m=None,
        frame_pressure_head_m=None,
    )


def _build_mesh(req: SolveRequest) -> Mesh:
    if req.geometry == "profile":
        assert req.profile_x_m is not None and req.profile_z_m is not None
        return build_profile_mesh(req.profile_x_m, req.profile_z_m, req.n_reaches, req.wave_speed_ms)
    assert req.length_m is not None and req.pipe_elevation_m is not None
    return build_horizontal_mesh(req.length_m, req.n_reaches, req.wave_speed_ms, req.pipe_elevation_m)


def _floats(values: np.ndarray) -> list[float]:
    return values.astype(float).tolist()


# ------------------------------------------------------------------ validation messages
_TYPE_MESSAGES = {
    "missing": "falta el campo obligatorio",
    "extra_forbidden": "campo no admitido (revisa el nombre)",
    "float_type": "debe ser un número",
    "float_parsing": "debe ser un número",
    "finite_number": "debe ser un número finito",
    "int_type": "debe ser un número entero",
    "int_parsing": "debe ser un número entero",
    "int_from_float": "debe ser un número entero",
    "bool_type": "debe ser true o false",
    "bool_parsing": "debe ser true o false",
    "list_type": "debe ser una lista de números",
    "literal_error": "valor no admitido",
    "model_type": "la entrada debe ser un objeto JSON con los datos del cálculo",
    "model_attributes_type": "la entrada debe ser un objeto JSON con los datos del cálculo",
}


_MAX_MESSAGE = 400  # the portal shows at most 400 characters of detail (kit 02 §3)


def _format_loc(loc: tuple) -> str:
    """``closure_time_s.1`` -> ``closure_time_s (punto 2)``: 1-based like our messages."""
    name = ".".join(str(p) for p in loc if not isinstance(p, int))
    points = [p for p in loc if isinstance(p, int)]
    if points:
        name = f"{name} (punto {points[-1] + 1})" if name else f"punto {points[-1] + 1}"
    return name


def _format_validation_error(exc: ValidationError) -> str:
    """Spanish, field-named message for a Pydantic ValidationError (kit 02 §3)."""
    parts: list[str] = []
    for err in exc.errors(include_url=False):
        loc = _format_loc(tuple(err.get("loc", ())))
        if err["type"] == "value_error":
            # Our own validators: the message is already Spanish and names the field.
            msg = str(err["msg"]).removeprefix("Value error, ")
        else:
            text = _TYPE_MESSAGES.get(err["type"], "valor no válido")
            if err["type"] == "literal_error":
                expected = (err.get("ctx") or {}).get("expected")
                if expected:
                    text = f"{text}; se admite {str(expected).replace(' or ', ' o ')}"
            msg = f"{loc}: {text}." if loc else f"{text[0].upper()}{text[1:]}."
        if msg not in parts:
            parts.append(msg)
    return _join_within_limit(parts)


def _join_within_limit(parts: list[str]) -> str:
    """Join messages without exceeding the portal limit; say how many were left out."""
    text = parts[0][:_MAX_MESSAGE]
    for i, part in enumerate(parts[1:], start=1):
        remaining = len(parts) - i
        candidate = f"{text} {part}"
        tail = f" (y {remaining - 1} error{'es' if remaining - 1 != 1 else ''} más)"
        if len(candidate) + (len(tail) if remaining > 1 else 0) <= _MAX_MESSAGE:
            text = candidate
            continue
        more = f" (y {remaining} error{'es' if remaining != 1 else ''} más)"
        return text + more if len(text) + len(more) <= _MAX_MESSAGE else text
    return text
