# Verificación — Fase 4 (verificaciones: checks, status, Joukowsky / Michaud)

| | |
|---|---|
| Fase | 4: verificaciones (plan 01 §5) |
| Commit verificado | `92a3dedbf334aa8674f05d2671aaa5e38971a68b` (árbol limpio) |
| Plan | `doc/plans/01-golpe-ariete-v1.md`, estado **congelado** (G4, 2026-11-14) |
| Kit | `KIT_VERSION = 3.0.0` (portal `C:\Dev\web_apps`). `portal/HANDOFF.md` dice 3.0.0: coinciden |
| Verificador | `hie-verifier`, 2026-11-14 |
| Kit leído | `README.md`, `01` (§2–6 y §9), `02`, `04` §2–3 |

Alcance del commit `[medido]` (`git show --stat HEAD`): `_checks.py` (nuevo, 171 líneas), `_format.py` (+13,
`fmt_pressure`), `_moc.py` (primer cruce dentro del bucle), `_solve.py` (enlaza `build_checks` y `status_of`),
`tests/test_checks.py` (nuevo, 81 tests) y `CHANGELOG.md`. `_theory.py` ya existía y no cambia en este commit,
pero entra en la fase 4 del plan («`_theory`, `_checks`, `status`, mensajes»), así que también lo verifiqué. No
toca `portal/`, `__init__.py`, `schemas.py` ni `pyproject.toml`.

## Entornos de ejecución

- **`.venv` del repo** `[medido]`: `.venv\Scripts\python -m pytest -q` da **226 passed in 3.15s**, y
  `tests/test_checks.py` solo da **81 passed**. Después, `git status` sigue limpio.
