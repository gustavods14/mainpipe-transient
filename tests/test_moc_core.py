"""Phase 1: MOC core on a horizontal pipe (plan 01 §5 fase 1; V-01..V-09, V-14, V-15).

Tolerances and sources come from plan 01 §6. Reference values against the Excel are
read from ``tests/reference/excel_case.json`` (U-28), not from the rounded literals
printed in the plan (F0-02).
"""

from __future__ import annotations

import math

import numpy as np
import pytest

from mainpipe_transient._closure import build_closure_law
from mainpipe_transient._geometry import count_steps
from moc_cases import EXCEL, FRICTIONLESS, Recorder, run

H_TOL = 1e-6  # m (U-29)
Q_TOL_LPS = 1e-6  # L/s (U-29)


def _mask(t: np.ndarray, lo: float, hi: float) -> np.ndarray:
    """Open interval lo < t < hi, robust to k*dt rounding."""
    eps = 1e-9
    return (t > lo + eps) & (t < hi - eps)


# --------------------------------------------------------------------------- V-01
def test_v01_steady_state_darcy_weisbach(excel_reference):
    res = run(EXCEL)
    der = res.derived
    d, a, f, g, q0, L = 0.3, 1000.0, 0.02, 9.81, 0.1, 1000.0
    area = math.pi * d**2 / 4
    v0 = q0 / area
    hf = f * L / d * v0**2 / (2 * g)

    assert der.velocity_initial_ms == pytest.approx(1.415, abs=0.001)
    assert der.head_loss_m == pytest.approx(6.80, abs=0.01)
    assert der.area_m2 == pytest.approx(area, rel=1e-12)
    assert der.velocity_initial_ms == pytest.approx(v0, rel=1e-12)
    assert der.head_loss_m == pytest.approx(hf, rel=1e-12)

    x = res.mesh.x_m
    assert res.head_initial_m[x == 500.0][0] == pytest.approx(96.60, abs=0.01)
    np.testing.assert_allclose(res.head_initial_m, 100.0 - hf * x / L, rtol=1e-12)

    # Same derived quantities as sheet 1_Datos.
    ref = excel_reference["derived"]
    assert res.mesh.dx_m == ref["dx_m"]
    assert res.mesh.dt_s == ref["dt_s"]
    assert res.duration_s == ref["duration_s"]
    assert der.area_m2 == pytest.approx(ref["area_m2"], rel=1e-12)
    assert der.velocity_initial_ms == pytest.approx(ref["velocity_initial_ms"], rel=1e-12)
    assert der.wave_constant == pytest.approx(ref["wave_constant_s_m2"], rel=1e-12)
    assert der.friction_constant == pytest.approx(ref["friction_constant_s2_m5"], rel=1e-12)
    assert der.head_loss_m == pytest.approx(ref["head_loss_m"], rel=1e-12)
    assert der.reflection_time_s == ref["reflection_time_s"]
    assert der.wave_period_s == ref["wave_period_s"]


# --------------------------------------------------------------------------- V-02
def test_v02_joukowsky_without_friction():
    res = run(FRICTIONLESS)
    t = res.time_s
    np.testing.assert_allclose(res.head_valve_m[_mask(t, 0.05, 2.0)], 244.21, atol=0.01)
    np.testing.assert_allclose(res.head_valve_m[_mask(t, 2.05, 4.0)], -44.21, atol=0.01)
    np.testing.assert_allclose(
        1000.0 * res.flow_reservoir_m3s[_mask(t, 1.05, 3.0)], -100.0, atol=0.1
    )


