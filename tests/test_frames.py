"""Phase 5 (2.0): player series (plan 01 §1.4, §5 phase 5; U-10, U-11, U-24, U-33, U-42; V-16, V-17).

Covers HU-4.1 crit. 1-4 and HU-4.2 crit. 1-2 as amended on 2026-11-15: the only frame matrix is
``frame_head_m`` (no ``frame_pressure_head_m``, D-64), at 3 decimals (U-39), and the pressure
head of a frame is derived as ``frame_head_m[k][j] - elevation_m[j]``. The series invariants of
D-64 (3) (plan 01 §1.4, U-42) are checked on the Excel case, a generic profile and the
subsampled U-34 recipe:

1. ``frame_x_m == x_m``;
2. ``|(frame_head_m[k][j] - elevation_m[j]) - r(H - z)(x_j, t_{i_k})| <= 0.001 m + 1e-9 m``,
   with H and z at full precision from the internal ``MocResult``;
3. ``time_s[i_k] == frame_time_s[k]`` with i_k = k*frame_stride except the last frame
   (i = n_steps), and the derived pressure at x = L and L/2 within the same bound of
   ``pressure_head_valve_m[i_k]`` / ``pressure_head_midpoint_m[i_k]`` for every k.

The payload measurements of V-18 live in ``tools/measure_payload.py`` (tested at the end).
"""

from __future__ import annotations

import json
import statistics
import time

import numpy as np
import pytest

from mainpipe_transient import SolveResponse, solve
from mainpipe_transient._closure import build_closure_law
from mainpipe_transient._frames import FRAME_CELL_BUDGET, MAX_FRAMES, max_frames, plan_frames
from mainpipe_transient._geometry import (
    MAX_STEPS,
    build_horizontal_mesh,
    build_profile_mesh,
    count_steps,
    default_duration_s,
)
from mainpipe_transient._moc import MocResult, PipeData, simulate
from rounding import DIFF_TOL, r3, r3_list
from test_contract import case
from test_profile import GENERIC_X, GENERIC_Z, LOMA_X, LOMA_Z, profile, worst_case_profile

FRAME_KEYS = ("frame_stride", "frame_time_s", "frame_x_m", "frame_head_m")


def worst_case_with_frames() -> dict:
    return {**worst_case_profile(), "include_frames": True}


@pytest.fixture(scope="module")
def excel_out() -> dict:
    return solve(case())  # include_frames defaults to true (U-24)


@pytest.fixture(scope="module")
def worst_out() -> dict:
    return solve(worst_case_with_frames())


def internal_frames(data: dict) -> MocResult:
    """The same run through the internal API: full-precision frames and mesh (no rounding)."""
    if data.get("geometry", "horizontal") == "profile":
        mesh = build_profile_mesh(
            data["profile_x_m"], data["profile_z_m"], data["n_reaches"], data["wave_speed_ms"]
        )
    else:
        mesh = build_horizontal_mesh(
            data["length_m"], data["n_reaches"], data["wave_speed_ms"], data["pipe_elevation_m"]
        )
    q0 = data["initial_flow_lps"] / 1000.0
    law = build_closure_law(
        data["closure_time_s"], [q / 1000.0 for q in data["closure_flow_lps"]], q0
    )
    duration = data.get("duration_s")
    if duration is None:
        duration = default_duration_s(law.closure_duration_s, mesh.length_m, data["wave_speed_ms"])
    n_steps = count_steps(duration, mesh.dt_s)
    pipe = PipeData(
        diameter_m=data["inner_diameter_mm"] / 1000.0,
        wave_speed_ms=data["wave_speed_ms"],
        friction_factor=data["darcy_friction_factor"],
        initial_flow_m3s=q0,
        reservoir_level_m=data["reservoir_level_m"],
        gravity_ms2=9.81,  # U-40
    )
    plan = plan_frames(n_steps, mesh.station_x_m.size)
    return simulate(pipe, mesh, law, n_steps, frame_steps=plan.steps)


