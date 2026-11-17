"""Orchestration of :func:`solve` and the error wrapper (plan 01 §1.1, kit 01 §3, kit 02 §1).

Plan phases 2-5: horizontal and profile geometry, checks and status, and the player
frames (U-10, U-24). Contract 2.0: rho and g are constants (U-40) and the m / m.c.a. / L/s
output lists are rounded once, here, when the response is built (U-39, D-63).
Phase 7 (amendment F5R-02, U-44): a result that is not representable in ``float64`` is a
422 about the input, not a 500.
"""

from __future__ import annotations

import logging
import math
from typing import Any

import numpy as np
from pydantic import ValidationError

from ._checks import build_checks, status_of
from ._closure import build_closure_law
from ._constants import DENSITY_KGM3, GRAVITY_MS2
from ._frames import plan_frames
from ._geometry import (
    Mesh,
    build_horizontal_mesh,
    build_profile_mesh,
    count_steps,
    default_duration_s,
)
from ._moc import MocResult, PipeData, simulate
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

# U-44 (1), plan 01 §1.6: the single message of a non-representable result.
UNREPRESENTABLE_MESSAGE = (
    "El resultado del cálculo queda fuera del rango numérico representable: revisa las "
    "magnitudes extremas del nivel del depósito (reservoir_level_m), de las cotas "
    "(pipe_elevation_m o profile_z_m), de la longitud, del diámetro y del caudal inicial. "
    "Con valores de proyecto no se llega a este límite."
)

_UNEXPECTED_MESSAGE = (
    "Error interno inesperado durante el cálculo del transitorio. Los datos de entrada "
    "pasaron la validación; si el problema persiste, informa del caso al equipo de la API."
)


