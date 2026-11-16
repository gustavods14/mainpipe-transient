# Verificación: fase 6 (entrega), reverificación

| | |
|---|---|
| Fase | 6, Entrega (plan 01 §5, fila 6). Reverificación tras `08-fase-6.md` («no pasa»: F6-01, F6-02 mayores; F6-03, F6-04 menores) |
| Commit verificado | `fcbff53ace2af9373591497446aa67b96a9d02d7` (`git rev-parse HEAD`, árbol limpio, rama `hie/etapas-0-3`) |
| Plan | `doc/plans/01-golpe-ariete-v1.md`, estado **congelado** (G4 del 2026-11-15, `SCHEMA_VERSION` = `"2.0"`) |
| Kit | Portal `C:\Dev\web_apps\doc\upstream-kit`, `KIT_VERSION` = `3.0.1`. `portal/HANDOFF.md` y el plan siguen en `3.0.0` (F6-04, sin cambios). La 3.0.1 es un *patch* que solo toca `kit 03 §1` y `§3` (IA); esta app no tiene IA (D-62) |
| Verificador | `hie-verifier`, 2026-11-15 |

## Entornos de ejecución

Todos los venvs se crearon desde cero con `py -3.12 -m venv`, fuera del repo, en el scratchpad de la
sesión. El paquete se instaló **desde GitHub**:
`pip install "mainpipe-transient @ git+https://github.com/gustavods14/mainpipe-transient.git@fcbff53…"`.

| venv | Python | numpy | pydantic | Para qué |
|---|---|---|---|---|
| A | 3.12.10 | 2.5.5 | 2.14.3 | lo que resuelve pip por defecto (las versiones de `generated_with`) |
| B | 3.12.10 | 2.5.4 | 2.13.4 | las versiones fijadas en `C:\Dev\web_apps\backend\requirements.txt` |
| T | 3.12.10 | 2.5.5 | 2.14.3 | herramientas (jsonschema) y comprobación de `INTEGRATION.md` |

`[medido]` `direct_url.json` del paquete instalado: `"url": "https://github.com/gustavods14/mainpipe-transient.git"`,
`"commit_id": "fcbff53…"`. El `RECORD` contiene los 12 módulos de §4 (Estructura interna) y `py.typed`.

La suite y las herramientas se ejecutaron desde un `git clone` de GitHub en `fcbff53`, **con
`src/` borrado**, para que solo pudiera cargarse el paquete instalado. Un plugin de pytest imprimió
al terminar `mainpipe_transient.__file__` = `…\venvA\Lib\site-packages\mainpipe_transient\__init__.py`
(ídem en B) `[medido]`.

## Estado de los hallazgos de `08-fase-6.md`

| ID | Antes | Ahora | Evidencia |
|---|---|---|---|
| F6-01 | mayor | **cerrado** | `[medido]` `git ls-remote origin` → `fcbff53… refs/heads/hie/etapas-0-3`; `git status -sb` sin «ahead». Instalación desde GitHub en el sha completada en A y B (ver arriba) y, desde ella, suite, `make_examples.py` y `measure_payload.py` (ver el criterio) |
| F6-02 | mayor | **cerrado** | `[leído]` `portal/INTEGRATION.md:352-355` y `:380-401`. El párrafo «Lectura» presenta 2 819 475 B como «la medición de la receta adversaria publicada, **no** la respuesta más grande posible»; cita la variante con datum negativo (2 844 325 B); da la cota analítica de 3 285 874 B como «el techo para toda entrada admitida»; y dice que «D-57 (1) se da por cumplido para toda entrada admitida solo con la guarda de D-57 (2) del portal en verde, no con la cuenta (D-65 (4)) ni con las mediciones del upstream». Cumple el plan, fase 6 (a), la frase de D-65 (4) (`C:\Dev\web_apps\doc\decisions\D-65-…md`, punto 4) y las tres condiciones de la aceptación de F5R-01 (`07-fase-5.md`, «Decisión del dueño»). `[medido]` venv B: `solve(adversarial_negative_datum_recipe())` → `json_dumps_compact` 2 844 325 B y `pydantic_model_dump_json` 2 844 325 B, 126 033 números, 22.568 B por número. Las cifras de la tabla coinciden con lo medido |
| F6-03 | menor | **cerrado** | `[medido]` venv B (numpy 2.5.4, pydantic 2.13.4): `make_examples.py --check` → «12 examples checked, 0 differences», exit 0. En una copia manipulada de `portal/examples/` (`expected.status` cambiado en un caso y `generated_with.numpy` en otro), el resultado es «FAIL: solve-sin-friccion-ok: differs in expected», «1 differences», exit 1. Ignora `generated_with` y nombra la clave que difiere |
| F6-04 | menor | **abierto** | `[leído]` `portal/HANDOFF.md:9` y la cabecera del plan dicen `3.0.0`; el kit vigente es `3.0.1`. Adoptarla le toca a `hie-architect` con el dueño (`hie-kit` §3) |

