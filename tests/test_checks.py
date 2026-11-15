"""Phase 4 of plan 01: theory reference, checks, status and messages.

Covers HU-3.1 ... HU-3.5 and V-11, V-12, V-13 (plan 01 §1.5, §6; U-16, U-17, U-20,
U-25, U-26, U-36). «Caso Excel» and «caso sin fricción» as in plan 01 §6 and HU-1.1.
"""

from __future__ import annotations

import json
import re

import numpy as np
import pytest

from mainpipe_transient import solve
from mainpipe_transient._checks import PN_NEAR_LIMIT_PCT, build_checks
from mainpipe_transient._format import fmt_pressure
from mainpipe_transient._closure import build_closure_law
from mainpipe_transient._geometry import build_horizontal_mesh, build_profile_mesh, count_steps
from mainpipe_transient._moc import Extreme, PipeData, simulate

from moc_cases import Recorder
from rounding import r3, r3_list
from test_profile import GENERIC_X, GENERIC_Z, LOMA_X, LOMA_Z, horizontal, profile

REL = 1e-9  # U-29 for derived magnitudes against the Excel reference (V-11)


def frictionless(**changes) -> dict:
    """HU-1.1 crit. 3: f = 0, closure in one step, horizontal at z = 0, T = 5 s."""
    base = dict(
        darcy_friction_factor=0.0,
        duration_s=5.0,
        closure_time_s=[0.0, 0.05],
        closure_flow_lps=[100.0, 0.0],
    )
    base.update(changes)
    return horizontal(**base)


def codes(out: dict) -> list[str]:
    return [c["code"] for c in out["checks"]]


def check(out: dict, code: str) -> dict:
    found = [c for c in out["checks"] if c["code"] == code]
    assert len(found) == 1, (code, codes(out))
    return found[0]


def validation(excel_reference) -> dict:
    return {c: e["value"] for c, e in excel_reference["validation"].items()}


# Cases used by the cross-cutting properties (HU-3.2 crit. 2, V-13). Each is
# (name, input); the profile ones exercise stations that are not nodes.
STEADY_X = [0.0, 300.0, 1000.0]
PROPERTY_CASES = [
    ("excel", horizontal()),
    ("frictionless", frictionless()),
    ("frictionless-136", frictionless(reservoir_level_m=136.0)),
    ("frictionless-150", frictionless(reservoir_level_m=150.0, pn_bar=40.0)),
    ("loma", profile(LOMA_X, LOMA_Z)),
    ("generic-profile", profile(GENERIC_X, GENERIC_Z)),
    ("vertex-520", profile([0.0, 520.0, 1250.0], [0.0, 40.0, 0.0])),
    ("steady-98", profile(STEADY_X, [0.0, 98.0, 0.0])),
    ("steady-110", profile(STEADY_X, [0.0, 110.0, 0.0])),
    ("limit-7", frictionless(reservoir_level_m=136.0, min_allowed_pressure_head_m=-7.0)),
    ("pn-20", frictionless(pn_bar=20.0)),
]


# F4-02: two valve heads one ulp apart give the same pressure head at steps 300 and 420;
# U-25 asks for the first instant (t = 5.556 s, not 7.778 s). Data of the phase-4 report
# with z and H_dep found by a sweep so that the heads differ while p = H - z ties. The 2.0
# contract fixes g = 9.81 m/s2 (U-40); the 1.0 case used g = 9.78 and its tie vanished, so
# z and H_dep were swept again (seeded sweep over H_dep in [120, 260] m, z in [-150, 60] m).
TIE_CASE = horizontal(
    length_m=500.0,
    inner_diameter_mm=358.9,
    pipe_elevation_m=-135.20707463783273,
    darcy_friction_factor=0.0,
    wave_speed_ms=900.0,
    n_reaches=30,
    initial_flow_lps=40.0,
    reservoir_level_m=255.84901546757607,
    pn_bar=6.0,
    closure_time_s=[0.0, 4.0, 8.0],
    closure_flow_lps=[40.0, 26.5256, 0.0],
    duration_s=14.6667,
)
# F4-03: steady pressure head exactly -10.0 m at x = 300 m (110 m = H_dep + 10, f = 0):
# equal to the limit is not a crossing. Case from the phase-4 report.
EQUAL_LIMIT_CASE = profile(
    [0.0, 300.0, 1000.0],
    [0.0, 110.0, 0.0],
    darcy_friction_factor=0.0,
    duration_s=5.0,
    closure_time_s=[0.0, 0.05],
    closure_flow_lps=[100.0, 0.0],
)
# F4-04: the same tie on the minimum. At the vertex x = 444.954 m, p = H - z ties at steps 155,
# 315 and 475 while H at step 155 is one ulp lower; U-25 asks for t = 1.55 s. Case s5-rand23
# of the phase-4 reverification.
MIN_TIE_CASE = profile(
    [0.0, 79.969, 181.099, 245.039, 323.393, 444.954, 500.0],
    [0.0, -3.4748182177556437, 21.178338131466013, 31.01524372045673, -3.878710106476934,
     54.777384027393, -2.505818076104738],
    wave_speed_ms=1250.0,
    darcy_friction_factor=0.0,
    reservoir_level_m=52.663473975976785,
    closure_time_s=[0.0, 0.5, 1.0],
    closure_flow_lps=[100.0, 10.797511596483291, 0.0],
    n_reaches=40,
    duration_s=5.8,
    min_allowed_pressure_head_m=-10.33,
)
PROPERTY_CASES += [
    ("f4-02-tie", TIE_CASE),
    ("f4-03-equal-limit", EQUAL_LIMIT_CASE),
    ("f4-04-min-tie", MIN_TIE_CASE),
]


