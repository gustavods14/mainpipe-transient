"""Phase 5: player series (plan 01 §1.4, §5 phase 5; U-10, U-11, U-24, U-33; V-16, V-17).

Covers HU-4.1 crit. 1-4 and HU-4.2 crit. 1-2 (as amended by D-57). Tolerance ± 1e-9 m
(V-17). The payload measurements of V-18 live in ``tools/measure_payload.py``.
"""

from __future__ import annotations

import json
import statistics
import time

import numpy as np
import pytest

from mainpipe_transient import SolveResponse, solve
from mainpipe_transient._frames import FRAME_CELL_BUDGET, MAX_FRAMES, max_frames, plan_frames
from mainpipe_transient._geometry import MAX_STEPS
from test_contract import case
from test_profile import GENERIC_X, GENERIC_Z, LOMA_X, LOMA_Z, profile, worst_case_profile

TOL = 1e-9  # m (V-17)
FRAME_KEYS = ("frame_stride", "frame_time_s", "frame_x_m", "frame_head_m", "frame_pressure_head_m")


def worst_case_with_frames() -> dict:
    return {**worst_case_profile(), "include_frames": True}


@pytest.fixture(scope="module")
def excel_out() -> dict:
    return solve(case())  # include_frames defaults to true (U-24)


@pytest.fixture(scope="module")
def worst_out() -> dict:
    return solve(worst_case_with_frames())


def arrays(out: dict) -> tuple[np.ndarray, np.ndarray]:
    return np.array(out["frame_head_m"]), np.array(out["frame_pressure_head_m"])


def close(actual, expected) -> None:
    np.testing.assert_allclose(actual, expected, rtol=0.0, atol=TOL)


# --------------------------------------------------------------------------- U-10 frame plan
def test_frame_cap_formula():
    assert FRAME_CELL_BUDGET == 100_000 and MAX_FRAMES == 1001
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
    assert 2 * plan.n_frames * n_stations <= FRAME_CELL_BUDGET
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
    head, pressure = arrays(out)
    assert out["frame_stride"] == 1
    assert out["frame_time_s"] == out["time_s"]  # 401 instants, no subsampling
    assert head.shape == pressure.shape == (401, 21)
    assert out["frame_x_m"] == out["x_m"]
    x = np.array(out["x_m"])
    valve, mid, res = len(x) - 1, int(np.flatnonzero(x == 500.0)[0]), 0
    close(head[:, valve], out["head_valve_m"])
    close(head[:, mid], out["head_midpoint_m"])
    close(head[:, res], np.full(401, 100.0))  # constant-level reservoir
    close(pressure[:, valve], out["pressure_head_valve_m"])
    close(pressure[:, mid], out["pressure_head_midpoint_m"])


def test_hu41_crit1_also_holds_with_profile():
    out = solve(profile(GENERIC_X, GENERIC_Z, include_frames=True))
    head, pressure = arrays(out)
    assert out["frame_stride"] == 1
    x = np.array(out["x_m"])
    mid = int(np.flatnonzero((x == 500.0) & np.array(out["x_is_node"]))[0])
    close(head[:, -1], out["head_valve_m"])
    close(head[:, mid], out["head_midpoint_m"])
    close(pressure[:, -1], out["pressure_head_valve_m"])
    close(pressure[:, mid], out["pressure_head_midpoint_m"])


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
    head, pressure = arrays(out)
    close(pressure.max(axis=0), out["pressure_head_max_m"])
    close(pressure.min(axis=0), out["pressure_head_min_m"])
    close(head.max(axis=0), out["head_max_m"])
    close(head.min(axis=0), out["head_min_m"])
    close(head[0], out["head_initial_m"])
    close(pressure[0], out["pressure_head_initial_m"])


# --------------------------------------------------------------------------- HU-4.1 crit. 3
@pytest.mark.parametrize(
    "data",
    [case(), profile(GENERIC_X, GENERIC_Z, include_frames=True), worst_case_with_frames()],
    ids=["excel", "generic-profile", "worst-case"],
)
def test_hu41_crit3_pressure_is_head_minus_elevation(data):
    out = solve(data)
    head, pressure = arrays(out)
    close(pressure, head - np.array(out["elevation_m"]))


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
    head, pressure = arrays(out)
    assert out["frame_stride"] == 145
    assert len(times) == 70 <= cap
    assert head.shape == pressure.shape == (70, n_stations)
    assert times[0] == 0.0 and times[-1] == out["duration_s"] == out["time_s"][-1]
    assert out["frame_x_m"] == out["x_m"]
    # every frame instant is a value of time_s, at the planned steps
    index = {t: k for k, t in enumerate(out["time_s"])}
    steps = [index[t] for t in times]
    assert steps == list(range(0, 9861, 145)) + [MAX_STEPS]
    # each frame is the state of that step: exact against the valve / midpoint series
    x = np.array(out["x_m"])
    mid = int(np.flatnonzero((x == x[-1] / 2) & np.array(out["x_is_node"]))[0])
    close(head[:, -1], np.array(out["head_valve_m"])[steps])
    close(head[:, mid], np.array(out["head_midpoint_m"])[steps])
    close(pressure[:, -1], np.array(out["pressure_head_valve_m"])[steps])
    close(head[0], out["head_initial_m"])


def test_hu42_crit2_envelopes_use_every_step_not_the_frames(worst_out):
    out = worst_out
    head, pressure = arrays(out)
    # The frames sit inside the envelopes ...
    assert np.all(pressure.max(axis=0) <= np.array(out["pressure_head_max_m"]))
    assert np.all(pressure.min(axis=0) >= np.array(out["pressure_head_min_m"]))
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


@pytest.mark.parametrize("flag", [True, False])
def test_no_frame_flow_key(flag):
    out = solve(case(include_frames=flag))
    assert "frame_flow_lps" not in out  # U-33, D-57 (3)
    assert set(out) == set(SolveResponse.model_fields)


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


def test_v18_measured_sizes_fit_d57():
    """Response <= 3 500 000 B (larger of the two serialisations), request <= 65 536 B."""
    report = _measure_payload().measure(top=1, timing=False)
    assert report["recipe"]["n_stations"] == 699 and report["recipe"]["n_frames"] == 70
    assert report["worst_response"]["bytes"] <= 3_500_000, report["worst_response"]
    assert report["worst_request"]["bytes"] <= 65_536, report["worst_request"]
