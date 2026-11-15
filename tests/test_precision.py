"""Phase 5 (2.0): precision of the serialisation (plan 01 §1.4, §6 V-19; U-39, U-41, D-63 (1)-(2), (6)).

Covers HU-4.2 crit. 3-4, HU-1.3 crit. 1 and the "same value" identities of U-39 (7). Exact,
without tolerance: every m / m.c.a. / L/s list equals its own 3-decimal rounding and carries no
``-0.0``; ``time_s``, ``frame_time_s`` and the scalars are the full-precision values. The values
the golden cases will freeze are these rounded ones (D-63 (6)): ``solve()`` is what
``tools/make_examples.py`` dumps.
"""

from __future__ import annotations

import math

import numpy as np
import pytest

from mainpipe_transient import solve
from rounding import HALF_MM, is_rounded, r3, r3_list
from test_contract import case
from test_frames import internal_frames, worst_case_with_frames
from test_profile import GENERIC_X, GENERIC_Z, horizontal, profile

ROUNDED_SERIES = ("head_valve_m", "head_midpoint_m", "pressure_head_valve_m",
                  "pressure_head_midpoint_m", "flow_reservoir_lps", "flow_valve_lps")
ROUNDED_STATIONS = ("x_m", "elevation_m", "head_initial_m", "pressure_head_initial_m",
                    "head_max_m", "head_min_m", "pressure_head_max_m", "pressure_head_min_m")
ROUNDED_FRAMES = ("frame_x_m", "frame_head_m")
ROUNDED_LISTS = ROUNDED_SERIES + ROUNDED_STATIONS + ROUNDED_FRAMES
FULL_LISTS = ("time_s", "frame_time_s")
SCALARS = ("length_m", "area_m2", "velocity_initial_ms", "head_loss_m", "dx_m", "dt_s",
           "duration_s", "reflection_time_s", "wave_period_s", "closure_duration_s",
           "friction_number", "head_valve_max_m", "head_valve_max_time_s", "head_valve_min_m",
           "head_valve_min_time_s", "pressure_head_max_global_m", "pressure_head_max_global_x_m",
           "pressure_head_max_global_time_s", "pressure_head_min_global_m",
           "pressure_head_min_global_x_m", "pressure_head_min_global_time_s", "pn_head_m",
           "pressure_max_pn_ratio_pct", "min_allowed_pressure_head_m", "joukowsky_head_rise_m",
           "theoretical_head_rise_m", "moc_head_rise_valve_m", "theory_deviation_pct")


def small_dt_case() -> dict:
    """HU-4.2 crit. 4: Excel case with L = 100 m, a = 1500 m/s, N = 200 (dt = 1/3000 s),
    default duration Tc + 5*(4L/a) = 1.5 + 1.333... s -> 8 500 steps."""
    return case(length_m=100.0, wave_speed_ms=1500.0, n_reaches=200, duration_s=None)


V19_CASES = [
    ("excel", case()),
    ("u34-recipe", worst_case_with_frames()),
    ("hu42-crit4", small_dt_case()),
]


@pytest.fixture(scope="module", params=V19_CASES, ids=[n for n, _ in V19_CASES])
def v19(request) -> tuple[dict, dict]:
    _, data = request.param
    return data, solve(data)


# --------------------------------------------------------------------------- HU-4.2 crit. 3
def test_v19_every_rounded_list_equals_its_own_rounding(v19):
    _, out = v19
    for key in ROUNDED_LISTS:
        assert out[key] is not None, key
        assert is_rounded(out[key]), key  # also: no -0.0 anywhere


def test_v19_times_and_scalars_are_full_precision(v19):
    data, out = v19
    res = internal_frames(data)
    mesh = res.mesh
    # time_s and frame_time_s: the internal instants, not rounded
    assert out["time_s"] == res.time_s.tolist()
    assert res.frame_steps is not None
    assert out["frame_time_s"] == res.time_s[res.frame_steps].tolist()
    # scalars: the formulas / MocResult values, untouched
    assert out["dt_s"] == mesh.dt_s == mesh.length_m / (mesh.n_reaches * data["wave_speed_ms"])
    assert out["dx_m"] == mesh.dx_m
    assert (out["head_valve_max_m"], out["head_valve_max_time_s"]) == res.head_valve_max()
    assert (out["head_valve_min_m"], out["head_valve_min_time_s"]) == res.head_valve_min()
    p_max, p_min = res.pressure_head_max_global(), res.pressure_head_min_global()
    assert out["pressure_head_max_global_m"] == p_max.value_m
    assert out["pressure_head_max_global_x_m"] == p_max.x_m
    assert out["pressure_head_min_global_m"] == p_min.value_m
    assert out["pressure_head_min_global_x_m"] == p_min.x_m
    assert out["pn_head_m"] == data["pn_bar"] * 1e5 / (1000.0 * 9.81)
    for key in SCALARS:
        assert isinstance(out[key], float), key
    # the rounded lists are the internal arrays rounded once (U-39 (5))
    assert out["x_m"] == r3_list(mesh.station_x_m)
    assert out["head_valve_m"] == r3_list(res.head_valve_m)
    assert out["pressure_head_valve_m"] == r3_list(res.pressure_head_valve_m)
    assert out["flow_valve_lps"] == r3_list(1000.0 * res.flow_valve_m3s)
    assert out["pressure_head_min_m"] == r3_list(res.pressure_head_min_m)


