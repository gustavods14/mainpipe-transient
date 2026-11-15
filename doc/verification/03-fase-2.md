# Verificación — Fase 2 (contrato y topes)

| | |
|---|---|
| Fase | 2: contrato y topes (plan 01 §5) |
| Commit verificado | `61d9756d793566827b558253219bb4d72e4c57e5` (rama `hie/etapas-0-3`, árbol limpio, 3 commits por delante de `origin`: sin empujar) |
| Plan | `doc/plans/01-golpe-ariete-v1.md`, estado **congelado** (G4, 2026-11-14) |
| Kit | `KIT_VERSION = 3.0.0` (portal `C:\Dev\web_apps`). `portal/HANDOFF.md` dice 3.0.0: coinciden |
| Verificador | `hie-verifier`, 2026-11-14 |
| Kit leído | `README.md`, `01` (entero, con foco en §3–6 y §9), `02`, `04` §2–3 |

Alcance del commit `[medido]` (`git show --stat 61d9756`): `schemas.py` (+607), `_solve.py`,
`_format.py` (nuevo), `_theory.py` (nuevo), `_geometry.py`, `__init__.py`, `tests/test_contract.py`
(nuevo, 54 tests), `tests/test_package.py`, `tests/test_moc_core.py` (comentario), `CHANGELOG.md` y
`doc/DECISIONS.md` (U-08 corregida, U-38 nueva). No toca `portal/` ni `pyproject.toml`.

## Entornos de ejecución

- **`.venv` del repo** (editable; Python 3.12.10, numpy 2.5.4, pydantic 2.14.3) `[medido]`:
  `.venv\Scripts\python -m pytest -q` → **103 passed in 1.55s**. `git status` sigue limpio después.
