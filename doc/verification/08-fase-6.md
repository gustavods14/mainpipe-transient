# Verificación: fase 6 (entrega)

| | |
|---|---|
| Fase | 6, Entrega (plan 01 §5, fila 6): `tools/make_examples.py`, `portal/examples/`, `portal/INTEGRATION.md`, etiqueta. Criterio: checklist `kit 04 §3` completo, desde el paquete instalado en un venv limpio |
| Commit verificado | `db613b7bbede970495bc73efc4532882ef50a87d` (`git rev-parse HEAD`, árbol limpio, rama `hie/etapas-0-3`) |
| Plan | `doc/plans/01-golpe-ariete-v1.md`, estado **congelado** (nueva G4 del 2026-11-15, `SCHEMA_VERSION` = `"2.0"`) |
| Kit | Portal `C:\Dev\web_apps\doc\upstream-kit`, `KIT_VERSION` = `3.0.1`. `portal/HANDOFF.md` y el plan dicen `3.0.0`. La 3.0.1 es un *patch* que solo toca `kit 03 §3` (IA), así que no afecta a esta app (sin IA, D-62). Ver F6-04 |
| Verificador | `hie-verifier`, 2026-11-15 |

## Entornos de ejecución

Los dos venvs se crearon desde cero con `py -3.12 -m venv`, fuera del repo. En ambos se instaló
`git+file:///C:/Dev/MyApps/mainpipe_transient@db613b7…` más `pytest`. No se pudo instalar desde
GitHub: ver F6-01.

| venv | Python | numpy | pydantic | Para qué |
|---|---|---|---|---|
| A | 3.12.10 | 2.5.5 | 2.14.3 | lo que resuelve pip por defecto; mismas versiones que `generated_with` de los ejemplos |
| B | 3.12.10 | **2.5.4** | **2.13.4** | las versiones fijadas en `C:\Dev\web_apps\backend\requirements.txt` y en su `.venv` |

En los dos venvs, el paquete cargado es el de `site-packages`. Lo comprobé `[medido]` con un
plugin de pytest que imprime `mainpipe_transient.__file__` al terminar la sesión. El wheel
contiene los 12 módulos de §4 (Estructura interna) y `py.typed`.

## Criterio de «hecho» de la fase, literal

| Criterio (plan §5, fila 6) | Resultado | Evidencia |
|---|---|---|
| Suite ejecutada desde el paquete instalado en un venv limpio | cumple | `[medido]` `python -m pytest -q -p no:cacheprovider`: **446 passed** en A (14.0 s) y en B (13.3 s) |
| Ejemplos regenerados desde el paquete instalado en un venv limpio | cumple | `[medido]` A: `tools/make_examples.py --check` → «12 examples checked, 0 differences». Además, en A y en B regeneré los 12 ejemplos con `--out` en un directorio temporal y los comparé con un script propio. `inputs`, `expected` y `message` son **idénticos** en los 12, sin tolerancia. Los archivos también son idénticos byte a byte, salvo la línea `commit`. En B solo cambia `generated_with` (ver F6-03) |
| Mediciones de V-18 desde el paquete instalado en un venv limpio | cumple | `[medido]` `tools/measure_payload.py` en A y en B, con cifras idénticas: receta 964 274 B; peor caso del barrido 965 887 B (694 progresivas); adversaria 2 819 475 B, 22.37 B por número; cota 3 285 874 B; petición 19 919 B (19 311 B compacta); Excel 90 471 / 24 039 / 374 B. Las dos serializaciones dan los mismos bytes. Mediana de 5 del peor caso: 0.247 s en A y 0.243 s en B |
| (a) Tamaño: cifras medidas, dos recetas, cota de U-34 (3b) **con la frase de D-65 (4)**, cierre de F5-01, aviso de 4,5 MB | **no cumple** | Las cifras de `INTEGRATION.md:351-356` coinciden con mi medición `[medido]`. Las recetas en prosa (`:360-377`) corresponden a `worst_case_recipe`, `case_with_stations(694)` y `adversarial_recipe` `[leído]`. Pero el párrafo «Lectura» no recoge D-65 (4) y no cumple la condición de F5R-01: ver **F6-02** |
| (b) Precisión y comparación | cumple | `INTEGRATION.md:265-290` `[leído]`: qué va a 3 decimales y qué no, lista frente a escalar (0.0005 m), diferencia de listas (0.001 m) y U-41. Coincide con `_solve.py` (`_rounded`/`_floats`) y con D-63 (5) |
| (c) Regla del rojo | cumple | `INTEGRATION.md:292-318` `[leído]` sigue §1.5 y D-63 (3)-(4). `[medido]` en `solve-pn-superado`: `value_m`, `x_m` y `time_s` de `PN_EXCEEDED` son `==` al máximo global, y `limit_m` es `==` a `pn_head_m` |
| (d) Invariantes de la serie | cumple | `INTEGRATION.md:320-339` `[leído]`, con la salvedad del último fotograma submuestreado. `[medido]` en `solve-excel-horizontal`: `frame_x_m == x_m`, todo `frame_time_s` está en `time_s`, y `frame_head_m − elevation_m` en x = L es exactamente igual a `pressure_head_valve_m` |
| (e) Cambios 1.0 → 2.0 y constantes ρ, g | cumple | `INTEGRATION.md:100-102` y `:387-400` `[leído]`. El mensaje de `density_kgm3` que cita el documento es el literal de `error-campo-retirado-densidad` `[medido]` |
| Ejemplos de la 2.0: cada lista en m, m.c.a. y L/s de un caso de éxito es igual a su redondeo a 3 decimales (V-19, D-63 (6)) | cumple | `[medido]` script propio sobre los 6 casos de éxito y las 16 listas: 0 valores sin redondear y 0 `-0.0`. Cada `round(checks[].x_m, 3)` está en `x_m` y cada `checks[].time_s` está en `time_s` |
| Checklist `kit 04 §3` completo | **no cumple** | Ver la tabla siguiente (F6-01, F6-04 y las casillas de la etapa 6) |