- **Venv limpio** `[medido]`: extraje `git archive 92a3ded` a un directorio temporal, creé el venv con
  `py -3.12 -m venv` e instalé con `pip install ./tree "pydantic==2.13.4" pytest` (instalación normal, no
  editable). Quedaron pydantic 2.13.4 y numpy 2.5.4; `find_spec("mainpipe_transient._checks")` apunta a
  `venv\Lib\site-packages\`, y no hay ninguna ruta `src` en `sys.path`. Corrí la suite desde el árbol extraído:
  **226 passed in 3.34s** (`test_checks.py`: 81 passed).
- Mis scripts (`indep.py`, `excel.py`, `edge.py`, `eq.py`, `lit.py`, `tie.py`, `mut.sh`) están en el
  directorio temporal del verificador, fuera del repositorio, y los ejecuté contra el venv limpio. Los
  mutantes los apliqué sobre una copia del árbol extraído.

## Criterio de «hecho» de la fase (literal del plan) y resultado

> Fase 4, «Hecho cuando»: «V-11 … V-13 en verde; textos de HU-3.1-4 y HU-3.2-4 literales».

| Parte del criterio | Comprobación independiente | Resultado |
|---|---|---|
| **V-11**, caso rápido contra `4_Validacion` a rel. 10⁻⁹ | `[medido]` `excel.py` lee `tests/reference/excel_case.json`. ΔH_J frente a C11: rel. **0.0**. ΔH_MOC = 149.56440476119315 frente a C22: rel. **3.8·10⁻¹⁶**. `theory_deviation_pct` = 3.712151817531152 frente a 100·C27: rel. **1.1·10⁻¹⁴**. `full_pulse_length_m` = 250.0 frente a C12: diferencia **0.0**. `maneuver_type` = `rapid` y `michaud_head_rise_m` = `null` | cumple |
| **V-11**, caso lento: M16 a rel. 10⁻¹² y 28.84 ± 0.01 | `[medido]` ley (0; 100), (10; 0): `slow`, ΔH_M = 28.842214174542136; mi fórmula 2·L·V₀/(g·Tc) da rel. **0.0**. `full_pulse_length_m` = `null`, `theoretical_head_rise_m` = ΔH_M | cumple |
| **V-12**: `pn_head_m` ± 0.01, ratio ± 0.1 % | `[medido]` PN 25 bar da 254.841997961264 (HU-3.1 crit. 1: 254.84). Con ρ = 1025 y g = 9.78, el valor coincide bit a bit con 16·10⁵/(1025·9.78). El ratio del caso Excel, 95.26053096610715, frente a 100·C33/25 da rel. **1.5·10⁻¹⁶** | cumple |
| **V-13**: umbrales, presencia y ausencia exactas, `first_time_s` ± Δt, predicado por progresiva (D-60, U-36) y eco del límite | `[medido]` `indep.py`: transcripción propia de M1–M14 (bucle escalar nodo a nodo, progresivas y pesos propios) y de la tabla del plan §1.5 (condiciones, severidades, `value_m`/`limit_m`/`x_m`/`time_s`, primer cruce de U-25, orden, `status`, eco). La comparé con `solve()` en los 10 casos de las historias y en **200 casos aleatorios** (2 semillas: horizontal y perfil, N 10–40, L 500–2400 m, a 400–1250 m/s, f 0–0.03, ρ, g, PN de 6 a 40 bar, límite de −10.33 a 0). Todos los casos dan **los mismos códigos, severidades, orden, `status`, valores a 10⁻⁸, `first_*` exactos y mensajes de PN_EXCEEDED y COLUMN_SEPARATION_RISK idénticos**, salvo 2 casos con distinto instante de un máximo empatado: uno es ruido de mi transcripción (los `float` del paquete no empatan) y el otro es **F4-02** | cumple, salvo el detalle F4-02 |
| Primer cruce del caso Excel | `[medido]` lo calculé **directamente de la malla del Excel** (`grid.head_m`, 401 × 21): da t = 3.3 s, x = 950 m, p = −13.497785396184796. `solve` da `first_time_s` = 3.3000000000000003, `first_x_m` = 950.0 y `first_pressure_head_m` = −13.497785396184817 (diferencia 2·10⁻¹⁴ m) | cumple |
| Textos de HU-3.1 crit. 4 y HU-3.2 crit. 4, literales | `[medido]` `lit.py` extrae las citas «…» del propio `doc/stories/03-verificaciones.md`, normaliza los espacios, cambia «−» por «-» (U-26) y las compara con `solve()` (caso sin fricción con PN 20 y con H_dep = 100): las dos dan **True** | cumple |

**V-11, V-12 y V-13 en verde y textos literales**: se cumple el criterio de «hecho».

## Fórmulas frente al plan

| Elemento | Plan | Código | Comprobación |
|---|---|---|---|
| M15 Joukowsky | a·V₀/g | `_theory.py:37` | `[medido]` rel. 0 con C7/C11 |
| M16 Michaud | 2·L·V₀/(g·Tc), si Tc > 2L/a | `_theory.py:38` | `[medido]` rel. 0 |
| M17 Pulso | L − a·Tc/2, si Tc ≤ 2L/a | `_theory.py:39` | `[medido]` 250 en el caso Excel y 0 con Tc = 2L/a (test de frontera). El mutante `<=` → `<` muere |
| U-17 desviación | 100·(ΔH_MOC − ΔH_teo)/ΔH_teo, con ΔH_MOC = máx H_v − H_v(0) | `_theory.py:42,50` | `[medido]` 200 casos a 10⁻⁸ |
| M18 PN | PN·10⁵/(ρ·g) | `_solve.py` (`pn_head`) | `[medido]` |
| §1.5 PN_EXCEEDED / PN_NEAR_LIMIT | p_max > H_PN; 80 % < ratio ≤ 100 % (U-16) | `_checks.py:51-54` | `[medido]` fronteras con mutantes (abajo) |
| §1.5 COLUMN_SEPARATION_RISK / SUBATMOSPHERIC_PRESSURE | p_min < límite; límite ≤ p_min < 0, `limit_m` = 0 | `_checks.py:57-62,133` | `[medido]` |
| §1.5 STEADY_NEGATIVE_PRESSURE | p de régimen < 0; `error` si < límite; `limit_m` = 0 o límite; t = 0 | `_checks.py:65-66,136-151` | `[medido]` HU-3.3: −0.04 m da `warning` en x = 300 y −12.04 m da `error` |
| U-25 primer cruce | primer paso (incluido k = 0) con algún punto bajo el límite; entre ellos el de menor p y luego menor x | `_moc.py:218-229,280-281` | `[medido]` 200 casos y la malla del Excel. `[leído]` Buscarlo solo cuando `lower.any()` es correcto: si p_j(k) < límite ≤ p_j(k′) para todo k′ < k, entonces H_j(k) es un mínimo estricto nuevo (la resta de una z fija es monótona en coma flotante) |
| Orden y `status` | errores y después avisos, en el orden de la tabla; `status` = severidad máxima, `ok` sin avisos | `_checks.py:21-27,68,72-76` | `[medido]` |
| Paleta D-13 (U-20) | `warning` → `warning`, `error` → `danger` | `Literal["warning","error"]` en `Check` y `status` | `[leído]` |

## Unidades de extremo a extremo

- `pn_bar` (bar) → `pn_head_m` (m.c.a.) = PN·10⁵/(ρ·g), con `density_kgm3` y `gravity_ms2` de la entrada.
  La conversión la ejercita `test_v12_pn_with_other_density_and_gravity` (ρ = 1025, g = 9.78) y la
  comprobé bit a bit `[medido]`. En el muestreo aleatorio variaron ρ y g.
- `min_allowed_pressure_head_m` (m.c.a.) se compara con p/γ = H − z (m.c.a.) sin conversión. El eco en la
  respuesta y `limit_m` coinciden con lo enviado: −10.0 por defecto, −7, −10.33 y 0 (`test_v13_limit_echo`,
  `[medido]`).
- `pressure_max_pn_ratio_pct` (%) = 100·p_max/H_PN `[medido]`.
- En `Check`, `value_m` y `limit_m` van en m.c.a., `x_m` en m y `time_s` en s, y los dos últimos son valores
  de `x_m` y `time_s` (`test_check_shape_order_and_location`, `[medido]`).

## Conformidad con el kit

| Regla | Resultado |
|---|---|
| `kit 01 §5`: un resultado no conforme no es una excepción | `[medido]` el caso Excel, la depresión en régimen (HU-3.3) y el PN superado devuelven la respuesta completa con `status` y `checks` |
| `kit 01 §5`: idioma de los textos | `[medido]` todos los `message` están en español, con «m.c.a.», punto decimal y signo menos ASCII. Los códigos y las severidades van en inglés |
| `kit 01 §4`: `null` documentado | `[leído]` `first_*` (`schemas.py:531-545`), `michaud_head_rise_m` y `full_pulse_length_m` (`schemas.py:652-657`) dicen cuándo vienen `null` |
| `kit 01 §4`: `allow_inf_nan=False` | `[leído]` en `Check` y en `SolveResponse` |
| `kit 01 §6`: pureza | `[leído]` en `src/` no hay `print`, `open`, `os.environ`, red ni `global`. `_SEVERITY_RANK` es un dict de módulo que no se muta. `[medido]` peor caso (N = 200, 699 progresivas, 10 000 pasos, sin fotogramas): mediana de 5 ejecuciones **0.128 s**, también con un límite que nunca se cruza (−10.33) |
| `kit 02 §1`: envoltorio | `[leído]` el `RuntimeError` defensivo de `_checks.py:59` lo envuelve `_solve.py:69-71` en `MainpipeTransientComputationError` |
| `kit 01 §3`: API pública | `[leído]` sin cambios. `build_checks` y `status_of` son privados |
| `portal/` | La fase no lo toca (`git show --stat`). Los `examples/` y el `INTEGRATION.md` son de la fase 6 |

## Mutantes `[medido]` (`mut.sh`, suite completa con `-x`)

| # | Mutación | Resultado |
|---|---|---|
| M1 | `p_max > pn_head` → `>=` | muere |
| M2 | `ratio > 80` → `>=` | muere |
| M3 | `p_min < límite` → `<=` | muere |
| M4 | `p_min < 0` → `<=` | muere |
| M5 | régimen: `< límite` → `<=` (severidad) | muere |
| M6 | primer cruce: primera progresiva bajo el límite en lugar de la de menor presión | muere |
| M7 | sin comprobar el cruce en k = 0 | muere |
| M8 | orden solo por la tabla, sin la severidad | muere |
| M9 | el mensaje de COLUMN_SEPARATION_RISK usa p_min en lugar del valor del primer cruce | muere |
| M10 | `limit_m` de SUBATMOSPHERIC = límite en lugar de 0 | muere |
| M11 | umbral de PN_NEAR_LIMIT al 85 % | muere |
| M12 | `rapid` con `<` en lugar de `<=` | muere |
| M13 | `limit_m` de STEADY `error` = 0 | muere |
| M14 | primer cruce con `<=` en lugar de `<` (`_moc.py:225`) | **sobrevive** (226 passed): **F4-03** |

## Hallazgos

| ID | Severidad | Archivo:línea | Qué está mal | Evidencia |
|---|---|---|---|---|
| F4-01 | menor | `_checks.py:84-123` (`_pn_exceeded`, `_pn_near_limit`, `_column_separation`) | Por el redondeo a 1 decimal de U-26, algunos mensajes cerca del umbral se contradicen. La fase ya corrige el caso análogo «−0.0» en STEADY, pero estos no: «La presión cae a -10.0 m.c.a., por debajo del límite admisible de -10.0 m.c.a.»; «La presión máxima (244.2 m.c.a. …) supera el PN 24 bar (244.2 m.c.a.)»; «alcanza el 100.0 % del PN …» sin superarlo; «alcanza el 80.0 % … por encima del umbral de aviso del 80 %». Los valores numéricos del contrato son exactos: el problema es solo del texto | `[medido]` `edge.py`, caso sin fricción con H_dep = 144.21107 − 10.04 (p_min = −10.04), con H_PN = 244.18 m, con ratio 99.97 % y con ratio 80.03 %. Mensajes copiados arriba, literales de la salida |
| F4-02 | menor | `_moc.py:169-180` (`_global_extreme`; código de la fase 1, pero lo hereda `time_s` de PN_EXCEEDED / PN_NEAR_LIMIT) | Desempate de U-25 («primer instante») en los extremos de **presión**: el instante sale del paso en que **H** alcanza su máximo (`head_max_step`, con `>` estricto). Si dos pasos dan H distintas en 1 ulp que, al restar z, dan **la misma p/γ**, se publica el instante posterior aunque un instante anterior alcanza exactamente el mismo `pressure_head_max_global_m`. En coherencia afecta al botón «Ir a t» (D-58) y a quien compruebe U-25 sobre los fotogramas sin submuestreo | `[medido]` `tie.py`: L = 500 m, z = 28.206079336694486, f = 0, a = 900, N = 30, Q₀ = 40 L/s, H_dep = 218.08511504123348, PN 6, ρ = 1025, g = 9.78, ley (0; 40), (4; 26.5256), (8; 0), T = 14.6667 s. Con el observador del propio paquete, p/γ en x = 500 vale **197.5836794887997 en los pasos 300 (t = 5.556 s) y 420 (t = 7.778 s)**, y H vale 225.78975882549418 frente a …942. `solve` publica `pressure_head_max_global_time_s` = 7.777777777777779 y PN_EXCEEDED con «t = 7.778 s»; por U-25 correspondería 5.556 s. Aparece en 1 de 200 casos aleatorios |
| F4-03 | menor | `tests/test_checks.py` (falta un caso); `_moc.py:225` | La desigualdad estricta del primer cruce (p < límite, como el predicado de D-60) no la cubre ningún test: el mutante `<=` pasa la suite. El caso es alcanzable con una entrada válida: un perfil con un vértice exactamente en H_dep + 10 y f = 0 da p de régimen = −10.0 exacto. El código actual responde bien, pero una regresión no se vería | `[medido]` `eq.py`: perfil (0; 0), (300; 110), (1000; 0), H_dep = 100, f = 0, cierre en un paso. El código actual da `first_x_m` = 1000, `first_time_s` = 2.05 y −44.21, que coincide con mi transcripción. El mutante M14 da `first_x_m` = 300, `first_time_s` = 0.0 y `first_pressure_head_m` = −10.0, que contradice HU-3.2 crit. 2, y aun así la suite da 226 passed |

Ningún hallazgo bloqueante ni mayor.

## Lo que no comprobé

- Los fotogramas, el tamaño de la respuesta y el tiempo con fotogramas: son de la fase 5 (`frame_*` siguen en
  `null`).
- `portal/examples/`, `portal/INTEGRATION.md` y la checklist de G5: son de la fase 6. Esta fase no los toca.
- La paleta D-13 en la pantalla real del portal: solo comprobé que los `Literal` del contrato encajan en ella.
- La equivalencia de V-13 con fotogramas submuestreados: depende de la fase 5. Aquí la comprobé sobre las
  envolventes, que se acumulan sobre todos los pasos.
- Las fuentes bibliográficas [WS], [Ch], [Jk] y [Mi]: no las consulté. Las fórmulas M15–M18 las contrasté
  con el plan y con la hoja `4_Validacion` del Excel congelado.
- Vértices a menos de 10⁻⁹·L de un nodo en el muestreo aleatorio: mi transcripción no los genera. Esa fusión
  se verificó en la fase 3.

## Veredicto

**Pasa** — sin hallazgos bloqueantes ni mayores. Quedan tres menores abiertos: F4-01, F4-02 y F4-03.

## Reverificación — 2026-11-14

| | |
|---|---|
| Commit verificado | `60e19c156e7ca2400dbdd25e0dfd60473f9d5d54` (árbol limpio; solo este informe está sin seguimiento) |
| Plan | `doc/plans/01-golpe-ariete-v1.md`, sigue **congelado** (G4). El commit no lo toca |
| Kit | `KIT_VERSION = 3.0.0`; `portal/HANDOFF.md` dice 3.0.0: coinciden |
| Kit leído | `README.md`, `01`, `02`, `04` §2–3 |

Alcance del commit `[medido]` (`git diff 92a3ded 60e19c1 --stat`):

- `_moc.py` (+53/−16): las envolventes de presión se acumulan sobre p = H − z con su propio paso, y el primer
  cruce se busca cuando baja la envolvente de p.
- `tests/test_checks.py` (+96): `TIE_CASE`, `EQUAL_LIMIT_CASE` y tres tests nuevos.
- `CHANGELOG.md` y `portal/HANDOFF.md`: solo la entrada de bitácora.

No toca `_checks.py`, `_theory.py`, `_solve.py`, `schemas.py`, `__init__.py`, `pyproject.toml`,
`portal/examples/` ni el plan.

### Entornos

- **`.venv` del repo** `[medido]`: `.venv\Scripts\python -m pytest -q` da **249 passed in 4.46s**. Después,
  `git status` solo muestra este informe.
- **Venv limpio** `[medido]`: extraje `git archive 60e19c1` a un directorio temporal, creé el venv con
  `py -3.12 -m venv` (Python 3.12.10) e instalé con `pip install ./tree "pydantic==2.13.4" pytest`
  (instalación normal, no editable). Quedaron pydantic 2.13.4 y numpy 2.5.4;
  `find_spec("mainpipe_transient._moc")` apunta a `venv\Lib\site-packages\`, y no hay ninguna ruta `src` en
  `sys.path`. La suite, corrida desde el árbol extraído, da **249 passed in 4.72s** (`test_checks.py`: 104
  passed).
- Todos los scripts del verificador (`hist.py`, `minrep.py`, `runmut.py`, `mut.sh` y los de la primera
  pasada) están en el directorio temporal del verificador, fuera del repositorio, y los ejecuté contra el venv
  limpio. Los mutantes los apliqué sobre copias del árbol extraído.

### Estado de los hallazgos

| ID | Estado | Evidencia |
|---|---|---|
| F4-01 | **aceptado por el dueño** (`CHANGELOG.md`, `portal/HANDOFF.md`) | `[medido]` `edge.py` da los mismos mensajes que en la primera pasada: el código no cambió, como corresponde a una aceptación |
| F4-02 | **cerrado** en el máximo y en el mínimo. El empate del mínimo no tiene test: **F4-04** | `[medido]` en el caso del informe (`tie.py`: z = 28.206079336694486, H_dep = 218.08511504123348), `pressure_head_max_global_time_s` vale ahora 5.555555555555556 (paso 300) en lugar de 7.778. `[medido]` `hist.py` compara `solve()` con la historia completa del propio paquete (observador, en cada paso y cada progresiva). Comprueba el valor, el primer instante y la menor x de U-25 para el máximo y el mínimo globales, las envolventes por progresiva, el primer cruce (D-60, U-25) y la ubicación de los checks. En **800 casos aleatorios** (semillas 1–8 × 100, horizontales y con perfil) hay **0 discrepancias**, con 4 empates de p con H distinta en el máximo y 7 en el mínimo. El mismo script contra el venv de `92a3ded` da las 2 discrepancias esperadas en el máximo (s1-rand39 y s2-rand28) |
| F4-03 | **cerrado** | `[medido]` el mutante M14 (`<=` en el primer cruce) ahora muere en `test_f403_…`. `eq.py` da `first_x_m` = 1000, `first_time_s` = 2.05 y −44.21, y STEADY `warning` con −10.0 / 0.0 |

`[leído]` La guarda `if higher.any() or lower.any()` (`_moc.py:297`) es correcta. Para una z fija, fl(H − z) es
monótona no decreciente en H, y la envolvente de p es fl(H_max − z). Por eso, si p sube estrictamente en una
progresiva, H también supera su máximo (y lo mismo al bajar). Los mutantes M17 y M18, que dejan la guarda con
un solo lado, mueren.

### Criterio de «hecho», repasado `[medido]`

- **V-11**: `excel.py` da ΔH_J con rel. 0.0, ΔH_MOC con rel. 3.8·10⁻¹⁶, la desviación con rel. 1.06·10⁻¹⁴ y
  el pulso con diferencia 0.0. En el caso lento, Michaud = 28.842214174542136 (rel. 0.0 con la fórmula). Primer
  cruce del Excel: t = 3.3 s, x = 950 m y −13.497785396184817 (la malla del Excel da −13.497785396184796).
- **V-12**: H_PN = 254.841997961264 y el ratio con rel. 1.5·10⁻¹⁶ frente a la hoja. La conversión con ρ y g
  coincide bit a bit.
- **V-13**: `indep.py` (mi transcripción escalar) con la semilla 1 × 100 y los casos con nombre: **todo ok**.
  Con la semilla 2 × 100 hay 5 diferencias de instante o progresiva en empates (rand17, rand38, rand62, rand87
  y rand94), y las 5 aparecen también contra `92a3ded`. La comparación decisiva para U-25 es con la historia
  en coma flotante del propio paquete (`hist.py`, arriba), y ahí no hay ninguna diferencia. Son ruido de
  redondeo de mi transcripción: empates que mis `float` producen y los del paquete no, o al revés. Contra
  `92a3ded` también discrepaba rand28, que era F4-02 y ya no aparece.
- **Textos literales**: `lit.py` da `HU-3.1-4 literal: True` y `HU-3.2-4 literal: True`.
- **Tiempo**: en el peor caso (N = 200, 699 progresivas, 10 000 pasos, sin fotogramas), la mediana es
  **0.146 s** (antes, 0.128 s). El coste añadido de las envolventes de p no pone en riesgo el objetivo de
  < 1 s (`kit 01 §6`).

### Mutantes `[medido]` (`mut.sh`, suite completa con `-x`, sobre `60e19c1`)

Los mutantes M1–M14 de la primera pasada **mueren todos**, también M14. Los nuevos, sobre el cambio de este
commit:

| # | Mutación | Resultado |
|---|---|---|
| M15 | `p_higher = st_p >= p_max` (último instante del empate) | muere |
| M16 | `p_lower = st_p <= p_min` | muere |
| M17 | guarda solo con `higher.any()` | muere |
| M18 | guarda solo con `lower.any()` | muere |
| M19 | máximo global con `head_max_step` (comportamiento anterior) | muere |
| M20 | mínimo global con `head_min_step` (comportamiento anterior, `_moc.py:173`) | **sobrevive** (249 passed): **F4-04** |
| M21 | desempate por x antes que por instante | muere |
| M22 | sin actualizar `p_max_step` | muere |

### Hallazgos nuevos

| ID | Severidad | Archivo:línea | Qué está mal | Evidencia |
|---|---|---|---|---|
| F4-04 | menor | `tests/test_checks.py:520-545` (falta un caso); `_moc.py:173` | La corrección de F4-02 cubre los dos extremos, pero los tests solo prueban el empate de p con H distinta en el **máximo**. Si el mínimo vuelve a usar el paso de H (M20), toda la suite pasa. El caso es alcanzable y afecta a un check: el `time_s` de COLUMN_SEPARATION_RISK / SUBATMOSPHERIC_PRESSURE es el instante del mínimo global. El código actual da el valor correcto | `[medido]` `runmut.py mt20` con `hist.py` en 800 casos: M20 publica un instante incorrecto en 3 (s5-rand23, s7-rand32 y s7-rand82). `minrep.py`, caso s5-rand23: perfil x = (0; 79.969; 181.099; 245.039; 323.393; 444.954; 500), z = (0; −3.4748182177556437; 21.178338131466013; 31.01524372045673; −3.878710106476934; 54.777384027393; −2.505818076104738), D = 300 mm, a = 1250, f = 0, Q₀ = 100 L/s, H_dep = 52.663473975976785, N = 40, ley (0; 100), (0.5; 10.797511596483291), (1; 0), T = 5.8 s, límite −10.33, ρ = 1025 y g = 9.81. En x = 444.954 m, p mín. = −162.91373976618752 en los pasos 155, 315 y 475; H vale −108.1363557387945 en el 155 y …452 en los otros dos. Con `60e19c1`, `solve` da `time_s` = 1.55 en COLUMN_SEPARATION_RISK, como pide U-25. M20 da 3.15 y la suite no lo detecta |

Ningún hallazgo bloqueante ni mayor.

### Lo que no comprobé en la reverificación

- Lo mismo que en la primera pasada: los fotogramas y la equivalencia con fotogramas submuestreados (fase 5);
  `portal/examples/`, `portal/INTEGRATION.md` y la checklist de G5 (fase 6); la paleta D-13 en la pantalla
  real; las fuentes bibliográficas [WS], [Ch], [Jk] y [Mi].
- Las entradas de bitácora de `portal/HANDOFF.md` y `CHANGELOG.md` solo las leí `[leído]`. Son coherentes con
  el estado de F4-01, F4-02 y F4-03 que medí.
- Empates de p con H distinta en progresivas de vértice a menos de 10⁻⁹·L de un nodo: mi generador no las
  produce.

### Veredicto de la reverificación

**Pasa**: sin hallazgos bloqueantes ni mayores. F4-02 y F4-03 quedan cerrados y F4-01 lo aceptó el dueño.
Queda abierto un menor nuevo, F4-04, que solo afecta a la cobertura de tests.
