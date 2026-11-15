# Verificación — Fase 1 (núcleo MOC horizontal)

| | |
|---|---|
| Fase | 1: núcleo MOC horizontal (plan 01 §5) |
| Commit verificado | `9d1d9b4a4f79f4654c38c3f139a8661b91bf5da5` (rama `hie/etapas-0-3`, sin empujar: 3 commits por delante de `origin`) |
| Plan | `doc/plans/01-golpe-ariete-v1.md`, estado **congelado** (G4, 2026-11-14) |
| Kit | `KIT_VERSION = 3.0.0` (portal `C:\Dev\web_apps`); `portal/HANDOFF.md` dice 3.0.0, así que coinciden |
| Verificador | `hie-verifier`, 2026-11-14 |
| Kit leído | `README.md`, `01` (entero, foco en §2–6 y §9), `02`, `04` §2–3 |

Alcance del commit `[medido]` (`git show --stat 9d1d9b4`): `_closure.py`, `_geometry.py`, `_moc.py`,
`tests/moc_cases.py`, `tests/test_moc_core.py` y `CHANGELOG.md`. No toca `portal/`, la API
pública ni `pyproject.toml`.

## Entornos de ejecución

- **Venv limpio** `[medido]`: `git archive 9d1d9b4`, extraído en un directorio temporal, `py -3.12 -m venv`,
  `pip install ./src pytest` (instalación normal, no editable). Resolvió numpy 2.5.4 y
  pydantic 2.14.3. `find_spec` encuentra `_closure`, `_geometry` y `_moc` en `site-packages`, así que
  los tres módulos nuevos están dentro del wheel. Ejecuté la suite desde el árbol extraído:
  **46 passed in 2.10s**, con `mainpipe_transient._moc.__file__` en `venv\Lib\site-packages\`.
- **`.venv` del repo** (instalación editable) `[medido]`: `python -m pytest -rA` da **46 passed**. Los 17
  tests de `test_moc_core.py` están en verde, igual que los 29 de las fases 0 y 1. `git status` sigue
  limpio después de las ejecuciones.

## Criterio de «hecho» de la fase (literal del plan) y resultado

> «V-01 … V-09, V-14, V-15 en verde. En particular: Excel paso a paso ± 10⁻⁶ m / ± 10⁻⁶ L/s
> (U-29); Joukowsky ± 0.01 m; Allievi ± 10⁻⁶ m».

Además de la suite, escribí una **transcripción independiente** de M1–M12 y M19 en Python puro, sin numpy
y sin importar código del paquete, a partir de la tabla §4 del plan. Con ella comparé cada caso
(scripts `indep.py` y `compare.py` en el directorio temporal, fuera del repo).

| V | Caso / tolerancia del plan | Test | Resultado | Evidencia |
|---|---|---|---|---|
| V-01 | V₀ ± 0.001, h_f ± 0.01, H(500) = 96.60 ± 0.01; rel. 10⁻¹² contra la fórmula | `test_v01_steady_state_darcy_weisbach` | cumple | `[medido]` V₀ = 1.414711 m/s, h_f = 6.800564 m, H(500) = 96.599718 m. Error relativo frente a mi transcripción: V₀ 0, h_f 0, B 0, R 2.2·10⁻¹⁶. φ = 0.00236 = R·Q₀/B |
| V-02 | H_v = 244.21 ± 0.01 (0.05 < t < 2.0); −44.21 ± 0.01 (2.05 < t < 4.0); Q_dep = −100 ± 0.1 L/s (1.05 < t < 3.0) | `test_v02_joukowsky_without_friction` | cumple | `[medido]` a·V₀/g = 144.211071 m. Desviación de H_v frente a 100 ± ΔH_J: **0.0** en las dos ventanas; Q_dep frente a −100: 1.4·10⁻¹⁴ L/s |
| V-03 | Allievi M19, ley del Excel y ley lineal de 3 s, f = 0, ± 10⁻⁶ m en todos los pasos | `test_v03_allievi_without_friction[ley-excel, ley-lineal-3s]` | cumple | `[medido]` el paquete frente a **mi** recurrencia de Allievi, con mi propia interpolación de la ley: 1.1·10⁻¹³ m (ley del Excel) y 7.1·10⁻¹⁴ m (ley lineal). Ver F1-03 |
| V-04 | `head_valve_max_m` ± 0.01 con N = 20 y N = 40 | `test_v04_…[20, 40]` | cumple | `[medido]` 244.211071 m en los dos casos |
| V-05 | H ± 10⁻⁶ m y Q ± 10⁻⁶ L/s en 21 nodos × 401 pasos; extremos ± 10⁻⁶ m con el instante exacto; máximo y mínimo de la tubería = los de la válvula | `test_v05_excel_step_by_step`, `test_v05_excel_extremes` | cumple | `[medido]` paquete frente a `excel_case.json`: máx \|ΔH\| = **6.0·10⁻¹³ m**, máx \|ΔQ\| = **4.1·10⁻¹³ L/s**, forma (401, 21). Mi transcripción frente al JSON: 4.6·10⁻¹³ / 3.4·10⁻¹³; paquete frente a mi transcripción: 5.8·10⁻¹³ / 3.7·10⁻¹³. Las series en la válvula, el punto medio y el depósito y las envolventes coinciden con la malla a ≤ 6·10⁻¹³. H_v máx = 242.76384038 en t = 2.0 y H_v mín = −37.89904017 en t = 4.0, con el instante en igualdad exacta. Extremos globales de la historia completa con el desempate de U-25: (242.76384, x = 1000, t = 2.0) y (−37.89904, x = 1000, t = 4.0), iguales a `pressure_head_*_global()` |
| V-06 | t = 0.55 s sin fricción: H = 100 ± 0.01 para x < 500; 244.21 ± 0.01 para x > 500 | `test_v06_wave_front_position` | cumple | `[medido]` desviación 0.0 a los dos lados del frente |
| V-07 | Caso del Excel, Q_dep sin cambio ± 10⁻⁶ L/s para t < L/a | `test_v07_causality_…` | cumple | `[medido]` desviación de 1.3·10⁻¹³ L/s para t < 1 s. Primer cambio en t = 1.05 s (Q_dep = 90.4501), que es el paso 21, como corresponde |
| V-08 | HU-1.2 crit. 1–4, ± 0.01 L/s; Tc exacto | `test_v08_*` (3) | cumple | `[medido]` Q_v(0.25) = 75.000000, Q_v(0.75) = 35.000000, Q_v(1.5) con la ley lineal = 50.000000; Q_v = 0 exacto para t ≥ 1.5 con la ley truncada; Tc = 1.5 y 3.0 en igualdad exacta. `[leído]` U-18: el primer punto se sustituye por Q₀ (`_closure.py:47-49`, `test_closure_first_point_replaced_by_initial_flow`) |
| V-09 | z = 50, H_dep = 150: H = original + 50; presiones iguales ± 10⁻⁶ | `test_v09_datum_invariance` | cumple | `[medido]` \|H − H₀ − 50\| ≤ 6.7·10⁻¹³ en toda la historia; ΔQ 4.7·10⁻¹³ L/s; envolventes de presión y p_v iguales a ≤ 6.7·10⁻¹³ |
| V-14 | máx. \|H_v − H_dep\| de cada periodo 4L/a no crece (después de Tc) | `test_v14_friction_damps_each_period` | cumple | `[medido]` picos por periodo desde Tc = 1.5 s: 142.76384, 133.3516, 125.09259, 117.78774 m |
| V-15 | Ley (0; Q₀), (5 s; Q₀), (6 s; 0): H y Q sin cambio para t < 5 s, ± 10⁻⁹ | `test_v15_steady_state_is_a_fixed_point` | cumple | `[medido]` 100 pasos con t < 5 s: máx \|ΔH\| 3.8·10⁻¹³ m, máx \|ΔQ\| 1.5·10⁻¹⁶ m³/s. Identidad N·R·Q₀² − h_f = 8.9·10⁻¹⁶ (nota del plan §4) |

**Sensibilidad de V-05** `[medido]` (`mut.py` en el directorio temporal): evaluar la ley en t_k en lugar
de t_{k+1} mueve H hasta 13.96 m, y subir f un 1 % lo mueve 0.279 m. Con una tolerancia de 10⁻⁶ m, la
comparación detecta los dos defectos.

## Fórmulas contra el plan (§4) `[leído]`

- M1, M2, M5 y φ (`_moc.py:59-72`): A = πD²/4, V₀ = Q₀/A, h_f = f·L·V₀²/(2gD), B = a/(gA),
  R = fΔx/(2gDA²), φ = fΔxV₀/(2Da), 2L/a y 4L/a. Coinciden con el plan en coeficientes, signos y
  exponentes.
- M3 (`_moc.py:179`): H(x) = H_dep − h_f·x/L y Q = Q₀, sin pérdida de entrada (U-04).
- M6–M8 (`_moc.py:205-210`): u = BQ − RQ|Q|; C⁺ = H_{i−1} + u_{i−1}; C⁻ = H_{i+1} − u_{i+1}. Los índices
  están comprobados: `cp[j]` corresponde al nodo j+1 y `cm[j]` al nodo j. En los nodos interiores, H = (C⁺+C⁻)/2 y Q = (C⁺−C⁻)/(2B).
- M9 (`:212-213`): depósito con H = H_dep y Q = (H_dep − C⁻)/B. M10 (`:215-217`): Q = Q_ley(t_{k+1}) y
  H = C⁺ − BQ.
- M4 / U-07 / U-08 (`_geometry.py`): Δx = L/N, Δt = Δx/a, x_i = L·i/N con el último nodo = L exacto,
  `n_steps` = ⌈T/Δt − 10⁻⁹⌉ y t_k = k·Δt (no es una suma acumulada). Duración por defecto Tc + 5·(4L/a).
- M11 (`_closure.py`): interpolación lineal en el orden de operaciones del Excel; constante a partir del último punto;
  Tc = primer t con Q = 0.
- U-19: las envolventes y el paso del primer extremo se acumulan dentro del bucle con desigualdad estricta, y no se guarda
  la historia. `test_hu15_envelopes` las compara en igualdad exacta con max, min y argmax de la historia
  completa. U-25: desempate por (paso, x) (`_moc.py:145-155`, `test_u25_global_extreme_tie_break`).

## Unidades de extremo a extremo

En la fase 1, `src/` trabaja **solo en SI** (m, s, m³/s) y no contiene ningún factor de conversión
(`[leído]`: `PipeData.diameter_m`, `initial_flow_m3s`; series `flow_*_m3s`). Las conversiones del
contrato (mm → m, L/s → m³/s, m³/s → L/s) solo existen en el arnés de pruebas
(`tests/moc_cases.py:72-74, 83`; `1000.0 *` en los tests). Que «Q ± 10⁻⁶ L/s» de V-05 se cumpla
dice que el núcleo es correcto en SI, pero no ejerce ninguna conversión del paquete, porque todavía no existe
(llega con `schemas.py` y `solve` en la fase 2). Anotado como F1-02 para que no se pierda.

## Conformidad con el kit

| Regla | Resultado | Evidencia |
|---|---|---|
| `kit 01 §2` layout | cumple | `[medido]` los módulos nuevos son privados (`_*.py`) y entran en el wheel |
| `kit 01 §3` API pública | cumple, sin cambios | `[leído]` `__init__.py` no cambia en el commit; el núcleo no se exporta. `[medido]` `test_public_api_phase0` en verde |
| `kit 01 §4` modelos, NaN/inf | no aplica aún | no hay modelos de respuesta en la fase 1. φ ≤ 0.5 (U-03) llega en la fase 2 |
| `kit 01 §5` no conforme ≠ excepción; idioma | no aplica / cumple | sin `checks` en la fase 1. Docstrings y nombres en inglés |
| `kit 01 §6` pureza | cumple | `[medido]` grep en `src/` de `print(`, `open(`, `os.environ`, `getenv`, `global`, `random`, `time.time`, `warnings`, `seterr`: sin coincidencias. `test_no_print_in_package` y `test_import_has_no_side_effects` en verde. Las dataclasses son `frozen` y los arrays de `Mesh`, de solo lectura. Tiempo, como dato informativo: mediana de 5 ejecuciones de `simulate`, **4.9 ms** en el caso del Excel y **143.7 ms** con N = 200 y 10 000 pasos sin vértices (`timing.py`; la medida contractual es de la fase 2, V-16) |
| `kit 02` excepciones | sin cambios | `[leído]` el único `raise` nuevo es `ValueError` interno en `_closure.py:40` (ver la observación de abajo) |
| `kit 04 §2` `portal/` | no aplica | `[medido]` el commit no toca `portal/` |

## Hallazgos

| ID | Severidad | Archivo:línea | Qué está mal | Evidencia |
|---|---|---|---|---|
| F1-01 | **mayor** | `doc/stories/01-transitorio-cierre-valvula.md` (no existe); referencias en `doc/plans/01-golpe-ariete-v1.md:487` (fase 1, «HU-1.7 (1–4)») y `:488` (fase 2, «1.7 (5)»), `doc/stories/01-transitorio-cierre-valvula.md:186` (HU-1.6 crit. 13 «calculado como en HU-1.7 crit. 4»), `doc/DECISIONS.md:20-21` (U-08, U-09), `doc/stories/00-epica.md:96,125`, `doc/stories/04-serie-reproduccion.md:78` | **La historia HU-1.7 no existe.** El plan declara que la fase 1 cierra HU-1.7 crit. 1–4 y que la fase 2 cierra el crit. 5, y otros artefactos citan su crit. 4 como definición de `n_steps`. El archivo de historias F1 termina en HU-1.6, y ninguna versión del repositorio tuvo HU-1.7. Por eso no se puede verificar que la fase 1 cumpla cuatro de los criterios de aceptación que declara. El código sí cubre lo que se deduce de las referencias (N configurable, duración por defecto Tc + 5·4L/a, `n_steps` según U-08, `time_s` = k·Δt: `test_default_duration_and_step_count`, `test_hu14_series_shape`), pero eso es inferencia, no un criterio. **El defecto no está en `src/` ni en `tests/`**: es de las historias (G1) o del plan (G4). Responsables: `hie-product-owner` (restaurar HU-1.7) o `hie-architect` (enmendar las referencias). Comprobación: cuando exista el texto, cotejar sus crit. 1–4 con los tests de la fase 1 | `[medido]` `grep -n "^## " doc/stories/01-transitorio-cierre-valvula.md` → HU-1.1 … HU-1.6, no hay HU-1.7. `grep -rn "HU-1.7" doc/ portal/` → solo referencias. `git log -- doc/stories/01-transitorio-cierre-valvula.md` → solo `7ce6c30`, y en él `grep -c '^## HU-1.7'` = 0 |
| F1-02 | menor | `tests/moc_cases.py:72-74, 83`; `src/mainpipe_transient/_moc.py:33-42` | Las conversiones de unidades del contrato (mm → m, L/s ↔ m³/s) no están en `src/`. V-05 en L/s solo ejerce el `×1000` del arnés de pruebas. No es un defecto de la fase 1 (el contrato llega en la fase 2), pero la fase 2 tiene que repetir V-05 (H ± 10⁻⁶ m y `flow_*_lps` ± 10⁻⁶ L/s) **a través de `solve()`** con las entradas en mm y L/s, para que haya una prueba que ejerza cada factor de conversión | `[leído]` |
| F1-03 | menor | `tests/test_moc_core.py:169, 173` | La referencia de Allievi de V-03 construye Q(t) con `build_closure_law` y `flow_at` del propio paquete. Si la ley tuviera un defecto, se cancelaría entre el motor y la referencia, así que V-03 no es independiente en la ley de cierre. Lo mitigan V-08 (tres puntos) y V-05 (Q en la válvula frente a la columna de la ley del Excel en los 401 pasos), que sí son independientes; para la ley lineal de 3 s solo hay un punto de control. Comprobación: sustituir la interpolación de la referencia por una propia | `[medido]` con mi Allievi y mi interpolación, el paquete coincide a 1.1·10⁻¹³ / 7.1·10⁻¹⁴ m: hoy no hay error, solo falta de independencia |

Sin hallazgos bloqueantes. Un hallazgo mayor (F1-01), documental y ajeno al código.

**Observación (no es hallazgo):** `_closure.py:40` lanza un `ValueError` en inglés si la ley nunca
llega a Q = 0. Hoy no se alcanza (en la fase 2, la validación exigirá el último Q = 0), pero
`MainpipeTransientValidationError` hereda de `ValueError`: en la fase 2 conviene comprobar que el
envoltorio de `solve` no deje salir ese texto como si fuera un mensaje de validación (`kit 02 §1, §3`).

## Lo que no comprobé

- **HU-1.7 crit. 1–4**: no existen (F1-01).
- **Contrato** (`SolveRequest`/`SolveResponse`, `allow_inf_nan=False`, envoltorio de excepciones,
  mensajes, φ ≤ 0.5, `MAX_STEPS`): es de la fase 2. Tampoco ejecuté nada con `pydantic==2.13.4`,
  porque la fase 1 no importa pydantic.
- **Estabilidad con φ > 0.5**: no probé casos inestables. El rechazo es de la fase 2 (U-03).
- **Presupuesto de tiempo contractual (V-16) y HU-1.1 crit. 5**: solo hice una medida informativa del núcleo
  (4.9 ms en el caso del Excel), sin `solve` ni perfil.
- **`pip install git+…@9d1d9b4`**: el commit no está empujado. Instalé desde un `git archive`.
- Ejecución en Linux/macOS: no la hice.
- `portal/examples/` e `INTEGRATION.md`: fuera del alcance de la fase 1.

## Veredicto

**No pasa**: el criterio de «hecho» (V-01 … V-09, V-14 y V-15, con sus tolerancias) se cumple, medido desde un venv limpio y contra una transcripción independiente, pero queda abierto el mayor F1-01: la fase declara cubrir HU-1.7 (1–4) y esa historia no existe. Basta con corregir el documento, sin tocar `src/` ni `tests/`.