## Checklist `kit 04 §3`, casilla por casilla

| Casilla | Resultado | Evidencia |
|---|---|---|
| `HANDOFF.md`: etapas cerradas, `kit_version` vigente, commit a pinear | pendiente (etapa 6) / F6-04 | `[leído]` La etapa 5 está «en curso», la 6 «pendiente» y el commit a pinear es «—». Según `hie-flow` y `hie-api` §3, el commit en `HANDOFF.md` y la etiqueta se ponen en la etapa 6, después de G5, así que no los cuento como hallazgo. El kit, en cambio, sí es un desajuste (F6-04) |
| Commit empujado (y etiqueta recomendada) | **no cumple** (F6-01) | `[medido]` `git ls-remote origin`: `refs/heads/hie/etapas-0-3` está en `1cab79f`; el local va 4 commits por delante. `git tag -l`: vacío |
| `pip install git+…@<sha>` funciona en un entorno limpio con Python 3.12 | **no cumple** (F6-01) | `[medido]` `pip download --no-deps "mainpipe-transient @ git+https://github.com/gustavods14/mainpipe-transient.git@db613b7…"` → `fatal: remote error: upload-pack: not our ref db613b7…`, exit 128. Instalado desde el repo local en el mismo commit, funciona en A y en B |
| Motor construido y verificado desde el paquete instalado, en un venv limpio | cumple (desde el commit local) | Ver las tres primeras filas del criterio. Queda repetirlo desde GitHub una vez empujado (F6-01) |
| `DECISION-REQUESTS.md` sin bloqueantes abiertos | cumple | `[leído]` DR-1 a DR-10 en estado `resuelto` (D-57 a D-66) |
| `INTEGRATION.md` coincide con el código (firmas, modelos, unidades, excepciones) | cumple, salvo F6-02 | `[medido]` script contra los modelos instalados (venv B): las 58 claves de `SolveResponse` y las 10 de `Check` aparecen en «Contrato de respuesta», sin nombres de más. Las 18 filas de entrada coinciden con `SolveRequest` en obligatoriedad y valor por defecto. `__all__`, la firma `solve(data: dict[str, Any]) -> dict[str, Any]`, la configuración `extra="forbid"`/`allow_inf_nan=False` y la jerarquía con `http_status` 500/422/500 también coinciden. «Ejemplo mínimo» (`:409-422`) reproducido exacto: `242.76384038253607`, `-37.89904017427625`, `[93.199, 100.41, 107.621]`, 401 × 21. Extracto de `solve-sin-friccion-ok` (`:461-469`) exacto. Mensaje ≤ 400 caracteres: una entrada con 16 errores da 326 caracteres, con «(y 12 errores más)» y `__cause__` `ValidationError` |
| `examples/` regenerados con el código entregado; sin cambios en `src/` entre el `commit` de los ejemplos y el pin | cumple | `[medido]` los 12 ejemplos registran `a8a1675…`, y `git diff --stat a8a1675 db613b7 -- src` sale vacío. También `pyproject.toml` es igual |
| `ui-spec.json` valida contra `06-ui-spec.schema.json` y todo `contract_path` existe | cumple | `[medido]` jsonschema: 0 errores. Hay 86 `contract_path` y todos resuelven contra los campos de `SolveRequest`, `SolveResponse` y `Check` instalados |
| Informes de `hie-verifier` sin bloqueantes abiertos | cumple | `[leído]` `01`–`07`: todos con veredicto «pasa» en la última verificación. Hasta este informe no había ningún bloqueante abierto |

