"""Phase 3: real pipe profile (plan 01 §5 phase 3, M13-M14, U-07, U-22; V-10).

Covers HU-2.1 crit. 1-5, HU-2.2 crit. 1-3 and HU-2.3 crit. 1-5. Tolerance ± 1e-6 m
(V-10); the loma check is the identity p_min(500) = p_min horizontal - 40.
"""

from __future__ import annotations

import json
import statistics
import time

import numpy as np
import pytest

from mainpipe_transient import MainpipeTransientValidationError, solve
from mainpipe_transient._closure import build_closure_law
from mainpipe_transient._geometry import (
    MAX_STEPS,
    build_horizontal_mesh,
    build_profile_mesh,
    count_steps,
)
from mainpipe_transient._moc import PipeData, simulate
from moc_cases import Recorder

TOL = 1e-6  # m (V-10)

HORIZONTAL = {
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
    "include_frames": False,
}

LOMA_X = [0.0, 500.0, 1000.0]
LOMA_Z = [0.0, 40.0, 0.0]
# Any profile ending at 1000 m below the initial hydraulic grade line (HU-2.1 crit. 1),
# with vertices on and off the nodes.
GENERIC_X = [0.0, 137.0, 300.0, 520.0, 733.3, 1000.0]
GENERIC_Z = [0.0, -12.5, 8.0, 31.0, 4.2, -20.0]

SERIES = ("time_s", "head_valve_m", "head_midpoint_m", "flow_reservoir_lps", "flow_valve_lps")
NODE_ENVELOPES = ("head_initial_m", "head_max_m", "head_min_m")


def horizontal(**changes) -> dict:
    data = json.loads(json.dumps(HORIZONTAL))
    data.update(changes)
    return data


def profile(x: list[float], z: list[float], **changes) -> dict:
    data = horizontal(**changes)
    data.pop("length_m", None)
    data.pop("pipe_elevation_m", None)
    data.update(geometry="profile", profile_x_m=list(x), profile_z_m=list(z))
    return data


def reject(data: dict) -> str:
    with pytest.raises(MainpipeTransientValidationError) as info:
        solve(data)
    assert info.value.http_status == 422
    assert info.value.__cause__ is not None
    message = str(info.value)
    assert "Value error" not in message and len(message) <= 400, message
    return message


def at(out: dict, field: str, x: float) -> float:
    return out[field][out["x_m"].index(x)]


def node_values(out: dict, field: str) -> np.ndarray:
    mask = np.array(out["x_is_node"])
    return np.array(out[field])[mask]


def nodal_history(mesh, data: dict) -> tuple[np.ndarray, np.ndarray]:
    """Full H/Q history at the nodes through the internal API (tests only)."""
    q0 = data["initial_flow_lps"] / 1000.0
    law = build_closure_law(data["closure_time_s"], [q / 1000 for q in data["closure_flow_lps"]], q0)
    pipe = PipeData(
        diameter_m=data["inner_diameter_mm"] / 1000.0,
        wave_speed_ms=data["wave_speed_ms"],
        friction_factor=data["darcy_friction_factor"],
        initial_flow_m3s=q0,
        reservoir_level_m=data["reservoir_level_m"],
        gravity_ms2=9.81,
    )
    rec = Recorder()
    res = simulate(pipe, mesh, law, count_steps(data["duration_s"], mesh.dt_s), observer=rec)
    return rec.head_m, rec.flow_lps, res


# --------------------------------------------------------------------------- HU-2.1
def test_hu21_crit1_profile_does_not_change_head_and_flow():
    """Through solve(): series and nodal H envelopes equal the horizontal case (± 1e-6)."""
    h = solve(horizontal())
    p = solve(profile(GENERIC_X, GENERIC_Z))
    for field in SERIES:
        np.testing.assert_allclose(p[field], h[field], rtol=0, atol=TOL, err_msg=field)
    for field in NODE_ENVELOPES:
        np.testing.assert_allclose(node_values(p, field), h[field], rtol=0, atol=TOL, err_msg=field)


def test_hu21_crit1_full_nodal_history_is_identical():
    """Every node, every step: H and Q of the profile mesh equal the horizontal ones (M13)."""
    data = HORIZONTAL
    hh, qh, _ = nodal_history(build_horizontal_mesh(1000.0, 20, 1000.0, 0.0), data)
    hp, qp, _ = nodal_history(build_profile_mesh(GENERIC_X, GENERIC_Z, 20, 1000.0), data)
    assert hh.shape == hp.shape == (401, 21)
    np.testing.assert_allclose(hp, hh, rtol=0, atol=TOL)
    np.testing.assert_allclose(qp, qh, rtol=0, atol=TOL)