# --------------------------------------------------------------------------- V-03
def _allievi_valve_head(case, n_steps: int) -> np.ndarray:
    """M19, f = 0: H(t) + H(t - 2L/a) - 2 H_dep = B [Q(t - 2L/a) - Q(t)], H = H_dep, Q = Q0 for t <= 0."""
    q0 = case.initial_flow_lps / 1000.0
    area = math.pi * (case.inner_diameter_mm / 1000.0) ** 2 / 4
    b = case.wave_speed_ms / (case.gravity_ms2 * area)
    # Closure law evaluated independently of the package (np.interp, constant after the end).
    law_t = np.array(case.closure_time_s)
    law_q = np.array(case.closure_flow_lps) / 1000.0
    dt = case.length_m / case.n_reaches / case.wave_speed_ms
    lag = 2 * case.n_reaches  # 2L/a in steps
    h_dep = case.reservoir_level_m
    q = [q0] + [float(np.interp(k * dt, law_t, law_q)) for k in range(1, n_steps + 1)]
    h = [h_dep]
    for k in range(1, n_steps + 1):
        if k - lag <= 0:
            h_lag, q_lag = h_dep, q0
        else:
            h_lag, q_lag = h[k - lag], q[k - lag]
        h.append(2 * h_dep - h_lag + b * (q_lag - q[k]))
    return np.array(h)


@pytest.mark.parametrize(
    "law_t, law_q",
    [
        (EXCEL.closure_time_s, EXCEL.closure_flow_lps),
        ([0.0, 3.0], [100.0, 0.0]),
    ],
    ids=["ley-excel", "ley-lineal-3s"],
)
def test_v03_allievi_without_friction(law_t, law_q):
    case = EXCEL.with_(darcy_friction_factor=0.0, closure_time_s=law_t, closure_flow_lps=law_q)
    res = run(case)
    expected = _allievi_valve_head(case, res.n_steps)
    np.testing.assert_allclose(res.head_valve_m, expected, rtol=0, atol=H_TOL)


# --------------------------------------------------------------------------- V-04
@pytest.mark.parametrize("n_reaches", [20, 40])
def test_v04_mesh_independence_without_friction(n_reaches):
    res = run(FRICTIONLESS.with_(n_reaches=n_reaches))
    h_max, _ = res.head_valve_max()
    assert h_max == pytest.approx(244.21, abs=0.01)


# --------------------------------------------------------------------------- V-05
def test_v05_excel_step_by_step(excel_reference):
    rec = Recorder()
    res = run(EXCEL, rec)
    grid = excel_reference["grid"]
    ref_h = np.array(grid["head_m"])
    ref_q_lps = 1000.0 * np.array(grid["flow_m3s"])

    assert res.n_steps == 400
    np.testing.assert_array_equal(res.mesh.x_m, grid["x_m"])
    np.testing.assert_allclose(res.time_s, grid["time_s"], rtol=0, atol=1e-12)
    np.testing.assert_allclose(rec.head_m, ref_h, rtol=0, atol=H_TOL)
    np.testing.assert_allclose(rec.flow_lps, ref_q_lps, rtol=0, atol=Q_TOL_LPS)
    np.testing.assert_allclose(
        1000.0 * res.flow_valve_m3s, 1000.0 * np.array(grid["valve_law_flow_m3s"]),
        rtol=0, atol=Q_TOL_LPS,
    )


def test_v05_excel_extremes(excel_reference):
    res = run(EXCEL)
    val = {c: e["value"] for c, e in excel_reference["validation"].items()}

    assert res.head_valve_m[0] == pytest.approx(val["C13"], abs=H_TOL)
    h_max, t_max = res.head_valve_max()
    h_min, t_min = res.head_valve_min()
    assert h_max == pytest.approx(val["C18"], abs=H_TOL)
    assert t_max == val["C19"] == 2.0
    assert h_min == pytest.approx(val["C20"], abs=H_TOL)
    assert t_min == val["C21"] == 4.0

    # Pipe-wide extremes are the valve's.
    assert res.head_max_m.max() == pytest.approx(val["C23"], abs=H_TOL)
    assert res.head_min_m.min() == pytest.approx(val["C24"], abs=H_TOL)
    assert res.head_max_m.max() == h_max
    assert res.head_min_m.min() == h_min


# --------------------------------------------------------------------------- V-06
def test_v06_wave_front_position():
    rec = Recorder()
    run(FRICTIONLESS, rec)
    k = 11  # t = 0.55 s
    head = rec.head_m[k]
    x = np.arange(21) * 50.0
    np.testing.assert_allclose(head[x < 500.0], 100.0, atol=0.01)
    np.testing.assert_allclose(head[x > 500.0], 244.21, atol=0.01)