## Cobertura de `examples/` (`kit 04 §2`, plan §5)

`[medido]` Todos los ejemplos que prevé el plan están presentes, y además `solve-pn-superado`.

- Camino feliz horizontal y con perfil.
- `status` `ok`, `warning` y `error`.
- Los cinco códigos de `checks`, incluido `STEADY_NEGATIVE_PRESSURE` con severidad `error`.
- Seis `MainpipeTransientValidationError` 422, entre ellos el de migración por `density_kgm3`.
- Solo `solve-excel-horizontal` lleva fotogramas (401 × 21, `frame_stride` 1).
- `ComputationError` no es alcanzable con una entrada fija prevista: el kit no lo exige.

Comprobé que las descripciones dicen la verdad:
- sin fricción, p_min = 5.789 m.c.a. y 72.2 % del PN;
- subatmosférica, p_min = −8.211;
- en la loma, p_min(500) = −48.623 frente a −8.623 en horizontal, es decir −40 exacto;
- régimen negativo, −12.04 m en x = 300 m.

En `solve-excel-horizontal` los valores de control de V-05 se cumplen:

| Valor | Ejemplo | Error frente a la referencia |
|---|---|---|
| H_v máx | 242.76384038 m en t = 2.0 s | 3.8·10⁻⁷ m |
| H_v mín | −37.89904017 m en t = 4.0 s | 1.7·10⁻⁷ m |

Además, `theory_deviation_pct` = 3.712 %. `pn_head_m`, V₀ y h_f coinciden bit a bit con M18, M1 y M2.

Los mensajes de error están en español, con unidades, y señalan el punto que falla.

## Hallazgos

| ID | Severidad | Archivo:línea | Qué está mal | Evidencia |
|---|---|---|---|---|
| F6-01 | **mayor** | (repositorio remoto) | El commit a pinear **no está en GitHub**. Por eso fallan dos casillas de `kit 04 §3`: «commit empujado» y «`pip install git+https://github.com/gustavods14/mainpipe-transient.git@<sha>` funciona en un entorno limpio con Python 3.12». `hie-api` §3.1 pide que la casilla del entorno limpio se ejecute con el commit a pinear «(empujado)». La verificación desde el paquete instalado solo pude hacerla desde el repo local. Cómo comprobarlo: `git ls-remote origin` debe mostrar el sha, y la instalación de arriba debe completarse en un venv nuevo, seguida de la suite y de `make_examples.py --check` | `[medido]` `git ls-remote origin` → `1cab79f… refs/heads/hie/etapas-0-3`; `git status -sb` → `[ahead 4]`; `pip download … @db613b7…` → `not our ref`, exit 128 |
| F6-02 | **mayor** | `portal/INTEGRATION.md:379-383` | El párrafo «Lectura» de (a) dice que el techo de 3 500 000 B «vale **para toda entrada admitida** con las dos mediciones en verde —receta realista y adversaria—» y deja la cota analítica «como apoyo». Hay tres problemas. (1) El plan, fase 6 (a), exige **la frase de D-65 (4)**: el techo vale para toda entrada admitida **solo con la guarda de D-57 (2) del portal en verde**, no con la cuenta ni con las mediciones del upstream. Esa condición no aparece; el texto atribuye el cumplimiento a las mediciones del upstream. (2) La aceptación de F5R-01 por el dueño (`07-fase-5.md`, «Decisión del dueño») estaba condicionada a que `INTEGRATION.md` presentara la cota analítica (3 285 874 B) **como el techo** para toda entrada admitida, y la adversaria como medición de la receta publicada, no como máximo, citando la variante con datum negativo (2 844 325 B). No se hizo: no se menciona la variante y la cota queda como apoyo. (3) Tal como está, la afirmación es falsa por medición: hay una entrada admitida que pesa más que las dos recetas, así que ellas no acotan «toda entrada admitida». Lo que la acota es la cota analítica. No hay riesgo de tamaño, pero el documento que copia el portal fundamenta mal la garantía. Cómo comprobarlo: el párrafo debe decir lo de D-65 (4) y lo de F5R-01, y citar 2 844 325 B | `[medido]` venv B: `adversarial_recipe()` con `reservoir_level_m` y `profile_z_m` desplazados −9.8765432109876543·10¹⁵⁰ → 2 844 325 B en las dos serializaciones, más que los 2 819 475 B publicados y menos que la cota de 3 285 874 B. `[leído]` `C:\Dev\web_apps\doc\decisions\D-65-…md` (4): «D-57 (1) se da por cumplido para toda entrada admitida **solo con esa guarda en verde**, no con la cuenta» |
| F6-03 | menor | `tools/make_examples.py:41` | `--check` compara `generated_with` (versiones de Python, numpy y pydantic) como parte del ejemplo, y solo ignora `generated_at`. En el entorno del portal (numpy 2.5.4, pydantic 2.13.4), `--check` da «12 differences» y marca los 12 ejemplos como `differs`, aunque `inputs`, `expected` y `message` son idénticos. Tampoco dice qué clave difiere. Una comprobación de reproducción que falla en el entorno de destino con resultados idénticos lleva a regenerar sin necesidad o a desconfiar de ejemplos correctos | `[medido]` venv B: `make_examples.py --check` → 12 × «FAIL: … differs». Con mi comparación: 0 diferencias fuera de `commit` y `generated_with.{numpy,pydantic}` |
| F6-04 | menor | `portal/HANDOFF.md` (fila «Kit con el que se diseñó»), plan (cabecera) | Dicen `3.0.0`, pero el `KIT_VERSION` vigente del portal es `3.0.1`. La casilla 1 de `kit 04 §3` pide `kit_version` vigente. El cambio de la 3.0.1 no afecta a esta app (solo `kit 03 §3`, IA). Adoptarla le corresponde a `hie-architect` con el dueño (`hie-kit` §3); ya está anotado en `HANDOFF.md` el 2026-11-15 | `[leído]` `C:\Dev\web_apps\doc\upstream-kit\README.md`: `KIT_VERSION = 3.0.1` |

