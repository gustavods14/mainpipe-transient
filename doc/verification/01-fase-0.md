# Verificación — Fase 0 (andamiaje y referencia del Excel)

| | |
|---|---|
| Fase | 0 — Andamiaje y referencia (plan 01 §5) |
| Commit verificado | `905e53a31a83f5a625048c048f15a2c6c55aa3f0` (rama `hie/etapas-0-3`, sin empujar: 1 commit por delante de `origin`) |
| Plan | `doc/plans/01-golpe-ariete-v1.md`, estado **congelado** (G4, 2026-11-14) |
| Kit | `KIT_VERSION = 3.0.0` (portal `C:\Dev\web_apps`); `portal/HANDOFF.md` dice 3.0.0: coinciden |
| Verificador | `hie-verifier`, 2026-11-14 |
| Kit leído | `README.md`, `01` (entero, foco §2–6 y §9), `02`, `04` §2–3; `07` §1 para cotas |

## Criterio de «hecho» de la fase (literal del plan) y resultado

| # | Criterio | Resultado | Evidencia |
|---|---|---|---|
| C1 | `pip install .` en un venv limpio de Python 3.12 funciona | cumple | `[medido]` `git archive 905e53a` → directorio temporal; `python3.12 -m venv`; `pip install ./src905` → `Successfully installed … mainpipe-transient-0.1.0 numpy-2.5.4 pydantic-2.14.3 …`. El `RECORD` instalado contiene `__init__.py`, `_solve.py`, `exceptions.py`, `py.typed`. `Requires-Python: >=3.12`, `Requires-Dist: numpy>=1.24`, `pydantic>=2.6` (admiten las del portal: numpy 2.5.4, pydantic 2.13.4, `backend/requirements.txt`) |
| C2 | `import mainpipe_transient` sin efectos | cumple | `[medido]` `test_import_has_no_side_effects` en verde desde el venv limpio (subproceso en directorio vacío: sin stdout/stderr, sin archivos creados, sin `win32com`/`pywintypes`/`openpyxl` en `sys.modules`). `[leído]` `src/` no usa `os.environ`, `open`, red, `global` ni `print` (grep sin coincidencias); lo único que lee es `importlib.metadata.version`, que el kit exige (`kit 01 §3`) |
| C3 | El JSON tiene 401 instantes × 21 nodos de H y Q sin ningún `null` | cumple | `[medido]` tests `test_grid_is_401_by_21_without_nulls[head_m|flow_m3s]` en verde; además mi transcripción independiente recorre las 2 × 401 × 21 celdas con aritmética (fallaría con un `None`) |
| C4 | Su SHA-256 de origen coincide con el `.xlsx` archivado | cumple | `[medido]` `sha256sum doc/archive/2026-11-pre-hie/Transitorio_MOC_Animado.xlsx` → `1e18cc0c…b3b1b8` = `provenance.source_sha256`. `git log` del `.xlsx`: solo `7ce6c30` lo toca (el original no se modificó) |
| C5 | Reproduce los valores de control de V-05 (H_v máx = 242.76384 m en t = 2.00 s) | cumple | `[medido]` H_v(0) = 93.19943562, H_v máx = 242.76384038 en k = 40 (t = 2.00 s), H_v mín = −37.89904017 en k = 80 (t = 4.00 s); máximo y mínimo de toda la tubería = los de la válvula (test `test_v05_control_values`) |
| C6 | La suite corre sin Excel ni pywin32 instalados | cumple (ver «no comprobado») | `[medido]` en el venv limpio `find_spec` de `win32com`, `pywintypes`, `openpyxl` → `[]`; `python -m pytest -v` → **17 passed in 0.45s**, con `mainpipe_transient.__file__` en `venv312\Lib\site-packages\` (paquete instalado, no el árbol de trabajo) |

Contenido de la fase también comprobado: `pyproject.toml` con layout `src/`, `requires-python >=3.12`,
`numpy>=1.24`, `pydantic>=2.6` `[leído]`; `py.typed` empaquetado `[medido]`; `CHANGELOG.md`
presente `[leído]`; excepciones y `solve` provisional `[medido]` (tests en verde) y `[leído]`.

## Comprobaciones independientes de la referencia (más allá de la suite)

1. **Re-extracción con Excel** `[medido]`. Ejecuté `tools/extract_excel_reference.py` del commit
   (Excel 16.0 por COM, pywin32 312 del `.venv` del repo) redirigiendo la salida a un archivo
   temporal fuera del repo (`sys.dont_write_bytecode`, `TARGET` sustituido). Comparación con
   `tests/reference/excel_case.json`: `units`, `inputs`, `derived`, `grid` y `validation`
   **idénticos** (igualdad exacta de `float`); solo difieren `generated_at_utc` y
   `repo_head_at_generation`, como se espera. `git status` del repo sin cambios tras la ejecución.
   El JSON versionado salió de Excel, no se editó a mano.
2. **Transcripción independiente de M1–M12** `[medido]` (script propio en el directorio temporal,
   Python puro, escrito desde la tabla §4 del plan, no desde el código del repo):
   - Derivados contra las fórmulas: A, V₀, B = a/(gA), h_f, Δx, Δt, 2L/a, 4L/a con error relativo 0;
     R = fΔx/(2gDA²) con 2·10⁻¹⁶.
   - V-01: V₀ = 1.414711 m/s, h_f = 6.800564 m, H(500) = 96.599718 m (plan: 96.60 ± 0.01).
   - Malla completa 401 × 21: máx |H_mía − H_json| = **4.5·10⁻¹³ m**, máx |Q_mía − Q_json| =
     **3.4·10⁻¹³ L/s**, ley de cierre (M10/M11, evaluada en t_{k+1}) idéntica a
     `valve_law_flow_m3s` (error 0). Confirma la afirmación del riesgo 1 del plan (10⁻¹³ m).
   - φ = R·Q₀/B = 0.0024 (≪ 0.5, U-03).
   - V-11 (`4_Validacion`): C11 = a·V₀/g = 144.2111 m; C22 = 149.56440 m; 100·C27 = 3.7122 % =
     100·(C22 − C11)/C11.
3. **Procedencia** `[medido]`: `git hash-object tools/extract_excel_reference.py` = `e709f0b1…` =
   `provenance.script_git_blob` (el script versionado es el que generó el JSON).

## Unidades de extremo a extremo

La fase 0 no tiene fórmulas en `src/` ni factores de conversión. La referencia está en SI con la
unidad en el nombre (`inner_diameter_m`, `initial_flow_m3s`, `flow_m3s`, `head_m`) y un bloque
`units` explícito `[leído]`. El contrato usa mm y L/s (plan §1.2): **la conversión ×1000 de
`flow_m3s` a L/s y de mm a m entra en la fase 1/2 y debe quedar ejercida por V-05** (Q ± 10⁻⁶ L/s);
no es hallazgo de esta fase.

## Conformidad con el kit

| Regla | Resultado | Evidencia |
|---|---|---|
| `kit 01 §1` nombres | cumple | `[leído]` distribución `mainpipe-transient`, import `mainpipe_transient` |
| `kit 01 §2` layout | cumple para la fase | `[medido]` wheel con `py.typed`; `src/`; `schemas` llega en fase 2 (plan §5, `CHANGELOG.md`) |
| `kit 01 §3` API | cumple para la fase | `[medido]` `solve(data: dict) -> dict` sin argumentos extra; `__version__` = `importlib.metadata.version("mainpipe-transient")` = `0.1.0`; `SCHEMA_VERSION = "1.0"` `str`. `SolveRequest`/`SolveResponse`/`Check` diferidos a fase 2 por el plan |
| `kit 01 §4` NaN/inf | no aplica aún | sin modelos de respuesta en fase 0 |
| `kit 01 §5` idioma | cumple | `[leído]` mensaje de `solve` en español; docstrings, logger y nombres en inglés |
| `kit 01 §6` pureza | cumple | ver C2; `logging.getLogger("mainpipe_transient")` |
| `kit 01 §7` dependencias | cumple | `[medido]` solo cotas inferiores; `openpyxl`/`pywin32` como extra `excel-reference`, no en `Requires-Dist` base; test `test_dev_only_tools_are_not_imported_by_src_or_tests` en verde |
| `kit 02 §1` jerarquía | cumple | `[medido]` `ValidationError(Error, ValueError)` 422, `ComputationError` 500, base 500, prefijo único `MainpipeTransient`, sin `ServiceError` (plan §1.6) |
| `kit 04 §2` `portal/` | no aplica | `[medido]` `git show --stat` del commit no toca `portal/` |

## Hallazgos

| ID | Severidad | Archivo:línea | Qué está mal | Evidencia |
|---|---|---|---|---|
| F0-01 | menor | `tools/extract_excel_reference.py:254-255`; `tests/reference/excel_case.json` (`provenance`) | El plan (§5 fase 0) y U-28 piden «commit del script» en la procedencia. El JSON guarda `script_git_blob` y `repo_head_at_generation` = `cb82a62`, un commit que **no contiene** el script (se añadió en `905e53a`). La trazabilidad existe por el blob, pero quien siga `repo_head_at_generation` no encuentra el script ahí. Se resuelve documentando el campo o con una enmienda del texto de U-28; no afecta a los números | `[medido]` `git hash-object` del script = `e709f0b1…` = `script_git_blob`; `git log --oneline -- tools/extract_excel_reference.py` → solo `905e53a` |
| F0-02 | menor | `doc/plans/01-golpe-ariete-v1.md:515` (V-05) y `:521` (V-11) | Los literales del plan tienen menos cifras que su propia tolerancia. H_v(0) = 93.19944 frente a 93.19943562 en el JSON (diferencia 4.4·10⁻⁶ > ± 10⁻⁶ m); ΔH_J = 144.2111 frente a 144.21107087 (rel. 2.0·10⁻⁷ > 10⁻⁹); `theory_deviation_pct` = 3.712 frente a 3.71215 (rel. 4.1·10⁻⁵ > 10⁻⁹). Las filas dicen que la fuente es el JSON, así que la lectura correcta es «contra el JSON a 10⁻⁶ / rel. 10⁻⁹; los literales son informativos», pero un test de fase 1 o 4 que tome el literal con la tolerancia del plan fallará. Para `hie-architect` (aclaración de texto sin cambio de contrato) y aviso para `hie-api` en fases 1 y 4. Los tests de fase 0 usan media unidad de la última cifra impresa, que es correcto | `[medido]` script de comparación: `diff vs printed -4.38e-06 …`; `rel C11 2.02e-07`, `rel 100C27 4.09e-05` |
| F0-03 | menor | `portal/HANDOFF.md:22` | La etapa 5 (Construcción) sigue `pendiente` con la fase 0 ya entregada en `905e53a`; el estado que corresponde es `en curso`. Responsable: `hie-flow` | `[leído]` |

Sin hallazgos bloqueantes ni mayores.

## Lo que no comprobé

- **`pip install git+https://github.com/gustavods14/mainpipe-transient.git@905e53a`**: el commit no
  está empujado (`git status`: 1 commit por delante de `origin/hie/etapas-0-3`). Instalé desde un
  `git archive` del commit, que es equivalente para el criterio de la fase (`pip install .`), no
  para la casilla de G5.
