# Verificación: fase 8 (entrega 0.2.0, enmienda F5R-02)

| | |
|---|---|
| Fase | 8 (plan 01 §5, fila 8) |
| Commit verificado | `af5c09ff748375110e86c56bc9a274d382e6387a` (`git rev-parse HEAD`, árbol limpio, rama `main`, **sin empujar**: `origin/main` = `fd58bff`) |
| Plan | `doc/plans/01-golpe-ariete-v1.md`, estado **congelado** (G4 del 2026-11-16, enmienda F5R-02, `SCHEMA_VERSION` = `"2.0"`) |
| Kit | Portal `C:\Dev\web_apps\doc\upstream-kit`, `KIT_VERSION` = `3.0.1`. Es el mismo que declaran el plan y `portal/HANDOFF.md` |
| Informe anterior | `doc/verification/12-fase-7.md` (`dea8a8f`, pasa) |
| Verificador | `hie-verifier`, 2026-11-22 |

## Entorno de ejecución

- **venv `v8`**: nuevo, creado con `py -3.12 -m venv` (Python 3.12.10) en el scratchpad de la
  sesión, fuera del repo
  (`C:\Users\gusta\AppData\Local\Temp\claude\f98149e085510c81\a484aced-e649-4130-8828-a03467881c45\scratchpad`).
  Como el commit no está en GitHub, instalé desde el repo local, por commit:
  `pip install "git+file:///C:/Dev/MyApps/mainpipe_transient@af5c09ff…" "pydantic==2.13.4" pytest`.
  Versiones: numpy 2.5.5 y pydantic **2.13.4** (el pin del portal). `mainpipe_transient.__file__`
  apunta a `v8\Lib\site-packages\…`. El wheel trae los 12 módulos de `src/mainpipe_transient/` y
  `py.typed` (`pip show -f`) `[medido]`.
- **Árbol `exp`**: exportación del commit con `git archive af5c09f`, con `src/` **borrado**. La
  suite, `tools/make_examples.py` y `tools/measure_payload.py` corrieron desde ahí con el
  intérprete de `v8`. Sin `src/`, lo único que se puede importar es el paquete instalado.