def test_v19_some_scalar_is_not_on_the_millimetre_grid():
    """Guard against rounding the scalars by mistake (U-39 (2))."""
    out = solve(case())
    assert any(out[k] != round(out[k], 3) for k in SCALARS)
    assert out["dt_s"] == 0.05 and out["time_s"][1] == 0.05


# --------------------------------------------------------------------------- HU-4.2 crit. 4
def test_hu42_crit4_instants_are_not_rounded():
    out = solve(small_dt_case())
    assert out["n_steps"] == 8500
    assert out["dt_s"] == pytest.approx(1.0 / 3000.0, abs=1e-15)
    t = np.array(out["time_s"])
    np.testing.assert_allclose(np.diff(t), out["dt_s"], rtol=0, atol=1e-9)
    assert np.all(np.diff(t) > 0) and len(set(out["time_s"])) == len(t)
    frames = out["frame_time_s"]
    assert np.all(np.diff(frames) > 0) and len(set(frames)) == len(frames)
    in_time = set(out["time_s"])
    assert all(f in in_time for f in frames)
    # with 1 mm rounding these instants would collapse: 1/3000 s is not a multiple of 1 ms
    assert len(set(r3_list(t))) < len(t)


# --------------------------------------------------------------------------- U-39 (7)
def test_hu13_crit1_first_valve_head_equals_last_initial_head():
    for data in (case(), profile(GENERIC_X, GENERIC_Z), small_dt_case()):
        out = solve(data)
        assert out["head_valve_m"][0] == out["head_initial_m"][-1]


def test_hu11_crit4_datum_invariance_through_solve():
    """V-09 through solve(): z = 50, H_dep = 150 -> H + 50 and same pressures (0.001 m)."""
    base = solve(horizontal())
    shifted = solve(horizontal(pipe_elevation_m=50.0, reservoir_level_m=150.0))
    tol = 0.001 + 1e-9
    for key in ("head_valve_m", "head_midpoint_m", "head_initial_m", "head_max_m", "head_min_m"):
        np.testing.assert_allclose(shifted[key], np.array(base[key]) + 50.0, rtol=0, atol=tol)
    for key in ("pressure_head_valve_m", "pressure_head_midpoint_m", "pressure_head_initial_m",
                "pressure_head_max_m", "pressure_head_min_m"):
        np.testing.assert_allclose(shifted[key], base[key], rtol=0, atol=tol)
    for key in ("flow_valve_lps", "flow_reservoir_lps"):
        np.testing.assert_allclose(shifted[key], base[key], rtol=0, atol=tol)
    # scalars at full precision: ± 1e-6 m (V-09)
    assert shifted["pressure_head_min_global_m"] == pytest.approx(
        base["pressure_head_min_global_m"], abs=1e-6
    )


def test_d63_list_versus_scalar_comparison_rule():
    """D-63 (5): a list equals a scalar only after rounding the scalar (HU-1.5 crit. 2)."""
    out = solve(case())
    assert out["head_max_m"][-1] == r3(out["head_valve_max_m"])
    assert abs(out["head_max_m"][-1] - out["head_valve_max_m"]) <= HALF_MM + 1e-9
    assert out["head_max_m"][-1] != out["head_valve_max_m"]  # not equal unrounded


def test_u41_scalar_chainage_is_located_in_x_after_rounding():
    """U-41 (2): a chainage scalar is in x_m once rounded to 3 decimals."""
    x = [0.0, 137.12345, 300.0, 520.98765, 733.3, 1000.0]
    out = solve(profile(x, [0.0, -12.5, 8.0, 31.0, 4.2, -20.0]))
    assert 137.123 in out["x_m"] and 520.988 in out["x_m"]
    for c in out["checks"]:
        assert r3(c["x_m"]) in out["x_m"]
    for key in ("pressure_head_max_global_x_m", "pressure_head_min_global_x_m"):
        assert r3(out[key]) in out["x_m"]


def test_u41_two_chainages_closer_than_a_millimetre_may_show_the_same_value():
    """U-41 (1): a vertex 0.3 mm from a node is kept (> 1e-9*L) and both show the same x."""
    out = solve(profile([0.0, 500.0003, 1000.0], [0.0, 20.0, 0.0]))
    xs = out["x_m"]
    assert xs.count(500.0) == 2
    assert all(b >= a for a, b in zip(xs, xs[1:]))  # non-decreasing
    j = [i for i, v in enumerate(xs) if v == 500.0]
    assert [out["x_is_node"][i] for i in j] == [True, False]


def test_rounding_helper_follows_u39_4():
    """The single private rounding: Python round(x, 3), no -0.0, huge magnitudes untouched."""
    from mainpipe_transient._solve import _rounded

    values = np.array([-0.0004, -0.0, 0.0004, 2.675, -2.6755, 1e15 + 0.123, 1e300, -1.7e308])
    out = _rounded(values)
    assert out == [round(v, 3) + 0.0 for v in values.tolist()]
    assert all(math.copysign(1.0, v) == 1.0 for v in out[:3])  # 0.0, never -0.0
    assert out[-2:] == [1e300, -1.7e308] and all(math.isfinite(v) for v in out)
    with np.errstate(over="ignore", invalid="ignore"):
        assert not np.isfinite(np.round(np.array([-1.7e308]), 3)[0])  # why not numpy.round