def frame_steps(out: dict) -> list[int]:
    """i_k of D-64 (3): k*frame_stride, except the last frame, which is always n_steps."""
    n = len(out["frame_time_s"])
    return [k * out["frame_stride"] for k in range(n - 1)] + [out["n_steps"]]


def derived_pressure(out: dict) -> np.ndarray:
    """What the screen does (D-64 (2)): frame_head_m[k][j] - elevation_m[j]."""
    return np.array(out["frame_head_m"]) - np.array(out["elevation_m"])


def midpoint_index(out: dict) -> int:
    x = np.array(out["x_m"])
    return int(np.flatnonzero((x == r3(out["length_m"] / 2)) & np.array(out["x_is_node"]))[0])


def within(actual, expected, tol: float = DIFF_TOL) -> None:
    np.testing.assert_allclose(actual, expected, rtol=0.0, atol=tol)


# --------------------------------------------------------------------------- U-10 frame plan
def test_frame_cap_formula():
    """D-65 (1)-(2): the 1.0 formula, now 50 000 cells in the single matrix."""
    assert FRAME_CELL_BUDGET == 50_000 and MAX_FRAMES == 1001
    assert max_frames(21) == 1001  # min(1001, 2380)
    assert max_frames(50) == 1000
    assert max_frames(699) == 71  # floor(50 000 / 699)


def test_worst_case_plan_matches_the_contract_example():
    """Plan 01 §1.4: 699 stations, 10 000 steps -> cap 71, stride 145, 70 frames."""
    plan = plan_frames(MAX_STEPS, 699)
    assert plan.stride == 145
    assert plan.n_frames == 70
    assert plan.steps.tolist() == list(range(0, 9861, 145)) + [10_000]


def test_no_subsampling_when_every_step_fits():
    cap = max_frames(21)
    plan = plan_frames(cap - 1, 21)  # n_steps + 1 == cap
    assert plan.stride == 1
    assert plan.steps.tolist() == list(range(cap))
    plan = plan_frames(cap, 21)  # one step more: subsampled
    assert plan.stride == 2
    assert plan.n_frames <= cap - 1


@pytest.mark.parametrize("n_stations", [21, 50, 101, 201, 202, 333, 500, 698, 699])
@pytest.mark.parametrize("n_steps", [1, 2, 70, 71, 400, 999, 1000, 1001, 4321, 9999, MAX_STEPS])
def test_frame_plan_properties(n_steps, n_stations):
    cap = max_frames(n_stations)
    plan = plan_frames(n_steps, n_stations)
    steps = plan.steps
    assert plan.n_frames <= cap
    assert plan.n_frames * n_stations <= FRAME_CELL_BUDGET  # one matrix since 2.0
    assert steps[0] == 0 and steps[-1] == n_steps
    assert np.all(np.diff(steps) > 0)
    assert np.all(steps[:-1] % plan.stride == 0)
    assert np.all(np.diff(steps) <= plan.stride)  # only the last interval may be shorter
    if n_steps + 1 <= cap:
        assert plan.stride == 1 and plan.n_frames == n_steps + 1
    else:
        assert plan.n_frames <= cap - 1


# --------------------------------------------------------------------------- HU-4.1 crit. 1
def test_hu41_crit1_excel_frames_match_series(excel_out):
    out = excel_out
    head = np.array(out["frame_head_m"])
    assert out["frame_stride"] == 1
    assert out["frame_time_s"] == out["time_s"]  # 401 instants, no subsampling
    assert head.shape == (401, 21)
    assert out["frame_x_m"] == out["x_m"]
    valve, mid = len(out["x_m"]) - 1, midpoint_index(out)
    # same full-precision value, same rounding: identical (V-19)
    assert head[:, valve].tolist() == out["head_valve_m"]
    assert head[:, mid].tolist() == out["head_midpoint_m"]
    assert head[:, 0].tolist() == [r3(100.0)] * 401  # constant-level reservoir
    # derived pressure against the series of pressure (difference of rounded lists)
    pressure = derived_pressure(out)
    within(pressure[:, valve], out["pressure_head_valve_m"])
    within(pressure[:, mid], out["pressure_head_midpoint_m"])