def station_pressure_history(data: dict) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """(time_s, x_m, p[k][j]) on every output station and step, via the internal API."""
    time_s, x_m, _, pressure = station_history(data)
    return time_s, x_m, pressure


def station_history(data: dict) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """(time_s, x_m, H[k][j], p[k][j]) at full precision, via the internal API."""
    if data["geometry"] == "profile":
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
    pipe = PipeData(
        diameter_m=data["inner_diameter_mm"] / 1000.0,
        wave_speed_ms=data["wave_speed_ms"],
        friction_factor=data["darcy_friction_factor"],
        initial_flow_m3s=q0,
        reservoir_level_m=data["reservoir_level_m"],
        gravity_ms2=9.81,  # U-40
    )
    rec = Recorder()
    res = simulate(pipe, mesh, law, count_steps(data["duration_s"], mesh.dt_s), observer=rec)
    head = np.array([mesh.station_head(h) for h in rec.head])
    return res.time_s, mesh.station_x_m, head, head - mesh.station_elevation_m


# --------------------------------------------------------------------------- HU-3.1 / V-12
def test_hu31_crit1_pn_head():
    out = solve(horizontal(pn_bar=25.0))
    assert out["pn_head_m"] == pytest.approx(254.84, abs=0.01)


def test_hu31_crit2_ratio_and_near_limit():
    out = solve(frictionless(pn_bar=25.0))
    assert out["pressure_head_max_global_m"] == pytest.approx(244.21, abs=0.01)
    assert out["pressure_max_pn_ratio_pct"] == pytest.approx(95.8, abs=0.1)
    c = check(out, "PN_NEAR_LIMIT")
    assert c["severity"] == "warning"
    assert c["value_m"] == out["pressure_head_max_global_m"]
    assert c["limit_m"] == out["pn_head_m"]
    assert (c["x_m"], c["time_s"]) == (
        out["pressure_head_max_global_x_m"],
        out["pressure_head_max_global_time_s"],
    )
    assert "PN_EXCEEDED" not in codes(out)


def test_hu31_crit3_exceeded_and_no_pn_check():
    out20 = solve(frictionless(pn_bar=20.0))
    assert out20["pn_head_m"] == pytest.approx(203.87, abs=0.01)
    assert check(out20, "PN_EXCEEDED")["severity"] == "error"
    assert "PN_NEAR_LIMIT" not in codes(out20)
    out40 = solve(frictionless(pn_bar=40.0))
    assert not {"PN_EXCEEDED", "PN_NEAR_LIMIT"} & set(codes(out40))


def test_hu31_crit4_exceeded_message_is_literal():
    c = check(solve(frictionless(pn_bar=20.0)), "PN_EXCEEDED")
    assert c["message"] == (
        "La presión máxima (244.2 m.c.a. en x = 1000 m, t = 0.05 s) supera el PN 20 bar "
        "(203.9 m.c.a.). Aumente la clase de la tubería o alargue el cierre."
    )
    assert c["first_x_m"] is None and c["first_time_s"] is None
    assert c["first_pressure_head_m"] is None


def test_v12_pn_uses_the_fixed_density_and_gravity():
    """2.0: rho = 1000 kg/m3 and g = 9.81 m/s2 are constants (U-40, V-12)."""
    out = solve(horizontal(pn_bar=16.0))
    assert out["pn_head_m"] == pytest.approx(16e5 / (1000.0 * 9.81), rel=1e-12)
    assert out["pressure_max_pn_ratio_pct"] == pytest.approx(
        100 * out["pressure_head_max_global_m"] / out["pn_head_m"], rel=1e-3
    )