- **venv `vtools`**: Python 3.12 con `jsonschema`. Solo sirvió para validar `ui-spec.json`.
- Mis scripts están en `…\scratchpad\vc\` y `…\scratchpad\cmp_old.py`: `new3.py`, `integ.py`,
  `uispec.py` y `paths_check.py`. Los ejecuté con `python -I`.

## Qué cambia la fase

`git diff --stat dea8a8f af5c09f` `[medido]` toca `pyproject.toml` (versión), `CHANGELOG.md`,
`tools/make_examples.py` (tres casos nuevos), `tests/test_examples.py` (un test nuevo),
`portal/INTEGRATION.md` y `portal/examples/` (12 archivos con metadatos nuevos y 3 archivos nuevos).
**`src/` no cambia**: `git diff --quiet dea8a8f af5c09f -- src` sale con código 0 `[medido]`. Por
tanto las fórmulas, las unidades y la pureza son las mismas que ya verificó el informe 12.

## Criterio de «hecho» de la fase 8, punto por punto

| Criterio (plan §5, fila 8) | Resultado | Evidencia |
|---|---|---|
| `__version__` 0.2.0 (`pyproject.toml`) y entrada 0.2.0 en `CHANGELOG.md` | cumple | `[medido]` en `v8`: `__version__` = `0.2.0` y `SCHEMA_VERSION` = `"2.0"`. `[leído]` `pyproject.toml:7` y `CHANGELOG.md:6-48` (`## [0.2.0] — 2026-11-22`) |
| `portal/examples/` regenerados con `make_examples.py` desde el paquete instalado | cumple | `[medido]` En `exp` con `v8`, `make_examples.py --check` da «15 examples checked, 0 differences» y sale con 0. Regeneré los 15 con `--commit 61e1848… --out <tmp>` y comparé con `diff` contra los entregados. Solo cambia una línea por archivo: `generated_with.pydantic` es `2.13.4` en mi venv y `2.14.4` en los entregados. Lo demás coincide byte a byte (`inputs`, `expected`, `message`, `commit` y `generated_at`). Con el pin del portal salen exactamente los mismos ejemplos |
| Tres ejemplos nuevos con las entradas del plan | cumple | `[medido]` `vc/new3.py`. Las entradas de cada ejemplo nuevo son las del caso del Excel (`solve-excel-horizontal`) con `include_frames: false` y solo el cambio que pide el plan: `pn_bar` = 100.5; `pn_bar` = 0.5; `pn_bar` = 1 con `reservoir_level_m` = 1e308. Con el paquete instalado, los tres dan `MainpipeTransientValidationError` 422, y el mensaje es igual al `message` del ejemplo. Los dos de PN son, carácter a carácter, los literales de §1.3 (`tests/test_examples.py:158-166` los fija). El de U-44 es el literal de §1.6. En el de U-44, `SolveRequest.model_validate` acepta la entrada y `__cause__` es `None`: sale de la guarda de ±inf y no de la validación del modelo, como dicen el plan y `INTEGRATION.md` |
| Los `expected` de los 12 ejemplos existentes no cambian | cumple | `[medido]` `cmp_old.py` compara los 12 de `a04431e` (v0.1.0) con los de `af5c09f`. En los 12 no cambia ninguna clave fuera de los metadatos. Además de `package_version` y `commit`, cambian `generated_at` y `generated_with` (ver F8-01) |
| Checklist `kit 04 §3` completo desde el paquete instalado en un venv limpio | cumple, salvo la casilla del push, que queda pendiente (abajo) | Ver la sección «Checklist `kit 04 §3`» |
| `INTEGRATION.md`: fila `pn_bar` con 1 ≤ PN ≤ 100 | cumple | `[leído]` `portal/INTEGRATION.md:76`. `[medido]` `description` del campo = «Pipe pressure rating PN (bar). 1 <= PN <= 100.» |
| `INTEGRATION.md`: los dos mensajes de U-43 | cumple | `[leído]` `:91-103`. `[medido]` `vc/integ.py`: `SolveRequest.model_validate` con 100.5, 0.5, 0, −1, 100.00000000001 y 0.99999999999 da `loc` = `('pn_bar',)`, `type` = `value_error`, y `msg` = «Value error, » seguido del texto de §1.3. Con 100.00000000001 y 0.99999999999 el valor sale con `repr`. Coincide con lo que dice el párrafo |
| `INTEGRATION.md`: el 422 de U-44 en el mapeo de errores, con su mensaje, y que llega por `http_status` y no por la validación de FastAPI | cumple | `[leído]` `:236`. El mensaje es el literal de §1.6, y el texto dice «No es validación del modelo: FastAPI no la ve; llega … por el `http_status` …, sin el prefijo». `[medido]` `http_status` = 422 y `model_validate` acepta la entrada (fila anterior) |
| `INTEGRATION.md`: sección «Cambios 0.1.0 → 0.2.0» con lo que pide el plan | cumple | `[leído]` `:433-451` (sección (f)). Incluye `SCHEMA_VERSION` sin cambio, PN fuera de [1, 100] → 422, entradas extremas 500 → 422, tres ejemplos nuevos y `validation` de `pn_bar` en `ui-spec.json` a [1, 100]. `[medido]` La validación coincide con el archivo: `portal/ui-spec.json:93-105` tiene `min: 1`, `max: 100` y `hint` «1 ≤ PN ≤ 100 bar.»; en `a04431e` era `min: 0` |
| V-18 corre desde lo instalado sin cifras nuevas | cumple | `[medido]` `tools/measure_payload.py` en `exp` con `v8`. Receta realista: 964 274 B. Peor caso del barrido: 965 887 B (694 progresivas). Adversaria: 2 819 475 B, con 22.37 B por número (≥ 20). Variante con datum negativo: 2 844 325 B. Cota: 3 285 874 B. Petición: 19 919 B. Excel: 90 471 / 24 039 / 374 B. Las dos serializaciones dan los mismos bytes. Las cifras son idénticas a las del informe 09 (fase 6) y a las de `INTEGRATION.md` (cada una aparece en el texto, `grep`). Todas están dentro de los topes |
| `__version__` en `INTEGRATION.md` | cumple | `[leído]` `:16`: `0.2.0`, con la referencia al pin anterior `a04431e` |
| Commit en `main` con etiqueta `v0.2.0` | **pendiente** (no es un defecto del commit) | `[medido]` `git ls-remote origin`: `main` = `fd58bff`. `git tag -l` = `v0.1.0`. El encargo deja el push y la etiqueta para después de este veredicto (etapa 6 de `HANDOFF.md`) |