- **«Sin Excel»** en sentido literal: Excel está instalado en esta máquina. Lo comprobado es que el
  venv limpio no tiene pywin32 ni openpyxl, que ningún archivo de `src/` ni `tests/` los importa
  y que la suite pasa así; no ejecuté la suite en una máquina sin Excel ni en Linux/macOS.
- **Compatibilidad con `pydantic==2.13.4`** (pin del portal): el venv resolvió 2.14.3. La fase 0 no
  importa pydantic; la cota `>=2.6` admite 2.13.4, pero no la ejecuté con ese pin. Pasa a la
  fase 2.
- Presupuesto de tiempo, NaN/inf en la respuesta, envoltorio de excepciones ajenas y
  `portal/examples/` / `INTEGRATION.md`: fuera del alcance de la fase 0.

## Veredicto

**Pasa** — los seis puntos del criterio de «hecho» de la fase 0 se cumplen, medidos desde un venv limpio con Python 3.12; quedan tres hallazgos menores, sin bloqueantes ni mayores.

## Resolución de los hallazgos

Anotado por `hie-api` el 2026-11-14, con la decisión del dueño.

| ID | Resolución |
|---|---|
| F0-01 | **Aceptado por el dueño** (2026-11-14). El blob `e709f0b1…` identifica el contenido exacto del script; `git log --find-object=e709f0b` lleva al commit `905e53a`. No se regenera el JSON. |
| F0-02 | **Aceptado por el dueño** (2026-11-14). En las fases 1 y 4 los tests comparan contra `tests/reference/excel_case.json` con las tolerancias del plan (10⁻⁶ m, rel. 10⁻⁹); los literales de V-05 y V-11 se tratan como informativos. La aclaración del texto del plan queda para `hie-architect`, sin cambio de contrato. |
| F0-03 | **Corregido**: `portal/HANDOFF.md`, etapa 5 en `en curso` (vía `hie-flow`). |