## Criterio de «hecho» de la fase, literal

| Criterio (plan §5, fila 6) | Resultado | Evidencia |
|---|---|---|
| Suite ejecutada desde el paquete instalado en un venv limpio | cumple | `[medido]` `python -m pytest -q -p no:cacheprovider`: **446 passed** en A (15.3 s) y en B (14.4 s), con el paquete de `site-packages` |
| Ejemplos regenerados desde el paquete instalado en un venv limpio | cumple | `[medido]` `--check` en A y B: «12 examples checked, 0 differences». Además regeneré los 12 con `--out` a un directorio temporal en A y en B y los comparé con un script propio (recursivo, igualdad exacta, ignorando solo `commit`, `generated_at` y `generated_with`): **0 diferencias** en los 12, en los dos. En A los archivos son idénticos línea a línea, salvo `generated_at` y `commit` |
| Mediciones de V-18 desde el paquete instalado en un venv limpio | cumple | `[medido]` `tools/measure_payload.py` en A y en B, con cifras idénticas: receta 964 274 B; peor caso del barrido 965 887 B (694 progresivas); adversaria publicada 2 819 475 B, 22.37 B por número (≥ 20); variante con datum negativo 2 844 325 B, 22.57 B por número; cota 126 328 × 25 + 127 674 = 3 285 874 B; petición 19 919 B (19 311 B compacta); Excel 90 471 / 24 039 / 374 B. Las dos serializaciones dan los mismos bytes. Todo ≤ 3 500 000 B y ≤ 65 536 B. Mediana de 5 del peor caso con fotogramas: 0.244 s (A) y 0.274 s (B), < 0.8 s |
| (a) Tamaño: cifras medidas, dos recetas, cota de U-34 (3b) con la frase de D-65 (4), cierre de F5-01, aviso de 4,5 MB | cumple | Ver F6-02. Las recetas en prosa (`:362-378`) no cambiaron desde `db613b7` y ya se cotejaron allí con `worst_case_recipe`, `case_with_stations(694)` y `adversarial_recipe`. El aviso de D-47 está en `:400-401` |
| (b) Precisión y comparación | cumple | Sin cambios desde `db613b7` (`git diff`), ya verificado en `08-fase-6.md` |
| (c) Regla del rojo | cumple | ídem |
| (d) Invariantes de la serie | cumple | ídem |
| (e) Cambios 1.0 → 2.0 y constantes ρ, g | cumple | ídem. `[medido]` `solve({"density_kgm3": 1000})` → `MainpipeTransientValidationError`, 116 caracteres, `__cause__` `ValidationError` |
| Ejemplos de la 2.0: cada lista en m, m.c.a. y L/s de un caso de éxito es igual a su redondeo a 3 decimales (V-19) | cumple | `[medido]` script propio sobre los 6 casos de éxito y las 16 listas: 18 486 valores, 0 sin redondear, 0 `-0.0` |
| Checklist `kit 04 §3` completo | cumple, salvo las casillas que el flujo deja para la etapa 6 | Ver la tabla siguiente |

## Checklist `kit 04 §3`, casilla por casilla