# --------------------------------------------------------------------------- HU-3.2
def test_hu32_crit1_excel_column_separation_and_full_result():
    out = solve(horizontal())
    assert out["pressure_head_min_global_m"] == pytest.approx(-37.9, abs=0.05)
    c = check(out, "COLUMN_SEPARATION_RISK")
    assert c["severity"] == "error"
    assert out["status"] == "error"
    assert c["value_m"] == out["pressure_head_min_global_m"]
    assert c["limit_m"] == -10.0
    assert (c["x_m"], c["time_s"]) == (
        out["pressure_head_min_global_x_m"],
        out["pressure_head_min_global_time_s"],
    )
    # computed and returned in full, not a 422
    assert len(out["time_s"]) == out["n_steps"] + 1 == 401
    assert len(out["pressure_head_min_m"]) == len(out["x_m"]) == 21


@pytest.mark.parametrize("name,data", PROPERTY_CASES, ids=[n for n, _ in PROPERTY_CASES])
def test_hu32_crit2_first_crossing_is_the_first(name, data):
    """first_* lie on the grid, are below the limit, nothing earlier is (U-25)."""
    out = solve(data)
    limit = out["min_allowed_pressure_head_m"]
    time_s, x_m, p = station_pressure_history(data)
    below = p < limit
    if "COLUMN_SEPARATION_RISK" not in codes(out):
        assert not below.any(), name
        return
    c = check(out, "COLUMN_SEPARATION_RISK")
    assert c["first_x_m"] in out["x_m"]
    assert c["first_time_s"] in out["time_s"]
    k = out["time_s"].index(c["first_time_s"])
    j = out["x_m"].index(c["first_x_m"])
    assert c["first_pressure_head_m"] == p[k, j]
    assert c["first_pressure_head_m"] < limit
    assert not below[:k].any()
    # U-25: among the stations below the limit at that step, the lowest pressure, then lower x
    assert p[k, j] == p[k].min()
    assert j == int(np.flatnonzero(p[k] == p[k].min())[0])
    np.testing.assert_array_equal(time_s, out["time_s"])
    np.testing.assert_array_equal(x_m, out["x_m"])


def test_hu32_crit3_frictionless_first_crossing():
    c = check(solve(frictionless()), "COLUMN_SEPARATION_RISK")
    assert c["first_x_m"] == 1000.0
    assert c["first_time_s"] == pytest.approx(2.05, abs=0.05)
    assert c["value_m"] == pytest.approx(-44.21, abs=0.01)


def test_hu32_crit4_column_separation_message_is_literal():
    c = check(solve(frictionless()), "COLUMN_SEPARATION_RISK")
    # HU-3.2 crit. 4 with the ASCII minus sign (U-26)
    assert c["message"] == (
        "La presión cae a -44.2 m.c.a., por debajo del límite admisible de -10.0 m.c.a., por "
        "primera vez en x = 1000 m y t = 2.05 s. A partir de ese instante puede haber "
        "separación de columna y los resultados del MOC simple dejan de ser físicos: las "
        "presiones y caudales posteriores no son fiables."
    )


def test_hu32_crit4_message_order_when_first_crossing_is_not_the_minimum():
    """Excel case: the first crossing (x = 950 m, t = 3.3 s) precedes the minimum (t = 4 s)."""
    c = check(solve(horizontal()), "COLUMN_SEPARATION_RISK")
    assert c["first_time_s"] < c["time_s"]
    msg = c["message"]
    value = msg.index(f"{c['first_pressure_head_m']:.1f} m.c.a.")
    limit = msg.index("-10.0 m.c.a.")
    where = msg.index(f"x = {c['first_x_m']:g} m")
    when = msg.index(f"t = {c['first_time_s']:.3g} s")
    unphysical = msg.index("dejan de ser físicos")
    assert value < limit < where < when < unphysical


def test_hu32_crit5_subatmospheric_without_column_separation():
    out = solve(frictionless(reservoir_level_m=136.0))
    assert out["pressure_head_min_global_m"] == pytest.approx(-8.21, abs=0.01)
    assert "COLUMN_SEPARATION_RISK" not in codes(out)
    c = check(out, "SUBATMOSPHERIC_PRESSURE")
    assert c["severity"] == "warning"
    assert (c["value_m"], c["limit_m"]) == (out["pressure_head_min_global_m"], 0.0)
    assert "-8.2 m.c.a." in c["message"]
    assert "x = 1000 m" in c["message"] and "t = 2.05 s" in c["message"]
    assert c["first_x_m"] is None


def test_hu32_crit6_limit_entered_by_the_user():
    out = solve(frictionless(reservoir_level_m=136.0, min_allowed_pressure_head_m=-7.0))
    assert "SUBATMOSPHERIC_PRESSURE" not in codes(out)
    c = check(out, "COLUMN_SEPARATION_RISK")
    assert c["limit_m"] == -7.0
    assert "límite admisible de -7.0 m.c.a." in c["message"]