- **Venv limpio con el pin del portal** `[medido]`: `git archive 61d9756` extraído en un directorio
  temporal, `py -3.12 -m venv`, `pip install ./tree "pydantic==2.13.4" pytest` (instalación normal).
  Resolvió pydantic **2.13.4** (pin del portal, `kit 01 §4`) y numpy 2.5.4. `find_spec` sitúa
  `_format`, `_theory`, `schemas` y `_solve` en `venv\Lib\site-packages\`: los módulos nuevos están en
  el wheel. Suite desde el árbol extraído (no tiene `src/` en `sys.path`; `conftest.py` no lo añade):
  **103 passed in 1.74s**.
- Mis scripts (`probe.py`, `sweep.py`, `tb.py` y el plugin `mutplug.py`) están en el directorio temporal
  del verificador, fuera del repositorio. Se ejecutaron contra el venv limpio.

## Criterio de «hecho» de la fase (literal del plan) y resultado

> «Cada criterio de HU-1.6 tiene su test con el mensaje esperado; para el crit. 13, en el caso del
> Excel con N = 200: `duration_s` = 50 calcula con `n_steps` = 10 000, `duration_s` = 50.001 da 422
> con «50 s», y la cifra que muestra el mensaje en un caso con Δt no redondo, reenviada, calcula sin
> error; la duración por defecto que no cabe da la variante «por defecto»; `solve` nunca deja salir
> una excepción ajena (test con fallo inyectado); mediana de 5 ejecuciones del peor caso < 0.8 s,
> anotada en `DECISIONS.md` (V-16)».

| Parte del criterio | Test | Resultado | Evidencia |
|---|---|---|---|
| HU-1.6 crit. 1 (tiempos no crecientes, punto 3, t = 1 s) | `test_hu16_crit1_…` | cumple | `[medido]` «…deben ser estrictamente crecientes: el punto 3 (t = 1 s) no es mayor que el punto 2 (t = 1 s).» |
| crit. 2 (empezar en t = 0) | `test_hu16_crit2_…` | cumple | `[medido]` «La ley de cierre debe empezar en t = 0 s: el punto 1 de closure_time_s es t = 0.5 s.» |
| crit. 3 (primer caudal > 0.1 %, ambos valores en L/s) | `test_hu16_crit3_…` | cumple | `[medido]` «…closure_flow_lps[0] = 99.8 L/s) difiere del caudal inicial (initial_flow_lps = 100 L/s) en más de 0.1 %…». Con 99.95 L/s calcula y `flow_valve_lps[0]` = 100.0 (U-18). También con 100.2 L/s |
| crit. 4 (ley que no cierra) | `test_hu16_crit4_…` | cumple | `[medido]` «…debe terminar con la válvula cerrada (Q = 0 L/s)… Los cierres parciales no están admitidos.» |
| crit. 5 (Q < 0 o > Q₀, punto y rango) | `test_hu16_crit5_…[-5, 120]` | cumple | `[medido]` «El caudal del punto 2 de la ley de cierre (t = 1 s) es -5 L/s: debe estar entre 0 y 100 L/s (caudal inicial).» |
| crit. 6 (longitudes distintas, < 2 o > 20 puntos) | `test_hu16_crit6_…` (3 casos) | cumple | `[medido]` «…deben tener el mismo número de puntos: tienen 3 y 2.»; «…entre 2 y 20 puntos; closure_time_s tiene 1…» |
| crit. 7 (a > 1500, f > 0.1, límite < −10.33, L/D/Q/PN ≤ 0; campo y límite) | `test_hu16_crit7_…` (12 casos) | cumple | `[medido]` p. ej. «wave_speed_ms = 1600 m/s está fuera de rango: … como máximo 1500 m/s.»; «pn_bar = 0 bar no es válido: … mayor que 0 bar.» |
| crit. 8 (tubería sobre el depósito) | `test_hu16_crit8_…` | cumple | `[medido]` «La tubería queda por encima del nivel del depósito: pipe_elevation_m = 120 m es mayor que reservoir_level_m = 100 m…» |
| crit. 9 (N impar o fuera de 10–200) | `test_hu16_crit9_…[21, 8, 202]` | cumple | `[medido]` «n_reaches = 21 no es válido: … entero par entre 10 y 200.» |
| crit. 10 (T < Tc + 2L/a; Tc, 2L/a y 32 s) | `test_hu16_crit10_…` | cumple | `[medido]` «duration_s = 20 s es menor que la duración mínima de 32 s (Tc = 30 s más 2L/a = 2 s)… Usa duration_s >= 32 s.» Con T = 32 s calcula (640 pasos). Barrido de 300 casos con Δt no redondo: la mínima mostrada (redondeada hacia arriba a 3 decimales), reenviada, nunca da el 422 del crit. 10 |
| crit. 11 (fallo interno → `ComputationError` 500, mensaje genérico) | `test_hu16_crit11_unexpected_failure_is_wrapped`, `…_nan_in_response…` | cumple **en el cálculo**, **no** en la validación | `[medido]` el envoltorio de `_solve.py:56-63` funciona: un `NaN` real (`reservoir_level_m` = 1e308) sale como `MainpipeTransientComputationError` (500) con el texto genérico. Pero las reglas cruzadas del validador lanzan excepciones ajenas que salen tal cual de `solve`: **F2-01** |
| crit. 12 (entregable `portal/`) | — | fuera de fase | fase 6 |
| crit. 13: T = 50 con N = 200 → 10 000 pasos | `test_hu16_crit13_excel_n200` | cumple | `[medido]` `n_steps` = 10000, `dt_s` = 0.005 |
| crit. 13: T = 50.001 → 422 con «50 s» | ídem | cumple | `[medido]` «duration_s = 50.001 s necesita 10001 pasos con n_reaches = 200 y supera el tope de 10000 pasos. La duración máxima admisible con esa malla es 50 s: acorta duration_s a 50 s o menos o usa una malla más gruesa (n_reaches <= 198).» (227 caracteres) |
| crit. 13: cifra mostrada con Δt no redondo, reenviada, calcula | `test_hu16_crit13_displayed_maximum_resent_computes` | cumple, salvo el caso límite de **F2-03** | `[medido]` barrido propio de 400 casos aleatorios (L, a, N): la T_max mostrada, reenviada, da `n_steps` ≤ 10 000 en todos. Excepción: si Tc + 2L/a cae entre la T_max truncada y la T_max exacta, la cifra reenviada da el 422 del crit. 10 (F2-03) |
| Duración por defecto que no cabe → variante «por defecto» | `test_default_duration_is_not_trimmed_to_the_cap` | cumple | `[medido]` «La duración por defecto Tc + 5·(4L/a) = 51 s necesita 10200 pasos… La duración máxima admisible con esa malla es 50 s: envía duration_s <= 50 s o usa una malla más gruesa (n_reaches <= 196).» Las variantes «duración mínima fuera de tope» y «cierre demasiado lento» también se emiten (`test_hu16_crit13_minimum_…`, `…_too_slow…`) |
| `solve` nunca deja salir una excepción ajena | `test_hu16_crit11_unexpected_failure_is_wrapped` | **no cumple** | `[medido]` el test inyecta el fallo en `simulate`, dentro del `try`. La validación (`SolveRequest.model_validate`, `_solve.py:51-54`) solo captura `pydantic.ValidationError`, y las reglas cruzadas pueden lanzar `OverflowError` y `ZeroDivisionError`, que pydantic no convierte. Ver **F2-01** |
| Mediana de 5 del peor caso < 0.8 s, anotada en `DECISIONS.md` | `test_hu17_crit5_worst_case_time_budget`; U-38 | cumple (peor caso **horizontal**) | `[medido]` venv limpio, `solve` con el caso del Excel, N = 200, T = 50 s (10 000 pasos, 201 nodos): 0.0981, 0.0950, 0.0939, 0.0935, 0.0937 s → **mediana 0.094 s**. U-38 anota 0.088 s en el mismo equipo. El peor caso del plan (§2: 500 vértices de perfil) no se puede ejecutar hasta la fase 3, y U-38 lo deja pendiente. Lo acepto como medición parcial de V-16 |

HU-1.7 crit. 5 (< 1 s con N = 200 y 10 000 pasos): cumple, con la medición de arriba.

## Hallazgos de la fase 1 que pasaban a la fase 2

| ID | Estado | Evidencia |
|---|---|---|
| F1-02 (conversiones de unidades solo en el arnés) | **cerrado** | `[leído]` `_solve.py:31-32, 73-90, 133-134`: mm → m, L/s → m³/s (Q₀ y cada punto de la ley) y m³/s → L/s en la salida. `test_v05_through_solve_with_contract_units` repite V-05 por `solve()` (H ± 10⁻⁶ m; `flow_*_lps` ± 10⁻⁶ L/s; envolventes). `[medido]` mutante sin el `×1000` de `flow_valve_lps` (plugin `-p mutplug`, `MUT=lps_out`) → 3 tests fallan, entre ellos V-05 por `solve` |
| F1-04 (tolerancia 10⁻⁹ de U-08 sin ejercer) | **cerrado** | `[medido]` `repr(1.0/dt)` = `26.000000000000004`, `repr(4.0/dt)` = `104.00000000000001` con N = 26, y `repr(20/0.05)` = `400.0`: el texto nuevo de U-08 y el comentario de `_geometry.py:20-23` son ciertos. Mutante con `_STEP_TOLERANCE = 0` (`MUT=tol0`) → `test_u08_step_tolerance_is_needed` falla (1 failed, 102 passed) |
| F1-05 (valores por defecto y ecos por el contrato) | **cerrado** | `[medido]` en verde: `test_defaults_through_contract` (sin `n_reaches` ni `duration_s` → N = 20, `dx_m` = 50, `dt_s` = 0.05, 430 pasos, 21.5 s), `test_echo_of_mesh_and_effective_duration` (20 → 400, 20.01 → 401 / 20.05 s, N = 40 → 800) y `test_default_duration_is_not_trimmed_to_the_cap` |

## Fórmulas contra el plan (§1.4, §4)

Comparé la respuesta de `solve` (caso del Excel) con una transcripción independiente en Python puro
(`probe.py`) `[medido]`:

| Campo | Fórmula del plan | Error relativo |
|---|---|---|
| `area_m2`, `velocity_initial_ms`, `head_loss_m` | M1, M2 | 0 |
| `dx_m`, `dt_s`, `reflection_time_s`, `wave_period_s`, `closure_duration_s`, `length_m` | M4, 2L/a, 4L/a, M11 | 0 |
| `friction_number` | φ = f·Δx·V₀/(2Da) (U-03) | 0 |
| `pn_head_m` | M18, PN·10⁵/(ρg); también con ρ = 998.2 y g = 9.78 → 256.0846742951218 en los dos | 0 |
| `pressure_max_pn_ratio_pct` | 100·p_max/`pn_head_m` | 0 |
| `joukowsky_head_rise_m` | M15, a·V₀/g = 144.21107087 | 0 |
| `full_pulse_length_m` | M17, L − a·Tc/2 = 250 | 0 |
| `moc_head_rise_valve_m` | H_v máx − H_v(0) = 149.56440476 | 0 |
| `theory_deviation_pct` | 100·C27 de `4_Validacion` = 3.71215181753 | 1.1·10⁻¹⁴ |
| Caso lento HU-3.4 crit. 2 (informativo; V-11 es de la fase 4) | M16: 2LV₀/(gTc) = 28.8422 | 0; `maneuver_type` = `slow`, `full_pulse_length_m` = `null` |

`[leído]` `_theory.py:35-51`: «rápida» si Tc ≤ 2L/a, Michaud `null` si la maniobra es rápida y pulso
`null` si es lenta, como §1.4. U-03 (`schemas.py:410-436`): el `n_reaches` mínimo par que propone es
correcto. `[medido]` φ(N) = 37.497/N con los datos del test → 76; con 74 da 422 y con 76 calcula.

## Unidades de extremo a extremo

| Campo de entrada | Conversión en `src/` | Prueba que la ejerce |
|---|---|---|
| `inner_diameter_mm` | `/1000` (`_solve.py:83`; φ en `schemas.py:411`) | V-05 por `solve` (H ± 10⁻⁶) y `test_unit_conversions_are_exercised` (D × 2 → V₀ / 4) |
| `initial_flow_lps`, `closure_flow_lps` | `/1000` (`_solve.py:73-75`) | V-05 por `solve` (H y Q ± 10⁻⁶) |
| `flow_valve_lps`, `flow_reservoir_lps` (salida) | `×1000` (`_solve.py:133-134`) | V-05 por `solve`. Mutante `lps_out` detectado `[medido]` |
| `pn_bar` → `pn_head_m` | `·10⁵/(ρ·g)` (`_solve.py:97`) | `test_derived_and_reference_fields_excel`, solo con ρ = 1000 y g = 9.81: **el factor ρ no lo ejerce ninguna prueba** (F2-02) |
| `min_allowed_pressure_head_m` | eco sin conversión | `test_min_allowed_pressure_echo` |

## Conformidad con el kit

| Regla | Resultado | Evidencia |
|---|---|---|
| `kit 01 §2` layout | cumple | `[medido]` los módulos nuevos están en el wheel (venv limpio) |
| `kit 01 §3` API pública | cumple | `[leído]` `__init__.py`: `__all__` = plan §1.1. `solve(data) -> dict`; valida con `model_validate`, envuelve `ValidationError` con `raise … from exc` (`_solve.py:51-54`) y devuelve `model_dump(mode="json")`. `[medido]` `test_public_api`, `test_response_is_strict_json_and_valid_contract` |
| `kit 01 §4` Pydantic, compatible con 2.13.4 | cumple | `[medido]` 103 passed con pydantic 2.13.4 |
| `kit 01 §4` `allow_inf_nan=False` y `NaN`/`inf` | cumple | `[leído]` `SolveResponse`, `Check` y también `SolveRequest` (`schemas.py:67, 442, 476`). `[medido]` un `NaN` en una lista de la respuesta → 2043 errores `finite_number` → `MainpipeTransientComputationError`; `inf` en `closure_time_s` → 422 «closure_time_s.1: debe ser un número finito.» |
| `kit 01 §4` unidades en el nombre, `null` documentado | cumple | `[leído]` todos los campos llevan la unidad en el nombre y la `description`. `michaud_head_rise_m`, `full_pulse_length_m`, `first_*` y `frame_*` dicen cuándo son `null`. Interino: `frame_*` es `null` aunque `include_frames` = `true` hasta la fase 5 (declarado en `CHANGELOG.md`) |
| `kit 01 §5` no conforme ≠ excepción | cumple en lo que hay | `[leído]` `status` y `checks` están en la respuesta. `checks` queda vacío hasta la fase 4 |
| `kit 01 §5` / `kit 02 §3` idioma y formato de los mensajes | cumple, con detalles menores (F2-04) | `[medido]` todos los mensajes de HU-1.6 están en español, con unidades, punto decimal, el campo y el límite, sin «Value error» ni nombres de clase |
| `kit 01 §6` pureza | cumple | `[medido]` grep en `src/` de `print(`, `open(`, `os.environ`, `getenv`, `global`, `random`, `time.time`, `perf_counter`, `warnings`, `seterr`, `requests`, `urllib`, `socket`: sin coincidencias en el código. Los dicts de módulo (`_SEVERITY_RANK`, `_TYPE_MESSAGES`) son constantes y no se mutan. `logging` con el logger `mainpipe_transient` (`_solve.py:27`) |
| `kit 01 §6` tiempo | cumple (horizontal) | mediana 0.094 s (tabla de arriba) |
| `kit 02 §1` jerarquía y `http_status` | cumple | `[medido]` `test_exception_hierarchy_and_http_status`: 422 y 500, sin `ServiceError` (plan §1.6) |
| `kit 02 §1` todo fallo sale como `<Pkg>Error` | **no cumple** | **F2-01** |
| `kit 04 §2` `portal/` | no aplica | `[medido]` el commit no toca `portal/` |

## Hallazgos

| ID | Severidad | Archivo:línea | Qué está mal | Evidencia |
|---|---|---|---|---|
| F2-01 | **bloqueante** | `src/mainpipe_transient/_solve.py:51-54`; origen en `schemas.py:365, 383, 396` (vía `_geometry.py:73` `math.ceil`), `schemas.py:413` (división por un área que se hace 0) y `schemas.py:354` (vía `_format.py:80` `math.ceil`) | **`solve` deja salir excepciones ajenas** (`OverflowError`, `ZeroDivisionError`), en contra del criterio de «hecho» («`solve` nunca deja salir una excepción ajena»), de HU-1.6 crit. 11 y de `kit 02 §1`. Las reglas cruzadas del `model_validator` hacen aritmética que, con entradas que pasan los validadores de campo, desborda o divide por cero. Pydantic solo convierte `ValueError` y `AssertionError` en `ValidationError`; el resto se propaga, y `solve` solo captura `ValidationError` alrededor de `model_validate`. El mismo fallo ocurre en el portal **antes** de llamar al paquete, porque FastAPI valida el cuerpo con el modelo re-exportado (`kit 02 §3`): sale un 500 en texto plano, categoría `unknown` («Error inesperado»), que es justo lo que `kit 02 §1` existe para evitar. Las entradas que lo provocan son físicamente absurdas, pero el criterio y la regla del kit no admiten excepciones, y el test con fallo inyectado no lo cubre porque inyecta dentro del `try` del cálculo. Comprobación: llamar a `solve` y a `SolveRequest.model_validate` con las tres entradas de la columna de evidencia; las dos llamadas tienen que lanzar una excepción del paquete (o `pydantic.ValidationError` en el caso de `model_validate`) | `[medido]` (`probe.py`, `tb.py`, venv limpio, pydantic 2.13.4), caso del Excel con un solo cambio: `duration_s` = 1e306 → `builtins.OverflowError: cannot convert float infinity to integer` (`schemas.py:396` → `_geometry.py:84` → `:73`); `inner_diameter_mm` = 1e-170 → `ZeroDivisionError` (`schemas.py:359` → `:413`); `wave_speed_ms` = 1e-320 → `OverflowError` (`schemas.py:354` → `_format.py:80`). Las tres salen igual de `solve` y de `SolveRequest.model_validate` |
| F2-02 | menor | `src/mainpipe_transient/_solve.py:97`; `tests/test_contract.py:112` | **El factor ρ (y la g) de `pn_head_m` = PN·10⁵/(ρ·g) no lo ejerce ninguna prueba.** El único test usa ρ = 1000 y g = 9.81, y V-12 / HU-3.1 crit. 1 (fase 4) tampoco cambia ρ. `density_kgm3` solo entra en este campo, así que un defecto (ρ fija en 1000, kg/m³ tomados como g/cm³) pasaría inadvertido. El código es correcto hoy | `[medido]` mutante que sustituye `req.density_kgm3` por `1000.0` (`MUT=rho1000`) → **103 passed**. `[medido]` con ρ = 998.2 y g = 9.78 el paquete da 256.0846742951218, igual a la fórmula |
| F2-03 | menor | `src/mainpipe_transient/schemas.py:369, 396-408` (`_max_duration_display` y la variante «acorta») | **La T_max truncada que propone el 422 del crit. 13 puede ser menor que la duración mínima** Tc + 2L/a. Ocurre cuando la mínima cabe en el tope pero cae entre la T_max truncada a 3 decimales y la exacta. El mensaje dice «acorta duration_s a X s o menos» y, al reenviar X, sale el 422 del crit. 10. Contradice «enviar la cifra mostrada calcule sin error» (plan §1.3, HU-1.6 crit. 13). La ventana es de 0.001 s, y la alternativa de engrosar la malla del mismo mensaje sí es válida | `[medido]` L = 1234.5 m, a = 1100 m/s, N = 200, ley (0; 100), (53.8691; 0), `duration_s` = 60: «…La duración máxima admisible con esa malla es 56.113 s: acorta duration_s a 56.113 s o menos…». Con `duration_s` = 56.113: «duration_s = 56.113 s es menor que la duración mínima de 56.114 s…». T_max exacta = 56.11363636, Tc + 2L/a = 56.11334545 |
| F2-04 | menor | `src/mainpipe_transient/_solve.py:211-216, 206`; `_format.py:39-44`; `schemas.py:427, 354` | **Fragmentos de los mensajes no conformes con `kit 02 §3` / `kit 01 §5`**: (a) el error de `Literal` deja una palabra en inglés que viene del `ctx` de pydantic: «geometry: valor no admitido; se admite 'horizontal' or 'profile'.»; (b) los errores de tipo dentro de una lista dan la posición con índice 0 («closure_time_s.1: debe ser un número.» para el 2.º punto), mientras que los mensajes propios cuentan desde 1 («el punto 2»); (c) con magnitudes extremas, φ y la duración mínima se imprimen con formato fijo y cientos de dígitos (`fmt_trim` usa `f"{v:.3f}"`), y el mensaje deja de ser legible antes del corte de 400 caracteres; (d) varios errores de campo a la vez se concatenan y superan los 400 caracteres (454 en la prueba), así que el portal cortaría los últimos. (a) y (b) se dan con entradas corrientes | `[medido]` (`probe.py`): casos `geom_lit`, `list_item`, `length_1e308` (φ = 2357851008768819937426…, más de 250 dígitos) y `multi` (454 caracteres) |

**Severidad de F2-01.** Es bloqueante porque el criterio de «hecho» de la fase dice literalmente
«`solve` nunca deja salir una excepción ajena», y lo he medido falso. El impacto práctico es bajo, porque
hacen falta entradas absurdas (≥ 10³⁰⁶ s, diámetros de 10⁻¹⁷⁰ mm, celeridades subnormales). Que el
dueño lo rebaje es una decisión suya. La forma de comprobar el arreglo está en la tabla.

## Observaciones (no son hallazgos)

- Con la duración por defecto y la variante «duración mínima fuera de tope» (`schemas.py:390-394`), el
  mensaje propone `n_reaches <= N` calculado para la duración **mínima**, como dice el plan. Si el
  usuario sigue sin enviar `duration_s`, la duración por defecto con ese N puede seguir sin caber y
  recibirá otro 422 (caso: N = 200, ley (0; 100), (49; 0): propone N ≤ 196, y con 196 la duración por
  defecto de 69 s supera los 51.02 s). Cumple el plan; lo anoto por si se quiere afinar el texto.
- `fmt_value` usa 10 cifras significativas: una `duration_s` como 50.00000000001 con N = 200 se
  muestra como «duration_s = 50 s necesita 10001 pasos… La duración máxima admisible… es 50 s». Solo
  pasa con entradas de más de 10 cifras.
- Interinos de la fase, declarados en `CHANGELOG.md`: `geometry = "profile"` pasa la validación y
  `solve` responde `MainpipeTransientComputationError` (500) «todavía no está disponible»;
  `checks` = [] y `status` = `ok`; `frame_*` = `null`. Tienen que desaparecer en las fases 3–5.
- Tamaño informativo `[medido]`: la respuesta del caso N = 200 / 10 000 pasos sin fotogramas ocupa
  1 148 301 B (`json.dumps`). El plan §2 estima ≈ 1,4 MB sin fotogramas para el peor caso con 699
  progresivas.

## Lo que no comprobé

- **Perfil** (HU-2.3, U-22), **checks** (§1.5, V-11 … V-13), **fotogramas** (V-17) y **tamaño** (V-18): son
  de las fases 3, 4 y 5. Los campos de teoría solo los contrasté de forma informativa.
- **V-16 con el peor caso del plan** (500 vértices de perfil, y con fotogramas): no se puede ejecutar
  hasta las fases 3 y 5. Solo medí el peor caso horizontal.
- **Cotas inferiores de las dependencias** (`pydantic>=2.6`, `numpy>=1.24`): solo probé con pydantic
  2.13.4 y 2.14.3 y numpy 2.5.4.
- **`pip install git+…@61d9756`**: el commit no está empujado. Instalé desde un `git archive`.
- Ejecución en Linux/macOS: no la hice.
- La ruta del portal (FastAPI validando con el modelo re-exportado): no la ejecuté. Que el fallo de
  F2-01 también aparece ahí es una inferencia `[leído]` de `kit 02 §3`, apoyada en que
  `SolveRequest.model_validate` lanza la misma excepción ajena `[medido]`.
- `portal/examples/` e `INTEGRATION.md`: el commit no los toca (fase 6).
- No repetí V-01 … V-15 del núcleo. `_moc.py` y `_closure.py` no cambian en este commit
  (`git show --stat`), y la suite que los cubre está en verde.

## Veredicto

**No pasa**: el bloqueante F2-01 sigue abierto. `solve` deja salir `OverflowError` y `ZeroDivisionError` de las reglas cruzadas del validador, en contra del criterio de «hecho» y de `kit 02 §1`. El resto del criterio se cumple: los mensajes de HU-1.6, las variantes del tope de 10 000 pasos y la mediana de 0.094 s, con 103 tests en verde también con pydantic 2.13.4. F1-02, F1-04 y F1-05 quedan cerrados, y hay tres menores abiertos (F2-02, F2-03, F2-04).

---

## Reverificación — 2026-11-14

| | |
|---|---|
| Commit verificado | `f29ae4dbff7dd8876c4d67212ad064bcb6717e9f` (rama `hie/etapas-0-3`, árbol limpio, 4 commits por delante de `origin`: sin empujar) |
| Plan | `doc/plans/01-golpe-ariete-v1.md`, estado **congelado** (sin cambios desde `61d9756`) |
| Kit | `KIT_VERSION = 3.0.0`; `portal/HANDOFF.md` dice 3.0.0: coinciden. Releídos `README.md`, `01` §4–6 y §9, `02`, `04` §2–3 |
| Verificador | `hie-verifier`, 2026-11-14 |

Alcance del commit `[medido]` (`git show --stat f29ae4d`): `_solve.py`, `schemas.py`, `_format.py`,
`tests/test_contract.py` (+11 tests), `CHANGELOG.md` y este informe. No toca `_moc.py`, `_closure.py`,
`_geometry.py`, `portal/` ni el plan.

### Entornos

- **`.venv` del repo** `[medido]`: `.venv\Scripts\python -m pytest -q` → código de salida 0, todo en
  verde. El `-q` del comando más el `addopts = "-q"` de `pyproject.toml` suprimen la línea de
  resumen; con `-o addopts=""` sale **114 passed in 1.66s**. `git status` sigue limpio después.
- **Venv limpio con el pin del portal** `[medido]`: `git archive f29ae4d` extraído en un directorio
  temporal, `py -3.12 -m venv`, `pip install ./tree "pydantic==2.13.4" pytest`. Resolvió pydantic
  2.13.4 y numpy 2.5.4, y `find_spec` sitúa `_format`, `_solve`, `schemas` y `_theory` en
  `venv\Lib\site-packages\`. La suite desde el árbol extraído da **114 passed in 1.86s**.
- Mis scripts (`probe2.py`, `sweep2.py`, `f203.py`, `f203b.py`, `f204.py`, `timing.py`) están en el
  directorio temporal del verificador, fuera del repositorio. Los mutantes se aplicaron a la copia
  instalada en el venv limpio y se restauraron (después: 114 passed).

### Estado de los hallazgos

| ID | Estado | Evidencia |
|---|---|---|
| F2-01 (bloqueante) | **cerrado** | `[leído]` `schemas.py:290-300` envuelve las reglas cruzadas y convierte `ArithmeticError` (`OverflowError`, `ZeroDivisionError`) en `ValueError`, que pydantic transforma en `ValidationError`. `_solve.py:55-57` envuelve cualquier otra excepción de la validación en `MainpipeTransientComputationError` con el mensaje genérico y `from exc`. `[medido]` Las tres entradas del informe y `length_m` = 1e308 dan un 422 en `solve` y un `ValidationError` en `SolveRequest.model_validate`, con «Los datos producen valores fuera del rango numérico representable: …». También hice un barrido aleatorio de **16 000 casos** (4 semillas; de 1 a 4 campos numéricos con magnitudes entre 10⁻³²³ y 1.8·10³⁰⁸ y ambos signos, sin `duration_s` en el 30 % de los casos, Tc extremo, N ∈ {10, 100, 200}): **0** excepciones ajenas en `solve` y **0** en `model_validate`. Mutantes: `except ArithmeticError` → `except KeyError` hace fallar 5 tests (`test_f201_*`), y quitar el `except Exception` de la validación en `_solve.py` hace fallar `test_f201_validator_bug_is_wrapped` |
| F2-02 (menor) | **cerrado** | `[medido]` `test_f202_density_and_gravity_enter_pn_head` (ρ = 998.2 / g = 9.78 y ρ = 1025). Mutante ρ → 1000.0: **1 failed** (`test_f202`). Mutante g → 9.81: **1 failed**. En el informe anterior, el mutante de ρ sobrevivía con 103 passed |
| F2-03 (menor) | **cerrado en el código**; su test de regresión no lo ejerce (**F2-05**) | `[leído]` `schemas.py:397-412`: si la mínima mostrada (redondeada hacia arriba) supera la T_max mostrada, el mensaje solo propone engrosar la malla, y la N se calcula con la mínima mostrada. `[medido]` Caso que reproduce el defecto (L = 1234.5 m, a = 1100 m/s, N = 200, ley (0; 100), (**53.8688**; 0), T = 60 s; véase la errata más abajo): «…La duración mínima Tc + 2L/a = 56.114 s supera la máxima admisible con esa malla (56.113 s): usa una malla más gruesa, n_reaches <= 198.» Reenviado con N = 198 y T = 56.114 s, calcula con 9901 pasos. Barrido `sweep2.py` (2 semillas, 3000 casos, 2302 con el 422 del tope, **1247 en la ventana de F2-03**): «acorta» no aparece **ninguna vez** dentro de la ventana, y ninguna cifra propuesta falla al reenviarla, en ninguna de las cuatro variantes: acorta (396 casos), envía (56), solo malla más gruesa, reenviada con la mínima mostrada (1826), y malla más gruesa como alternativa, reenviada con la duración original (439) |
| F2-04 (menor) | **cerrado**, con un residuo menor (**F2-06**) | `[medido]` (`f204.py`): (a) «geometry: valor no admitido; se admite 'horizontal' o 'profile'.»; (b) «closure_time_s (punto 2): debe ser un número.» y «closure_time_s (punto 3): debe ser un número finito.»; (c) `duration_s` = 1e200 → «…necesita 2e+201 pasos…», `length_m` = 1e200 → «…duración mínima de 2e+197 s…», `wave_speed_ms` = 1e-300 → «φ = … = 2.357851009e+300…», y `length_m` = 1e308 → el 422 genérico de F2-01; (d) con 8 errores de campo: **395 caracteres**, 4 mensajes y «(y 4 errores más)», y el recuento es correcto. El barrido de F2-01 no dio **ningún** mensaje de más de 400 caracteres ni ninguna tira de 16 dígitos o más. Otros mensajes de tipo revisados (campo que falta, campo extra, `n_reaches` = 20.5 / "x", booleano, lista, `null`): en español y sin restos en inglés. Los 4 tests `test_f204_*` fallan con el código de `61d9756` `[medido]` |

**Errata del informe anterior.** En F2-03 escribí Tc = 53.8691 s, pero las cifras que cité
(Tc + 2L/a = 56.11334545) corresponden a **Tc = 53.8688 s**. Con 53.8691 s, Tc + 2L/a = 56.11364545 es mayor
que la T_max exacta, y ya el código de `61d9756` respondía con la variante «solo malla más gruesa».
`[medido]` (código de `61d9756` vía `PYTHONPATH`): con 53.8691 → «…usa una malla más gruesa, n_reaches <= 198.»;
con 53.8688 → «…acorta duration_s a 56.113 s o menos…». El defecto que describí era real, pero el caso de
reproducción que publiqué estaba mal. Esta errata es el origen de F2-05.

### Criterio de «hecho» de la fase, repasado

| Parte | Resultado | Evidencia |
|---|---|---|
| HU-1.6 crit. 1–11 y 13 con su test y mensaje | cumple | `[medido]` 114 passed en los dos entornos. Los tests de la primera verificación no cambian, salvo los 11 nuevos |
| crit. 13: T = 50 → 10 000 pasos; 50.001 → 422 con «50 s»; cifra con Δt no redondo reenviada calcula | cumple | `[medido]` en la suite. Barrido `sweep2.py`: ninguna cifra propuesta falla al reenviarla, ni siquiera en la ventana de F2-03 |
| Variante «por defecto» | cumple | `[medido]` en la suite; 56 casos «envía duration_s <=» del barrido, todos calculan al reenviarlos |
| `solve` nunca deja salir una excepción ajena | **cumple** | `[medido]` F2-01 cerrado: barrido de 16 000 casos y test con fallo inyectado **en la validación** (`test_f201_validator_bug_is_wrapped`) además del que lo inyecta en el cálculo |
| Mediana de 5 del peor caso < 0.8 s (V-16, U-38) | cumple (peor caso horizontal) | `[medido]` venv limpio, Excel con N = 200 y T = 50 s, 10 000 pasos: 0.0997, 0.0995, 0.0936, 0.0936, 0.0942 s → **mediana 0.094 s** |

Conformidad con el kit, sin cambios respecto de la primera verificación, salvo `kit 02 §1`, que
ahora **cumple**. Pureza `[medido]`: el mismo grep sobre `src/` no encuentra coincidencias en el
código. `logger.exception` es `logging`, que el kit permite. `portal/` no se toca.

### Hallazgos nuevos

| ID | Severidad | Archivo:línea | Qué está mal | Evidencia |
|---|---|---|---|---|
| F2-05 | menor | `tests/test_contract.py:490-499` (dato en `:493`) | **`test_f203_displayed_maximum_below_minimum_suggests_coarser_mesh` no ejerce la corrección de F2-03.** Usa Tc = 53.8691 s, copiado de la errata del informe anterior. Con ese dato, la mínima ya no cabe en el tope y el código entra en la rama «solo malla más gruesa» por la primera condición (`count_steps(t_min, dt) > MAX_STEPS`), no por la guarda nueva `t_min_shown > t_max`. El test pasa sin la corrección. Para comprobarlo: quitar `or t_min_shown > t_max` de `schemas.py:398` y ejecutar la suite, que debería fallar; o ejecutar el test contra el código de `61d9756`, donde también debería fallar | `[medido]` mutante sin la guarda → **114 passed**. Con ese mismo mutante, el caso con Tc = 53.8688 da «acorta duration_s a 56.113 s o menos…», es decir, el defecto vuelve sin que la suite lo detecte. Test contra `61d9756` (vía `PYTHONPATH`): `test_f203` y `test_f202` **pasan**, y los otros 9 tests `test_f20*` fallan |
| F2-06 | menor | `src/mainpipe_transient/schemas.py:445` (con `_format.py:44-45` y `:70`) | **El mensaje de U-03 muestra «φ = … = inf»** cuando Δx/a desborda a infinito sin pasar por la aritmética que lanza excepción. Pasa con la duración por defecto, porque con `duration_s` explícito salta antes el 422 genérico de F2-01. `fmt_trim` delega los no finitos en `fmt_value`, que imprime `inf`. Es un valor no finito en un texto para el usuario y no es accionable (`kit 02 §3`). Es un residuo de F2-04 (c). Solo ocurre con entradas absurdas | `[medido]` `wave_speed_ms` = 1e-320 sin `duration_s` → «El número de fricción del tramo φ = f·Δx·V₀/(2·D·a) = inf con n_reaches = 20 supera 0.5…». Lo mismo con `length_m` = 1e306 y `wave_speed_ms` = 1e-10. Aparece en 72 de los 16 000 casos del barrido, siempre en este mensaje |

### Observaciones (no son hallazgos)

- **Entradas absurdas que pasan la validación terminan en 500.** `inner_diameter_mm` = 5e100 da
  `OverflowError` en el cálculo, y `pn_bar` = 1.8e308 da una respuesta no finita (`allow_inf_nan`).
  Las dos salen como `MainpipeTransientComputationError` con el texto «Los datos de entrada pasaron la
  validación…» `[medido]` (de 108 a 129 casos por cada 4000 del barrido). Cumple `kit 02 §1` y el
  criterio de la fase, porque no es una excepción ajena. Pero un desbordamiento en la validación es un
  422 y uno en el cálculo es un 500, y `kit 02 §1` dice que `ComputationError` «no debería ocurrir con
  entradas válidas». El plan no pone cota superior a L, D, Q ni PN (HU-1.6 crit. 7). Si conviene
  ponerla lo decide `hie-architect`. En esos casos, numpy emite `RuntimeWarning` por `warnings`, sin
  `print`.
- El 422 genérico de F2-01 no nombra el campo ni el valor: enumera los campos candidatos. Como solo
  aparece con magnitudes extremas, lo acepto.
- La observación de la primera verificación sobre la N propuesta para la duración **mínima** sigue en
  pie. Afecta también a la variante nueva de F2-03: en el caso de reproducción, reenviar N = 198 con la
  T = 60 s original vuelve a dar un 422. Cumple el plan.

### Lo que no comprobé

- Lo mismo que en la primera verificación: perfil, checks, fotogramas, tamaño, V-16 con el peor caso
  del plan, cotas inferiores de las dependencias, `pip install git+…` (el commit no está empujado),
  Linux/macOS y la ruta FastAPI del portal.
- No repetí la comparación de fórmulas contra la transcripción independiente (`probe.py`). El commit no
  toca `_theory.py`, `_moc.py` ni el bloque de cálculo de `_solve.py`, salvo el `except` de la
  validación, y los tests de fórmulas siguen en verde.
- El barrido de F2-01 es aleatorio, no exhaustivo, aunque cubre las magnitudes límite de `float`.

### Veredicto

**Pasa.** F2-01 (bloqueante), F2-02, F2-03 y F2-04 quedan cerrados en el código. No hay bloqueantes ni mayores abiertos. Quedan dos menores nuevos: F2-05 (el test de F2-03 no ejerce la corrección) y F2-06 («φ = inf» en el mensaje de U-03 con entradas absurdas).
