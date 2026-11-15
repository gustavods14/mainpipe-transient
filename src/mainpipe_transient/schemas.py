"""Layer-1 contract: request and response models (plan 01 §1.3-§1.5, SCHEMA_VERSION 1.0).

Range and cross-field rules are custom validators with Spanish messages (U-13), so
that the portal's FastAPI 422 carries them in Spanish (kit 02 §3). Units are in the
field names (U-06): flows in L/s, diameter in mm, lengths/heads in m, pressure heads
in m of water column (``_m``), times in s, PN in bar.
"""

from __future__ import annotations

import math
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from ._format import ceil_decimals, floor_decimals, fmt_time, fmt_trim, fmt_value
from ._geometry import (
    MAX_STEPS,
    N_REACHES_MAX,
    N_REACHES_MIN,
    count_steps,
    default_duration_s,
    max_even_reaches,
    time_step_s,
)

__all__ = ["SCHEMA_VERSION", "SolveRequest", "SolveResponse", "Check", "CheckCode"]

SCHEMA_VERSION = "1.0"  # frozen at G4 (U-15, U-37)

CLOSURE_POINTS_MIN = 2
CLOSURE_POINTS_MAX = 20
FIRST_FLOW_REL_TOL = 1e-3  # 0.1 % of Q0 (HU-1.6 crit. 3, U-18)
FRICTION_NUMBER_MAX = 0.5  # U-03
_DURATION_ABS_TOL = 1e-9  # binary noise when comparing durations (same spirit as U-08)

CheckCode = Literal[
    "PN_EXCEEDED",
    "PN_NEAR_LIMIT",
    "COLUMN_SEPARATION_RISK",
    "SUBATMOSPHERIC_PRESSURE",
    "STEADY_NEGATIVE_PRESSURE",
]


def _lps(value: float) -> str:
    return fmt_trim(value, 3)


def _count(n: int) -> str:
    """Step count for messages; huge counts in scientific notation (F2-04)."""
    return str(n) if n < 10**9 else f"{float(n):.3g}"


def _closure_duration(times: list[float], flows: list[float]) -> float:
    """Tc: first table instant with Q = 0 (M11). Requires a law ending at 0."""
    return next(t for t, q in zip(times, flows) if q == 0.0)


def _max_duration_display(length_m: float, n_reaches: int, wave_speed_ms: float) -> float:
    """T_max = MAX_STEPS*dt truncated to the decimals of U-26, guaranteed to fit (HU-1.6-13)."""
    dt = time_step_s(length_m, n_reaches, wave_speed_ms)
    shown = floor_decimals(MAX_STEPS * dt)
    while count_steps(shown, dt) > MAX_STEPS:  # pragma: no cover - defensive against rounding
        shown = round(shown - 0.001, 3)
    return shown