# --------------------------------------------------------------------------- V-07
def test_v07_causality_reservoir_flow_before_l_over_a():
    res = run(EXCEL)
    before = res.time_s < 1.0 - 1e-9
    np.testing.assert_allclose(
        1000.0 * res.flow_reservoir_m3s[before], 100.0, rtol=0, atol=Q_TOL_LPS
    )


# --------------------------------------------------------------------------- V-08
def _flow_valve_lps_at(res, t: float) -> float:
    k = int(round(t / res.mesh.dt_s))
    assert res.time_s[k] == pytest.approx(t, abs=1e-12)
    return 1000.0 * float(res.flow_valve_m3s[k])


def test_v08_closure_law_excel():
    res = run(EXCEL)
    assert _flow_valve_lps_at(res, 0.25) == pytest.approx(75.0, abs=0.01)
    assert _flow_valve_lps_at(res, 0.75) == pytest.approx(35.0, abs=0.01)
    law = build_closure_law(EXCEL.closure_time_s, [q / 1000 for q in EXCEL.closure_flow_lps], 0.1)
    assert law.closure_duration_s == 1.5


def test_v08_closure_law_constant_after_last_point():
    case = EXCEL.with_(closure_time_s=[0.0, 0.5, 1.0, 1.5], closure_flow_lps=[100.0, 50.0, 20.0, 0.0])
    res = run(case)
    after = res.time_s >= 1.5 - 1e-9
    assert res.time_s[-1] > 1.5
    assert np.all(res.flow_valve_m3s[after] == 0.0)


def test_v08_closure_law_linear_3s():
    case = EXCEL.with_(closure_time_s=[0.0, 3.0], closure_flow_lps=[100.0, 0.0])
    res = run(case)
    assert _flow_valve_lps_at(res, 1.5) == pytest.approx(50.0, abs=0.01)
    law = build_closure_law([0.0, 3.0], [0.1, 0.0], 0.1)
    assert law.closure_duration_s == 3.0


def test_closure_first_point_replaced_by_initial_flow():
    """U-18: the first law point is Q0 after validation (here off by 0.05 %)."""
    law = build_closure_law([0.0, 1.0], [0.10005, 0.0], 0.1)
    assert law.flow_m3s[0] == 0.1
    assert law.flow_at(0.0) == 0.1


# --------------------------------------------------------------------------- V-09
def test_v09_datum_invariance():
    rec0, rec1 = Recorder(), Recorder()
    base = run(EXCEL, rec0)
    shifted = run(EXCEL.with_(pipe_elevation_m=50.0, reservoir_level_m=150.0), rec1)
    np.testing.assert_allclose(rec1.head_m, rec0.head_m + 50.0, rtol=0, atol=H_TOL)
    np.testing.assert_allclose(rec1.flow_lps, rec0.flow_lps, rtol=0, atol=Q_TOL_LPS)
    for name in ("pressure_head_valve_m", "pressure_head_midpoint_m",
                 "pressure_head_initial_m", "pressure_head_max_m", "pressure_head_min_m"):
        np.testing.assert_allclose(
            getattr(shifted, name), getattr(base, name), rtol=0, atol=H_TOL, err_msg=name
        )


# --------------------------------------------------------------------------- V-14
def test_v14_friction_damps_each_period():
    res = run(EXCEL)
    tc, period = 1.5, res.derived.wave_period_s
    dev = np.abs(res.head_valve_m - EXCEL.reservoir_level_m)
    peaks = []
    start = tc
    while start + period <= res.duration_s + 1e-9:
        window = (res.time_s >= start - 1e-9) & (res.time_s < start + period - 1e-9)
        peaks.append(dev[window].max())
        start += period
    assert len(peaks) >= 4
    assert all(later <= earlier for earlier, later in zip(peaks, peaks[1:])), peaks


