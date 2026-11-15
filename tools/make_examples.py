"""Generate ``portal/examples/*.json`` by running ``mainpipe_transient.solve`` (plan 01, phase 6).

Format: ``<portal>/doc/upstream-kit/templates/example.json`` (kit 04 §2), which reproduces the
portal snapshot (``backend/tests/golden_lib.py``, ``run_case``): on success ``expected`` is the
output of ``solve`` passed through JSON; on error ``expected`` is
``{"exception": <concrete class name>, "http_status": <int>}``, the case carries
``"expects_error": true`` and the message goes apart, in ``message`` (informative).

The examples are never written by hand: every ``expected`` comes from calling the package that
is importable when this script runs. In the delivery that is the package installed in a clean
venv from the commit to pin (kit 04 §3), so run it with that venv's interpreter::

    <clean-venv>/Scripts/python tools/make_examples.py --commit <sha>   # write
    <clean-venv>/Scripts/python tools/make_examples.py --check          # compare, write nothing

Without ``--commit`` the commit is ``git rev-parse HEAD`` and the script refuses to run if
``src/`` differs from it (the examples must come from committed code). The versions of Python,
numpy and pydantic used are recorded in every example (plan 01 §5, note on ``REL_TOL``).

This script is outside the package; it may touch the disk and print.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any

import numpy
import pydantic

import mainpipe_transient as mpt
from mainpipe_transient import MainpipeTransientError, solve

REPO = Path(__file__).resolve().parents[1]
EXAMPLES_DIR = REPO / "portal" / "examples"
VOLATILE_KEYS = ("generated_at",)  # ignored by --check

# ----------------------------------------------------------------------------- inputs
# «Caso Excel» (plan 01 §6, HU-1.1): Transitorio_MOC_Animado.xlsx, horizontal at z = 0.
EXCEL: dict[str, Any] = {
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


def excel(**changes: Any) -> dict[str, Any]:
    data = json.loads(json.dumps(EXCEL))
    data.update(changes)
    return data


def profile(x: list[float], z: list[float], **changes: Any) -> dict[str, Any]:
    data = excel(**changes)
    data.pop("length_m")
    data.pop("pipe_elevation_m")
    data.update(geometry="profile", profile_x_m=list(x), profile_z_m=list(z))
    return data


def frictionless(**changes: Any) -> dict[str, Any]:
    """HU-1.1 crit. 3: f = 0, closure in one step (0.05 s), horizontal at z = 0, T = 5 s."""
    base: dict[str, Any] = {
        "darcy_friction_factor": 0.0,
        "duration_s": 5.0,
        "closure_time_s": [0.0, 0.05],
        "closure_flow_lps": [100.0, 0.0],
    }
    base.update(changes)
    return excel(**base)


# (id, description, inputs). Only the first one carries the player series (D-57 (8)).
CASES: list[tuple[str, str, dict[str, Any]]] = [
    (
        "solve-excel-horizontal",
        "Camino feliz, geometría horizontal: el caso del Excel (Transitorio_MOC_Animado.xlsx). "
        "status error con COLUMN_SEPARATION_RISK y PN_NEAR_LIMIT. Único ejemplo con la serie "
        "del reproductor (include_frames: true, 401 fotogramas × 21 progresivas, sin "
        "submuestreo).",
        excel(include_frames=True),
    ),
    (
        "solve-perfil-loma",
        "Camino feliz, geometría profile: el caso del Excel con una loma de 40 m en "
        "x = 500 m (vértice en un nodo). La depresión en el punto alto es mayor que en "
        "horizontal; status error con COLUMN_SEPARATION_RISK y PN_NEAR_LIMIT.",
        profile([0.0, 500.0, 1000.0], [0.0, 40.0, 0.0]),
    ),
    (
        "solve-sin-friccion-ok",
        "status ok, sin checks: sin fricción, cierre en 0.05 s, depósito a 150 m y PN 40. "
        "La presión mínima (≈ 5.8 m.c.a.) queda por encima de 0 y la máxima por debajo del "
        "80 % del PN.",
        frictionless(reservoir_level_m=150.0, pn_bar=40.0),
    ),
    (
        "solve-subatmosferica-warning",
        "status warning con un único aviso SUBATMOSPHERIC_PRESSURE: sin fricción, depósito a "
        "136 m y PN 40. La presión mínima (≈ -8.2 m.c.a.) es negativa pero no baja del límite "
        "de -10 m.c.a.",
        frictionless(reservoir_level_m=136.0, pn_bar=40.0),
    ),
    (
        "solve-pn-superado",
        "status error con PN_EXCEEDED (el aviso que gobierna la línea del PN en la regla del "
        "rojo, D-63) y SUBATMOSPHERIC_PRESSURE: el caso anterior con PN 25.",
        frictionless(reservoir_level_m=136.0),
    ),
    (
        "solve-regimen-negativo",
        "Régimen con presión negativa: perfil con un punto alto de 110 m en x = 300 m (vértice "
        "fuera de nodo) por encima de la línea piezométrica de régimen. "
        "STEADY_NEGATIVE_PRESSURE con severidad error (régimen bajo el límite), junto con "
        "COLUMN_SEPARATION_RISK y PN_NEAR_LIMIT; errores primero.",
        profile([0.0, 300.0, 1000.0], [0.0, 110.0, 0.0]),
    ),
    (
        "error-ley-no-creciente",
        "422: los tiempos de la ley de cierre no son estrictamente crecientes (punto 3 igual "
        "al punto 2).",
        excel(closure_time_s=[0.0, 1.0, 1.0, 2.0], closure_flow_lps=[100.0, 50.0, 20.0, 0.0]),
    ),
    (
        "error-ley-sin-cierre",
        "422: la ley de cierre no termina en Q = 0 (cierre parcial, no admitido).",
        excel(closure_time_s=[0.0, 1.0, 2.0], closure_flow_lps=[100.0, 50.0, 10.0]),
    ),
    (
        "error-perfil-no-creciente",
        "422: la progresiva del perfil no es estrictamente creciente (punto 3 menor que el 2).",
        profile([0.0, 500.0, 400.0, 1000.0], [0.0, 10.0, 5.0, 0.0]),
    ),
    (
        "error-duracion-insuficiente",
        "422: duration_s menor que la duración mínima Tc + 2L/a (no cubre el cierre y su "
        "primera reflexión).",
        excel(duration_s=2.5),
    ),
    (
        "error-tope-de-pasos",
        "422: más pasos que MAX_STEPS = 10 000 (HU-1.6 crit. 13, D-57): caso del Excel con "
        "n_reaches = 200 y duration_s = 50.001 s; el mensaje da la duración máxima admisible "
        "(50 s) y la malla más gruesa que la admite.",
        excel(n_reaches=200, duration_s=50.001),
    ),
    (
        "error-campo-retirado-densidad",
        "422 de migración 1.0 → 2.0 (U-40): la petición trae density_kgm3, que ya no es un "
        "dato de entrada (ρ = 1000 kg/m³ fija). Mensaje propio en español.",
        excel(density_kgm3=1000.0),
    ),
]


# ----------------------------------------------------------------------------- build
def _git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=REPO, check=True, capture_output=True, text=True
    ).stdout.strip()


def resolve_commit(explicit: str | None) -> str:
    if explicit:
        return explicit
    dirty = _git("status", "--porcelain", "--", "src")
    if dirty:
        raise SystemExit(
            "src/ differs from HEAD; examples must come from committed code:\n" + dirty
        )
    return _git("rev-parse", "HEAD")


def build_case(case_id: str, description: str, inputs: dict[str, Any], *, commit: str,
               today: str) -> dict[str, Any]:
    record: dict[str, Any] = {
        "id": case_id,
        "description": description,
        "function": "solve",
        "package_version": mpt.__version__,
        "schema_version": mpt.SCHEMA_VERSION,
        "generated_at": today,
        "commit": commit,
        "generated_with": {
            "python": platform.python_version(),
            "numpy": numpy.__version__,
            "pydantic": pydantic.__version__,
        },
        "inputs": inputs,
    }
    try:
        output = solve(json.loads(json.dumps(inputs)))
    except MainpipeTransientError as exc:
        record["expects_error"] = True
        record["expected"] = {"exception": type(exc).__name__, "http_status": exc.http_status}
        record["message"] = str(exc)
        return record
    # «pasada por JSON», as golden_lib.run_case does.
    record["expected"] = json.loads(json.dumps(output, allow_nan=False))
    return record


def build_all(commit: str, today: str) -> dict[str, dict[str, Any]]:
    ids = [c[0] for c in CASES]
    assert len(ids) == len(set(ids)), "duplicate example id"
    return {cid: build_case(cid, desc, inp, commit=commit, today=today)
            for cid, desc, inp in CASES}


def _compact(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, allow_nan=False, separators=(", ", ": "))


def dump(record: dict[str, Any]) -> str:
    """One key per line down to the fields of ``inputs`` / ``expected``; values compact.

    Keeps the files readable and diffable without one line per number (``frame_head_m``).
    """
    lines = ["{"]
    items = list(record.items())
    for i, (key, value) in enumerate(items):
        sep = "," if i < len(items) - 1 else ""
        if isinstance(value, dict) and value and key in ("inputs", "expected", "generated_with"):
            lines.append(f"  {json.dumps(key)}: {{")
            sub = list(value.items())
            for j, (k2, v2) in enumerate(sub):
                sep2 = "," if j < len(sub) - 1 else ""
                lines.append(f"    {json.dumps(k2)}: {_compact(v2)}{sep2}")
            lines.append(f"  }}{sep}")
        else:
            lines.append(f"  {json.dumps(key)}: {_compact(value)}{sep}")
    lines.append("}")
    text = "\n".join(lines) + "\n"
    assert json.loads(text) == record
    return text


def _stable(record: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in record.items() if k not in VOLATILE_KEYS}


# ----------------------------------------------------------------------------- main
def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--commit", help="sha of the code installed (default: git HEAD, src/ clean)")
    parser.add_argument("--check", action="store_true",
                        help="regenerate in memory and compare with portal/examples/ "
                             "(ignoring generated_at); write nothing")
    parser.add_argument("--out", type=Path, default=EXAMPLES_DIR)
    args = parser.parse_args(argv)

    print(f"mainpipe_transient {mpt.__version__} (schema {mpt.SCHEMA_VERSION}) from "
          f"{mpt.__file__}")
    print(f"python {platform.python_version()}, numpy {numpy.__version__}, "
          f"pydantic {pydantic.__version__}")

    if args.check:
        on_disk = {p.stem: json.loads(p.read_text(encoding="utf-8"))
                   for p in sorted(args.out.glob("*.json"))}
        commits = {r.get("commit") for r in on_disk.values()}
        if len(commits) != 1:
            print(f"FAIL: examples carry several commits: {sorted(map(str, commits))}")
            return 1
        commit = args.commit or commits.pop()
        today = dt.date.today().isoformat()
        fresh = build_all(commit, today)
        problems = []
        for cid in sorted(set(on_disk) | set(fresh)):
            if cid not in on_disk:
                problems.append(f"{cid}: missing on disk")
            elif cid not in fresh:
                problems.append(f"{cid}: on disk but not generated by this script")
            elif _stable(on_disk[cid]) != _stable(fresh[cid]):
                problems.append(f"{cid}: differs")
        for p in problems:
            print("FAIL:", p)
        print(f"{len(fresh)} examples checked, {len(problems)} differences")
        return 1 if problems else 0

    commit = resolve_commit(args.commit)
    today = dt.date.today().isoformat()
    records = build_all(commit, today)
    args.out.mkdir(parents=True, exist_ok=True)
    stale = {p.stem for p in args.out.glob("*.json")} - set(records)
    for cid in sorted(stale):
        (args.out / f"{cid}.json").unlink()
        print(f"removed stale {cid}.json")
    for cid, record in records.items():
        path = args.out / f"{cid}.json"
        path.write_text(dump(record), encoding="utf-8", newline="\n")
        kind = (f"error {record['expected']['exception']} {record['expected']['http_status']}"
                if record.get("expects_error") else f"status {record['expected']['status']}")
        print(f"{path.name:40s} {kind:45s} {path.stat().st_size:>9,d} B")
    print(f"{len(records)} examples written to {args.out} (commit {commit})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
