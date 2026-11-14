"""Generate ``tests/reference/excel_case.json`` from the archived Excel workbook (plan 01, U-28).

The archived ``.xlsx`` holds formulas but no cached results (``openpyxl`` with
``data_only=True`` returns ``None`` for every formula cell). This script copies the
workbook to a temporary directory, opens the **copy** in Microsoft Excel through COM,
forces a full recalculation, and dumps:

* the inputs and derived parameters of sheet ``1_Datos``;
* H (m) and Q (m3/s) at the 21 nodes for the 401 time steps of sheet ``2_Malla_MOC``;
* every value of sheet ``4_Validacion``;
* a provenance block (date, Excel version, SHA-256 of the archived workbook,
  git blob of this script, repository HEAD).

It is meant to run **once**; the JSON is versioned and the test suite only reads it,
so neither Excel, Windows nor ``pywin32`` are needed to run the tests.

Requirements (development only, never imported from ``src/`` or ``tests/``):
Windows, Microsoft Excel, ``pywin32``.

Usage::

    python tools/extract_excel_reference.py
"""

from __future__ import annotations

import datetime as _dt
import hashlib
import json
import math
import platform
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SOURCE = REPO / "doc" / "archive" / "2026-11-pre-hie" / "Transitorio_MOC_Animado.xlsx"
TARGET = REPO / "tests" / "reference" / "excel_case.json"

N_NODES = 21
N_TIMES = 401
GRID_FIRST_ROW = 12
GRID_LAST_ROW = GRID_FIRST_ROW + N_TIMES - 1  # 412

# 1_Datos: (json key, cell, unit)
INPUT_CELLS = [
    ("length_m", "C6", "m"),
    ("inner_diameter_m", "C7", "m"),
    ("wave_speed_ms", "C8", "m/s"),
    ("darcy_friction_factor", "C9", "-"),
    ("initial_flow_m3s", "C10", "m3/s"),
    ("reservoir_level_m", "C11", "m"),
    ("pipe_elevation_m", "C12", "m"),
    ("density_kgm3", "C13", "kg/m3"),
    ("gravity_ms2", "C14", "m/s2"),
    ("n_reaches", "C18", "-"),
    ("n_steps", "C19", "-"),
    ("pn_bar", "C33", "bar"),
    ("min_allowed_pressure_head_m", "C34", "m"),
]
DERIVED_CELLS = [
    ("dx_m", "C20", "m"),
    ("dt_s", "C21", "s"),
    ("duration_s", "C22", "s"),
    ("area_m2", "C23", "m2"),
    ("velocity_initial_ms", "C24", "m/s"),
    ("wave_constant_s_m2", "C25", "s/m2"),
    ("friction_constant_s2_m5", "C26", "s2/m5"),
    ("head_loss_m", "C27", "m"),
    ("reflection_time_s", "C28", "s"),
    ("wave_period_s", "C29", "s"),
]
INTEGER_KEYS = {"n_reaches", "n_steps"}
CLOSURE_RANGE = "C38:D45"  # t (s), Q (m3/s)
VALIDATION_ROWS = list(range(6, 15)) + list(range(18, 25)) + [27, 28] + list(range(33, 38))


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def git(*args: str) -> str:
    out = subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True, check=True)
    return out.stdout.strip()


def as_float(value: object, where: str) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise RuntimeError(f"{where}: expected a number, got {value!r}")
    x = float(value)
    if not math.isfinite(x):
        raise RuntimeError(f"{where}: non-finite value {x!r}")
    return x


def read_block(ws, address: str) -> list[list[object]]:
    value = ws.Range(address).Value
    return [list(row) for row in value]