Observaciones que no son hallazgos:

- Los ejemplos se generaron con pydantic 2.14.3 y numpy 2.5.5, y no con las versiones fijadas en
  el portal. Con esas versiones (venv B) los valores salen idénticos, así que no afecta a los casos
  dorados.
- En `INTEGRATION.md`, las secciones del contrato van en el orden (b), (c), (d), (a), (e). Es solo
  presentación: los encabezados de la plantilla del portal (`doc/apps/_TEMPLATE/INTEGRATION.md`)
  están todos.
- La tabla de `Check` documenta `code` como `str`, mientras que el modelo es un `Literal` de cinco
  valores. Los cinco aparecen en la tabla contigua.

## Lo que no comprobé

- **La instalación desde GitHub, ni la suite ni la regeneración de ejemplos desde ella**:
  el commit no está en el remoto (F6-01). Todo lo `[medido]` en un venv limpio se instaló desde
  el repo local en el mismo sha.
- **La etiqueta y el commit a pinear en `HANDOFF.md`**: son de la etapa 6, después de G5
  (`hie-flow`, `hie-api` §3).
- **La conversión a casos dorados en el portal** (`golden_cases.py`, `--update-golden`). Nunca
  se escribe en el portal. La comparación con `REL_TOL = 1e-9` la cubre `tests/test_examples.py`
  (en verde en A y en B), y mi comparación exacta es más estricta. `golden_lib.run_case` solo lo
  leí `[leído]`: misma forma que `make_examples.build_case`.
- **La física de las fases 0–5**: fuera de los valores de control citados arriba, no la volví a
  verificar por mi cuenta, porque esas fases ya están verificadas y `src/` no cambió desde
  `a8a1675`. Aquí solo ejecuté su suite.
- Ejecución en Linux o en el CI del portal.

## Cómo se ejecutó

Scripts temporales en el scratchpad de la sesión, fuera del repo:

| Script | Qué hace |
|---|---|
| `cmp_examples.py` | compara recursivamente los ejemplos regenerados con los entregados |
| `cmp_integration.py` | contrasta `INTEGRATION.md` con los modelos instalados |
| `check_values.py` | ejemplo mínimo, valores de control, V-19 e invariantes sobre los ejemplos |

Además: la variante con datum negativo, `pip download` desde GitHub y jsonschema sobre
`ui-spec.json`. No se modificó nada de `src/`, `tests/`, `portal/` ni del plan.

## Veredicto

**No pasa**: dos hallazgos mayores abiertos, F6-01 (el commit a pinear no está empujado y
`pip install git+https://…@db613b7` falla) y F6-02 (el párrafo «Lectura» de `INTEGRATION.md`
omite la condición de D-65 (4) y la de la aceptación de F5R-01, y afirma una garantía que la
medición contradice). El resto del criterio se cumple desde el paquete instalado.