class SolveRequest(BaseModel):
    """Input of :func:`mainpipe_transient.solve`."""

    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)

    scenario: Literal["reservoir_pipe_valve"] = Field(
        "reservoir_pipe_valve",
        description="System layout. Only 'reservoir_pipe_valve' in v1 "
        "(constant-level reservoir, pipe, downstream valve).",
    )
    geometry: Literal["horizontal", "profile"] = Field(
        "horizontal",
        description="'horizontal': single pipe elevation (length_m, pipe_elevation_m). "
        "'profile': real alignment (profile_x_m, profile_z_m).",
    )
    length_m: float | None = Field(
        None,
        description="Pipe length (m). Required and > 0 with geometry 'horizontal'; "
        "not allowed with 'profile' (L = last profile_x_m).",
    )
    pipe_elevation_m: float | None = Field(
        None,
        description="Pipe elevation (m), same datum as reservoir_level_m. Required and "
        "<= reservoir_level_m with geometry 'horizontal'; not allowed with 'profile'.",
    )
    profile_x_m: list[float] | None = Field(
        None,
        description="Profile chainages (m). Required with geometry 'profile', not allowed "
        "with 'horizontal'. 2-500 points, starts at 0, strictly increasing.",
    )
    profile_z_m: list[float] | None = Field(
        None,
        description="Profile elevations (m), same length as profile_x_m; the first one "
        "<= reservoir_level_m.",
    )
    inner_diameter_mm: float = Field(..., description="Inner diameter D (mm). > 0.")
    wave_speed_ms: float = Field(..., description="Wave speed a (m/s). 0 < a <= 1500.")
    darcy_friction_factor: float = Field(
        ..., description="Darcy-Weisbach friction factor f (dimensionless). 0 <= f <= 0.1."
    )
    initial_flow_lps: float = Field(..., description="Steady-state flow Q0 (L/s). > 0.")
    reservoir_level_m: float = Field(
        ..., description="Constant reservoir level H_dep (m), same datum as the pipe."
    )
    density_kgm3: float = Field(1000.0, description="Water density (kg/m3). > 0.")
    gravity_ms2: float = Field(9.81, description="Gravity g (m/s2). 9.7 <= g <= 9.9.")
    pn_bar: float = Field(..., description="Pipe pressure rating PN (bar). > 0.")
    min_allowed_pressure_head_m: float = Field(
        -10.0,
        description="Minimum allowed pressure head (m of water column). "
        "-10.33 <= value <= 0. Default -10.",
    )
    closure_time_s: list[float] = Field(
        ...,
        description="Closure law times (s). 2-20 points, starts at 0, strictly increasing.",
    )
    closure_flow_lps: list[float] = Field(
        ...,
        description="Closure law flows (L/s), same length as closure_time_s. First within "
        "0.1 % of initial_flow_lps (replaced by Q0), 0 <= Q <= Q0, last = 0 (full closure).",
    )
    n_reaches: int = Field(
        20, description="Number of reaches N of the mesh. Even, 10 <= N <= 200. Default 20."
    )
    duration_s: float | None = Field(
        None,
        description="Simulated duration T (s). Default (null): Tc + 5*(4L/a). Must be "
        f">= Tc + 2L/a and need at most {MAX_STEPS} time steps of dt = L/(N*a), "
        "also when defaulted.",
    )
    include_frames: bool = Field(
        True,
        description="If false, frame_* fields and frame_stride come back null.",
    )

    # ------------------------------------------------------------ field rules
    @field_validator("length_m")
    @classmethod
    def _length_positive(cls, v: float | None) -> float | None:
        if v is not None and not v > 0:
            raise ValueError(
                f"length_m = {fmt_value(v)} m no es válido: la longitud de la tubería debe "
                "ser mayor que 0 m."
            )
        return v

    @field_validator("inner_diameter_mm")
    @classmethod
    def _diameter_positive(cls, v: float) -> float:
        if not v > 0:
            raise ValueError(
                f"inner_diameter_mm = {fmt_value(v)} mm no es válido: el diámetro interior "
                "debe ser mayor que 0 mm."
            )
        return v

    @field_validator("wave_speed_ms")
    @classmethod
    def _wave_speed_range(cls, v: float) -> float:
        if not 0 < v <= 1500:
            raise ValueError(
                f"wave_speed_ms = {fmt_value(v)} m/s está fuera de rango: la celeridad debe "
                "ser mayor que 0 y como máximo 1500 m/s."
            )
        return v

    @field_validator("darcy_friction_factor")
    @classmethod
    def _friction_range(cls, v: float) -> float:
        if not 0 <= v <= 0.1:
            raise ValueError(
                f"darcy_friction_factor = {fmt_value(v)} está fuera de rango: el factor de "
                "fricción de Darcy debe estar entre 0 y 0.1."
            )
        return v

    @field_validator("initial_flow_lps")
    @classmethod
    def _flow_positive(cls, v: float) -> float:
        if not v > 0:
            raise ValueError(
                f"initial_flow_lps = {fmt_value(v)} L/s no es válido: el caudal inicial debe "
                "ser mayor que 0 L/s."
            )
        return v

    @field_validator("density_kgm3")
    @classmethod
    def _density_positive(cls, v: float) -> float:
        if not v > 0:
            raise ValueError(
                f"density_kgm3 = {fmt_value(v)} kg/m³ no es válido: la densidad debe ser "
                "mayor que 0 kg/m³."
            )
        return v

    @field_validator("gravity_ms2")
    @classmethod
    def _gravity_range(cls, v: float) -> float:
        if not 9.7 <= v <= 9.9:
            raise ValueError(
                f"gravity_ms2 = {fmt_value(v)} m/s² está fuera de rango: la gravedad debe "
                "estar entre 9.7 y 9.9 m/s²."
            )
        return v

    @field_validator("pn_bar")
    @classmethod
    def _pn_positive(cls, v: float) -> float:
        if not v > 0:
            raise ValueError(
                f"pn_bar = {fmt_value(v)} bar no es válido: el timbraje (PN) debe ser mayor "
                "que 0 bar."
            )
        return v

    @field_validator("min_allowed_pressure_head_m")
    @classmethod
    def _min_pressure_range(cls, v: float) -> float:
        if not -10.33 <= v <= 0:
            raise ValueError(
                f"min_allowed_pressure_head_m = {fmt_value(v)} m.c.a. está fuera de rango: "
                "la presión mínima admisible debe estar entre -10.33 y 0 m.c.a."
            )
        return v

    @field_validator("n_reaches")
    @classmethod
    def _n_reaches_range(cls, v: int) -> int:
        if v % 2 != 0 or not N_REACHES_MIN <= v <= N_REACHES_MAX:
            raise ValueError(
                f"n_reaches = {v} no es válido: el número de tramos debe ser un entero par "
                f"entre {N_REACHES_MIN} y {N_REACHES_MAX}."
            )
        return v

    @field_validator("duration_s")
    @classmethod
    def _duration_positive(cls, v: float | None) -> float | None:
        if v is not None and not v > 0:
            raise ValueError(
                f"duration_s = {fmt_value(v)} s no es válido: la duración de la simulación "
                "debe ser mayor que 0 s."
            )
        return v

    @field_validator("closure_time_s")
    @classmethod
    def _closure_times(cls, v: list[float]) -> list[float]:
        n = len(v)
        if not CLOSURE_POINTS_MIN <= n <= CLOSURE_POINTS_MAX:
            raise ValueError(
                f"La ley de cierre debe tener entre {CLOSURE_POINTS_MIN} y "
                f"{CLOSURE_POINTS_MAX} puntos; closure_time_s tiene {n}."
            )
        if v[0] != 0:
            raise ValueError(
                "La ley de cierre debe empezar en t = 0 s: el punto 1 de closure_time_s "
                f"es t = {fmt_value(v[0])} s."
            )
        for i in range(1, n):
            if not v[i] > v[i - 1]:
                raise ValueError(
                    "Los tiempos de la ley de cierre (closure_time_s) deben ser estrictamente "
                    f"crecientes: el punto {i + 1} (t = {fmt_value(v[i])} s) no es mayor que "
                    f"el punto {i} (t = {fmt_value(v[i - 1])} s)."
                )
        return v

    @field_validator("closure_flow_lps")
    @classmethod
    def _closure_flow_count(cls, v: list[float]) -> list[float]:
        n = len(v)
        if not CLOSURE_POINTS_MIN <= n <= CLOSURE_POINTS_MAX:
            raise ValueError(
                f"La ley de cierre debe tener entre {CLOSURE_POINTS_MIN} y "
                f"{CLOSURE_POINTS_MAX} puntos; closure_flow_lps tiene {n}."
            )
        return v

    # ------------------------------------------------------------ cross rules
    @model_validator(mode="after")
    def _cross_rules(self) -> SolveRequest:
        # Pydantic only converts ValueError/AssertionError; extreme magnitudes that pass the
        # field rules can overflow or divide by zero here (F2-01). Report them as a 422.
        try:
            return self._cross_rules_unchecked()
        except ArithmeticError as exc:
            raise ValueError(
                "Los datos producen valores fuera del rango numérico representable: revisa "
                "las magnitudes extremas de longitud, diámetro, celeridad, caudal y duración."
            ) from exc

    def _cross_rules_unchecked(self) -> SolveRequest:
        self._check_geometry_fields()
        self._check_closure_flows()
        if self.geometry == "profile":
            # Profile validation (HU-2.3) and the profile engine arrive in plan phase 3.
            return self
        assert self.length_m is not None
        self._check_mesh_and_duration(self.length_m)
        return self

    def _check_geometry_fields(self) -> None:
        if self.geometry != "horizontal":
            return
        missing = [n for n in ("length_m", "pipe_elevation_m") if getattr(self, n) is None]
        if missing:
            raise ValueError(
                f"Con geometry = horizontal hay que enviar {' y '.join(missing)}."
            )
        extra = [n for n in ("profile_x_m", "profile_z_m") if getattr(self, n) is not None]
        if extra:
            raise ValueError(
                f"Con geometry = horizontal no se admite {' ni '.join(extra)}: el perfil "
                "solo se usa con geometry = profile."
            )
        assert self.pipe_elevation_m is not None
        if self.pipe_elevation_m > self.reservoir_level_m:
            raise ValueError(
                "La tubería queda por encima del nivel del depósito: pipe_elevation_m = "
                f"{fmt_value(self.pipe_elevation_m)} m es mayor que reservoir_level_m = "
                f"{fmt_value(self.reservoir_level_m)} m. La cota de la tubería no puede "
                "superar el nivel del depósito."
            )

    def _check_closure_flows(self) -> None:
        times, flows, q0 = self.closure_time_s, self.closure_flow_lps, self.initial_flow_lps
        if len(times) != len(flows):
            raise ValueError(
                "closure_time_s y closure_flow_lps deben tener el mismo número de puntos: "
                f"tienen {len(times)} y {len(flows)}."
            )
        if abs(flows[0] - q0) > FIRST_FLOW_REL_TOL * q0:
            raise ValueError(
                f"El primer caudal de la ley (closure_flow_lps[0] = {_lps(flows[0])} L/s) "
                f"difiere del caudal inicial (initial_flow_lps = {_lps(q0)} L/s) en más de "
                "0.1 %: deben coincidir."
            )
        for i, (t, q) in enumerate(zip(times, flows)):
            if i > 0 and not 0 <= q <= q0:
                raise ValueError(
                    f"El caudal del punto {i + 1} de la ley de cierre (t = {fmt_value(t)} s) "
                    f"es {_lps(q)} L/s: debe estar entre 0 y {_lps(q0)} L/s (caudal inicial)."
                )
        if flows[-1] != 0:
            raise ValueError(
                "La ley de cierre debe terminar con la válvula cerrada (Q = 0 L/s): el último "
                f"punto (t = {fmt_value(times[-1])} s) tiene Q = {_lps(flows[-1])} L/s. Los "
                "cierres parciales no están admitidos."
            )

    def _check_mesh_and_duration(self, length_m: float) -> None:
        a, n = self.wave_speed_ms, self.n_reaches
        tc = _closure_duration(self.closure_time_s, self.closure_flow_lps)
        reflection = 2.0 * length_m / a
        t_min = tc + reflection

        if self.duration_s is not None and self.duration_s < t_min - _DURATION_ABS_TOL:
            raise ValueError(
                f"duration_s = {fmt_value(self.duration_s)} s es menor que la duración mínima "
                f"de {fmt_time(ceil_decimals(t_min))} s (Tc = {fmt_time(tc)} s más "
                f"2L/a = {fmt_time(reflection)} s): la simulación no cubriría el cierre y su "
                f"primera reflexión. Usa duration_s >= {fmt_time(ceil_decimals(t_min))} s."
            )

        self._check_friction_number(length_m)

        dt = time_step_s(length_m, n, a)
        defaulted = self.duration_s is None
        duration = default_duration_s(tc, length_m, a) if defaulted else self.duration_s
        assert duration is not None
        steps = count_steps(duration, dt)
        if steps <= MAX_STEPS:
            return

        t_max = _max_duration_display(length_m, n, a)
        if defaulted:
            head = (
                f"La duración por defecto Tc + 5·(4L/a) = {fmt_time(duration)} s necesita "
                f"{_count(steps)} pasos con n_reaches = {n} y supera el tope de {MAX_STEPS} pasos."
            )
        else:
            head = (
                f"duration_s = {fmt_value(duration)} s necesita {_count(steps)} pasos con "
                f"n_reaches = {n} y supera el tope de {MAX_STEPS} pasos."
            )

        t_min_shown = ceil_decimals(t_min)
        if count_steps(t_min, dt) > MAX_STEPS or t_min_shown > t_max:
            # The minimum duration does not fit (or no 3-decimal duration lies between the
            # displayed minimum and maximum, F2-03): only a coarser mesh helps.
            n_fit = max_even_reaches(t_min_shown, length_m, a)
            if n_fit is None:
                raise ValueError(
                    f"{head} La duración mínima Tc + 2L/a = {fmt_time(t_min_shown)} s "
                    f"tampoco cabe ni con la malla más gruesa (n_reaches = {N_REACHES_MIN}): "
                    "el cierre es demasiado lento para el tope de pasos de cálculo."
                )
            raise ValueError(
                f"{head} La duración mínima Tc + 2L/a = {fmt_time(t_min_shown)} s "
                f"supera la máxima admisible con esa malla ({fmt_time(t_max)} s): usa una "
                f"malla más gruesa, n_reaches <= {n_fit}."
            )

        n_fit = max_even_reaches(duration, length_m, a)
        coarser = (
            f" o usa una malla más gruesa (n_reaches <= {n_fit})" if n_fit is not None else ""
        )
        if defaulted:
            raise ValueError(
                f"{head} La duración máxima admisible con esa malla es {fmt_time(t_max)} s: "
                f"envía duration_s <= {fmt_time(t_max)} s{coarser}."
            )
        raise ValueError(
            f"{head} La duración máxima admisible con esa malla es {fmt_time(t_max)} s: "
            f"acorta duration_s a {fmt_time(t_max)} s o menos{coarser}."
        )

    def _check_friction_number(self, length_m: float) -> None:
        d = self.inner_diameter_mm / 1000.0
        area = math.pi * d**2 / 4.0
        v0 = (self.initial_flow_lps / 1000.0) / area
        f, a = self.darcy_friction_factor, self.wave_speed_ms

        def phi(n: int) -> float:
            return f * (length_m / n) * v0 / (2.0 * d * a)

        value = phi(self.n_reaches)
        if not math.isfinite(value):
            raise OverflowError("non-finite friction number")  # -> range message (F2-06)
        if value <= FRICTION_NUMBER_MAX:
            return
        n_ok = next(
            (n for n in range(N_REACHES_MIN, N_REACHES_MAX + 1, 2) if phi(n) <= FRICTION_NUMBER_MAX),
            None,
        )
        head = (
            f"El número de fricción del tramo φ = f·Δx·V₀/(2·D·a) = {fmt_trim(value, 3)} con "
            f"n_reaches = {self.n_reaches} supera {FRICTION_NUMBER_MAX} y el cálculo sería "
            "inestable."
        )
        if n_ok is None:
            raise ValueError(
                f"{head} Ni con la malla más fina (n_reaches = {N_REACHES_MAX}) se cumple: "
                "revisa el factor de fricción, el diámetro o el caudal."
            )
        raise ValueError(f"{head} Usa n_reaches >= {n_ok} (par) para cumplirlo.")


