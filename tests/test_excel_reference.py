"""Phase 0: the frozen Excel reference is complete, traceable and reproduces V-05's control values.

Source: ``tests/reference/excel_case.json`` (U-28), produced once by
``tools/extract_excel_reference.py`` from ``doc/archive/2026-11-pre-hie/Transitorio_MOC_Animado.xlsx``.
"""

from __future__ import annotations

import hashlib
import math

import pytest

from conftest import ARCHIVED_XLSX

N_TIMES = 401
N_NODES = 21


def _is_number(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)


def test_source_sha256_matches_archived_workbook(excel_reference):
    digest = hashlib.sha256(ARCHIVED_XLSX.read_bytes()).hexdigest()
    assert excel_reference["provenance"]["source_sha256"] == digest


def test_provenance_block_is_complete(excel_reference):
    prov = excel_reference["provenance"]
    for key in (
        "generated_at_utc",
        "source_file",
        "source_sha256",
        "excel_version",
        "excel_build",
        "script",
        "script_git_blob",
        "repo_head_at_generation",
    ):
        assert prov.get(key), key
    assert prov["source_file"] == "doc/archive/2026-11-pre-hie/Transitorio_MOC_Animado.xlsx"
    assert prov["script"] == "tools/extract_excel_reference.py"


@pytest.mark.parametrize("field", ["head_m", "flow_m3s"])
def test_grid_is_401_by_21_without_nulls(excel_reference, field):
    rows = excel_reference["grid"][field]
    assert len(rows) == N_TIMES
    for k, row in enumerate(rows):
        assert len(row) == N_NODES, k
        assert all(_is_number(v) for v in row), k


def test_time_and_space_axes(excel_reference):
    grid = excel_reference["grid"]
    assert grid["k"] == list(range(N_TIMES))
    assert len(grid["time_s"]) == N_TIMES
    for k, t in enumerate(grid["time_s"]):
        assert t == pytest.approx(k * 0.05, abs=1e-12)
    assert grid["x_m"] == [50.0 * i for i in range(N_NODES)]
    assert len(grid["valve_law_flow_m3s"]) == N_TIMES
    assert all(_is_number(v) for v in grid["valve_law_flow_m3s"])


def test_inputs_are_the_excel_case(excel_reference):
    """The case the plan calls «Caso Excel» (plan 01 §6)."""
    assert excel_reference["inputs"] == {
        "length_m": 1000.0,
        "inner_diameter_m": 0.3,
        "wave_speed_ms": 1000.0,
        "darcy_friction_factor": 0.02,
        "initial_flow_m3s": 0.1,
        "reservoir_level_m": 100.0,
        "pipe_elevation_m": 0.0,
        "density_kgm3": 1000.0,
        "gravity_ms2": 9.81,
        "n_reaches": 20,
        "n_steps": 400,
        "pn_bar": 25.0,
        "min_allowed_pressure_head_m": -10.0,
        "closure_time_s": [0.0, 0.5, 1.0, 1.5, 2.0, 5.0, 10.0, 20.0],
        "closure_flow_m3s": [0.1, 0.05, 0.02, 0.0, 0.0, 0.0, 0.0, 0.0],
    }


def test_v05_control_values(excel_reference):
    """V-05 control values, printed in the plan with 5 decimals (so half a unit of the 5th)."""
    grid = excel_reference["grid"]
    head_valve = [row[-1] for row in grid["head_m"]]
    times = grid["time_s"]
    tol = 0.5e-5

    assert head_valve[0] == pytest.approx(93.19944, abs=tol)

    h_max = max(head_valve)
    assert h_max == pytest.approx(242.76384, abs=tol)
    assert times[head_valve.index(h_max)] == pytest.approx(2.00, abs=1e-12)

    h_min = min(head_valve)
    assert h_min == pytest.approx(-37.89904, abs=tol)
    assert times[head_valve.index(h_min)] == pytest.approx(4.00, abs=1e-12)

    # Pipe-wide extremes are the valve's (V-05).
    all_heads = [h for row in grid["head_m"] for h in row]
    assert max(all_heads) == h_max
    assert min(all_heads) == h_min


def test_validation_sheet_agrees_with_grid(excel_reference):
    """4_Validacion was recalculated together with the grid: its values are the grid's, exactly."""
    grid = excel_reference["grid"]
    val = {cell: entry["value"] for cell, entry in excel_reference["validation"].items()}
    head_valve = [row[-1] for row in grid["head_m"]]
    all_heads = [h for row in grid["head_m"] for h in row]

    assert val["C13"] == head_valve[0]
    assert val["C18"] == max(head_valve)
    assert val["C20"] == min(head_valve)
    assert val["C23"] == max(all_heads)
    assert val["C24"] == min(all_heads)
    assert val["C19"] == 2.0
    assert val["C21"] == 4.0
    assert val["C22"] == pytest.approx(val["C18"] - val["C13"], rel=1e-15)
    # Values V-11 cites (4_Validacion C11, C22, C27), to the digits printed in the plan.
    assert val["C11"] == pytest.approx(144.2111, abs=0.5e-4)
    assert val["C22"] == pytest.approx(149.56440, abs=0.5e-5)
    assert 100 * val["C27"] == pytest.approx(3.712, abs=0.5e-3)