def test_hu41_crit1_also_holds_with_profile():
    out = solve(profile(GENERIC_X, GENERIC_Z, include_frames=True))
    head = np.array(out["frame_head_m"])
    assert out["frame_stride"] == 1
    mid = midpoint_index(out)
    assert head[:, -1].tolist() == out["head_valve_m"]
    assert head[:, mid].tolist() == out["head_midpoint_m"]
    pressure = derived_pressure(out)
    within(pressure[:, -1], out["pressure_head_valve_m"])
    within(pressure[:, mid], out["pressure_head_midpoint_m"])


# --------------------------------------------------------------------------- HU-4.1 crit. 2
@pytest.mark.parametrize(
    "data",
    [
        case(),
        profile(GENERIC_X, GENERIC_Z, include_frames=True),
        profile(LOMA_X, LOMA_Z, include_frames=True),
    ],
    ids=["excel", "generic-profile", "loma"],
)
def test_hu41_crit2_frame_extremes_equal_envelopes_without_subsampling(data):
    out = solve(data)
    assert out["frame_stride"] == 1
    head = np.array(out["frame_head_m"])
    pressure = derived_pressure(out)
    within(pressure.max(axis=0), out["pressure_head_max_m"])
    within(pressure.min(axis=0), out["pressure_head_min_m"])
    within(pressure[0], out["pressure_head_initial_m"])
    # rounding is monotonic: the extreme of the rounded frames is the rounded envelope
    assert head.max(axis=0).tolist() == out["head_max_m"]
    assert head.min(axis=0).tolist() == out["head_min_m"]
    assert head[0].tolist() == out["head_initial_m"]


# --------------------------------------------------------------------------- HU-4.1 crit. 3
@pytest.mark.parametrize("flag", [True, False])
def test_hu41_crit3_no_frame_pressure_nor_flow_keys(flag):
    out = solve(case(include_frames=flag))
    assert "frame_pressure_head_m" not in out  # D-64 (1)
    assert "frame_flow_lps" not in out  # U-33, D-57 (3)
    assert "frame_pressure_head_m" not in SolveResponse.model_fields
    assert set(out) == set(SolveResponse.model_fields)


# --------------------------------------------------------------------------- D-64 (3), U-42
INVARIANT_CASES = [
    ("excel", case()),
    ("generic-profile", profile(GENERIC_X, GENERIC_Z, include_frames=True)),
    ("worst-case", worst_case_with_frames()),
]


@pytest.fixture(scope="module", params=INVARIANT_CASES, ids=[n for n, _ in INVARIANT_CASES])
def invariant_run(request) -> tuple[dict, MocResult]:
    _, data = request.param
    return solve(data), internal_frames(data)


def test_d64_invariant1_frame_x_is_x(invariant_run):
    out, _ = invariant_run
    assert out["frame_x_m"] == out["x_m"]  # identical lists, same floats


def test_d64_invariant2_pressure_is_head_minus_elevation(invariant_run):
    """|(frame_head_m - elevation_m) - r(H - z)| <= 0.001 m + 1e-9 m, H and z at full precision."""
    out, res = invariant_run
    assert res.frame_steps is not None and res.frame_head_m is not None
    assert res.frame_steps.tolist() == frame_steps(out)
    exact = res.frame_head_m - res.mesh.station_elevation_m  # p = H - z (M13)
    expected = np.array(r3_list(exact)).reshape(exact.shape)
    within(derived_pressure(out), expected)
    # elevation_m is the same z with which every pressure_head_* field is computed
    assert out["elevation_m"] == r3_list(res.mesh.station_elevation_m)
    # and the frames themselves are the full-precision heads rounded once (U-39 (5))
    assert out["frame_head_m"] == [r3_list(row) for row in res.frame_head_m]


