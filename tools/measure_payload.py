"""Measure request and response sizes of ``mainpipe_transient.solve`` (plan 01 V-18, U-34).

Contract 2.0 (D-63, D-64, D-65): one frame matrix (``frame_head_m``), the m / m.c.a. / L/s
lists at 3 decimals. Protocol U-34 (doc/DECISIONS.md), as amended by D-65 (3)-(5):

1. Units: 3.5 MB = 3 500 000 B (10^6, the strictest reading of D-57 (1)); 64 KiB = 65 536 B.
2. Response serialisations, the larger one counts:
   - ``json.dumps(out, ensure_ascii=False, allow_nan=False, separators=(",", ":"))``
     (what Starlette's ``JSONResponse`` emits);
   - ``SolveResponse.model_validate(out).model_dump_json()`` (if FastAPI serialises with
     Pydantic).
   The request is measured compact, like ``JSON.stringify``.
3. Worst response: the deterministic recipe :func:`worst_case_recipe` (profile, N = 200,
   500 vertices with the 498 interior ones off-node, L = 1234.5 m, a = 1100 m/s,
   duration 56.113 s -> 10 000 steps, 20-point law with Tc = 50 s, frames on), and the
   input that maximises the count of numbers in an analytic sweep of the station count
   over [202, 699]. The larger one counts.
3b. Adversarial input of magnitude (D-65 (3)): the deterministic recipe
   :func:`adversarial_recipe`, admitted but without physical sense, with H, z, x, Q and t of
   the order of 1e150 written with 17 significant digits (f = 0, so phi = 0 and nothing
   overflows), 699 stations and 10 000 steps: the 3-decimal rounding cannot shorten any of
   those numbers. It must average >= 20 B per number. Plus the analytic bound of U-34 (3b):
   (largest admitted count of numbers) x 25 B + structure.
   Both responses (3) and (3b) must be <= 3 500 000 B; if either is not, phase 5 stops and a
   decision request is opened (U-34 (6), D-65): the frame budget is not touched here.
4. Worst request: the recipe with every number written with 17 significant digits.
5. Also the Excel case, with and without frames.

Runs against whatever ``mainpipe_transient`` is importable: in the delivery (plan phase 6)
from the installed package in a clean venv (kit 04 §3). This script is outside the
package; it may print.

Usage::

    python tools/measure_payload.py            # human-readable report
    python tools/measure_payload.py --json     # machine-readable report
"""

from __future__ import annotations

import argparse
import json
import math
import platform
import statistics
import sys
import time
from typing import Any

import mainpipe_transient as mpt
from mainpipe_transient import SolveResponse, solve
from mainpipe_transient._frames import plan_frames

RESPONSE_LIMIT_B = 3_500_000  # D-57 (1), U-34 (1)
MAX_NUMBER_B = 25  # longest float repr (24 chars, e.g. -1.2345678901234567e+150) + separator
MIN_ADVERSARIAL_B_PER_NUMBER = 20.0  # D-65 (3)
REQUEST_LIMIT_B = 65_536  # D-57 (10), D-48, U-34 (1)

N_REACHES = 200
LENGTH_M = 1234.5
N_VERTICES = 500  # 499 intervals, 499 prime: no interior vertex falls on a node
SERIES_KEYS = ("time_s", "head_valve_m", "head_midpoint_m", "pressure_head_valve_m",
               "pressure_head_midpoint_m", "flow_reservoir_lps", "flow_valve_lps")
STATION_FLOAT_KEYS = ("x_m", "elevation_m", "head_initial_m", "pressure_head_initial_m",
                      "head_max_m", "head_min_m", "pressure_head_max_m", "pressure_head_min_m")


# ----------------------------------------------------------------------------- inputs
def _loma(x: float) -> float:
    """Profile with a hump that gives negative pressures (U-34 (3))."""
    return 62.0 * math.sin(math.pi * x / LENGTH_M) - 0.01 * x