| Casilla | Resultado | Evidencia |
|---|---|---|
| `HANDOFF.md`: etapas cerradas, `kit_version` vigente, commit a pinear | pendiente (etapa 6) / F6-04 | `[leído]` `portal/HANDOFF.md:11` «Commit a pinear: —»; etapa 5 «en curso», etapa 6 «pendiente». Según `hie-flow` y `hie-api` §3, el commit y la etiqueta se ponen en la etapa 6, después de G5: no es hallazgo. El kit, en cambio, sigue desajustado (F6-04) |
| Commit empujado (y etiqueta recomendada) | cumple; sin etiqueta | `[medido]` `git ls-remote origin` → `fcbff53…`. `git tag -l` vacío: la etiqueta es recomendada y corresponde a la etapa 6 |
| `pip install git+…@<sha>` funciona en un entorno limpio con Python 3.12 | cumple | `[medido]` instalación desde `https://github.com/gustavods14/mainpipe-transient.git@fcbff53…` en A, B y T, Python 3.12.10 |
| Motor construido y verificado desde el paquete instalado, en un venv limpio | cumple | Ver las tres primeras filas del criterio, desde la instalación de GitHub y con `src/` ausente del árbol |
| `DECISION-REQUESTS.md` sin bloqueantes abiertos | cumple | `[leído]` DR-1 a DR-10: «Estado: resuelto» (líneas 83, 159, 219, 270, 331, 362, 392, 462, 507, 560) |
| `INTEGRATION.md` coincide con el código (firmas, modelos, unidades, excepciones) | cumple | `[medido]` venv T contra los modelos instalados: los 18 campos de `SolveRequest`, los 58 de `SolveResponse` y los 10 de `Check` aparecen en sus secciones. `extra="forbid"` y `allow_inf_nan=False` coinciden. `__all__` y la firma `solve(data: dict[str, Any]) -> dict[str, Any]` también. `http_status` es 500/422/500 y `ValidationError` hereda de `ValueError`. «Ejemplo mínimo» (`:420-440`) reproducido exacto: `error`, `["COLUMN_SEPARATION_RISK", "PN_NEAR_LIMIT"]`, `242.76384038253607` en t = 2.0, `-37.89904017427625` en x = 1000.0 y t = 4.0, `[93.199, 100.41, 107.621]`, 401 y 21 |
| `examples/` regenerados con el código entregado; sin cambios en `src/` entre el `commit` de los ejemplos y el pin | cumple | `[medido]` los 12 ejemplos registran `a8a1675531428a121656f84e765390dd693e160e`. `git diff a8a1675 fcbff53 -- src pyproject.toml` → 0 líneas. `portal/examples/` no cambió entre `db613b7` y `fcbff53` |
| `ui-spec.json` valida contra `06-ui-spec.schema.json` y todo `contract_path` existe | cumple | `[medido]` jsonschema: 0 errores. Los 86 `contract_path` resuelven contra los campos instalados de `SolveRequest`, `SolveResponse` y `Check` |
| Informes de `hie-verifier` sin bloqueantes abiertos | cumple | `[leído]` `01`–`08`: ninguno con bloqueante abierto (`08` tenía dos mayores, cerrados arriba) |

## Hallazgos

| ID | Severidad | Archivo:línea | Qué está mal | Evidencia |
|---|---|---|---|---|
| F6-04 | menor | `portal/HANDOFF.md:9`, plan (cabecera, fila «kit») | Sin cambios desde `08-fase-6.md`: dicen `3.0.0`, y el `KIT_VERSION` vigente es `3.0.1`. La casilla 1 de `kit 04 §3` pide la versión vigente. El *patch* no afecta a esta app (solo `kit 03 §1` y `§3`, IA). Le toca a `hie-architect` con el dueño. Cómo comprobarlo: la fila del `HANDOFF.md` debe decir `3.0.1`, o recoger una decisión explícita de quedarse en `3.0.0` | `[leído]` `C:\Dev\web_apps\doc\upstream-kit\README.md`: `KIT_VERSION = 3.0.1` |
| F6R-01 | menor | `doc/DECISIONS.md:56` (U-34, enmienda D-65 y «Medición de la fase 5 rehecha») | U-34 lee D-65 (4) al revés que `INTEGRATION.md` tras la corrección de F6-02. Dice que «el techo para toda entrada admitida y el cierre de F5-01 valen solo con **las dos mediciones en verde**, no con la cuenta (D-65 (4))», y que con ellas «el techo de D-57 (1) se cumple para toda entrada admitida». Pero D-65 (4) condiciona el cumplimiento a la **guarda de D-57 (2) del portal** en verde. Además, la variante con datum negativo muestra que las dos recetas no acotan toda entrada admitida. No toca el contrato con el portal (`portal/INTEGRATION.md` es correcto), pero el registro interno contradice el documento entregado. Corresponde a `hie-architect`. Cómo comprobarlo: el texto de U-34 sobre D-65 (4) debe coincidir con `INTEGRATION.md:380-399` | `[leído]` `doc/DECISIONS.md:56` frente a `portal/INTEGRATION.md:390-396` y a D-65, punto 4 |