def test_hu32_crit7_no_minimum_pressure_check():
    out = solve(frictionless(reservoir_level_m=150.0))
    assert out["pressure_head_min_global_m"] == pytest.approx(5.79, abs=0.01)
    assert not {"COLUMN_SEPARATION_RISK", "SUBATMOSPHERIC_PRESSURE"} & set(codes(out))


# --------------------------------------------------------------------------- HU-3.3
def test_hu33_crit1_steady_negative_warning():
    out = solve(profile(STEADY_X, [0.0, 98.0, 0.0]))
    assert out["pressure_head_initial_m"][out["x_m"].index(300.0)] == pytest.approx(
        -0.04, abs=0.005
    )
    c = check(out, "STEADY_NEGATIVE_PRESSURE")
    assert c["severity"] == "warning"
    assert (c["x_m"], c["time_s"], c["limit_m"]) == (300.0, 0.0, 0.0)
    # the list is at 3 decimals (U-39), the check value at full precision
    assert r3(c["value_m"]) == min(out["pressure_head_initial_m"])
    # a small depression keeps its sign in the message
    assert "-0.0 m.c.a. en x = 300 m" in c["message"]


def test_hu33_crit2_steady_negative_error():
    out = solve(profile(STEADY_X, [0.0, 110.0, 0.0]))
    c = check(out, "STEADY_NEGATIVE_PRESSURE")
    assert c["severity"] == "error"
    assert c["value_m"] == pytest.approx(-12.04, abs=0.005)
    assert (c["x_m"], c["time_s"], c["limit_m"]) == (300.0, 0.0, -10.0)
    assert "-12.0 m.c.a." in c["message"] and "-10.0 m.c.a." in c["message"]
    # independent checks: below the limit already at t = 0
    sep = check(out, "COLUMN_SEPARATION_RISK")
    assert (sep["first_x_m"], sep["first_time_s"]) == (300.0, 0.0)


@pytest.mark.parametrize("z_top", [98.0, 110.0])
def test_hu33_crit3_result_is_complete(z_top):
    out = solve(profile(STEADY_X, [0.0, z_top, 0.0]))
    assert out["status"] == "error"  # COLUMN_SEPARATION_RISK in both cases
    assert len(out["time_s"]) == out["n_steps"] + 1
    assert len(out["head_max_m"]) == len(out["x_m"])


def test_no_steady_check_on_a_feasible_profile():
    assert "STEADY_NEGATIVE_PRESSURE" not in codes(solve(profile(LOMA_X, LOMA_Z)))


# --------------------------------------------------------------------------- HU-3.4 / V-11
def test_hu34_crit1_and_v11_rapid_against_excel(excel_reference):
    out = solve(horizontal())
    val = validation(excel_reference)
    assert out["maneuver_type"] == "rapid"
    assert out["joukowsky_head_rise_m"] == pytest.approx(val["C7"], rel=REL)
    assert out["theoretical_head_rise_m"] == pytest.approx(val["C11"], rel=REL)
    assert out["theoretical_head_rise_m"] == out["joukowsky_head_rise_m"]
    assert out["moc_head_rise_valve_m"] == pytest.approx(val["C22"], rel=REL)
    assert out["theory_deviation_pct"] == pytest.approx(100 * val["C27"], rel=REL)
    assert out["full_pulse_length_m"] == pytest.approx(val["C12"], abs=1e-9)
    assert out["michaud_head_rise_m"] is None
    # tolerances of the story
    assert out["joukowsky_head_rise_m"] == pytest.approx(144.2, abs=0.1)
    assert out["full_pulse_length_m"] == pytest.approx(250.0, abs=0.1)
    assert out["moc_head_rise_valve_m"] == pytest.approx(149.6, abs=0.1)
    assert out["theory_deviation_pct"] == pytest.approx(3.712, abs=5e-4)


def test_hu34_crit2_and_v11_slow_maneuver():
    out = solve(horizontal(closure_time_s=[0.0, 10.0], closure_flow_lps=[100.0, 0.0]))
    assert out["maneuver_type"] == "slow"
    v0, g, L, tc = out["velocity_initial_ms"], 9.81, 1000.0, 10.0
    assert out["michaud_head_rise_m"] == pytest.approx(2 * L * v0 / (g * tc), rel=1e-12)
    assert out["michaud_head_rise_m"] == pytest.approx(28.84, abs=0.01)
    assert out["theoretical_head_rise_m"] == out["michaud_head_rise_m"]
    assert out["full_pulse_length_m"] is None
    assert out["joukowsky_head_rise_m"] == pytest.approx(1000.0 * v0 / g, rel=1e-12)
    th = out["theoretical_head_rise_m"]
    assert out["theory_deviation_pct"] == pytest.approx(
        100 * (out["moc_head_rise_valve_m"] - th) / th, rel=1e-12
    )