def _base(profile_x: list[float]) -> dict[str, Any]:
    t = [0.0] + [50.0 * (i / 19) ** 1.3 for i in range(1, 20)]
    q0 = 87.654321
    flows = [q0 * (1.0 - (ti / 50.0) ** 0.7) for ti in t]
    flows[-1] = 0.0
    return {
        "geometry": "profile",
        "profile_x_m": profile_x,
        "profile_z_m": [_loma(x) for x in profile_x],
        "inner_diameter_mm": 287.3,
        "wave_speed_ms": 1100.0,
        "darcy_friction_factor": 0.0173,
        "initial_flow_lps": q0,
        "reservoir_level_m": 60.0,
        "pn_bar": 16.0,
        "closure_time_s": t,
        "closure_flow_lps": flows,
        "n_reaches": N_REACHES,
        "duration_s": 56.113,
        "include_frames": True,
    }


def worst_case_recipe() -> dict[str, Any]:
    """U-34 (3) deterministic recipe: x_j = L*j/499, j = 0..499 (699 stations)."""
    x = [LENGTH_M * j / (N_VERTICES - 1) for j in range(N_VERTICES)]
    x[-1] = LENGTH_M
    return _base(x)


def case_with_stations(n_stations: int) -> dict[str, Any]:
    """Same recipe with ``n_stations - 201`` interior vertices, none on a node."""
    n_free = n_stations - (N_REACHES + 1)
    dx = LENGTH_M / N_REACHES
    x = [0.0]
    for j in range(1, n_free + 1):
        xj = LENGTH_M * j / (n_free + 1)
        if abs(xj / dx - round(xj / dx)) < 1e-6:  # on a node: nudge it off
            xj += 1e-4 * LENGTH_M
        x.append(xj)
    x.append(LENGTH_M)
    return _base(x)


def adversarial_recipe() -> dict[str, Any]:
    """U-34 (3b) deterministic adversarial input of magnitude (D-65 (3)).

    Same layout as :func:`worst_case_recipe` (N = 200, 500 vertices at x_j = L*j/499, so 699
    stations) scaled to L ~ 1.23e150 m, with a reservoir level, elevations, flows and closure
    instants of the order of 1e150 (1e148 for the instants) and 17 significant digits. The flow
    is chosen so that the Joukowsky rise a*V0/g is itself ~1e150 m: heads, pressures and flows
    keep all their digits through the MOC. f = 0 (phi = 0, no V0^2 term). Duration 9999.5*dt ->
    exactly 10 000 steps; Tc = 0.9599*9599*dt keeps T >= Tc + 2L/a and few closed-valve zeros.
    """
    length = 1.2345678901234567e150
    x = [length * j / (N_VERTICES - 1) for j in range(N_VERTICES)]
    x[-1] = length
    level = 3.1415926535897932e150
    z = [2.7182818284590452e150 * math.sin(math.pi * xi / length + 0.3) - 1.4142135623730951e150
         * (xi / length) for xi in x]
    a = 1234.5678901234567
    dt = (length / N_REACHES) / a  # as the package computes it (U-08)
    tc = 0.9599 * 9599.0 * dt
    t = [0.0] + [tc * (i / 19) ** 1.3 for i in range(1, 20)]
    q0 = 1.6180339887498949e151  # L/s -> V0 ~ 2e148 m/s with D = 1 m, a*V0/g ~ 2.6e150 m
    flows = [q0 * (1.0 - (ti / tc) ** 0.7) for ti in t]
    flows[-1] = 0.0
    return {
        "geometry": "profile",
        "profile_x_m": x,
        "profile_z_m": z,
        "inner_diameter_mm": 1000.0,
        "wave_speed_ms": a,
        "darcy_friction_factor": 0.0,
        "initial_flow_lps": q0,
        "reservoir_level_m": level,
        "pn_bar": 16.0,
        "closure_time_s": t,
        "closure_flow_lps": flows,
        "n_reaches": N_REACHES,
        "duration_s": 9999.5 * dt,
        "include_frames": True,
    }


NEGATIVE_DATUM_SHIFT_M = -9.8765432109876543e150