class Check(BaseModel):
    """A non-conforming result that does not prevent computing (kit 01 §5, plan 01 §1.5)."""

    model_config = ConfigDict(allow_inf_nan=False)

    code: CheckCode = Field(..., description="Stable check code.")
    severity: Literal["warning", "error"] = Field(
        ..., description="Portal palette (D-13): warning -> warning, error -> danger."
    )
    message: str = Field(..., description="User-facing message, in Spanish, with units.")
    value_m: float = Field(..., description="Value that triggers the check (m of water column).")
    limit_m: float = Field(..., description="Threshold crossed (m of water column).")
    x_m: float = Field(..., description="Chainage of the value (m); one of x_m.")
    time_s: float = Field(..., description="Instant of the value (s); one of time_s.")
    first_x_m: float | None = Field(
        None,
        description="COLUMN_SEPARATION_RISK only: first chainage below the limit (m). "
        "null for the other codes.",
    )
    first_time_s: float | None = Field(
        None,
        description="COLUMN_SEPARATION_RISK only: first instant below the limit (s). "
        "null for the other codes.",
    )
    first_pressure_head_m: float | None = Field(
        None,
        description="COLUMN_SEPARATION_RISK only: pressure head at that point and instant "
        "(m of water column). null for the other codes.",
    )


