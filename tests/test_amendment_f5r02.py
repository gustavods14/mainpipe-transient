"""Phase 7: amendment F5R-02 — PN range and non-representable results (plan 01 §5 phase 7).

Covers U-43 (``pn_bar`` in [1, 100] bar, both included, with its two messages), U-44 (a
result that ``float64`` cannot represent is a 422, not a 500), V-12 (range part), V-20 and
HU-1.6 crits. 7 and 14 (a-d). With an admitted PN the response is bit for bit the one of
v0.1.0: the 12 examples of ``portal/examples/`` are reproduced exactly, without regenerating
them. ``SCHEMA_VERSION`` stays "2.0" (U-45).

The four inputs of V-20 (b) were checked against v0.1.0 (``a04431e``) before the guard was
written: all four gave ``MainpipeTransientComputationError`` (500). Note for V-20 (b): with
the default f = 0.02 a V0 > 1.3e154 m/s is rejected earlier by the friction-number rule
(phi <= 0.5, U-03), so the V0^2 overflow case uses f = 1e-200 (still f > 0, as V-20 asks);
it is the same input type, not a substitute.
"""

from __future__ import annotations

import dataclasses
import importlib.util
import json
import logging
import math
import warnings
from pathlib import Path

import numpy as np
import pydantic
import pytest

import mainpipe_transient as mpt
from conftest import REPO
from mainpipe_transient import (
    MainpipeTransientComputationError,
    MainpipeTransientError,
    MainpipeTransientValidationError,
    SolveRequest,
    solve,
)
from mainpipe_transient import _solve

EXCEL = {
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
    "include_frames": True,
}

HINT = "El timbraje (PN) debe estar entre 1 y 100 bar."
UNREPRESENTABLE = (
    "El resultado del cálculo queda fuera del rango numérico representable: revisa las "
    "magnitudes extremas del nivel del depósito (reservoir_level_m), de las cotas "
    "(pipe_elevation_m o profile_z_m), de la longitud, del diámetro y del caudal inicial. "
    "Con valores de proyecto no se llega a este límite."
)


def case(**changes) -> dict:
    data = json.loads(json.dumps(EXCEL))
    data.update(changes)
    return data


def above(v_text: str) -> str:
    return f"pn_bar = {v_text} bar está fuera de rango: supera el máximo de 100 bar. {HINT}"


def below(v_text: str) -> str:
    return f"pn_bar = {v_text} bar está fuera de rango: es menor que el mínimo de 1 bar. {HINT}"