## Checklist `kit 04 §3`

| Casilla | Resultado | Evidencia |
|---|---|---|
| `HANDOFF.md`: etapas cerradas, `kit_version` vigente, commit a pinear | pendiente (etapa 6) | `[leído]` `portal/HANDOFF.md:9` dice kit `3.0.1`, que es el vigente. `:11` sigue con `a04431e`, y `:22-23` tiene las etapas 5 y 6 en «pendiente». Según el flujo, el commit a pinear y el cierre de etapas se escriben tras G5, igual que en la entrega 0.1.0 (informe 09). No lo cuento como hallazgo |
| Commit empujado (y etiqueta recomendada) | **pendiente** | Ver la última fila de la tabla anterior. Hay que comprobarlo después del push |
| `pip install git+…@<sha>` funciona en un entorno limpio con Python 3.12 | cumple con `git+file` | `[medido]` Instalé en `v8` desde el repo local. Desde GitHub no se puede probar mientras el commit no esté empujado (ver «Lo que no comprobé») |
| Motor construido y verificado desde el paquete instalado, en un entorno limpio | cumple | `[medido]` La suite corrió en `exp` (sin `src/`) con `v8`: `python -m pytest -q -p no:cacheprovider tests` → **538 passed**. Con `-W error`: 538 passed. La regeneración de `examples/` está en la tabla anterior (0 diferencias en `inputs`, `expected` y `message`) |
| `DECISION-REQUESTS.md`: ningún bloqueante `abierto` | cumple | `[leído]` Todas las filas «Estado» dicen `resuelto` (DR-1 … DR-10), y la cabecera (`:41`) dice «ninguno `abierto`». `grep -i abierto` solo encuentra texto narrativo |
| `INTEGRATION.md` coincide con el código del commit | cumple | `[medido]` `vc/integ.py` contra los modelos instalados. Los 18 campos de `SolveRequest`, los 58 de `SolveResponse` y los 10 de `Check` aparecen en el documento. `extra="forbid"` está en la petición, y `allow_inf_nan=False` en la petición, la respuesta y `Check`. Firma: `solve(data: dict[str, Any]) -> dict[str, Any]`. `http_status` = 500/422/500, y `ValidationError` hereda de `ValueError`. `__all__` tiene 9 símbolos, los de §1.1 del plan |
| `examples/` sin cambios en `src/` entre el commit de los ejemplos y el commit a pinear | cumple | `[medido]` Los 15 ejemplos registran `commit` = `61e18482…`. `git diff --stat 61e1848 af5c09f -- src` sale vacío. Si se pinea un commit posterior (por ejemplo, el que añada este informe), hay que repetir esta comprobación |
| `ui-spec.json` valida contra `06-ui-spec.schema.json` y todo `contract_path` existe | cumple | `[medido]` `vc/uispec.py` en `vtools` (draft 2020-12): 0 errores. `vc/paths_check.py` en `v8`: los 86 `contract_path` existen en `SolveRequest`, en `SolveResponse` o en `Check` |
| Informes de `hie-verifier` sin bloqueantes abiertos | cumple | El informe 12 pasa sin abiertos. Este informe no tiene bloqueantes ni mayores |