def test_d64_invariant3_frame_to_step_and_series(invariant_run):
    out, _ = invariant_run
    steps = frame_steps(out)
    time_s = out["time_s"]
    assert [time_s[i] for i in steps] == out["frame_time_s"]  # exact
    assert len(set(steps)) == len(steps)
    pressure = derived_pressure(out)
    valve, mid = len(out["x_m"]) - 1, midpoint_index(out)
    within(pressure[:, valve], np.array(out["pressure_head_valve_m"])[steps])
    within(pressure[:, mid], np.array(out["pressure_head_midpoint_m"])[steps])


def test_d64_last_frame_of_the_subsampled_recipe_is_not_k_times_stride(worst_out):
    """With subsampling the last frame is i = n_steps, not 69*145 = 10 005 (U-42 (3))."""
    out = worst_out
    k_last = len(out["frame_time_s"]) - 1
    assert k_last * out["frame_stride"] == 10_005 != out["n_steps"]
    assert out["frame_time_s"][-1] == out["time_s"][out["n_steps"]]
    # the bound holds at x = L and L/2 for that last frame as well
    p = derived_pressure(out)[-1]
    assert abs(p[-1] - out["pressure_head_valve_m"][-1]) <= DIFF_TOL
    assert abs(p[midpoint_index(out)] - out["pressure_head_midpoint_m"][-1]) <= DIFF_TOL


@pytest.mark.parametrize("data", [d for _, d in INVARIANT_CASES] + [profile(LOMA_X, LOMA_Z)],
                         ids=[n for n, _ in INVARIANT_CASES] + ["loma"])
def test_d64_same_elevation_in_every_pressure_field(data):
    """head_* - elevation_m against pressure_head_* within 0.001 m + 1e-9 m at every j (U-42)."""
    out = solve(data)
    z = np.array(out["elevation_m"])
    for h_key, p_key in (("head_initial_m", "pressure_head_initial_m"),
                         ("head_max_m", "pressure_head_max_m"),
                         ("head_min_m", "pressure_head_min_m")):
        within(np.array(out[h_key]) - z, out[p_key])


# --------------------------------------------------------------------------- HU-4.1 crit. 4
def test_hu41_crit4_wave_front_at_055_s_on_frames():
    out = solve(case(darcy_friction_factor=0.0, duration_s=5.0,
                     closure_time_s=[0.0, 0.05], closure_flow_lps=[100.0, 0.0]))
    assert out["frame_stride"] == 1
    k = out["frame_time_s"].index(out["time_s"][11])  # t = 11 * 0.05 s
    assert out["frame_time_s"][k] == pytest.approx(0.55, abs=1e-12)
    head = np.array(out["frame_head_m"][k])
    x = np.array(out["frame_x_m"])
    assert np.all(np.abs(head[x < 500.0] - 100.0) <= 0.01)
    assert np.all(np.abs(head[x > 500.0] - 244.21) <= 0.01)