# --------------------------------------------------------------------------- V-15
def test_v15_steady_state_is_a_fixed_point():
    rec = Recorder()
    case = EXCEL.with_(closure_time_s=[0.0, 5.0, 6.0], closure_flow_lps=[100.0, 100.0, 0.0],
                       duration_s=None)
    res = run(case, rec)
    before = res.time_s < 5.0 - 1e-9
    h0, q0 = rec.head_m[0], rec.flow_lps[0]
    np.testing.assert_allclose(rec.head_m[before], np.broadcast_to(h0, rec.head_m[before].shape),
                               rtol=0, atol=1e-9)
    np.testing.assert_allclose(rec.flow_lps[before] / 1000.0,
                               np.broadcast_to(q0 / 1000.0, rec.flow_lps[before].shape),
                               rtol=0, atol=1e-9)


# ------------------------------------------------------------- stories (HU-1.1 .. 1.5)
def test_hu11_crit1_excel_case_acceptance():
    res = run(EXCEL)
    assert res.mesh.dx_m == 50.0
    assert res.mesh.dt_s == 0.05
    assert res.n_steps == 400
    assert res.duration_s == 20.0
    assert res.derived.reflection_time_s == 2.0
    assert res.derived.wave_period_s == 4.0
    assert res.head_valve_max()[0] == pytest.approx(242.8, abs=0.1)
    assert res.head_valve_min()[0] == pytest.approx(-37.9, abs=0.1)


def test_hu13_initial_regime():
    res = run(EXCEL)
    x = res.mesh.x_m
    assert res.head_initial_m[0] == 100.0
    assert res.head_initial_m[x == 1000.0][0] == pytest.approx(93.20, abs=0.01)
    assert res.head_valve_m[0] == res.head_initial_m[-1]
    assert 1000.0 * res.flow_reservoir_m3s[0] == pytest.approx(100.0, abs=1e-12)
    assert 1000.0 * res.flow_valve_m3s[0] == pytest.approx(100.0, abs=1e-12)


@pytest.mark.parametrize("case", [EXCEL, FRICTIONLESS, EXCEL.with_(duration_s=None)],
                         ids=["excel", "sin-friccion", "duracion-por-defecto"])
def test_hu14_series_shape(case):
    res = run(case)
    n = res.n_steps + 1
    for arr in (res.time_s, res.head_valve_m, res.head_midpoint_m,
                res.flow_reservoir_m3s, res.flow_valve_m3s):
        assert arr.shape == (n,)
    assert res.time_s[0] == 0.0
    assert res.time_s[-1] == res.duration_s
    np.testing.assert_allclose(np.diff(res.time_s), res.mesh.dt_s, rtol=1e-12)


def test_hu14_midpoint_and_valve_pressure():
    rec = Recorder()
    res = run(EXCEL.with_(pipe_elevation_m=50.0, reservoir_level_m=150.0), rec)
    assert res.mesh.x_m[res.mesh.midpoint_index] == 500.0
    np.testing.assert_array_equal(res.head_midpoint_m, rec.head_m[:, 10])
    np.testing.assert_array_equal(res.pressure_head_valve_m, res.head_valve_m - 50.0)