def test_hu21_crit2_loma_elevation_and_pressure_identity():
    out = solve(profile(LOMA_X, LOMA_Z))
    assert at(out, "elevation_m", 250.0) == pytest.approx(20.0, abs=TOL)
    z = np.array(out["elevation_m"])
    for p_field, h_field in (("pressure_head_min_m", "head_min_m"),
                             ("pressure_head_max_m", "head_max_m"),
                             ("pressure_head_initial_m", "head_initial_m")):
        np.testing.assert_allclose(out[p_field], np.array(out[h_field]) - z, rtol=0, atol=TOL)


def test_hu21_crit3_two_point_flat_profile_equals_horizontal():
    h = solve(horizontal())
    p = solve(profile([0.0, 1000.0], [0.0, 0.0]))
    assert p.pop("geometry") == "profile"
    assert h.pop("geometry") == "horizontal"
    assert p == h  # identical, not just within tolerance


def test_hu21_crit4_length_is_last_chainage():
    out = solve(profile([0.0, 400.0, 1250.0], [0.0, 10.0, -5.0], duration_s=None))
    assert out["length_m"] == 1250.0
    assert out["dx_m"] == 62.5
    assert out["reflection_time_s"] == 2.5
    assert out["x_m"][-1] == 1250.0
    # default duration Tc + 5*(4L/a) = 1.5 + 25 = 26.5 s
    assert out["duration_s"] == pytest.approx(26.5, abs=1e-12)


def test_hu21_crit5_midpoint_pressure_uses_profile_elevation():
    """z(L/2) interpolated between vertices that do not include L/2."""
    out = solve(profile([0.0, 300.0, 1000.0], [0.0, 30.0, -40.0]))
    z_mid = 30.0 + (500.0 - 300.0) / 700.0 * (-70.0)  # = 10.0
    assert at(out, "elevation_m", 500.0) == pytest.approx(z_mid, abs=1e-12)
    np.testing.assert_allclose(
        out["pressure_head_midpoint_m"], np.array(out["head_midpoint_m"]) - z_mid, rtol=0, atol=TOL
    )
    np.testing.assert_allclose(
        out["pressure_head_valve_m"], np.array(out["head_valve_m"]) + 40.0, rtol=0, atol=TOL
    )


# --------------------------------------------------------------------------- HU-2.2
def test_hu22_crit1_vertex_between_nodes_is_a_station():
    out = solve(profile([0.0, 520.0, 1000.0], [0.0, 33.0, 0.0]))
    assert len(out["x_m"]) == 22
    assert 520.0 in out["x_m"]
    assert at(out, "elevation_m", 520.0) == 33.0
    assert at(out, "x_is_node", 520.0) is False
    assert sum(out["x_is_node"]) == 21
    assert at(out, "x_is_node", 500.0) is True and at(out, "x_is_node", 550.0) is True


def test_m14_vertex_head_is_interpolated_at_every_step():
    """Envelope at a vertex = max/min over steps of the H interpolated between its nodes."""
    x, z = [0.0, 520.0, 1000.0], [0.0, 33.0, 0.0]
    mesh = build_profile_mesh(x, z, 20, 1000.0)
    heads, _, res = nodal_history(mesh, HORIZONTAL)
    h520 = heads[:, 10] + 0.4 * (heads[:, 11] - heads[:, 10])
    s = int(np.flatnonzero(mesh.station_x_m == 520.0)[0])
    assert res.head_max_m[s] == pytest.approx(h520.max(), abs=1e-12)
    assert res.head_min_m[s] == pytest.approx(h520.min(), abs=1e-12)
    assert res.head_initial_m[s] == pytest.approx(h520[0], abs=1e-12)
    # first instant of the extreme (U-25 tie-break input)
    assert res.head_min_step[s] == int(np.argmin(h520))


def test_u07_vertex_close_to_node_is_merged():
    eps = 0.5e-9 * 1000.0  # below 1e-9 * L
    out = solve(profile([0.0, 500.0 + eps, 1000.0], [0.0, 40.0, 0.0]))
    assert len(out["x_m"]) == 21 and all(out["x_is_node"])
    assert at(out, "elevation_m", 500.0) == 40.0  # the vertex elevation is kept
    apart = solve(profile([0.0, 500.0 + 1e-5, 1000.0], [0.0, 40.0, 0.0]))
    assert len(apart["x_m"]) == 22