No hay hallazgos bloqueantes ni mayores abiertos.

Observaciones que no son hallazgos:

- `--check` nombra solo la clave de primer nivel que difiere (`expected`), no la ruta dentro de
  ella. Es suficiente para lo que pedía F6-03.
- Siguen valiendo las tres observaciones de `08-fase-6.md`: versiones de generación distintas de
  las del portal, con valores idénticos; orden (b), (c), (d), (a), (e) de las secciones; `code`
  documentado como `str`.

## Lo que no comprobé

- **La etiqueta y el commit a pinear en `HANDOFF.md`**: son de la etapa 6, después de G5
  (`hie-flow`, `hie-api` §3).
- **Las secciones (b)–(e) de `INTEGRATION.md`, las recetas en prosa y las descripciones de los
  ejemplos**: no las volví a cotejar una por una, porque no cambiaron desde `db613b7` (`git diff`)
  y ya se verificaron en `08-fase-6.md`. Sí volví a ejecutar la cobertura de campos, la firma, las
  excepciones y el ejemplo mínimo.
- **La derivación de 126 328 como máximo recuento admitido de números** (cota de U-34 (3b)): la
  tomé de la verificación de la fase 5. Aquí solo medí que `measure_payload.py` la reproduce.
- **La física de las fases 0–5**: `src/` no cambió desde `a8a1675` (fase 5 verificada, «pasa»).
  Aquí solo ejecuté su suite desde el paquete instalado.
- **La conversión a casos dorados en el portal** (`golden_cases.py`): nunca se escribe en el
  portal. Mi comparación exacta de los ejemplos es más estricta que `REL_TOL = 1e-9`.
- Ejecución en Linux o en el CI del portal.

## Cómo se ejecutó

Scripts temporales en el scratchpad de la sesión, fuera del repo:

| Script | Qué hace |
|---|---|
| `conftest_probe.py` | plugin de pytest que imprime el origen de `mainpipe_transient` |
| `cmp.py` | compara recursivamente los ejemplos regenerados con los entregados |
| `uispec.py` | jsonschema de `ui-spec.json` y resolución de los `contract_path` |
| `integ.py` | contrasta `INTEGRATION.md` con los modelos instalados y reproduce el ejemplo mínimo |
| `v19.py` | V-19 sobre los ejemplos de éxito |

Además: la medición directa de `adversarial_negative_datum_recipe()` y el `--check` sobre una copia
manipulada de los ejemplos. No se modificó nada de `src/`, `tests/`, `portal/`, `tools/` ni del plan.

## Veredicto

**Pasa**: F6-01, F6-02 y F6-03 cerrados, sin bloqueantes ni mayores abiertos. Quedan dos menores,
F6-04 y F6R-01, ambos para `hie-architect`.

## Decisión del dueño sobre los menores (2026-11-15)

- **F6-04 — aceptado, para `hie-architect`.** Adoptar el kit 3.0.1 (patch de IA, sin efecto en esta
  app) lo decide `hie-architect` con el dueño; `HANDOFF.md` y el plan siguen en 3.0.0 hasta entonces.
- **F6R-01 — aceptado, para `hie-architect`.** Alinear U-34 en `doc/DECISIONS.md` con D-65 (4) (la
  guarda del portal en verde, no las dos mediciones) es de `hie-architect`. `portal/INTEGRATION.md`,
  que es lo que consume el portal, ya lo dice bien.