def _measure_payload():
    spec = importlib.util.spec_from_file_location(
        "measure_payload", REPO / "tools" / "measure_payload.py"
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


# --------------------------------------------------------------------------- V-12: range (U-43)
@pytest.mark.parametrize("pn", [1.0, 100.0])
def test_v12_limits_are_admitted(pn):
    """HU-1.6 crit. 14 a: both limits compute; M18 at rel. 1e-12."""
    out = solve(case(pn_bar=pn))
    assert out["pn_head_m"] == pytest.approx(pn * 1e5 / (1000.0 * 9.81), rel=1e-12)
    if pn == 100.0:
        assert out["pn_head_m"] == pytest.approx(1019.37, abs=0.01)


# (value, literal message). {v} is the U-26 echo (10 significant digits).
REJECTED = [
    (100.5, above("100.5")),
    (1e304, above("1e+304")),
    (0.5, below("0.5")),
    (5e-324, below("4.940656458e-324")),
    (1e-320, below("9.999888672e-321")),
    (1e-300, below("1e-300")),
    (0.0, below("0")),
    (-1.0, below("-1")),
    # U-43 (2): when the echo reads as the limit, repr(v) is written instead.
    (100.00000000001, above("100.00000000001")),
    (0.99999999999, below("0.99999999999")),
]


@pytest.mark.parametrize(("pn", "message"), REJECTED)
def test_v12_out_of_range_is_422_with_the_literal_message(pn, message):
    """HU-1.6 crits. 7, 14 b and 14 c: 422, names pn_bar, value and limit in bar."""
    with pytest.raises(MainpipeTransientValidationError) as info:
        solve(case(pn_bar=pn))
    assert info.value.http_status == 422
    assert str(info.value) == message


@pytest.mark.parametrize(("pn", "message"), REJECTED)
def test_v12_same_text_through_the_model_fastapi_validates(pn, message):
    """kit 02 §3: FastAPI validates SolveRequest first; our text travels in its 422."""
    with pytest.raises(pydantic.ValidationError) as info:
        SolveRequest.model_validate(case(pn_bar=pn))
    errors = info.value.errors(include_url=False)
    assert [e["loc"] for e in errors] == [("pn_bar",)]
    assert errors[0]["msg"] == f"Value error, {message}"


@pytest.mark.parametrize("pn", [100.00000000001, 0.99999999999])
def test_v12_never_says_the_limit_exceeds_itself(pn):
    with pytest.raises(MainpipeTransientValidationError) as info:
        solve(case(pn_bar=pn))
    text = str(info.value)
    assert "= 100 bar supera" not in text and "= 1 bar es menor" not in text


def test_v12_field_description_and_schema_version():
    assert SolveRequest.model_fields["pn_bar"].description == (
        "Pipe pressure rating PN (bar). 1 <= PN <= 100."
    )
    assert mpt.SCHEMA_VERSION == "2.0"  # U-45 (1)


# --------------------------------------------------------------------------- V-20 (a): admitted PN
def _recipes() -> dict[str, dict]:
    mp = _measure_payload()
    return {
        "excel": case(),
        "realistic": mp.worst_case_recipe(),
        "adversarial": mp.adversarial_recipe(),
        "adversarial_negative_datum": mp.adversarial_negative_datum_recipe(),
    }


RECIPES = _recipes()


@pytest.mark.parametrize("pn", [1.0, 100.0])
@pytest.mark.parametrize("name", sorted(RECIPES))
def test_v20a_admitted_pn_never_500_and_finite(name, pn):
    """HU-1.6 crit. 14 d; V-20 (a) and (c): no exception, PN head and ratio finite."""
    data = dict(RECIPES[name], pn_bar=pn)
    out = solve(data)
    assert math.isfinite(out["pn_head_m"])
    assert math.isfinite(out["pressure_max_pn_ratio_pct"])


# --------------------------------------------------------------------------- V-20 (b): 500 -> 422
OVERFLOW_CASES = {
    # PN at its minimum and H_dep = 1e308: the PN ratio overflows (U-44, [razonado]).
    "pn_ratio_overflow": (case(pn_bar=1.0, reservoir_level_m=1e308), None),
    # Elevations of opposite sign ~1e308: H - z = +/-inf.
    "opposite_elevations": (
        case(reservoir_level_m=1e308, pipe_elevation_m=-1e308),
        None,
    ),
    # V0 ~ 1.4e156 m/s > 1.3e154 with f > 0: V0**2 raises OverflowError.
    "v0_squared_overflow": (
        case(
            darcy_friction_factor=1e-200,
            initial_flow_lps=1e158,
            closure_flow_lps=[1e158, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        ),
        OverflowError,
    ),
    # Q0 underflows to 0 in m3/s: Joukowsky = 0 and the deviation divides by zero.
    "q0_underflow": (
        case(
            initial_flow_lps=5e-324,
            closure_flow_lps=[5e-324, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        ),
        ZeroDivisionError,
    ),
}


# F7-01 (phase 7 verification): L*j/N overflows, some chainages are inf and the envelopes NaN.
# With any admitted PN this gave a 500 (ValueError in the global-extreme search) in v0.1.0 and
# in the first phase-7 commit, because the inf search ran after the extremes.
for _pn in (1.0, 25.0, 100.0):
    OVERFLOW_CASES[f"chainage_overflow_pn{_pn:g}"] = (
        case(darcy_friction_factor=0.0, length_m=1e307, duration_s=None, pn_bar=_pn),
        None,
    )
OVERFLOW_CASES["chainage_overflow_n200"] = (
    case(darcy_friction_factor=0.0, length_m=1e306, n_reaches=200, duration_s=None),
    None,
)
OVERFLOW_CASES["chainage_overflow_profile"] = (
    {
        **{k: v for k, v in case(darcy_friction_factor=0.0, duration_s=None).items()
           if k not in ("length_m", "pipe_elevation_m")},
        "geometry": "profile",
        "profile_x_m": [0.0, 5e306, 1e307],
        "profile_z_m": [0.0, -5.0, 0.0],
    },
    None,
)


# F7R-01 (phase 7 re-verification): tiny a and huge D make B = a/(g*A) underflow to 0; the
# MOC divided by it with numpy and got NaN without any inf, a 500 in v0.1.0 and 6720689.
# U-44 (1): a value that underflows to 0 and is divided by is a 422 (FloatingPointError).
_Q = 1e143
_TINY_B = dict(
    darcy_friction_factor=0.0,
    wave_speed_ms=1e-190,
    inner_diameter_mm=1e73,
    initial_flow_lps=_Q,
    closure_flow_lps=[_Q, _Q / 2, _Q / 5, 0.0, 0.0, 0.0, 0.0, 0.0],
    duration_s=None,
)
for _pn in (1.0, 25.0, 100.0):
    OVERFLOW_CASES[f"wave_constant_underflow_pn{_pn:g}"] = (
        case(**_TINY_B, pn_bar=_pn),
        FloatingPointError,
    )
OVERFLOW_CASES["wave_constant_underflow_no_frames_f1e-200"] = (
    case(**{**_TINY_B, "darcy_friction_factor": 1e-200}, include_frames=False),
    FloatingPointError,
)
OVERFLOW_CASES["wave_constant_underflow_profile"] = (
    {
        **{k: v for k, v in case(**_TINY_B).items() if k not in ("length_m", "pipe_elevation_m")},
        "geometry": "profile",
        "profile_x_m": [0.0, 400.0, 1000.0],
        "profile_z_m": [0.0, 10.0, 0.0],
    },
    FloatingPointError,
)


@pytest.mark.parametrize("name", sorted(OVERFLOW_CASES))
def test_v20b_non_representable_result_is_422(name):
    data, cause = OVERFLOW_CASES[name]
    SolveRequest.model_validate(data)  # admitted by the model: the 422 comes from the guard
    with pytest.raises(MainpipeTransientValidationError) as info:
        solve(data)
    assert info.value.http_status == 422
    assert str(info.value) == UNREPRESENTABLE
    if cause is None:
        assert info.value.__cause__ is None
    else:
        assert isinstance(info.value.__cause__, cause)


@pytest.mark.parametrize("name", sorted(OVERFLOW_CASES))
def test_v20b_422_does_not_depend_on_the_caller_warning_filters(name):
    """F7-02: with warnings turned into errors the answer is still the 422, and no numpy
    RuntimeWarning leaks to the caller in the default mode."""
    data, _ = OVERFLOW_CASES[name]
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        with pytest.raises(MainpipeTransientValidationError) as info:
            solve(data)
    assert str(info.value) == UNREPRESENTABLE
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        with pytest.raises(MainpipeTransientValidationError):
            solve(data)
    assert caught == []


def test_v20b_floating_point_error_is_also_422(monkeypatch):
    """U-44 (1): every ArithmeticError of the computation, FloatingPointError included."""

    def boom(**_):
        raise FloatingPointError("overflow")

    monkeypatch.setattr(_solve, "theory", boom)
    with pytest.raises(MainpipeTransientValidationError) as info:
        solve(case())
    assert str(info.value) == UNREPRESENTABLE
    assert isinstance(info.value.__cause__, FloatingPointError)


def _patch_simulate(monkeypatch, mutate):
    original = _solve.simulate

    def patched(*args, **kwargs):
        res = original(*args, **kwargs)
        mutate(res)
        return res

    monkeypatch.setattr(_solve, "simulate", patched)


def _set(attr: str, value: float, index=3):
    def mutate(res):
        getattr(res, attr)[index] = value

    return mutate


@pytest.mark.parametrize(
    "mutate",
    [
        _set("time_s", math.inf),
        _set("flow_valve_m3s", -math.inf),
        _set("head_initial_m", math.inf),
        _set("head_min_m", -math.inf),
        _set("frame_head_m", math.inf, index=(1, 2)),
    ],
    ids=["time_s", "flow_valve", "head_initial", "head_min", "frame_head"],
)
def test_v20b_guard_covers_every_output_list(monkeypatch, mutate):
    """U-44 (1)-(2): +/-inf in any series, envelope or frame, before rounding -> 422."""
    _patch_simulate(monkeypatch, mutate)
    with pytest.raises(MainpipeTransientValidationError) as info:
        solve(case())
    assert str(info.value) == UNREPRESENTABLE


def test_v20b_guard_covers_scalars(monkeypatch):
    original = _solve.theory
    monkeypatch.setattr(
        _solve,
        "theory",
        lambda **kw: dataclasses.replace(original(**kw), michaud_head_rise_m=math.inf),
    )
    with pytest.raises(MainpipeTransientValidationError) as info:
        solve(case())
    assert str(info.value) == UNREPRESENTABLE


def test_v20b_guard_runs_before_rounding():
    """U-44 (2): the search uses full-precision values (rounding would keep inf anyway)."""
    _solve._ensure_representable([1.0, None], [np.array([1.0, 2.0])])
    with pytest.raises(MainpipeTransientValidationError):
        _solve._ensure_representable([1.0], [np.array([[0.0, -math.inf]])])
    with pytest.raises(MainpipeTransientValidationError):
        _solve._ensure_representable([math.inf], [])


# --------------------------------------------------------------------------- V-20 (d): NaN stays 500
@pytest.mark.parametrize("where", ["scalar", "series"])
def test_v20d_nan_without_overflow_is_still_500(monkeypatch, caplog, where):
    """U-44 (3), HU-1.6 crit. 11: a NaN with no inf is a package failure, not the input."""
    if where == "scalar":
        original = _solve.theory
        monkeypatch.setattr(
            _solve,
            "theory",
            lambda **kw: dataclasses.replace(original(**kw), theory_deviation_pct=math.nan),
        )
    else:
        _patch_simulate(monkeypatch, _set("head_valve_m", math.nan))
    caplog.set_level(logging.CRITICAL, logger="mainpipe_transient")
    with pytest.raises(MainpipeTransientComputationError) as info:
        solve(case())
    assert info.value.http_status == 500
    assert not isinstance(info.value, MainpipeTransientValidationError)


# --------------------------------------------------------------------------- examples unchanged
# The 12 examples delivered with v0.1.0 (a04431e), by name: phase 8 adds three more (F7-03).
V010_EXAMPLES = (
    "error-campo-retirado-densidad",
    "error-duracion-insuficiente",
    "error-ley-no-creciente",
    "error-ley-sin-cierre",
    "error-perfil-no-creciente",
    "error-tope-de-pasos",
    "solve-excel-horizontal",
    "solve-perfil-loma",
    "solve-pn-superado",
    "solve-regimen-negativo",
    "solve-sin-friccion-ok",
    "solve-subatmosferica-warning",
)
EXAMPLES_DIR = Path(REPO) / "portal" / "examples"
EXAMPLES = {
    cid: json.loads((EXAMPLES_DIR / f"{cid}.json").read_text(encoding="utf-8"))
    for cid in V010_EXAMPLES
    if (EXAMPLES_DIR / f"{cid}.json").exists()
}


def test_the_twelve_examples_of_v010_are_all_here():
    assert sorted(EXAMPLES) == sorted(V010_EXAMPLES)


@pytest.mark.parametrize("cid", sorted(EXAMPLES))
def test_examples_are_reproduced_exactly_without_regenerating(cid):
    """Phase 7 'done': with an admitted PN, solve() equals each expected bit for bit."""
    ex = EXAMPLES[cid]
    inputs = json.loads(json.dumps(ex["inputs"]))
    if ex.get("expects_error"):
        with pytest.raises(MainpipeTransientError) as info:
            solve(inputs)
        got = {"exception": type(info.value).__name__, "http_status": info.value.http_status}
        assert got == ex["expected"]
        assert str(info.value) == ex["message"]
    else:
        assert json.loads(json.dumps(solve(inputs))) == ex["expected"]