def test_hu34_maneuver_boundary_tc_equal_2l_over_a_is_rapid():
    out = solve(horizontal(closure_time_s=[0.0, 2.0], closure_flow_lps=[100.0, 0.0]))
    assert out["maneuver_type"] == "rapid"
    assert out["full_pulse_length_m"] == pytest.approx(0.0, abs=1e-9)


def test_hu34_crit3_deviation_never_produces_a_check():
    """Same case, deviation above 5 % or not: checks and status are identical."""
    slow = horizontal(closure_time_s=[0.0, 10.0], closure_flow_lps=[100.0, 0.0], pn_bar=40.0)
    out = solve(slow)
    assert abs(out["theory_deviation_pct"]) > 5.0
    assert out["checks"] == [] and out["status"] == "ok"
    text = json.dumps(out["checks"], ensure_ascii=False).lower()
    assert "joukowsky" not in text and "michaud" not in text


# --------------------------------------------------------------------------- HU-3.5
def test_hu35_crit1_ok_without_checks():
    out = solve(frictionless(reservoir_level_m=150.0, pn_bar=40.0))
    assert out["status"] == "ok"
    assert out["checks"] == []


def test_hu35_crit2_status_is_the_most_severe():
    warning_only = solve(frictionless(reservoir_level_m=136.0, pn_bar=40.0))
    assert codes(warning_only) == ["SUBATMOSPHERIC_PRESSURE"]
    assert warning_only["status"] == "warning"
    mixed = solve(horizontal())
    assert {c["severity"] for c in mixed["checks"]} == {"warning", "error"}
    assert mixed["status"] == "error"


def test_hu35_crit3_excel_checks_confirmed_by_validation_sheet(excel_reference):
    out = solve(horizontal())
    val = validation(excel_reference)
    assert codes(out) == ["COLUMN_SEPARATION_RISK", "PN_NEAR_LIMIT"]
    # the global maximum is the valve maximum (4_Validacion C18 = C23)
    assert out["pressure_head_max_global_m"] == pytest.approx(val["C23"], abs=1e-6)
    assert out["pressure_head_max_global_x_m"] == 1000.0
    # C33 is the maximum pressure in bar: ratio = C33 / PN
    assert out["pressure_max_pn_ratio_pct"] == pytest.approx(100 * val["C33"] / 25.0, rel=REL)
    assert out["pressure_max_pn_ratio_pct"] == pytest.approx(95.3, abs=0.05)
    assert "95.3 % del PN 25 bar (254.8 m.c.a.)" in check(out, "PN_NEAR_LIMIT")["message"]


@pytest.mark.parametrize("name,data", PROPERTY_CASES, ids=[n for n, _ in PROPERTY_CASES])
def test_hu35_crit4_messages_spanish_units_decimal_point(name, data):
    for c in solve(data)["checks"]:
        msg = c["message"]
        assert "m.c.a." in msg, msg
        assert re.search(r"\d,\d", msg) is None, msg  # decimal point, never comma
        assert "−" not in msg, msg  # ASCII minus (U-26)
        assert re.search(r"[áéíóúñ]", msg), msg  # Spanish text
        assert len(msg) <= 400, msg
        assert msg.endswith("."), msg


# --------------------------------------------------------------------------- V-13 / §1.5
BAND = 0.0005 + 1e-9  # m: the only disagreement D-63 (4) admits (plan 01 §1.5 (3))


def moc_result(data: dict):
    """Full-precision run through the internal API (MocResult), no rounding."""
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
    pipe = PipeData(data["inner_diameter_mm"] / 1000.0, data["wave_speed_ms"],
                    data["darcy_friction_factor"], q0, data["reservoir_level_m"], 9.81)
    return simulate(pipe, mesh, law, count_steps(data["duration_s"], mesh.dt_s))