def adversarial_negative_datum_recipe() -> dict[str, Any]:
    """:func:`adversarial_recipe` shifted to a negative datum (F5R-01, published in phase 6).

    Same input with ``reservoir_level_m`` and every ``profile_z_m`` shifted by
    ``NEGATIVE_DATUM_SHIFT_M``: more minus signs and larger magnitudes, so it weighs more than
    the published adversarial recipe. It shows that no concrete recipe bounds every admitted
    input; the analytic bound of U-34 (3b) does. Not one of the two recipes of the portal guard.
    """
    data = adversarial_recipe()
    data["reservoir_level_m"] += NEGATIVE_DATUM_SHIFT_M
    data["profile_z_m"] = [z + NEGATIVE_DATUM_SHIFT_M for z in data["profile_z_m"]]
    return data


def excel_case(include_frames: bool) -> dict[str, Any]:
    return {
        "geometry": "horizontal", "length_m": 1000.0, "pipe_elevation_m": 0.0,
        "inner_diameter_mm": 300.0, "wave_speed_ms": 1000.0, "darcy_friction_factor": 0.02,
        "initial_flow_lps": 100.0, "reservoir_level_m": 100.0, "pn_bar": 25.0,
        "closure_time_s": [0.0, 0.5, 1.0, 1.5, 2.0, 5.0, 10.0, 20.0],
        "closure_flow_lps": [100.0, 50.0, 20.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        "n_reaches": 20, "duration_s": 20.0, "include_frames": include_frames,
    }


# ----------------------------------------------------------------------------- sizes
def response_sizes(out: dict[str, Any]) -> dict[str, int]:
    """Bytes of the two serialisations of U-34 (2) and the larger one."""
    starlette = json.dumps(out, ensure_ascii=False, allow_nan=False, separators=(",", ":"))
    pydantic = SolveResponse.model_validate(out).model_dump_json()
    sizes = {
        "json_dumps_compact": len(starlette.encode("utf-8")),
        "pydantic_model_dump_json": len(pydantic.encode("utf-8")),
    }
    sizes["max"] = max(sizes.values())
    return sizes


def _dump_17(value: Any) -> str:
    """Compact JSON with every float written with 17 significant digits (U-34 (4))."""
    if isinstance(value, bool) or value is None or isinstance(value, (int, str)):
        return json.dumps(value, ensure_ascii=False)
    if isinstance(value, float):
        return format(value, ".17g")
    if isinstance(value, list):
        return "[" + ",".join(_dump_17(v) for v in value) + "]"
    if isinstance(value, dict):
        return "{" + ",".join(f"{json.dumps(k)}:{_dump_17(v)}" for k, v in value.items()) + "}"
    raise TypeError(type(value))


def request_size(data: dict[str, Any]) -> dict[str, int]:
    compact = json.dumps(data, ensure_ascii=False, allow_nan=False, separators=(",", ":"))
    text17 = _dump_17(data)
    assert json.loads(text17) == data  # 17 digits round-trip exactly
    return {"compact": len(compact.encode("utf-8")), "digits_17": len(text17.encode("utf-8"))}


def number_count(n_steps: int, n_stations: int) -> int:
    """Numbers (and booleans) in the lists of a response with frames, from the 2.0 shape."""
    plan = plan_frames(n_steps, n_stations)
    series = len(SERIES_KEYS) * (n_steps + 1)
    stations = (len(STATION_FLOAT_KEYS) + 1) * n_stations  # + x_is_node
    frames = plan.n_frames * n_stations + plan.n_frames + n_stations  # frame_head_m + time, x
    return series + stations + frames


def leaves(value: Any) -> list[Any]:
    """Every number and boolean of a JSON value (lists, scalars and inside ``checks``)."""
    if isinstance(value, dict):
        return [leaf for v in value.values() for leaf in leaves(v)]
    if isinstance(value, list):
        return [leaf for v in value for leaf in leaves(v)]
    return [value] if isinstance(value, (bool, int, float)) else []


def analytic_bound(out: dict[str, Any], max_steps: int = 10_000) -> dict[str, int]:
    """U-34 (3b): (largest admitted count of numbers) x 25 B + structure.

    The structure (keys, brackets, separators, strings, nulls) is measured on ``out``; the
    numbers are its scalar leaves plus the largest list count over every admitted station
    count (11 .. 699) with ``max_steps`` steps.
    """
    text = json.dumps(out, ensure_ascii=False, allow_nan=False, separators=(",", ":"))
    all_leaves = leaves(out)
    leaf_bytes = sum(len(json.dumps(v)) for v in all_leaves)
    structure = len(text.encode("utf-8")) - leaf_bytes
    list_count = number_count(out["n_steps"], len(out["x_m"]))
    scalars = len(all_leaves) - list_count
    max_lists = max(number_count(max_steps, n) for n in range(11, 700))
    numbers = max_lists + scalars
    return {"numbers": numbers, "structure_b": structure,
            "bound_b": numbers * MAX_NUMBER_B + structure}


def sweep(n_steps: int = 10_000, lo: int = 202, hi: int = 699) -> list[tuple[int, int]]:
    """(count, n_stations) for every station count, largest count first (U-34 (3))."""
    return sorted(((number_count(n_steps, n), n) for n in range(lo, hi + 1)), reverse=True)


def median_time(data: dict[str, Any], repeats: int = 5) -> float:
    solve(data)
    times = []
    for _ in range(repeats):
        start = time.perf_counter()
        solve(data)
        times.append(time.perf_counter() - start)
    return statistics.median(times)


# ----------------------------------------------------------------------------- report
def measure(top: int = 3, timing: bool = True) -> dict[str, Any]:
    report: dict[str, Any] = {
        "package_version": mpt.__version__,
        "schema_version": mpt.SCHEMA_VERSION,
        "package_file": mpt.__file__,
        "python": platform.python_version(),
        "limits_b": {"response": RESPONSE_LIMIT_B, "request": REQUEST_LIMIT_B},
    }

    recipe = worst_case_recipe()
    out = solve(recipe)
    report["recipe"] = {
        "n_stations": len(out["x_m"]),
        "n_steps": out["n_steps"],
        "n_frames": len(out["frame_time_s"]),
        "frame_stride": out["frame_stride"],
        "numbers": number_count(out["n_steps"], len(out["x_m"])),
        "response_b": response_sizes(out),
        "request_b": request_size(recipe),
    }
    if timing:
        report["recipe"]["median_time_s"] = median_time(recipe)

    candidates = []
    for count, n_stations in sweep()[:top]:
        data = case_with_stations(n_stations)
        res = solve(data)
        assert len(res["x_m"]) == n_stations, (len(res["x_m"]), n_stations)
        candidates.append({
            "n_stations": n_stations,
            "n_frames": len(res["frame_time_s"]),
            "frame_stride": res["frame_stride"],
            "numbers": count,
            "response_b": response_sizes(res),
        })
    report["sweep_top"] = candidates

    worst = max([report["recipe"], *candidates], key=lambda c: c["response_b"]["max"])
    adv_in = adversarial_recipe()
    adv = solve(adv_in)
    adv_sizes = response_sizes(adv)
    adv_leaves = len(leaves(adv))
    report["adversarial"] = {
        "n_stations": len(adv["x_m"]),
        "n_steps": adv["n_steps"],
        "n_frames": len(adv["frame_time_s"]),
        "frame_stride": adv["frame_stride"],
        "numbers": adv_leaves,
        "response_b": adv_sizes,
        "bytes_per_number": adv_sizes["max"] / adv_leaves,
        "request_b": request_size(adv_in),
        "fits": adv_sizes["max"] <= RESPONSE_LIMIT_B,
        "valid_recipe": adv_sizes["max"] / adv_leaves >= MIN_ADVERSARIAL_B_PER_NUMBER,
    }
    neg = solve(adversarial_negative_datum_recipe())
    neg_sizes = response_sizes(neg)
    neg_leaves = len(leaves(neg))
    report["adversarial_negative_datum"] = {
        "numbers": neg_leaves,
        "response_b": neg_sizes,
        "bytes_per_number": neg_sizes["max"] / neg_leaves,
    }
    bound = analytic_bound(adv)
    report["analytic"] = bound
    report["analytic_bound_b"] = bound["bound_b"]

    report["worst_response"] = {
        "source": "recipe" if worst is report["recipe"] else f"sweep n_stations={worst['n_stations']}",
        "bytes": worst["response_b"]["max"],
        "serialisation": max(
            ("json_dumps_compact", "pydantic_model_dump_json"),
            key=lambda k: worst["response_b"][k],
        ),
        "fits": worst["response_b"]["max"] <= RESPONSE_LIMIT_B,
    }
    report["worst_response_any"] = {
        "bytes": max(report["worst_response"]["bytes"], adv_sizes["max"]),
        "fits": report["worst_response"]["fits"] and report["adversarial"]["fits"],
    }
    req = report["recipe"]["request_b"]
    report["worst_request"] = {
        "bytes": max(req.values()),
        "fits": max(req.values()) <= REQUEST_LIMIT_B,
    }

    report["excel"] = {
        "with_frames_b": response_sizes(solve(excel_case(True))),
        "without_frames_b": response_sizes(solve(excel_case(False))),
        "request_b": request_size(excel_case(True)),
    }
    bare = {**recipe, "include_frames": False}
    report["recipe_without_frames_b"] = response_sizes(solve(bare))
    return report


def _print(report: dict[str, Any]) -> None:
    def b(n: int) -> str:
        return f"{n:,} B".replace(",", " ")

    r = report["recipe"]
    print(f"mainpipe_transient {report['package_version']} (schema {report['schema_version']}), "
          f"Python {report['python']}")
    print(f"  from {report['package_file']}")
    print(f"Recipe U-34 (3): {r['n_stations']} stations, {r['n_steps']} steps, "
          f"{r['n_frames']} frames (stride {r['frame_stride']}), {r['numbers']} numbers")
    for key, val in r["response_b"].items():
        print(f"  response {key:26s} {b(val)}")
    for key, val in r["request_b"].items():
        print(f"  request  {key:26s} {b(val)}")
    if "median_time_s" in r:
        print(f"  solve() median of 5            {r['median_time_s']:.3f} s")
    print("Sweep U-34 (3), top by number count:")
    for c in report["sweep_top"]:
        print(f"  {c['n_stations']} stations, {c['n_frames']} frames (stride {c['frame_stride']}), "
              f"{c['numbers']} numbers -> {b(c['response_b']['max'])}")
    w = report["worst_response"]
    print(f"Worst response: {b(w['bytes'])} ({w['serialisation']}, {w['source']}) "
          f"vs {b(report['limits_b']['response'])}: {'OK' if w['fits'] else 'EXCEEDS'}")
    a = report["adversarial"]
    print(f"Adversarial U-34 (3b): {a['n_stations']} stations, {a['n_steps']} steps, "
          f"{a['n_frames']} frames (stride {a['frame_stride']}), {a['numbers']} numbers")
    for key, val in a["response_b"].items():
        print(f"  response {key:26s} {b(val)}")
    print(f"  bytes per number               {a['bytes_per_number']:.2f} B "
          f"(>= {MIN_ADVERSARIAL_B_PER_NUMBER:.0f}: {'OK' if a['valid_recipe'] else 'NO'})")
    print(f"Adversarial response: {b(a['response_b']['max'])} vs "
          f"{b(report['limits_b']['response'])}: {'OK' if a['fits'] else 'EXCEEDS'}")
    g = report["adversarial_negative_datum"]
    print(f"Adversarial, negative datum (F5R-01): {b(g['response_b']['max'])}, "
          f"{g['bytes_per_number']:.2f} B per number")
    n = report["analytic"]
    print(f"Analytic bound U-34 (3b): {n['numbers']} numbers x {MAX_NUMBER_B} B + "
          f"{b(n['structure_b'])} structure = {b(n['bound_b'])}")
    q = report["worst_request"]
    print(f"Worst request:  {b(q['bytes'])} vs {b(report['limits_b']['request'])}: "
          f"{'OK' if q['fits'] else 'EXCEEDS'}")
    e = report["excel"]
    print(f"Excel case: with frames {b(e['with_frames_b']['max'])}, "
          f"without {b(e['without_frames_b']['max'])}, request {b(max(e['request_b'].values()))}")
    print(f"Recipe without frames: {b(report['recipe_without_frames_b']['max'])}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--json", action="store_true", help="print the report as JSON")
    parser.add_argument("--no-timing", action="store_true", help="skip the timing run")
    args = parser.parse_args(argv)
    report = measure(timing=not args.no_timing)
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        _print(report)
    ok = (report["worst_response_any"]["fits"] and report["worst_request"]["fits"]
          and report["adversarial"]["valid_recipe"])
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