# --------------------------------------------------------------------------- HU-4.2 crit. 2
def test_hu42_crit2_worst_case_subsampled(worst_out):
    out = worst_out
    assert out["n_steps"] == MAX_STEPS
    n_stations = len(out["x_m"])
    assert n_stations == 699
    cap = min(1001, 50_000 // n_stations)
    times = out["frame_time_s"]
    head = np.array(out["frame_head_m"])
    assert out["frame_stride"] == 145
    assert len(times) == 70 == cap - 1
    assert head.shape == (70, n_stations)
    assert times[0] == 0.0 and times[-1] == out["duration_s"] == out["time_s"][-1]
    assert out["frame_x_m"] == out["x_m"]
    # every frame instant is a value of time_s, at the planned steps
    index = {t: k for k, t in enumerate(out["time_s"])}
    steps = [index[t] for t in times]
    assert steps == list(range(0, 9861, 145)) + [MAX_STEPS] == frame_steps(out)
    # each frame is the state of that step: identical to the valve / midpoint series (V-19)
    assert head[:, -1].tolist() == np.array(out["head_valve_m"])[steps].tolist()
    assert head[:, midpoint_index(out)].tolist() == np.array(out["head_midpoint_m"])[steps].tolist()
    assert head[0].tolist() == out["head_initial_m"]


def test_hu42_crit2_envelopes_use_every_step_not_the_frames(worst_out):
    out = worst_out
    head = np.array(out["frame_head_m"])
    # The frames sit inside the envelopes ...
    assert np.all(head.max(axis=0) <= np.array(out["head_max_m"]))
    assert np.all(head.min(axis=0) >= np.array(out["head_min_m"]))
    # ... and miss the extremes somewhere: the envelopes come from all 10 001 steps.
    assert np.any(head.max(axis=0) < np.array(out["head_max_m"]))
    assert np.any(head.min(axis=0) > np.array(out["head_min_m"]))
    # Same envelopes, extremes and checks as without frames.
    bare = solve(worst_case_profile())
    for key, value in bare.items():
        if key not in FRAME_KEYS:
            assert out[key] == value, key


# --------------------------------------------------------------------------- U-24, U-33
def test_include_frames_false_gives_nulls_and_identical_results(excel_out):
    bare = solve(case(include_frames=False))
    for key in FRAME_KEYS:
        assert bare[key] is None, key
        assert excel_out[key] is not None, key
    for key, value in bare.items():
        if key not in FRAME_KEYS:
            assert excel_out[key] == value, key


def test_worst_case_with_frames_is_strict_json(worst_out):
    text = json.dumps(worst_out, allow_nan=False)
    assert json.loads(text) == worst_out
    SolveResponse.model_validate(worst_out)


# --------------------------------------------------------------------------- V-16 / HU-4.2-1
def _median_time(data: dict) -> float:
    solve(data)  # warm-up
    times = []
    for _ in range(5):
        start = time.perf_counter()
        solve(data)
        times.append(time.perf_counter() - start)
    return statistics.median(times)


def test_hu42_crit1_excel_case_with_frames_time_budget():
    assert _median_time(case()) < 1.0


def test_v16_worst_case_with_frames_time_budget():
    """N = 200, 500 vertices, 10 000 steps, frames on, through solve(): median of 5 < 0.8 s."""
    assert _median_time(worst_case_with_frames()) < 0.8


# --------------------------------------------------------------------------- V-18 (U-34)
def _measure_payload():
    import importlib.util

    from conftest import REPO

    spec = importlib.util.spec_from_file_location("measure_payload", REPO / "tools" / "measure_payload.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_measure_payload_recipe_is_the_worst_case_of_the_tests():
    """The published recipe (U-34 (3)) is the same input the V-16 tests time."""
    assert _measure_payload().worst_case_recipe() == worst_case_with_frames()


def test_v18_measured_sizes_fit_d57_d65():
    """D-65 (3)-(4): realistic recipe and adversarial input <= 3 500 000 B each (larger of the
    two serialisations), the adversarial one >= 20 B per number; request <= 65 536 B."""
    report = _measure_payload().measure(top=1, timing=False)
    assert report["recipe"]["n_stations"] == 699 and report["recipe"]["n_frames"] == 70
    assert report["worst_response"]["bytes"] <= 3_500_000, report["worst_response"]
    adv = report["adversarial"]
    assert adv["n_stations"] == 699 and adv["n_steps"] == MAX_STEPS
    assert adv["response_b"]["max"] <= 3_500_000, adv
    assert adv["bytes_per_number"] >= 20.0, adv
    assert report["analytic_bound_b"] <= 3_500_000
    # F5R-01: the negative-datum variant weighs more than the published recipe, and still
    # stays within the analytic bound, which is the ceiling for every admitted input.
    neg = report["adversarial_negative_datum"]["response_b"]["max"]
    assert adv["response_b"]["max"] < neg <= report["analytic_bound_b"]
    assert report["worst_request"]["bytes"] <= 65_536, report["worst_request"]