@pytest.mark.parametrize("n_reaches, dx, dt", [(20, 50.0, 0.05), (40, 25.0, 0.025)])
def test_hu17_crit1_crit2_mesh(n_reaches, dx, dt):
    """HU-1.7 crit. 1-2: dx = L/N, dt = dx/a, N + 1 stations ending at L exactly, L/2 is node N/2."""
    rec = Recorder()
    res = run(EXCEL.with_(n_reaches=n_reaches), rec)
    assert res.mesh.n_reaches == n_reaches
    assert res.mesh.dx_m == dx
    assert res.mesh.dt_s == dt
    assert res.mesh.x_m.shape == (n_reaches + 1,)
    np.testing.assert_allclose(res.mesh.x_m, dx * np.arange(n_reaches + 1), rtol=0, atol=1e-12)
    assert res.mesh.x_m[-1] == 1000.0
    assert res.mesh.midpoint_index == n_reaches // 2
    assert res.mesh.x_m[res.mesh.midpoint_index] == 500.0
    np.testing.assert_array_equal(res.head_midpoint_m, rec.head_m[:, n_reaches // 2])


def test_hu17_crit4_effective_duration():
    """HU-1.7 crit. 4: 20 s -> 400 steps (not 401); 20.01 s -> 401 steps and 20.05 s effective."""
    res = run(EXCEL.with_(duration_s=20.0))
    assert res.n_steps == 400
    assert res.duration_s == 20.0
    res = run(EXCEL.with_(duration_s=20.01))
    assert res.n_steps == 401
    assert res.duration_s == pytest.approx(20.05, abs=1e-12)
    assert res.time_s[-1] == res.duration_s


def test_default_duration_and_step_count():
    """Tc + 5*(4L/a) with U-08 rounding: Excel law -> 1.5 + 20 = 21.5 s -> 430 steps."""
    res = run(EXCEL.with_(duration_s=None))
    assert res.n_steps == 430
    assert res.duration_s == pytest.approx(21.5, abs=1e-12)
    assert count_steps(20.0, 0.05) == 400  # exact in binary; noise case: test_contract


@pytest.mark.parametrize("case", [EXCEL, FRICTIONLESS, EXCEL.with_(pipe_elevation_m=50.0,
                                                                   reservoir_level_m=150.0)],
                         ids=["excel", "sin-friccion", "cota-50"])
def test_hu15_envelopes(case):
    rec = Recorder()
    res = run(case, rec)
    h = rec.head_m
    assert np.all(res.head_max_m >= res.head_initial_m)
    assert np.all(res.head_initial_m >= res.head_min_m)
    assert np.all(res.pressure_head_max_m >= res.pressure_head_min_m)
    # Envelopes over every step, exactly.
    np.testing.assert_array_equal(res.head_max_m, h.max(axis=0))
    np.testing.assert_array_equal(res.head_min_m, h.min(axis=0))
    np.testing.assert_array_equal(res.head_max_step, h.argmax(axis=0))
    np.testing.assert_array_equal(res.head_min_step, h.argmin(axis=0))
    # Horizontal: elevation constant and pressure = head - z.
    np.testing.assert_array_equal(res.mesh.elevation_m, case.pipe_elevation_m)
    np.testing.assert_array_equal(res.pressure_head_max_m, res.head_max_m - case.pipe_elevation_m)
    np.testing.assert_array_equal(res.pressure_head_min_m, res.head_min_m - case.pipe_elevation_m)


def test_hu15_crit2_excel_envelope_extremes(excel_reference):
    res = run(EXCEL)
    val = {c: e["value"] for c, e in excel_reference["validation"].items()}
    assert res.head_max_m[-1] == res.head_valve_max()[0]
    assert res.head_min_m[-1] == res.head_valve_min()[0]

    p_max = res.pressure_head_max_global()
    p_min = res.pressure_head_min_global()
    assert p_max.value_m == pytest.approx(val["C23"] - 0.0, abs=0.1)
    assert p_max.time_s == pytest.approx(val["C19"], abs=res.mesh.dt_s)
    assert p_min.value_m == pytest.approx(val["C34"], abs=0.1)
    assert p_min.time_s == pytest.approx(val["C21"], abs=res.mesh.dt_s)
    # Bar figure of 4_Validacion C33 from the same maximum.
    assert p_max.value_m * 1000.0 * 9.81 / 1e5 == pytest.approx(val["C33"], abs=1e-6)


def test_u25_global_extreme_tie_break():
    """Steady frictionless case with no closure until late: all stations tie at t = 0.

    Tie-break U-25: first instant, then lower x -> x = 0, t = 0.
    """
    case = FRICTIONLESS.with_(closure_time_s=[0.0, 4.0, 4.05], closure_flow_lps=[100.0, 100.0, 0.0],
                              duration_s=4.0)
    res = run(case)
    p_min = res.pressure_head_min_global()
    assert p_min.value_m == 100.0
    assert p_min.time_s == 0.0
    assert p_min.x_m == 0.0