def solve(data: dict[str, Any]) -> dict[str, Any]:
    """Compute the water-hammer transient for one reservoir-pipe-valve case.

    Validates ``data`` with :class:`SolveRequest`, runs the MOC and returns
    ``SolveResponse(...).model_dump(mode="json")``.

    Raises:
        MainpipeTransientValidationError: invalid input (HTTP 422), message in Spanish; also
            when the input gives a result that ``float64`` cannot represent (U-44).
        MainpipeTransientComputationError: any unexpected internal failure (HTTP 500),
            including a NaN without overflow.
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
    except ArithmeticError as exc:  # U-44 (1): OverflowError, ZeroDivisionError, FloatingPointError
        logger.info("non-representable result (%s: %s)", type(exc).__name__, exc)
        raise MainpipeTransientValidationError(UNREPRESENTABLE_MESSAGE) from exc
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
        gravity_ms2=GRAVITY_MS2,
    )
    n_steps = count_steps(duration, mesh.dt_s)
    frames = plan_frames(n_steps, mesh.station_x_m.size) if req.include_frames else None
    res = simulate(
        pipe,
        mesh,
        law,
        n_steps,
        pressure_limit_m=req.min_allowed_pressure_head_m,
        frame_steps=None if frames is None else frames.steps,
    )
    der = res.derived

    h_vmax, t_vmax = res.head_valve_max()
    h_vmin, t_vmin = res.head_valve_min()
    p_max = res.pressure_head_max_global()
    p_min = res.pressure_head_min_global()
    steady_min = res.pressure_head_initial_min()
    first_below = res.first_below_limit()
    pn_head = req.pn_bar * 1e5 / (DENSITY_KGM3 * GRAVITY_MS2)  # M18, U-40
    pn_ratio_pct = 100.0 * p_max.value_m / pn_head
    th = theory(
        length_m=mesh.length_m,
        wave_speed_ms=req.wave_speed_ms,
        gravity_ms2=GRAVITY_MS2,
        velocity_initial_ms=der.velocity_initial_ms,
        closure_duration_s=tc,
        head_valve_initial_m=float(res.head_valve_m[0]),
        head_valve_max_m=h_vmax,
    )

    # Every number of the response, at full precision (before the rounding of U-39).
    scalars: dict[str, float | None] = {
        "length_m": mesh.length_m,
        "area_m2": der.area_m2,
        "velocity_initial_ms": der.velocity_initial_ms,
        "head_loss_m": der.head_loss_m,
        "dx_m": mesh.dx_m,
        "dt_s": mesh.dt_s,
        "duration_s": res.duration_s,
        "reflection_time_s": der.reflection_time_s,
        "wave_period_s": der.wave_period_s,
        "closure_duration_s": tc,
        "friction_number": der.friction_number,
        "head_valve_max_m": h_vmax,
        "head_valve_max_time_s": t_vmax,
        "head_valve_min_m": h_vmin,
        "head_valve_min_time_s": t_vmin,
        "pressure_head_max_global_m": p_max.value_m,
        "pressure_head_max_global_x_m": p_max.x_m,
        "pressure_head_max_global_time_s": p_max.time_s,
        "pressure_head_min_global_m": p_min.value_m,
        "pressure_head_min_global_x_m": p_min.x_m,
        "pressure_head_min_global_time_s": p_min.time_s,
        "pn_head_m": pn_head,
        "pressure_max_pn_ratio_pct": pn_ratio_pct,
        "min_allowed_pressure_head_m": req.min_allowed_pressure_head_m,
        "joukowsky_head_rise_m": th.joukowsky_head_rise_m,
        "michaud_head_rise_m": th.michaud_head_rise_m,
        "full_pulse_length_m": th.full_pulse_length_m,
        "theoretical_head_rise_m": th.theoretical_head_rise_m,
        "moc_head_rise_valve_m": th.moc_head_rise_valve_m,
        "theory_deviation_pct": th.theory_deviation_pct,
    }
    # Lists rounded to 3 decimals when the response is built (U-39 (1), D-63 (1)).
    rounded: dict[str, np.ndarray] = {
        "head_valve_m": res.head_valve_m,
        "head_midpoint_m": res.head_midpoint_m,
        "pressure_head_valve_m": res.pressure_head_valve_m,
        "pressure_head_midpoint_m": res.pressure_head_midpoint_m,
        "flow_reservoir_lps": _LPS_PER_M3S * res.flow_reservoir_m3s,
        "flow_valve_lps": _LPS_PER_M3S * res.flow_valve_m3s,
        "x_m": mesh.station_x_m,
        "elevation_m": mesh.station_elevation_m,
        "head_initial_m": res.head_initial_m,
        "pressure_head_initial_m": res.pressure_head_initial_m,
        "head_max_m": res.head_max_m,
        "head_min_m": res.head_min_m,
        "pressure_head_max_m": res.pressure_head_max_m,
        "pressure_head_min_m": res.pressure_head_min_m,
    }
    stride = None if frames is None else frames.stride
    frame_arrays = _frame_arrays(res, stride)
    # Check fields not already above: the steady minimum and the first crossing (§1.5).
    check_values = [
        v for e in (steady_min, first_below) if e is not None for v in (e.value_m, e.x_m, e.time_s)
    ]
    _ensure_representable(
        [*scalars.values(), *check_values],
        [res.time_s, *rounded.values(), *frame_arrays.values()],
    )

    checks = build_checks(
        pressure_max=p_max,
        pressure_min=p_min,
        steady_min=steady_min,
        first_below_limit=first_below,
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
        n_reaches=mesh.n_reaches,
        n_steps=res.n_steps,
        maneuver_type=th.maneuver_type,
        time_s=_floats(res.time_s),
        x_is_node=mesh.station_is_node.tolist(),
        **scalars,
        **{name: _rounded(values) for name, values in rounded.items()},
        **_frame_fields(frame_arrays, stride),
    )


def _ensure_representable(scalars: list[float | None], arrays: list[np.ndarray]) -> None:
    """U-44 (1)-(2): any +/-inf among the full-precision output values is a 422.

    Only infinities count: a NaN without overflow is a package failure and keeps failing as
    a 500 when the response is built (``allow_inf_nan=False``, U-44 (3)).
    """
    if any(v is not None and math.isinf(v) for v in scalars) or any(
        bool(np.isinf(a).any()) for a in arrays
    ):
        raise MainpipeTransientValidationError(UNREPRESENTABLE_MESSAGE)


def _build_mesh(req: SolveRequest) -> Mesh:
    if req.geometry == "profile":
        assert req.profile_x_m is not None and req.profile_z_m is not None
        return build_profile_mesh(req.profile_x_m, req.profile_z_m, req.n_reaches, req.wave_speed_ms)
    assert req.length_m is not None and req.pipe_elevation_m is not None
    return build_horizontal_mesh(req.length_m, req.n_reaches, req.wave_speed_ms, req.pipe_elevation_m)


def _frame_arrays(res: MocResult, stride: int | None) -> dict[str, np.ndarray]:
    """Full-precision player series (plan 01 §1.4, U-10, U-11); empty without frames (U-24)."""
    if stride is None or res.frame_steps is None or res.frame_head_m is None:
        return {}
    # No frame_pressure_head_m since 2.0 (D-64): p = frame_head_m[k][j] - elevation_m[j].
    return {
        "frame_time_s": res.time_s[res.frame_steps],
        "frame_x_m": res.mesh.station_x_m,
        "frame_head_m": res.frame_head_m,
    }


def _frame_fields(arrays: dict[str, np.ndarray], stride: int | None) -> dict[str, Any]:
    """Response fields of the player; all null without frames (U-24)."""
    if not arrays:
        return dict.fromkeys(("frame_stride", "frame_time_s", "frame_x_m", "frame_head_m"))
    return {
        "frame_stride": stride,
        "frame_time_s": _floats(arrays["frame_time_s"]),
        "frame_x_m": _rounded(arrays["frame_x_m"]),
        "frame_head_m": [_rounded(row) for row in arrays["frame_head_m"]],
    }


def _floats(values: np.ndarray) -> list[float]:
    """Full-precision list: time_s and frame_time_s are never rounded (U-39 (2))."""
    return values.astype(float).tolist()


_OUTPUT_DECIMALS = 3  # U-39 (1), D-63 (1)


def _rounded(values: np.ndarray) -> list[float]:
    """The single rounding of every m / m.c.a. / L/s output list (U-39 (3)-(5), D-63 (1)-(2)).

    Python's ``round(x, 3)`` gives the correctly rounded nearest decimal (ties to even) and
    leaves huge magnitudes untouched without overflowing, unlike ``numpy.round`` (U-39 (4));
    adding ``0.0`` turns ``-0.0`` into ``0.0``. Always applied to full-precision values,
    never to lists that are already rounded (U-39 (5)).
    """
    return [round(v, _OUTPUT_DECIMALS) + 0.0 for v in values.astype(float).tolist()]


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