def extract(workbook_path: Path) -> dict:
    import pywintypes  # noqa: F401  (fails early with a clear error if pywin32 is missing)
    import win32com.client

    excel = win32com.client.DispatchEx("Excel.Application")
    excel.Visible = False
    excel.DisplayAlerts = False
    excel.EnableEvents = False
    try:
        wb = excel.Workbooks.Open(str(workbook_path), UpdateLinks=0, ReadOnly=True)
        try:
            excel.CalculateFull()
            datos = wb.Worksheets("1_Datos")
            malla = wb.Worksheets("2_Malla_MOC")
            valid = wb.Worksheets("4_Validacion")

            inputs: dict[str, object] = {}
            units: dict[str, str] = {}
            for key, cell, unit in INPUT_CELLS:
                x = as_float(datos.Range(cell).Value, f"1_Datos!{cell}")
                inputs[key] = int(x) if key in INTEGER_KEYS else x
                units[key] = unit
            closure = read_block(datos, CLOSURE_RANGE)
            inputs["closure_time_s"] = [as_float(r[0], "1_Datos!C38:C45") for r in closure]
            inputs["closure_flow_m3s"] = [as_float(r[1], "1_Datos!D38:D45") for r in closure]
            units["closure_time_s"] = "s"
            units["closure_flow_m3s"] = "m3/s"

            derived: dict[str, float] = {}
            for key, cell, unit in DERIVED_CELLS:
                derived[key] = as_float(datos.Range(cell).Value, f"1_Datos!{cell}")
                units[key] = unit

            rows = f"{GRID_FIRST_ROW}:{GRID_LAST_ROW}"
            k_col = read_block(malla, f"A{GRID_FIRST_ROW}:A{GRID_LAST_ROW}")
            t_col = read_block(malla, f"B{GRID_FIRST_ROW}:B{GRID_LAST_ROW}")
            law_col = read_block(malla, f"C{GRID_FIRST_ROW}:C{GRID_LAST_ROW}")
            x_row = read_block(malla, "E10:Y10")[0]
            head = read_block(malla, f"E{GRID_FIRST_ROW}:Y{GRID_LAST_ROW}")
            flow = read_block(malla, f"AA{GRID_FIRST_ROW}:AU{GRID_LAST_ROW}")

            grid = {
                "k": [int(as_float(r[0], f"2_Malla_MOC!A{rows}")) for r in k_col],
                "time_s": [as_float(r[0], f"2_Malla_MOC!B{rows}") for r in t_col],
                "x_m": [as_float(v, "2_Malla_MOC!E10:Y10") for v in x_row],
                "valve_law_flow_m3s": [as_float(r[0], f"2_Malla_MOC!C{rows}") for r in law_col],
                "head_m": [
                    [as_float(v, f"2_Malla_MOC!E:Y row {GRID_FIRST_ROW + i}") for v in row]
                    for i, row in enumerate(head)
                ],
                "flow_m3s": [
                    [as_float(v, f"2_Malla_MOC!AA:AU row {GRID_FIRST_ROW + i}") for v in row]
                    for i, row in enumerate(flow)
                ],
            }
            units.update(
                {"time_s": "s", "x_m": "m", "valve_law_flow_m3s": "m3/s",
                 "head_m": "m", "flow_m3s": "m3/s"}
            )

            validation: dict[str, dict[str, object]] = {}
            for r in VALIDATION_ROWS:
                label = valid.Range(f"B{r}").Value
                value = valid.Range(f"C{r}").Value
                unit = valid.Range(f"D{r}").Value
                if isinstance(value, (int, float)) and not isinstance(value, bool):
                    value = as_float(value, f"4_Validacion!C{r}")
                validation[f"C{r}"] = {"label": label, "unit": unit, "value": value}

            excel_info = {"version": str(excel.Version), "build": str(excel.Build)}
        finally:
            wb.Close(SaveChanges=False)
    finally:
        excel.Quit()

    return {
        "excel": excel_info,
        "inputs": inputs,
        "derived": derived,
        "grid": grid,
        "validation": validation,
        "units": units,
    }


def check_shape(grid: dict) -> None:
    assert len(grid["k"]) == N_TIMES and grid["k"] == list(range(N_TIMES)), "k column"
    assert len(grid["time_s"]) == N_TIMES, "time column"
    assert len(grid["x_m"]) == N_NODES, "x row"
    for name in ("head_m", "flow_m3s"):
        assert len(grid[name]) == N_TIMES, name
        assert all(len(row) == N_NODES for row in grid[name]), name


def dumps(obj: object, indent: int = 0) -> str:
    """JSON with nested containers indented and flat number lists kept on one line."""
    pad, inner = " " * indent, " " * (indent + 2)
    if isinstance(obj, dict):
        if not obj:
            return "{}"
        items = [f"{inner}{json.dumps(k, ensure_ascii=False)}: {dumps(v, indent + 2)}"
                 for k, v in obj.items()]
        return "{\n" + ",\n".join(items) + "\n" + pad + "}"
    if isinstance(obj, list) and any(isinstance(v, (list, dict)) for v in obj):
        items = [inner + dumps(v, indent + 2) for v in obj]
        return "[\n" + ",\n".join(items) + "\n" + pad + "]"
    return json.dumps(obj, ensure_ascii=False, allow_nan=False)


def main() -> int:
    if sys.platform != "win32":
        print("This tool needs Windows with Microsoft Excel (COM).", file=sys.stderr)
        return 2
    source_sha = sha256_of(SOURCE)
    script_rel = Path(__file__).resolve().relative_to(REPO).as_posix()

    with tempfile.TemporaryDirectory(prefix="mpt_excel_") as tmp:
        copy = Path(tmp) / SOURCE.name
        shutil.copy2(SOURCE, copy)
        data = extract(copy)

    if sha256_of(SOURCE) != source_sha:
        raise RuntimeError("The archived workbook changed during extraction; aborting.")
    check_shape(data["grid"])

    pywin32_version = None
    try:
        from importlib.metadata import version

        pywin32_version = version("pywin32")
    except Exception:  # pragma: no cover - informative only
        pass

    out = {
        "provenance": {
            "description": (
                "Excel reference for plan 01 (U-28): workbook recalculated once in "
                "Microsoft Excel through COM on a temporary copy; the archived original "
                "was not modified."
            ),
            "generated_at_utc": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
            "source_file": SOURCE.relative_to(REPO).as_posix(),
            "source_sha256": source_sha,
            "excel_version": data["excel"]["version"],
            "excel_build": data["excel"]["build"],
            "recalculation": "Application.CalculateFull()",
            "script": script_rel,
            "script_git_blob": git("hash-object", script_rel),
            "repo_head_at_generation": git("rev-parse", "HEAD"),
            "python": platform.python_version(),
            "pywin32": pywin32_version,
            "cells": {
                "inputs": "1_Datos!C6:C34, closure law 1_Datos!C38:D45",
                "head_m": f"2_Malla_MOC!E{GRID_FIRST_ROW}:Y{GRID_LAST_ROW}",
                "flow_m3s": f"2_Malla_MOC!AA{GRID_FIRST_ROW}:AU{GRID_LAST_ROW}",
                "validation": "4_Validacion!B:D",
            },
        },
        "units": data["units"],
        "inputs": data["inputs"],
        "derived": data["derived"],
        "grid": data["grid"],
        "validation": data["validation"],
    }
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(dumps(out) + "\n", encoding="utf-8", newline="\n")
    print(f"Wrote {TARGET.relative_to(REPO).as_posix()} "
          f"({len(out['grid']['k'])} steps x {len(out['grid']['x_m'])} nodes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