@pytest.mark.parametrize(
    "x, z",
    [(LOMA_X, LOMA_Z), (GENERIC_X, GENERIC_Z), ([0.0, 520.0, 1000.0], [0.0, 33.0, 0.0])],
    ids=["loma", "generico", "vertice-520"],
)
def test_hu22_crit2_global_extremes_and_aligned_columns(x, z):
    out = solve(profile(x, z))
    n = len(out["x_m"])
    for field in ("x_is_node", "elevation_m", "head_initial_m", "pressure_head_initial_m",
                  "head_max_m", "head_min_m", "pressure_head_max_m", "pressure_head_min_m"):
        assert len(out[field]) == n, field
    assert np.all(np.diff(out["x_m"]) > 0)
    assert set(x) <= set(out["x_m"])  # no vertex lost (all of these are exact)
    assert out["pressure_head_min_global_m"] == min(out["pressure_head_min_m"])
    assert out["pressure_head_max_global_m"] == max(out["pressure_head_max_m"])
    assert out["pressure_head_min_global_x_m"] in out["x_m"]
    assert out["pressure_head_max_global_x_m"] in out["x_m"]
    assert out["pressure_head_min_global_time_s"] in out["time_s"]
    assert out["pressure_head_max_global_time_s"] in out["time_s"]
    j = out["x_m"].index(out["pressure_head_min_global_x_m"])
    assert out["pressure_head_min_m"][j] == out["pressure_head_min_global_m"]


@pytest.mark.parametrize(
    "x, z, which, x_expected",
    [
        ([0.0, 510.0, 520.0, 530.0, 1000.0], [0.0, 0.0, 60.0, 0.0, 0.0], "min", 520.0),
        ([0.0, 960.0, 970.0, 980.0, 1000.0], [0.0, 0.0, -60.0, 0.0, 0.0], "max", 970.0),
    ],
    ids=["minimo-en-pico", "maximo-en-valle"],
)
def test_f301_global_extreme_on_a_vertex_that_is_not_a_node(x, z, which, x_expected):
    """F3-01: a sharp peak/dip between nodes holds the global extreme; nodes alone miss it."""
    out = solve(profile(x, z))
    pick = min if which == "min" else max
    envelope = out[f"pressure_head_{which}_m"]
    assert out[f"pressure_head_{which}_global_x_m"] == x_expected
    assert at(out, "x_is_node", x_expected) is False
    assert out[f"pressure_head_{which}_global_m"] == pick(envelope)
    nodes_only = pick(v for v, node in zip(envelope, out["x_is_node"]) if node)
    assert abs(out[f"pressure_head_{which}_global_m"] - nodes_only) > 10.0


def test_hu22_crit3_loma_lowers_minimum_pressure_by_its_height():
    """V-10: p_min(500) with the loma = horizontal p_min(500) - 40 (± 1e-6 m)."""
    h = solve(horizontal())
    p = solve(profile(LOMA_X, LOMA_Z))
    assert at(p, "pressure_head_min_m", 500.0) == pytest.approx(
        at(h, "pressure_head_min_m", 500.0) - 40.0, abs=TOL
    )
    # and at every node, by exactly its elevation
    np.testing.assert_allclose(
        node_values(p, "pressure_head_min_m"),
        np.array(h["pressure_head_min_m"]) - node_values(p, "elevation_m"),
        rtol=0, atol=TOL,
    )
    assert p["pressure_head_min_global_m"] < h["pressure_head_min_global_m"]


# --------------------------------------------------------------------------- HU-2.3
def test_hu23_crit1_non_increasing_chainage_names_the_point():
    msg = reject(profile([0.0, 150.0, 300.0, 120.0, 600.0], [0.0, 1.0, 2.0, 3.0, 4.0]))
    assert "estrictamente creciente" in msg
    # HU-2.3 crit. 1 literal (0-based x[i]) plus the 1-based point used elsewhere (F3-03)
    assert "x[3] = 120 m (punto 4) es menor que x[2] = 300 m (punto 3)" in msg


def test_hu23_crit1_repeated_chainage():
    msg = reject(profile([0.0, 300.0, 300.0, 600.0], [0.0, 1.0, 2.0, 3.0]))
    assert "x[2] = 300 m (punto 3) es igual a x[1] = 300 m (punto 2)" in msg


@pytest.mark.parametrize(
    "x, z, expected",
    [
        ([0.0], [0.0], "entre 2 y 500 puntos; profile_x_m tiene 1"),
        ([float(i) for i in range(501)], [0.0] * 501, "entre 2 y 500 puntos; profile_x_m tiene 501"),
        ([0.0, 500.0, 1000.0], [0.0, 1.0], "mismo número de puntos: tienen 3 y 2"),
    ],
    ids=["1-punto", "501-puntos", "longitudes-distintas"],
)
def test_hu23_crit2_point_count(x, z, expected):
    assert expected in reject(profile(x, z))