## Conformidad con el kit (resumen)

- **Layout y API pública (`kit 01 §2–3`)**: `src/` y `py.typed` están en el wheel. `__version__`
  sale de `importlib.metadata`. `SCHEMA_VERSION` = `"2.0"` `[medido]`.
- **NaN/inf (`§4`), resultado no conforme frente a excepción (`§5`), pureza (`§6`) y errores
  (`kit 02`)**: `src/` es el mismo que verificó el informe 12. `grep` de `print(`, `open(`,
  `os.environ` y `global` en `src/` no encuentra ningún uso `[leído]`. El tiempo de V-16 es
  0.256 s (mediana de 5, receta realista con fotogramas, en `v8`) `[medido]`.
- **`examples/` (`kit 04 §2`)**: generados por script desde el paquete instalado y coherentes con
  el código (tabla anterior). Formato: el mismo de los 12 de la 0.1.0. Cubren la clase de excepción
  alcanzable (`MainpipeTransientValidationError`), avisos `warning` y `error`, y el camino feliz.

## Hallazgos

| ID | Severidad | Archivo:línea | Qué está mal | Evidencia |
|---|---|---|---|---|
| F8-01 | menor | `portal/INTEGRATION.md:444`; `CHANGELOG.md:41-42` | Los dos textos dicen que en los 12 ejemplos de la 0.1.0 solo cambian `package_version` y `commit`. También cambian `generated_at` (de 2026-11-15 a 2026-11-22) y `generated_with.pydantic` (de 2.14.3 a 2.14.4). El plan (§5, fila 8) usa la misma frase. No afecta al snapshot del portal, que copia solo `id`, `description`, `inputs` y `expects_error` (`kit 04 §2`). Aun así, quien compare los archivos verá más metadatos cambiados de los que anuncia el contrato | `[medido]` `python -I cmp_old.py <a04431e>/portal/examples portal/examples`: en cada uno de los 12, «non-meta diffs: []» y «meta changed: ['commit', 'generated_at', 'generated_with', 'package_version']» |

Sin hallazgos bloqueantes ni mayores.

**Observación (no es hallazgo).** Los ejemplos entregados declaran
`generated_with.pydantic` = `2.14.4`, no el pin del portal (`2.13.4`). Al regenerarlos con
`2.13.4` desde el paquete instalado, `inputs`, `expected` y `message` salen idénticos byte a byte.
El plan no exige generarlos con una versión concreta de pydantic.

## Lo que no comprobé

- **La instalación desde GitHub** (`pip install git+https://github.com/gustavods14/mainpipe-transient.git@<sha>`)
  y **la etiqueta `v0.2.0`**: el commit no está empujado. Instalé con `git+file` desde el repo
  local, que construye el mismo árbol del mismo commit. Hay que repetir el `pip install` desde
  GitHub después del push, con el sha final.
- **El commit a pinear definitivo**: si es posterior a `af5c09f` (por ejemplo, el que añada este
  informe), no lo he verificado. Basta con comprobar que `git diff <pin> 61e1848 -- src` sale vacío.
- **Las fórmulas, las unidades y los casos de referencia V-01 … V-17, V-19 y V-20**, uno por uno:
  `src/` no cambia desde `dea8a8f`, que ya verificaron el informe 12 y los anteriores. En esta fase
  solo los ejercité a través de la suite completa (538 tests en verde desde lo instalado).
- **La integración en el portal** (casos dorados, `golden_lib` con `REL_TOL = 1e-9`): es del
  portal. Mi comparación de ejemplos es por igualdad exacta, que es más estricta.
- **El venv del repo** (`.venv`, pydantic 2.14.x): no corrí la suite en él. Solo la corrí con el
  pin del portal.

## Veredicto

**Pasa**: sin bloqueantes ni mayores abiertos (F8-01 es menor). La casilla del push y la etiqueta
`v0.2.0` quedan pendientes, por diseño del flujo, y se comprueban después del push.
