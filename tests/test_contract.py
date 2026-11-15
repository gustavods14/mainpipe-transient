"""Phase 2: contract, validators, solve wrapper and step cap (plan 01 §1, §5 phase 2).

Covers HU-1.6 crit. 1-11 and 13, HU-1.7 crit. 5, U-03, and the phase-1 findings
carried over: F1-02 (V-05 through solve with mm and L/s), F1-04 (U-08 tolerance) and
F1-05 (defaults and echoes through the contract).
"""

from __future__ import annotations

import json
import math
import statistics
import time

import numpy as np
import pydantic
import pytest

import mainpipe_transient as mpt
from mainpipe_transient import (
    MainpipeTransientComputationError,
    MainpipeTransientError,
    MainpipeTransientValidationError,
    SolveResponse,
    solve,
)
from mainpipe_transient._geometry import MAX_STEPS, count_steps, time_step_s
from rounding import HALF_MM

EXCEL_INPUT = {
    "geometry": "horizontal",
    "length_m": 1000.0,
    "pipe_elevation_m": 0.0,
    "inner_diameter_mm": 300.0,
    "wave_speed_ms": 1000.0,
    "darcy_friction_factor": 0.02,
    "initial_flow_lps": 100.0,
    "reservoir_level_m": 100.0,
    "pn_bar": 25.0,
    "closure_time_s": [0.0, 0.5, 1.0, 1.5, 2.0, 5.0, 10.0, 20.0],
    "closure_flow_lps": [100.0, 50.0, 20.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    "n_reaches": 20,
    "duration_s": 20.0,
}

H_TOL = 1e-6  # m (U-29)
Q_TOL_LPS = 1e-6  # L/s (U-29)


def case(**changes) -> dict:
    data = json.loads(json.dumps(EXCEL_INPUT))
    for key, value in changes.items():
        if value is ...:
            data.pop(key, None)
        else:
            data[key] = value
    return data


def reject(data) -> str:
    with pytest.raises(MainpipeTransientValidationError) as info:
        solve(data)
    exc = info.value
    assert exc.http_status == 422
    assert exc.__cause__ is not None  # raise ... from exc (kit 01 §3)
    message = str(exc)
    assert "Value error" not in message
    assert len(message) <= 400, message  # the portal cuts detail at 400 characters
    return message


# --------------------------------------------------------------------------- public API
def test_public_api_exports_models():
    assert {"SolveRequest", "SolveResponse", "Check"} <= set(mpt.__all__)


def test_response_is_strict_json_and_valid_contract():
    out = solve(case())
    text = json.dumps(out, allow_nan=False)  # no NaN / inf / numpy types
    assert json.loads(text) == out
    SolveResponse.model_validate(out)
    assert out["schema_version"] == mpt.SCHEMA_VERSION == "2.0"
    assert out["scenario"] == "reservoir_pipe_valve"
    assert out["geometry"] == "horizontal"
    assert "frame_flow_lps" not in out  # U-33
    assert set(out) == set(SolveResponse.model_fields)


def test_response_lengths_are_consistent():
    out = solve(case())
    n = out["n_steps"] + 1
    for key in ("time_s", "head_valve_m", "head_midpoint_m", "pressure_head_valve_m",
                "pressure_head_midpoint_m", "flow_reservoir_lps", "flow_valve_lps"):
        assert len(out[key]) == n, key
    m = len(out["x_m"])
    for key in ("x_is_node", "elevation_m", "head_initial_m", "pressure_head_initial_m",
                "head_max_m", "head_min_m", "pressure_head_max_m", "pressure_head_min_m"):
        assert len(out[key]) == m, key
    assert all(out["x_is_node"])


def test_derived_and_reference_fields_excel(excel_reference):
    out = solve(case())
    der = excel_reference["derived"]
    val = {c: e["value"] for c, e in excel_reference["validation"].items()}
    assert out["area_m2"] == pytest.approx(der["area_m2"], rel=1e-12)
    assert out["velocity_initial_ms"] == pytest.approx(der["velocity_initial_ms"], rel=1e-12)
    assert out["head_loss_m"] == pytest.approx(der["head_loss_m"], rel=1e-12)
    assert out["reflection_time_s"] == 2.0
    assert out["wave_period_s"] == 4.0
    assert out["closure_duration_s"] == 1.5
    assert out["pn_head_m"] == pytest.approx(25e5 / (1000 * 9.81), rel=1e-12)
    assert out["pressure_max_pn_ratio_pct"] == pytest.approx(
        100 * out["pressure_head_max_global_m"] / out["pn_head_m"], rel=1e-12
    )
    assert out["min_allowed_pressure_head_m"] == -10.0
    assert out["maneuver_type"] == "rapid"
    assert out["theory_deviation_pct"] == pytest.approx(100 * val["C27"], rel=1e-9)


def test_min_allowed_pressure_echo():
    assert solve(case(min_allowed_pressure_head_m=-7.0))["min_allowed_pressure_head_m"] == -7.0


def test_include_frames_toggles_the_frame_fields():
    """U-24: frame_* null only with include_frames = false (phase 5 fills them)."""
    keys = ("frame_stride", "frame_time_s", "frame_x_m", "frame_head_m")  # 2.0: U-24, D-64
    with_frames = solve(case())
    without = solve(case(include_frames=False))
    for key in keys:
        assert with_frames[key] is not None, key
        assert without[key] is None, key


# --------------------------------------------------------------------------- F1-02
def test_v05_through_solve_with_contract_units(excel_reference):
    """V-05 repeated through solve(): D in mm, Q in L/s in and out (finding F1-02)."""
    out = solve(case())
    grid = excel_reference["grid"]
    ref_h = np.array(grid["head_m"])
    ref_q_lps = 1000.0 * np.array(grid["flow_m3s"])
    mid = 10

    assert out["n_steps"] == 400
    np.testing.assert_array_equal(out["x_m"], grid["x_m"])
    np.testing.assert_allclose(out["time_s"], grid["time_s"], rtol=0, atol=1e-12)
    # 2.0: the lists come at 3 decimals (U-39), so V-05 through solve() is ± (0.0005 + 1e-6)
    # m or L/s (plan 01 §6, V-05); ± 1e-6 still holds on MocResult (test_excel_reference)
    h_tol, q_tol = H_TOL + HALF_MM, Q_TOL_LPS + HALF_MM
    np.testing.assert_allclose(out["head_valve_m"], ref_h[:, -1], rtol=0, atol=h_tol)
    np.testing.assert_allclose(out["head_midpoint_m"], ref_h[:, mid], rtol=0, atol=h_tol)
    np.testing.assert_allclose(out["flow_valve_lps"], ref_q_lps[:, -1], rtol=0, atol=q_tol)
    np.testing.assert_allclose(out["flow_reservoir_lps"], ref_q_lps[:, 0], rtol=0, atol=q_tol)
    np.testing.assert_allclose(out["head_initial_m"], ref_h[0], rtol=0, atol=h_tol)
    np.testing.assert_allclose(out["head_max_m"], ref_h.max(axis=0), rtol=0, atol=h_tol)
    np.testing.assert_allclose(out["head_min_m"], ref_h.min(axis=0), rtol=0, atol=h_tol)
    # extremes are scalars at full precision: still ± 1e-6 m (V-05)
    assert out["head_valve_max_m"] == pytest.approx(ref_h[:, -1].max(), abs=H_TOL)
    assert out["head_valve_min_m"] == pytest.approx(ref_h[:, -1].min(), abs=H_TOL)


def test_unit_conversions_are_exercised():
    """Doubling D (mm) quarters V0; flows come back in L/s, not m3/s."""
    out = solve(case())
    big = solve(case(inner_diameter_mm=600.0))
    assert big["velocity_initial_ms"] == pytest.approx(out["velocity_initial_ms"] / 4, rel=1e-12)
    assert out["area_m2"] == pytest.approx(math.pi * 0.3**2 / 4, rel=1e-12)
    assert out["flow_valve_lps"][0] == 100.0
    assert out["flow_reservoir_lps"][0] == 100.0


# --------------------------------------------------------------------------- F1-04
def test_u08_step_tolerance_is_needed():
    """U-08: with N = 26, 4.0 s / dt = 104.00000000000001; the tolerance keeps 104 steps."""
    dt = time_step_s(1000.0, 26, 1000.0)
    assert 4.0 / dt > 104  # binary noise above the integer
    assert math.ceil(4.0 / dt) == 105  # what a plain ceil would give
    assert count_steps(4.0, dt) == 104
    assert count_steps(1.0, dt) == 26  # 1.0 / dt = 26.000000000000004
    out = solve(case(n_reaches=26, duration_s=4.0))
    assert out["n_steps"] == 104
    assert out["duration_s"] == pytest.approx(4.0, abs=1e-12)


# --------------------------------------------------------------------------- F1-05
def test_defaults_through_contract():
    """n_reaches defaults to 20; default duration Tc + 5*(4L/a) = 21.5 s -> 430 steps."""
    out = solve(case(n_reaches=..., duration_s=...))
    assert out["n_reaches"] == 20
    assert out["dx_m"] == 50.0
    assert out["dt_s"] == 0.05
    assert out["n_steps"] == 430
    assert out["duration_s"] == pytest.approx(21.5, abs=1e-12)
    assert out["time_s"][-1] == out["duration_s"]


@pytest.mark.parametrize(
    ("n_reaches", "duration", "n_steps", "effective"),
    [(20, 20.0, 400, 20.0), (20, 20.01, 401, 20.05), (40, 20.0, 800, 20.0)],
)
def test_echo_of_mesh_and_effective_duration(n_reaches, duration, n_steps, effective):
    """HU-1.7 crit. 1 and 4 through the contract: n_reaches, n_steps and duration_s echoed."""
    out = solve(case(n_reaches=n_reaches, duration_s=duration))
    assert out["n_reaches"] == n_reaches
    assert out["n_steps"] == n_steps
    assert out["duration_s"] == pytest.approx(effective, abs=1e-12)
    assert len(out["x_m"]) == n_reaches + 1


def test_default_duration_is_not_trimmed_to_the_cap():
    """HU-1.7 crit. 3: a default duration over the cap is a 422, never silently cut."""
    msg = reject(case(n_reaches=200, duration_s=..., closure_time_s=[0.0, 31.0],
                      closure_flow_lps=[100.0, 0.0]))
    assert "duración por defecto" in msg
    assert "51 s" in msg
    assert "duration_s <= 50 s" in msg


# --------------------------------------------------------------------------- HU-1.6
def test_hu16_crit1_times_strictly_increasing():
    msg = reject(case(closure_time_s=[0.0, 1.0, 1.0, 2.0], closure_flow_lps=[100.0, 50.0, 0.0, 0.0]))
    assert "estrictamente crecientes" in msg
    assert "punto 3 (t = 1 s)" in msg


def test_hu16_crit2_law_starts_at_zero():
    msg = reject(case(closure_time_s=[0.5, 1.0, 2.0], closure_flow_lps=[100.0, 50.0, 0.0]))
    assert "empezar en t = 0 s" in msg


def test_hu16_crit3_first_flow_matches_initial_flow():
    msg = reject(case(closure_time_s=[0.0, 2.0], closure_flow_lps=[99.8, 0.0]))
    assert "99.8 L/s" in msg and "100 L/s" in msg
    assert "0.1 %" in msg
    # Within 0.1 %: accepted and replaced by Q0 (U-18).
    out = solve(case(closure_time_s=[0.0, 2.0], closure_flow_lps=[99.95, 0.0]))
    assert out["flow_valve_lps"][0] == 100.0


def test_hu16_crit4_law_ends_closed():
    msg = reject(case(closure_time_s=[0.0, 2.0], closure_flow_lps=[100.0, 40.0]))
    assert "válvula cerrada (Q = 0 L/s)" in msg
    assert "cierres parciales no están admitidos" in msg


@pytest.mark.parametrize("bad", [-5.0, 120.0])
def test_hu16_crit5_flow_range(bad):
    msg = reject(case(closure_time_s=[0.0, 1.0, 2.0], closure_flow_lps=[100.0, bad, 0.0]))
    assert "punto 2" in msg
    assert "entre 0 y 100 L/s" in msg


@pytest.mark.parametrize(
    ("times", "flows", "expected"),
    [
        ([0.0, 1.0, 2.0], [100.0, 0.0], "mismo número de puntos"),
        ([0.0], [100.0], "entre 2 y 20 puntos"),
        ([float(i) for i in range(21)], [100.0] * 20 + [0.0], "entre 2 y 20 puntos"),
    ],
    ids=["distinta-longitud", "un-punto", "21-puntos"],
)
def test_hu16_crit6_law_length(times, flows, expected):
    assert expected in reject(case(closure_time_s=times, closure_flow_lps=flows, duration_s=...))


@pytest.mark.parametrize(
    ("field", "value", "expected"),
    [
        ("wave_speed_ms", 1600.0, "como máximo 1500 m/s"),
        ("wave_speed_ms", 0.0, "mayor que 0"),
        ("darcy_friction_factor", 0.11, "entre 0 y 0.1"),
        ("darcy_friction_factor", -0.01, "entre 0 y 0.1"),
        ("min_allowed_pressure_head_m", -10.5, "entre -10.33 y 0 m.c.a."),
        ("min_allowed_pressure_head_m", 1.0, "entre -10.33 y 0 m.c.a."),
        ("length_m", 0.0, "mayor que 0 m"),
        ("inner_diameter_mm", -300.0, "mayor que 0 mm"),
        ("initial_flow_lps", 0.0, "mayor que 0 L/s"),
        ("pn_bar", 0.0, "mayor que 0 bar"),
    ],
)
def test_hu16_crit7_ranges_name_field_and_limit(field, value, expected):
    msg = reject(case(**{field: value}))
    assert field in msg
    assert expected in msg


def test_hu16_crit8_pipe_above_reservoir():
    msg = reject(case(pipe_elevation_m=120.0))
    assert "por encima del nivel del depósito" in msg
    assert "120 m" in msg and "100 m" in msg


@pytest.mark.parametrize("n", [21, 8, 202])
def test_hu16_crit9_n_reaches(n):
    msg = reject(case(n_reaches=n))
    assert f"n_reaches = {n}" in msg
    assert "entero par entre 10 y 200" in msg


def test_hu16_crit10_duration_below_minimum():
    msg = reject(case(closure_time_s=[0.0, 30.0], closure_flow_lps=[100.0, 0.0], duration_s=20.0))
    assert "Tc = 30 s" in msg
    assert "2L/a = 2 s" in msg
    assert "32 s" in msg
    # Exactly the minimum is accepted.
    assert solve(case(closure_time_s=[0.0, 30.0], closure_flow_lps=[100.0, 0.0],
                      duration_s=32.0))["n_steps"] == 640


def test_hu16_crit11_unexpected_failure_is_wrapped(monkeypatch):
    import mainpipe_transient._solve as solve_module

    def boom(*args, **kwargs):
        raise RuntimeError("injected failure")

    monkeypatch.setattr(solve_module, "simulate", boom)
    with pytest.raises(MainpipeTransientComputationError) as info:
        solve(case())
    exc = info.value
    assert exc.http_status == 500
    assert isinstance(exc.__cause__, RuntimeError)
    assert "injected" not in str(exc)  # generic message, no internals
    assert "inesperado" in str(exc)


def test_hu16_crit11_nan_in_response_is_a_computation_error(monkeypatch):
    import mainpipe_transient._solve as solve_module

    real = solve_module.theory

    def nan_theory(**kwargs):
        from dataclasses import replace

        return replace(real(**kwargs), theory_deviation_pct=float("nan"))

    monkeypatch.setattr(solve_module, "theory", nan_theory)
    with pytest.raises(MainpipeTransientComputationError):
        solve(case())


def test_hu16_crit13_excel_n200():
    """D-57: 50 s fits exactly 10 000 steps; 50.001 s is a 422 that shows «50 s»."""
    out = solve(case(n_reaches=200, duration_s=50.0))
    assert out["n_steps"] == MAX_STEPS == 10_000
    assert out["dt_s"] == 0.005

    msg = reject(case(n_reaches=200, duration_s=50.001))
    assert "duration_s" in msg and "n_reaches = 200" in msg
    assert "10001 pasos" in msg
    assert "50 s" in msg
    assert "acorta duration_s" in msg and "malla más gruesa" in msg
    assert "n_reaches <= 198" in msg


def test_hu16_crit13_displayed_maximum_resent_computes():
    """With a non-round dt, the truncated T_max shown in the message computes without error."""
    data = case(length_m=1234.5, wave_speed_ms=1100.0, n_reaches=200, duration_s=60.0)
    dt = time_step_s(1234.5, 200, 1100.0)
    msg = reject(data)
    exact = MAX_STEPS * dt
    shown = math.floor(exact * 1000) / 1000
    text = f"{shown:.3f}".rstrip("0").rstrip(".")
    assert shown != exact
    assert f"{text} s" in msg
    out = solve(case(length_m=1234.5, wave_speed_ms=1100.0, n_reaches=200, duration_s=float(text)))
    assert out["n_steps"] <= MAX_STEPS


def test_hu16_crit13_minimum_duration_over_cap_suggests_coarser_mesh():
    msg = reject(case(n_reaches=200, duration_s=..., closure_time_s=[0.0, 49.0],
                      closure_flow_lps=[100.0, 0.0]))
    assert "duración mínima" in msg
    assert "n_reaches <= 196" in msg
    assert "acorta" not in msg


def test_hu16_crit13_closure_too_slow_for_any_mesh():
    msg = reject(case(n_reaches=10, duration_s=..., closure_time_s=[0.0, 999.0],
                      closure_flow_lps=[100.0, 0.0]))
    assert "demasiado lento" in msg


# --------------------------------------------------------------------------- U-03
def test_u03_friction_number_limit():
    data = case(length_m=50_000.0, inner_diameter_mm=100.0, darcy_friction_factor=0.05,
                initial_flow_lps=23.56, closure_time_s=[0.0, 2.0],
                closure_flow_lps=[23.56, 0.0], duration_s=...)
    msg = reject(data)
    assert "φ" in msg and "supera 0.5" in msg
    n_min = int(re_search(r"n_reaches >= (\d+)", msg))
    assert n_min % 2 == 0
    assert n_min == 76  # phi(N) = 37.5/N with these data -> N >= 75 -> 76 (even)
    out = solve({**data, "n_reaches": n_min})
    assert out["friction_number"] <= 0.5
    reject({**data, "n_reaches": n_min - 2})

    excel = solve(case())
    expected = 0.02 * excel["dx_m"] * excel["velocity_initial_ms"] / (2 * 0.3 * 1000.0)
    assert excel["friction_number"] == pytest.approx(expected, rel=1e-12)


def re_search(pattern: str, text: str) -> str:
    import re

    match = re.search(pattern, text)
    assert match, text
    return match.group(1)


# --------------------------------------------------------------------------- input shape
def test_extra_fields_are_forbidden():
    msg = reject(case(durations_s=20.0))
    assert "durations_s" in msg and "no admitido" in msg


def test_missing_required_field_named():
    msg = reject(case(pn_bar=...))
    assert "pn_bar" in msg and "obligatorio" in msg


def test_horizontal_requires_length_and_elevation():
    msg = reject(case(length_m=...))
    assert "length_m" in msg


def test_non_finite_input_rejected():
    msg = reject(case(reservoir_level_m=float("nan")))
    assert "reservoir_level_m" in msg


def test_non_dict_input_rejected():
    assert "objeto JSON" in reject("not a dict")


def test_everything_raised_is_a_package_error():
    for data in ({}, None, [], case(n_reaches="x")):
        with pytest.raises(MainpipeTransientError):
            solve(data)


# --------------------------------------------------------------------------- HU-1.7 crit. 5
def test_hu17_crit5_worst_case_time_budget():
    """N = 200, 10 000 steps through solve(): median of 5 runs < 0.8 s (V-16, kit 01 §6)."""
    data = case(n_reaches=200, duration_s=50.0)
    solve(data)  # warm-up
    times = []
    for _ in range(5):
        start = time.perf_counter()
        out = solve(data)
        times.append(time.perf_counter() - start)
    assert out["n_steps"] == 10_000
    assert statistics.median(times) < 0.8, times


# --------------------------------------------------------------------------- phase-2 findings
@pytest.mark.parametrize(
    "changes",
    [{"duration_s": 1e306}, {"inner_diameter_mm": 1e-170}, {"wave_speed_ms": 1e-320},
     {"length_m": 1e308}],
    ids=["duracion-1e306", "diametro-1e-170", "celeridad-1e-320", "longitud-1e308"],
)
def test_f201_extreme_magnitudes_never_leak_foreign_exceptions(changes):
    """F2-01: arithmetic failures in the cross rules are a 422, in solve and in the model."""
    from pydantic import ValidationError

    from mainpipe_transient import SolveRequest

    msg = reject(case(**changes))
    assert "fuera del rango numérico" in msg
    with pytest.raises(ValidationError):  # what FastAPI sees before calling the package
        SolveRequest.model_validate(case(**changes))


def test_f201_validator_bug_is_wrapped(monkeypatch):
    """A non-ValueError raised while validating still leaves as a package error."""
    from mainpipe_transient import SolveRequest

    def broken(self):
        raise KeyError("injected")

    monkeypatch.setattr(SolveRequest, "_check_geometry_fields", broken)
    with pytest.raises(MainpipeTransientComputationError) as info:
        solve(case())
    assert isinstance(info.value.__cause__, KeyError)
    assert "injected" not in str(info.value)


def test_u40_fixed_density_and_gravity_enter_pn_head():
    """2.0 replaces F2-02: rho and g are constants (U-40), PN*1e5/(1000*9.81) (V-12)."""
    out = solve(case())
    assert out["pn_head_m"] == pytest.approx(25e5 / (1000.0 * 9.81), rel=1e-12)
    assert "density_kgm3" not in mpt.SolveRequest.model_fields
    assert "gravity_ms2" not in mpt.SolveRequest.model_fields


DENSITY_MSG = (
    "density_kgm3: la densidad ya no es un dato de entrada; el cálculo usa ρ = 1000 kg/m³. "
    "Quite el campo de la petición."
)
GRAVITY_MSG = (
    "gravity_ms2: la gravedad ya no es un dato de entrada; el cálculo usa g = 9.81 m/s². "
    "Quite el campo de la petición."
)


@pytest.mark.parametrize(
    "extra, expected",
    [
        ({"density_kgm3": 1000.0}, [DENSITY_MSG]),
        ({"gravity_ms2": 9.81}, [GRAVITY_MSG]),
        ({"density_kgm3": 1025.0, "gravity_ms2": 9.78}, [DENSITY_MSG, GRAVITY_MSG]),
        ({"density_kgm3": None}, [DENSITY_MSG]),
    ],
    ids=["density", "gravity", "both", "null"],
)
def test_u40_retired_fields_give_their_own_422(extra, expected):
    """HU-1.6 crit. 7 in 2.0: a 1.0 request with rho or g is rejected with its own message."""
    msg = reject({**case(), **extra})
    for text in expected:
        assert text in msg
    assert "revisa el nombre" not in msg  # not the generic extra_forbidden text
    if len(expected) == 1:
        other = GRAVITY_MSG if expected[0] == DENSITY_MSG else DENSITY_MSG
        assert other not in msg


def test_u40_retired_field_message_travels_through_pydantic_in_spanish():
    """FastAPI validates with the same model first: the 422 must carry the Spanish text."""
    with pytest.raises(pydantic.ValidationError) as info:
        mpt.SolveRequest.model_validate({**case(), "gravity_ms2": 9.81})
    [err] = info.value.errors(include_url=False)
    assert err["type"] == "value_error"
    assert GRAVITY_MSG in err["msg"]


def test_unknown_field_keeps_the_generic_extra_forbidden_422():
    msg = reject({**case(), "densidad": 1000.0})
    assert "densidad: campo no admitido (revisa el nombre)." in msg


def test_f203_displayed_maximum_below_minimum_suggests_coarser_mesh():
    """If Tc + 2L/a lies between the truncated and the exact T_max, do not propose shortening."""
    data = case(length_m=1234.5, wave_speed_ms=1100.0, n_reaches=200, duration_s=60.0,
                closure_time_s=[0.0, 53.8688], closure_flow_lps=[100.0, 0.0])
    msg = reject(data)
    assert "acorta" not in msg
    assert "56.114 s" in msg
    n_fit = int(re_search(r"n_reaches <= (\d+)", msg))
    out = solve({**data, "n_reaches": n_fit, "duration_s": 56.114})
    assert out["n_steps"] <= MAX_STEPS


def test_f204_literal_message_is_spanish():
    msg = reject(case(geometry="vertical"))
    assert " or " not in msg
    assert "'horizontal' o 'profile'" in msg


def test_f204_list_positions_are_one_based():
    msg = reject(case(closure_time_s=[0.0, "a", 2.0], closure_flow_lps=[100.0, 50.0, 0.0]))
    assert "closure_time_s (punto 2)" in msg


def test_f204_huge_magnitudes_stay_readable():
    msg = reject(case(duration_s=1e200))
    assert "1e+200 s" in msg and "2e+201 pasos" in msg


def test_f204_many_errors_fit_the_portal_limit():
    msg = reject(case(wave_speed_ms=2000.0, darcy_friction_factor=1.0, pn_bar=-1.0,
                      min_allowed_pressure_head_m=5.0, initial_flow_lps=-1.0,
                      inner_diameter_mm=-1.0, n_reaches=3, length_m=-1.0))
    assert len(msg) <= 400
    assert "errores más)" in msg


def test_f206_non_finite_friction_number_uses_range_message():
    msg = reject(case(wave_speed_ms=1e-320, duration_s=...))
    assert "inf" not in msg
    assert "fuera del rango numérico" in msg