def test_hu23_crit2_500_points_is_accepted():
    x = [1000.0 * j / 499 for j in range(500)]
    out = solve(profile(x, [0.0] * 500))
    assert out["length_m"] == x[-1]


def test_hu23_crit3_profile_must_start_at_zero():
    msg = reject(profile([10.0, 500.0, 1000.0], [0.0, 0.0, 0.0]))
    assert "empezar en x = 0 m" in msg and "profile_x_m[0] = 10 m" in msg


def test_hu23_crit4_intake_above_reservoir():
    msg = reject(profile([0.0, 1000.0], [100.5, 0.0]))
    assert "por encima del nivel del depósito" in msg
    assert "100.5 m" in msg and "reservoir_level_m = 100 m" in msg


def test_hu23_intake_at_reservoir_level_is_accepted():
    out = solve(profile([0.0, 1000.0], [100.0, 0.0]))
    assert out["elevation_m"][0] == 100.0


def test_hu23_crit5_profile_geometry_without_profile():
    data = horizontal(geometry="profile")
    data.pop("length_m")
    data.pop("pipe_elevation_m")
    msg = reject(data)
    assert "geometry = profile hay que enviar profile_x_m y profile_z_m" in msg
    assert "geometry = horizontal" in msg


def test_hu23_crit5_horizontal_geometry_with_profile():
    msg = reject(horizontal(profile_x_m=[0.0, 1000.0], profile_z_m=[0.0, 0.0]))
    assert "geometry = horizontal no se admite profile_x_m ni profile_z_m" in msg
    assert "geometry = profile" in msg


@pytest.mark.parametrize("extra", ["length_m", "pipe_elevation_m"])
def test_u22_profile_with_horizontal_fields_is_rejected(extra):
    data = {**profile(LOMA_X, LOMA_Z), extra: 1000.0 if extra == "length_m" else 0.0}
    msg = reject(data)
    assert f"geometry = profile no se admite {extra}" in msg


def test_profile_step_cap_uses_profile_length():
    """MAX_STEPS with L = last chainage: L = 1250, N = 200 -> T_max = 62.5 s."""
    base = profile([0.0, 600.0, 1250.0], [0.0, 20.0, 0.0], n_reaches=200)
    assert solve({**base, "duration_s": 62.5})["n_steps"] == MAX_STEPS
    msg = reject({**base, "duration_s": 62.6})
    assert "62.5 s" in msg


# --------------------------------------------------------------------------- V-16 (profile)
def worst_case_profile() -> dict:
    """U-34 (3) recipe without frames: N = 200, 500 vertices off-node, 10 000 steps."""
    length, n_vertices = 1234.5, 500
    x = [length * j / (n_vertices - 1) for j in range(n_vertices)]
    x[-1] = length
    z = [62.0 * np.sin(np.pi * xi / length) - 0.01 * xi for xi in x]  # loma, negative pressures
    t = [0.0] + [50.0 * (i / 19) ** 1.3 for i in range(1, 20)]
    q0 = 87.654321
    flows = [q0 * (1.0 - (ti / 50.0) ** 0.7) for ti in t]
    flows[-1] = 0.0
    return {
        "geometry": "profile",
        "profile_x_m": x,
        "profile_z_m": [float(v) for v in z],
        "inner_diameter_mm": 287.3,
        "wave_speed_ms": 1100.0,
        "darcy_friction_factor": 0.0173,
        "initial_flow_lps": q0,
        "reservoir_level_m": 60.0,
        "pn_bar": 16.0,
        "closure_time_s": t,
        "closure_flow_lps": flows,
        "n_reaches": 200,
        "duration_s": 56.113,
        "include_frames": False,
    }


def test_v16_worst_case_profile_time_budget():
    """N = 200, 500 vertices, 10 000 steps through solve(): median of 5 < 0.8 s."""
    data = worst_case_profile()
    out = solve(data)  # warm-up
    assert out["n_steps"] == MAX_STEPS
    assert len(out["x_m"]) == 699  # 201 nodes + 498 interior vertices off-node
    assert out["pressure_head_min_global_m"] < 0
    times = []
    for _ in range(5):
        start = time.perf_counter()
        solve(data)
        times.append(time.perf_counter() - start)
    assert statistics.median(times) < 0.8, times