def assert_red_rule(out: dict, res) -> None:
    """V-13 (U-36, D-63 (3)-(4)): (a) check <=> full-precision crossing; (b) check fields are
    the full-precision global extreme; (c) STEADY error => COLUMN_SEPARATION_RISK; (d) every
    disagreement between the rounded-list predicate and the check falls inside the band."""
    pn, limit = out["pn_head_m"], out["min_allowed_pressure_head_m"]
    sides = (
        ("PN_EXCEEDED", "max", pn, res.pressure_max_m, np.greater, +1.0),
        ("COLUMN_SEPARATION_RISK", "min", limit, res.pressure_min_m, np.less, -1.0),
    )
    for code, key, threshold, envelope, crosses, sign in sides:
        extreme = out[f"pressure_head_{key}_global_m"]
        present = code in codes(out)
        # (a) exact, at full precision
        assert present is bool(crosses(extreme, threshold))
        assert present is bool(np.any(crosses(envelope, threshold)))
        if present:
            # (b) the marker fields are the full-precision global extreme (==, not rounded)
            c = check(out, code)
            assert c["value_m"] == extreme == (envelope.max() if key == "max" else envelope.min())
            assert c["x_m"] == out[f"pressure_head_{key}_global_x_m"]
            assert c["time_s"] == out[f"pressure_head_{key}_global_time_s"]
            assert c["limit_m"] == threshold
            assert r3(c["x_m"]) in out["x_m"]  # U-41 (2)
            assert c["time_s"] in out["time_s"]
        # (d) predicate on the rounded envelope versus the check
        listed = bool(np.any(crosses(np.array(out[f"pressure_head_{key}_m"]), threshold)))
        if listed and not present:
            assert 0.0 <= sign * (threshold - extreme) < BAND
        elif present and not listed:
            assert 0.0 < sign * (extreme - threshold) <= BAND
        if abs(extreme - threshold) > BAND:
            assert listed is present  # outside the band the two agree exactly
    # (c)
    steady = [c for c in out["checks"] if c["code"] == "STEADY_NEGATIVE_PRESSURE"]
    if steady and steady[0]["severity"] == "error":
        assert "COLUMN_SEPARATION_RISK" in codes(out)


def red_rule_cases() -> list[tuple[str, dict]]:
    from test_profile import worst_case_profile

    return PROPERTY_CASES + [("u34-recipe", worst_case_profile())]


@pytest.mark.parametrize("name,data", red_rule_cases(), ids=[n for n, _ in red_rule_cases()])
def test_v13_red_rule(name, data):
    assert_red_rule(solve(data), moc_result(data))


def test_v13_check_values_are_not_rounded():
    """(b): at least one case where value_m != round(value_m, 3), so U-39 did not touch it."""
    out = solve(horizontal())
    c = check(out, "COLUMN_SEPARATION_RISK")
    assert c["value_m"] != round(c["value_m"], 3)
    assert c["value_m"] == out["pressure_head_min_global_m"]


def _band_case(kind: str, side: str) -> tuple[dict, dict]:
    """A case with the threshold between the full-precision extreme P and r3(P) (V-13).

    ``side`` = "check-without-span": P crosses, r3(P) does not (check and marker, no span);
    "span-without-check": r3(P) crosses, P does not (a rounded j crosses, no check). The
    reservoir level is nudged in tenths of a millimetre (the pressure heads shift with it)
    until P - r3(P) has the wanted sign with some margin; the threshold is their midpoint.
    """
    if kind == "pn":
        base, key = frictionless(), "max"  # p_max ~ 244.2 m, PN ~ 24 bar
    else:
        base, key = frictionless(reservoir_level_m=136.0), "min"  # p_min ~ -8.2 m
    # PN: the check needs P > threshold; the span needs r3(P) > threshold. Limit: reversed.
    want_p_above_r3 = (side == "check-without-span") == (kind == "pn")
    for nudge in [k * 0.0001 for k in range(10)]:  # one full millimetre cycle
        data = {**base, "reservoir_level_m": base["reservoir_level_m"] + nudge}
        extreme = solve({**data, "include_frames": False})[f"pressure_head_{key}_global_m"]
        gap = extreme - r3(extreme)
        if abs(gap) >= 5e-5 and (gap > 0) == want_p_above_r3:
            break
    else:  # pragma: no cover - the nudges always find both signs
        raise AssertionError("no band case found")
    threshold = (extreme + r3(extreme)) / 2.0
    if kind == "pn":
        data["pn_bar"] = threshold * 1000.0 * 9.81 / 1e5
    else:
        data["min_allowed_pressure_head_m"] = threshold
    return data, solve(data)


@pytest.mark.parametrize("kind", ["pn", "limit"])
@pytest.mark.parametrize("side", ["check-without-span", "span-without-check"])
def test_v13_band_cases(kind, side):
    """The four constructed cases of V-13: PN and limit x both sides of the band (D-63 (4))."""
    data, out = _band_case(kind, side)
    code = "PN_EXCEEDED" if kind == "pn" else "COLUMN_SEPARATION_RISK"
    key = "max" if kind == "pn" else "min"
    threshold = out["pn_head_m"] if kind == "pn" else out["min_allowed_pressure_head_m"]
    if kind == "limit":
        assert -10.33 <= threshold <= 0.0
    extreme = out[f"pressure_head_{key}_global_m"]
    assert 0.0 < abs(extreme - threshold) < BAND  # inside the band
    rounded = np.array(out[f"pressure_head_{key}_m"])
    listed = bool(np.any(rounded > threshold if kind == "pn" else rounded < threshold))
    if side == "check-without-span":
        assert code in codes(out) and not listed
        assert check(out, code)["value_m"] == extreme  # the full-precision one
    else:
        assert code not in codes(out) and listed
    assert_red_rule(out, moc_result(data))