_NULL_WITHOUT_FRAMES = " null when include_frames is false."


class SolveResponse(BaseModel):
    """Output of :func:`mainpipe_transient.solve`. Series are parallel columns."""

    model_config = ConfigDict(allow_inf_nan=False)

    # identity and state
    schema_version: str = Field(..., description="Equal to SCHEMA_VERSION.")
    scenario: Literal["reservoir_pipe_valve"] = Field(..., description="Echo of the input.")
    geometry: Literal["horizontal", "profile"] = Field(..., description="Echo of the input.")
    status: Literal["ok", "warning", "error"] = Field(
        ..., description="Most severe severity in checks; 'ok' if there are none."
    )
    checks: list[Check] = Field(..., description="Errors first, then warnings.")

    # derived
    length_m: float = Field(..., description="Pipe length L (m).")
    area_m2: float = Field(..., description="Cross-section A = pi*D^2/4 (m2).")
    velocity_initial_ms: float = Field(..., description="Steady velocity V0 = Q0/A (m/s).")
    head_loss_m: float = Field(..., description="Steady friction loss h_f = f*(L/D)*V0^2/(2g) (m).")
    dx_m: float = Field(..., description="Reach length dx = L/N (m).")
    dt_s: float = Field(..., description="Time step dt = dx/a (s).")
    n_reaches: int = Field(..., description="Number of reaches N used.")
    n_steps: int = Field(..., description="Number of time steps, ceil(T/dt - 1e-9).")
    duration_s: float = Field(..., description="Effective duration n_steps*dt (s).")
    reflection_time_s: float = Field(..., description="2L/a (s).")
    wave_period_s: float = Field(..., description="4L/a (s).")
    closure_duration_s: float = Field(
        ..., description="Tc: first closure-law instant with Q = 0 (s)."
    )
    friction_number: float = Field(
        ..., description="Reach friction number phi = f*dx*V0/(2*D*a) (dimensionless, <= 0.5)."
    )

    # time series, length n_steps + 1
    time_s: list[float] = Field(..., description="Instants k*dt (s).")
    head_valve_m: list[float] = Field(..., description="Piezometric head at the valve (m).")
    head_midpoint_m: list[float] = Field(
        ..., description="Piezometric head at the node x = L/2 (m)."
    )
    pressure_head_valve_m: list[float] = Field(
        ..., description="Pressure head at the valve, H - z (m of water column)."
    )
    pressure_head_midpoint_m: list[float] = Field(
        ..., description="Pressure head at x = L/2, H - z (m of water column)."
    )
    flow_reservoir_lps: list[float] = Field(..., description="Flow at the reservoir (L/s).")
    flow_valve_lps: list[float] = Field(..., description="Flow at the valve (L/s).")

    # envelopes per chainage
    x_m: list[float] = Field(
        ..., description="Chainages (m): computational nodes and profile vertices, sorted."
    )
    x_is_node: list[bool] = Field(
        ..., description="true if the chainage is a computational node, false if only a vertex."
    )
    elevation_m: list[float] = Field(..., description="Pipe elevation z(x) (m).")
    head_initial_m: list[float] = Field(..., description="Steady-state head (m).")
    pressure_head_initial_m: list[float] = Field(
        ..., description="Steady-state pressure head (m of water column)."
    )
    head_max_m: list[float] = Field(..., description="Maximum head over all steps (m).")
    head_min_m: list[float] = Field(..., description="Minimum head over all steps (m).")
    pressure_head_max_m: list[float] = Field(
        ..., description="Maximum pressure head over all steps (m of water column)."
    )
    pressure_head_min_m: list[float] = Field(
        ..., description="Minimum pressure head over all steps (m of water column)."
    )

    # extremes (tie-break: first instant, then lower x)
    head_valve_max_m: float = Field(..., description="Maximum head at the valve (m).")
    head_valve_max_time_s: float = Field(..., description="Its first instant (s).")
    head_valve_min_m: float = Field(..., description="Minimum head at the valve (m).")
    head_valve_min_time_s: float = Field(..., description="Its first instant (s).")
    pressure_head_max_global_m: float = Field(
        ..., description="Maximum pressure head in the whole pipe (m of water column)."
    )
    pressure_head_max_global_x_m: float = Field(..., description="Its chainage (m).")
    pressure_head_max_global_time_s: float = Field(..., description="Its instant (s).")
    pressure_head_min_global_m: float = Field(
        ..., description="Minimum pressure head in the whole pipe (m of water column)."
    )
    pressure_head_min_global_x_m: float = Field(..., description="Its chainage (m).")
    pressure_head_min_global_time_s: float = Field(..., description="Its instant (s).")

    # pressure rating and depression limit
    pn_head_m: float = Field(
        ..., description="PN as pressure head, PN*1e5/(rho*g) (m of water column)."
    )
    pressure_max_pn_ratio_pct: float = Field(
        ..., description="100*pressure_head_max_global_m/pn_head_m (%)."
    )
    min_allowed_pressure_head_m: float = Field(
        ..., description="Echo of the depression limit used (m of water column)."
    )

    # theoretical reference (informative)
    maneuver_type: Literal["rapid", "slow"] = Field(
        ..., description="'rapid' if Tc <= 2L/a, else 'slow'."
    )
    joukowsky_head_rise_m: float = Field(..., description="Joukowsky rise a*V0/g (m).")
    michaud_head_rise_m: float | None = Field(
        ..., description="Michaud rise 2*L*V0/(g*Tc) (m). null for a rapid maneuver."
    )
    full_pulse_length_m: float | None = Field(
        ..., description="Full-pulse length L - a*Tc/2 (m). null for a slow maneuver."
    )
    theoretical_head_rise_m: float = Field(
        ..., description="Joukowsky if rapid, Michaud if slow (m)."
    )
    moc_head_rise_valve_m: float = Field(
        ..., description="head_valve_max_m minus the steady head at the valve (m)."
    )
    theory_deviation_pct: float = Field(
        ..., description="100*(MOC - theoretical)/theoretical (%)."
    )

    # player series
    frame_stride: int | None = Field(
        ..., description="Time steps between consecutive frames (1 = no subsampling); the "
        "last interval may be shorter." + _NULL_WITHOUT_FRAMES,
    )
    frame_time_s: list[float] | None = Field(
        ..., description="Frame instants (s), each one a value of time_s." + _NULL_WITHOUT_FRAMES
    )
    frame_x_m: list[float] | None = Field(
        ..., description="Identical to x_m (m)." + _NULL_WITHOUT_FRAMES
    )
    frame_head_m: list[list[float]] | None = Field(
        ..., description="[k][j]: head at frame k, chainage j (m)." + _NULL_WITHOUT_FRAMES
    )
    frame_pressure_head_m: list[list[float]] | None = Field(
        ...,
        description="[k][j]: pressure head H - z (m of water column)." + _NULL_WITHOUT_FRAMES,
    )
