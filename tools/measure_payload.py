"""Measure request and response sizes of ``mainpipe_transient.solve`` (plan 01 V-18, U-34).

Protocol U-34 (doc/DECISIONS.md):

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
    """Numbers (and booleans) in a response with frames, from the contract shape."""
    plan = plan_frames(n_steps, n_stations)
    series = len(SERIES_KEYS) * (n_steps + 1)
    stations = (len(STATION_FLOAT_KEYS) + 1) * n_stations  # + x_is_node
    frames = 2 * plan.n_frames * n_stations + plan.n_frames + n_stations  # + time, x
    return series + stations + frames


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
    report["worst_response"] = {
        "source": "recipe" if worst is report["recipe"] else f"sweep n_stations={worst['n_stations']}",
        "bytes": worst["response_b"]["max"],
        "serialisation": max(
            ("json_dumps_compact", "pydantic_model_dump_json"),
            key=lambda k: worst["response_b"][k],
        ),
        "fits": worst["response_b"]["max"] <= RESPONSE_LIMIT_B,
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
    ok = report["worst_response"]["fits"] and report["worst_request"]["fits"]
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