def test_v13_named_cases_have_expected_codes():
    assert set(codes(solve(horizontal()))) >= {"COLUMN_SEPARATION_RISK"}
    assert "COLUMN_SEPARATION_RISK" in codes(solve(profile(LOMA_X, LOMA_Z)))
    assert codes(solve(frictionless(reservoir_level_m=150.0, pn_bar=40.0))) == []


@pytest.mark.parametrize("sent,expected", [(None, -10.0), (-7.0, -7.0), (-10.33, -10.33), (0.0, 0.0)])
def test_v13_limit_echo(sent, expected):
    data = horizontal() if sent is None else horizontal(min_allowed_pressure_head_m=sent)
    out = solve(data)
    assert out["min_allowed_pressure_head_m"] == expected
    for c in out["checks"]:
        if c["code"] == "COLUMN_SEPARATION_RISK":
            assert c["limit_m"] == expected


@pytest.mark.parametrize("name,data", PROPERTY_CASES, ids=[n for n, _ in PROPERTY_CASES])
def test_check_shape_order_and_location(name, data):
    out = solve(data)
    severities = [c["severity"] for c in out["checks"]]
    assert severities == sorted(severities, key={"error": 0, "warning": 1}.get)
    order = ["PN_EXCEEDED", "PN_NEAR_LIMIT", "COLUMN_SEPARATION_RISK",
             "SUBATMOSPHERIC_PRESSURE", "STEADY_NEGATIVE_PRESSURE"]
    for sev in ("error", "warning"):
        same = [order.index(c["code"]) for c in out["checks"] if c["severity"] == sev]
        assert same == sorted(same)
    assert len(set(codes(out))) == len(codes(out))
    assert not {"PN_EXCEEDED", "PN_NEAR_LIMIT"} <= set(codes(out))
    assert not {"COLUMN_SEPARATION_RISK", "SUBATMOSPHERIC_PRESSURE"} <= set(codes(out))
    for c in out["checks"]:
        assert r3(c["x_m"]) in out["x_m"] and c["time_s"] in out["time_s"]  # U-41 (2)
        has_first = c["code"] == "COLUMN_SEPARATION_RISK"
        for key in ("first_x_m", "first_time_s", "first_pressure_head_m"):
            assert (c[key] is not None) is has_first, (c["code"], key)
    expected_status = "ok" if not severities else ("error" if "error" in severities else "warning")
    assert out["status"] == expected_status


# --------------------------------------------------------------------------- boundaries
P_MAX = Extreme(value_m=200.0, x_m=1000.0, time_s=2.0)
P_MIN = Extreme(value_m=5.0, x_m=1000.0, time_s=4.0)
STEADY_OK = Extreme(value_m=90.0, x_m=1000.0, time_s=0.0)


def boundary_codes(**overrides) -> list[str]:
    args = dict(
        pressure_max=P_MAX,
        pressure_min=P_MIN,
        steady_min=STEADY_OK,
        first_below_limit=None,
        pn_bar=25.0,
        pn_head_m=254.84,
        pn_ratio_pct=100 * 200.0 / 254.84,
        min_allowed_m=-10.0,
    )
    args.update(overrides)
    return [c.code for c in build_checks(**args)]


def test_boundary_pn():
    assert PN_NEAR_LIMIT_PCT == 80.0  # U-16
    at_pn = Extreme(value_m=254.84, x_m=1000.0, time_s=2.0)
    assert boundary_codes(pressure_max=at_pn, pn_ratio_pct=100.0) == ["PN_NEAR_LIMIT"]
    assert boundary_codes(pn_ratio_pct=80.0) == []  # 80 % < ratio is strict
    above = Extreme(value_m=254.85, x_m=1000.0, time_s=2.0)
    assert boundary_codes(pressure_max=above, pn_ratio_pct=100.0) == ["PN_EXCEEDED"]


def test_boundary_minimum_pressure():
    at_limit = Extreme(value_m=-10.0, x_m=1000.0, time_s=4.0)
    assert boundary_codes(pressure_min=at_limit) == ["SUBATMOSPHERIC_PRESSURE"]
    zero = Extreme(value_m=0.0, x_m=1000.0, time_s=4.0)
    assert boundary_codes(pressure_min=zero) == []
    below = Extreme(value_m=-10.01, x_m=1000.0, time_s=4.0)
    assert boundary_codes(pressure_min=below, first_below_limit=below) == [
        "COLUMN_SEPARATION_RISK"
    ]


def test_boundary_steady():
    at_limit = Extreme(value_m=-10.0, x_m=300.0, time_s=0.0)
    [c] = build_checks(
        pressure_max=P_MAX, pressure_min=P_MIN, steady_min=at_limit, first_below_limit=None,
        pn_bar=25.0, pn_head_m=254.84, pn_ratio_pct=78.5, min_allowed_m=-10.0,
    )
    assert (c.code, c.severity, c.limit_m) == ("STEADY_NEGATIVE_PRESSURE", "warning", 0.0)
    zero = Extreme(value_m=0.0, x_m=300.0, time_s=0.0)
    assert boundary_codes(steady_min=zero) == []


@pytest.mark.parametrize(
    "value,text", [(-0.04, "-0.0"), (-0.06, "-0.1"), (0.04, "0.0"), (-0.0, "0.0"), (-44.211, "-44.2")]
)
def test_fmt_pressure_keeps_the_sign(value, text):
    assert fmt_pressure(value) == text


# --------------------------------------------------------------------------- F4-02 / F4-03
def test_f402_pressure_extreme_tie_takes_the_first_instant():
    out = solve(TIE_CASE)
    time_s, x_m, h, p = station_history(TIE_CASE)
    j = out["x_m"].index(500.0)
    assert p[300, j] == p[420, j] == out["pressure_head_max_global_m"]
    # a real tie of p only: the full-precision heads differ (the later one is higher by one
    # ulp); the output lists, at 3 decimals (U-39), cannot show it
    assert h[300, -1] < h[420, -1]
    assert p[300, -1] == p[420, -1]
    assert out["pressure_head_valve_m"][300] == out["pressure_head_valve_m"][420]
    assert out["pressure_head_max_global_time_s"] == out["time_s"][300]
    c = check(out, "PN_EXCEEDED")
    assert c["time_s"] == out["time_s"][300]
    assert "t = 5.556 s" in c["message"]


@pytest.mark.parametrize("name,data", PROPERTY_CASES, ids=[n for n, _ in PROPERTY_CASES])
def test_f402_global_pressure_extremes_follow_u25(name, data):
    """Global extremes: value, first instant, then lower x, from the full history (U-25)."""
    out = solve(data)
    time_s, x_m, p = station_pressure_history(data)
    for key, value in (("max", p.max()), ("min", p.min())):
        assert out[f"pressure_head_{key}_global_m"] == value
        k, j = min(zip(*np.nonzero(p == value)), key=lambda kj: (kj[0], x_m[kj[1]]))
        assert out[f"pressure_head_{key}_global_time_s"] == time_s[k], name
        assert out[f"pressure_head_{key}_global_x_m"] == x_m[j], name
    # envelopes: the same full-precision values, rounded once (U-39 (5)); exact
    assert out["pressure_head_max_m"] == r3_list(p.max(axis=0))
    assert out["pressure_head_min_m"] == r3_list(p.min(axis=0))


def test_f404_minimum_pressure_tie_takes_the_first_instant():
    out = solve(MIN_TIE_CASE)
    time_s, x_m, p = station_pressure_history(MIN_TIE_CASE)
    j = out["x_m"].index(444.954)
    assert p[155, j] == p[315, j] == p[475, j] == out["pressure_head_min_global_m"]
    assert out["pressure_head_min_global_time_s"] == out["time_s"][155]
    assert out["pressure_head_min_global_x_m"] == 444.954
    c = check(out, "COLUMN_SEPARATION_RISK")
    assert (c["x_m"], c["time_s"]) == (444.954, out["time_s"][155])
    # a real tie of p only: the head reaches its minimum one ulp lower at a later step
    mesh = build_profile_mesh(
        MIN_TIE_CASE["profile_x_m"], MIN_TIE_CASE["profile_z_m"], 40, 1250.0
    )
    q0 = 0.1
    law = build_closure_law(MIN_TIE_CASE["closure_time_s"], [0.1, 0.010797511596483291, 0.0], q0)
    pipe = PipeData(0.3, 1250.0, 0.0, q0, MIN_TIE_CASE["reservoir_level_m"], 9.81)
    res = simulate(pipe, mesh, law, count_steps(5.8, mesh.dt_s))
    assert res.head_min_step[j] == 315 and res.pressure_min_step[j] == 155


def test_f403_pressure_equal_to_the_limit_is_not_a_crossing():
    out = solve(EQUAL_LIMIT_CASE)
    assert out["pressure_head_initial_m"][out["x_m"].index(300.0)] == -10.0
    c = check(out, "COLUMN_SEPARATION_RISK")
    assert (c["first_x_m"], c["first_time_s"]) == (1000.0, out["time_s"][41])
    assert c["first_pressure_head_m"] == pytest.approx(-44.21, abs=0.01)
    steady = check(out, "STEADY_NEGATIVE_PRESSURE")
    assert (steady["severity"], steady["value_m"], steady["limit_m"]) == ("warning", -10.0, 0.0)
