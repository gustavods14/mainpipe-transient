# Verificación — Fase 3 (perfil real)

| | |
|---|---|
| Fase | 3: perfil (plan 01 §5) |
| Commit verificado | `2febc3f56b59bd67ee23535e80995155608cc1b6` (rama `hie/etapas-0-3`, árbol limpio) |
| Plan | `doc/plans/01-golpe-ariete-v1.md`, estado **congelado** (G4, 2026-11-14) |
| Kit | `KIT_VERSION = 3.0.0` (portal `C:\Dev\web_apps`). `portal/HANDOFF.md` dice 3.0.0: coinciden |
| Verificador | `hie-verifier`, 2026-11-14 |
| Kit leído | `README.md`, `01` (entero, con foco en §2–6 y §9), `02`, `04` §2–3 |

Alcance del commit `[medido]` (`git show --stat 2febc3f`): `_geometry.py` (+109), `_moc.py`, `_solve.py`,
`schemas.py` (+68), `tests/test_profile.py` (nuevo, 28 tests), `CHANGELOG.md` y `doc/DECISIONS.md`
(U-38 con la medición del peor caso con perfil). No toca `portal/`, `__init__.py` ni `pyproject.toml`.

## Entornos de ejecución

- **`.venv` del repo** `[medido]`: `.venv\Scripts\python -m pytest -q` da **143 passed in 2.81s**.
  Después, `git status` sigue limpio.
- **Venv limpio con el pin del portal** `[medido]`: extraje `git archive 2febc3f` en un directorio
  temporal, creé el venv con `py -3.12 -m venv` e instalé con `pip install ./tree "pydantic==2.13.4" pytest`
  (instalación normal, no editable). Quedaron pydantic 2.13.4 y numpy 2.5.4. `find_spec` sitúa
  `mainpipe_transient._geometry` en `venv\Lib\site-packages\`. Ejecuté la suite desde el árbol extraído,
  sin `src/` en `sys.path`: **143 passed in 2.99s**, y `tests/test_profile.py` solo da **28 passed**.
- Mis scripts (`probe.py`, `excel_prof.py`, `edges.py`, `peak.py`, `mut.sh`) están en el directorio
  temporal del verificador, fuera del repositorio. Los ejecuté contra el venv limpio. Los mutantes se
  aplicaron sobre una copia del árbol extraído.

## Criterio de «hecho» de la fase (literal del plan) y resultado

> Fase 3, «Hecho cuando»: «V-10 en verde».
> V-10: «Perfil (M13–M14) · HU-2.1 y HU-2.2 (perfil plano de 2 puntos, loma 40 m, vértice en 520 m,
> L = 1250 m) · identidades · ± 10⁻⁶ m; loma: p_min(500) = p_min horizontal − 40 ± 10⁻⁶ m».

| Caso de V-10 | Test del repo | Comprobación independiente | Resultado |
|---|---|---|---|
| Perfil plano de 2 puntos = horizontal (HU-2.1 crit. 3) | `test_hu21_crit3_two_point_flat_profile_equals_horizontal` (igualdad exacta del dict) | `[medido]` `probe.py`: `solve` con perfil (0; 0), (1000; 0) frente al horizontal (L = 1000 m, z = 0 m). Fuera de `geometry`, los dos dicts son **iguales bit a bit** | cumple |
| Loma de 40 m: p_min(500) = p_min horizontal − 40 (HU-2.2 crit. 3) | `test_hu22_crit3_loma_lowers_minimum_pressure_by_its_height` | `[medido]` p_min(500) con loma = −48.62337386907075 m, horizontal = −8.623373869070743 m, **diferencia frente a −40 = 0.0** | cumple |
| Vértice en 520 m entre los nodos 500 y 550 (HU-2.2 crit. 1) | `test_hu22_crit1_vertex_between_nodes_is_a_station`, `test_m14_vertex_head_is_interpolated_at_every_step` | `[medido]` `x_m` contiene 520 con `x_is_node` = false, `elevation_m` = 33.0 (la cota del vértice) y 22 progresivas | cumple |
| L = 1250 m (HU-2.1 crit. 4) | `test_hu21_crit4_length_is_last_chainage` | `[medido]` `length_m` = 1250.0, `dx_m` = 62.5, `reflection_time_s` = 2.5 | cumple |
| z(250) = 20 en la loma (HU-2.1 crit. 2) | `test_hu21_crit2_loma_elevation_and_pressure_identity` | `[medido]` cumple a 10⁻⁶ | cumple |

**V-10 en verde**: se cumple el criterio de «hecho».

## Fórmulas (M13, M14, U-07) frente al plan

| Elemento | Plan | Código | Comprobación |
|---|---|---|---|
| L con perfil | L = última progresiva (HU-2.1, §1.4) | `schemas.py:310-316` (`pipe_length_m`), `_geometry.py` (`length_m = px[-1]`) | `[medido]` L = 1250 |
| z(x) | lineal entre vértices (M13) | `np.interp(x, px, pz)` en los nodos; z del vértice en los vértices | `[medido]` contra mi transcripción, abajo |
| Progresivas | nodos ∪ vértices, ordenados, sin duplicados; fusión a menos de 10⁻⁹·L conservando la z del vértice (U-07) | `build_profile_mesh` | `[medido]` vértice a 500 + 5·10⁻⁷ m se funde y a 500 + 1.0000001·10⁻⁶ m no (L = 1000 m). Hay un caso límite con dos vértices fundidos en el mismo nodo: **F3-02** |
| H en un vértice fuera de nodo | interpolación lineal entre los nodos vecinos **en cada paso** (M14) | `Mesh.station_head`, llamada dentro del bucle (`_moc.py:227`) | `[medido]` envolventes = máximo y mínimo en el tiempo del H interpolado, a 2.3·10⁻¹² m (abajo) |
| Q en vértices | no se calcula (M14, U-07 enmienda D-57) | no se interpola | `[leído]` |
| p/γ | H − z del punto (M13) | `pressure_head_* = head_* − station_elevation_m`; serie en la válvula con z[N], en el punto medio con z(L/2) interpolada | `[medido]` |
| H y Q en los nodos | no dependen del perfil (M13) | la cota no entra en el bucle | `[medido]` contra el Excel, abajo |

**Transcripción independiente** `[medido]` (`probe.py`). Escribí un MOC propio nodo a nodo a partir de
M1–M12 y una construcción propia de las progresivas según U-07 / M14, sin reutilizar código del paquete.
Lo comparé con `solve()` en **25 perfiles aleatorios** (N ∈ {10, 20, 36, 50, 120}, L entre 300 y 3000 m,
de 2 a 30 vértices, algunos exactamente en nodos, f entre 0 y 0.03; 3 casos dieron un 422 legítimo por
duración y los descarté). Comparé `x_m`, `elevation_m`, `head_initial/max/min_m`,
`pressure_head_max/min_m`, las series de la válvula, el punto medio y el depósito, los extremos globales
y su lugar e instante con el desempate de U-25. Error máximo: **2.33·10⁻¹²**, y todos los lugares e
instantes coinciden.

**HU-2.1 crit. 1 contra la referencia congelada** `[medido]` (`excel_prof.py`). Usé el caso del Excel
con tres perfiles: loma, el «genérico» de los tests y uno descendente. Las series de H y Q y las
envolventes de H en los nodos difieren de `tests/reference/excel_case.json` (`grid.head_m`,
`grid.flow_m3s`) en **5.97·10⁻¹³** como máximo.

**Extremo global en un vértice fuera de nodo** `[medido]` (`peak.py`). Con el perfil (0; 0), (510; 30),
(520; 60), (530; 30), (1000; 0), `pressure_head_min_global_m` = −69.733 m en x = 520 (`x_is_node` =
false). El mínimo solo en los nodos sería −53.028 m. El código acierta, pero ningún test lo protege
(**F3-01**).

## Unidades de extremo a extremo

`profile_x_m` (m) → L, Δx, Δt (m, s). `profile_z_m` (m) → `elevation_m` (m) → p/γ = H − z (m.c.a.).
La fase no introduce ningún factor de conversión. Los de L/s y mm (`_solve.py`) no cambian y ya los
ejercía la fase 1. `[leído]` y `[medido]` (comparaciones de arriba).

## Validación del perfil (HU-2.3, U-22) y mensajes

| Criterio | Test | Mensaje medido `[medido]` (`edges.py`) |
|---|---|---|
| crit. 1, no creciente | `test_hu23_crit1_*` | «La progresiva del perfil (profile_x_m) debe ser estrictamente creciente: x[3] = 120 m es menor que x[2] = 300 m.» Es el texto literal de la historia; la notación choca con la de otros mensajes (**F3-03**) |
| crit. 2, 2–500 puntos y misma longitud | `test_hu23_crit2_*` | lista vacía: «El perfil debe tener entre 2 y 500 puntos; profile_x_m tiene 0.» 500 puntos se aceptan |
| crit. 3, x[0] ≠ 0 | `test_hu23_crit3_*` | «El perfil debe empezar en x = 0 m (el depósito): profile_x_m[0] = 10 m.» Con x[0] = −0.0 se acepta |
| crit. 4, toma por encima del depósito | `test_hu23_crit4_*` | da los dos valores en m. z[0] = nivel se acepta (mutante `>` → `>=`: 1 test falla) |
| crit. 5 y U-22, datos de la otra geometría | `test_hu23_crit5_*`, `test_u22_*` | en español, dice qué datos van con cada geometría |
| NaN / inf / tipo en el perfil | — | «profile_x_m (punto 2): debe ser un número finito.», «profile_z_m (punto 2): debe ser un número finito.», «profile_x_m (punto 4): debe ser un número.» |
| Topes U-03 / U-09 con la L del perfil | `test_profile_step_cap_uses_profile_length` | L = 1250 m y N = 200: T = 62.5 s calcula con 10 000 pasos; T = 62.6 s da 422 con «62.5 s». L = 1e300 da el 422 de φ y L = 1e-300 el del tope, ambos en español y sin excepciones ajenas |

## Conformidad con el kit

| Regla | Resultado | Evidencia |
|---|---|---|
| `kit 01 §2–3` layout y API pública | sin cambios en la fase; cumple | `[leído]` `__init__.py` no se toca; `[medido]` los módulos están en el wheel |
| `kit 01 §4` series en columnas alineadas, `allow_inf_nan=False` | cumple | `[medido]` las 8 columnas de envolventes tienen la misma longitud que `x_m`, que es estrictamente creciente (test parametrizado y `probe.py`) |
| `kit 01 §5` resultado no conforme ≠ excepción | sin cambios (los `checks` son de la fase 4); una piezométrica bajo el perfil calcula y no lanza | `[medido]` el peor caso de U-34 calcula con p_min < 0 |
| `kit 01 §6` pureza | cumple | `[leído]` ni `print`, ni `open`, ni `os.environ`, ni `global` en `src/`; los arrays de `Mesh` quedan congelados (`setflags(write=False)`). Solo hay `logging` |
| `kit 01 §6` tiempo | cumple | `[medido]` peor caso con perfil (N = 200, 699 progresivas, 10 000 pasos, sin fotogramas): 0.134, 0.134, 0.135, 0.135, 0.135 s, **mediana 0.135 s** (U-38 anota 0.133 s) |
| `kit 02` excepciones y mensajes en español | cumple, con el detalle de F3-03 | tabla anterior |
| `portal/` | la fase no lo toca | `[medido]` `git show --stat` |

## Mutantes `[medido]` (`mut.sh`, suite completa con `-x`)

| Mutante | Resultado |
|---|---|
| M1 sin conservar la z del vértice fundido | 1 failed |
| M2 peso de interpolación invertido | 1 failed |
| M4 z del vértice interpolada de los nodos | 1 failed |
| M5 tolerancia de fusión 10⁻¹² | 1 failed |
| M6 H del vértice = nodo izquierdo | 1 failed |
| **M7 extremo global de presión buscado solo en los nodos** | **143 passed** (sobrevive, F3-01) |
| M8 z del punto medio = z(0) | 1 failed |
| M9 tolerancia de fusión 10⁻⁶ | 1 failed |
| M10 toma con `>=` en lugar de `>` | 1 failed |

## Hallazgos

| ID | Severidad | Archivo:línea | Qué está mal | Evidencia |
|---|---|---|---|---|
| F3-01 | menor | `tests/test_profile.py:233-250` (`test_hu22_crit2_global_extremes_and_aligned_columns`); código en `src/mainpipe_transient/_moc.py:147-157` | **Ningún test hace que el extremo global de presión caiga en un vértice fuera de nodo**, que es justo lo que pide HU-2.2 («no perder un punto alto que caiga entre dos nodos»). En los tres perfiles del test parametrizado (loma, genérico, vértice en 520) el mínimo y el máximo globales caen en un nodo, así que el aserto `pressure_head_min_global_m == min(pressure_head_min_m)` no distingue entre buscar en todas las progresivas o solo en los nodos. Hoy el código es correcto. Para comprobarlo: cambiar `value = pick(envelope)` por `value = pick(envelope[self.mesh.station_is_node])` en `_moc.py:150` y ejecutar la suite; debería fallar algún test | `[medido]` el mutante M7 sobrevive con **143 passed**. `[medido]` con el perfil (0; 0), (510; 30), (520; 60), (530; 30), (1000; 0), el paquete da −69.733 m en x = 520 (`x_is_node` = false); con M7 daría el mínimo de los nodos, −53.028 m, 16.7 m menos severo, sin que la suite lo detecte |
| F3-02 | menor | `src/mainpipe_transient/_geometry.py:136-139` | **Si dos vértices caen a menos de 10⁻⁹·L del mismo nodo, el nodo toma la cota del último**, y los dos vértices desaparecen de `x_m`. Un punto alto puede perderse según el orden: el comentario del código («the vertex is the high point») y U-07 («z es la del vértice») no cubren dos vértices. Solo ocurre con vértices separados menos de 10⁻⁹·L (1 µm con L = 1 km), lo que en la práctica es un escalón vertical | `[medido]` (`edges.py`) x = [0, 500, 500 + 1e-7, 1000], z = [0, 40, 0, 0] → 21 progresivas y `elevation_m(500)` = **0.0**: la loma de 40 m no aparece. En orden inverso, x = [0, 500 − 1e-7, 500, 1000], z = [0, 0, 40, 0] → `elevation_m(500)` = 40.0 |
| F3-03 | menor | `src/mainpipe_transient/schemas.py:378-385` (y `:374-376`) frente a `_solve.py:200-206` | **Se mezclan dos notaciones de posición para el mismo punto del perfil.** El mensaje de progresiva no creciente usa índices desde 0 («x[3] = 120 m» para el 4.º punto), mientras que los errores de tipo del mismo campo cuentan desde 1 («profile_x_m (punto 4)»), igual que los mensajes de la ley de cierre («el punto 2»). F2-04 (b) unificó la numeración desde 1. Aquí el código sigue literalmente HU-2.3 crit. 1, que escribe «x[3]» y «x[2]», así que la incoherencia está en la historia y el código la hereda. El valor en metros acompaña al índice, y eso permite localizar el punto | `[medido]` con [0, 150, 300, 120, 600]: «…x[3] = 120 m es menor que x[2] = 300 m.» Con [0, 150, 300, "a", 600]: «profile_x_m (punto 4): debe ser un número.» El mismo punto aparece como `[3]` y como «punto 4» |

No hay hallazgos **bloqueantes** ni **mayores**.

### Observaciones (sin ID, no cuentan para el veredicto)

- **Plan, incoherencia interna** `[leído]`: la fila de la fase 3 en §5 dice «interpolación de z, H y Q
  en vértices», mientras que M14 y U-07 (enmienda D-57) dicen que Q no se calcula en los vértices. El
  código sigue M14, que es lo vigente. Queda para `hie-architect`, si quiere corregir el texto.
- **Magnitudes absurdas en el perfil dan 500, no 422** `[medido]`: z = [1e308, −1e308] con nivel 1e308,
  o z = [−1e308, 1e308, −1e308], desbordan en la interpolación o en H − z, y salen como
  `MainpipeTransientComputationError` (500) con el mensaje genérico. Las dos excepciones de pydantic
  quedan envueltas y no se escapa ninguna excepción ajena. Es el mismo comportamiento que la fase 2
  aceptó para `reservoir_level_m` = 1e308 (HU-1.6 crit. 11).

## Lo que no comprobé

- La física del perfil más allá de las identidades del plan: el término V·sen α despreciado (U-05) no
  se contrasta con ninguna solución que lo incluya. V-10 solo exige identidades.
- `checks`, `status` y los fotogramas (fases 4 y 5): siguen vacíos o en `null`, como dice el plan.
- `portal/examples/` e `INTEGRATION.md`: la fase no los toca. Se revisan en la fase 6 y en G5.
- No volví a verificar F2-05 ni F2-06 (cerrados en `bc0a736`), salvo que la suite completa sigue en verde.
- La transcripción aleatoria cubre 22 perfiles válidos, no un barrido exhaustivo. No hice un barrido
  aleatorio de magnitudes extremas como el de la fase 2: solo los casos puntuales de `edges.py`.
- Tiempo con fotogramas (V-16 completa): es de la fase 5.

## Veredicto

**Pasa**: V-10 en verde y medido de forma independiente, sin bloqueantes ni mayores. Quedan tres menores
abiertos: F3-01 (falta un test con el extremo global en un vértice fuera de nodo), F3-02 (dos vértices
fundidos en el mismo nodo) y F3-03 (notación de posición desde 0 frente a desde 1).

## Reverificación — 2026-11-14

| | |
|---|---|
| Commit verificado | `38c56fa2df2bffcd0da17dcfaaec90942fd96cf6` (rama `hie/etapas-0-3`, 7 commits por delante de `origin`: sin empujar; único cambio en el árbol: este informe, sin seguimiento) |
| Plan | `doc/plans/01-golpe-ariete-v1.md`, estado **congelado**. No cambia desde `2febc3f` `[medido]` (`git diff --stat 2febc3f 38c56fa -- doc/plans/` vacío) |
| Kit | `KIT_VERSION = 3.0.0`. `portal/HANDOFF.md` dice 3.0.0: coinciden. Releídos `README.md`, el índice de `01`, `02` §3 y el índice de `04` |
| Verificador | `hie-verifier`, 2026-11-14 |

Alcance del commit `[medido]` (`git show --stat 38c56fa`): `schemas.py` (solo el texto del mensaje de
progresiva no creciente, 2 líneas), `tests/test_profile.py` (+2 tests parametrizados y 2 asertos
actualizados), `CHANGELOG.md` y `portal/HANDOFF.md` (nota). No toca `_moc.py`, `_geometry.py`,
`_solve.py`, `__init__.py`, `pyproject.toml`, `portal/examples/` ni el plan.

### Entornos

- **`.venv` del repo** `[medido]`: `.venv\Scripts\python -m pytest -q -o addopts=""` da **145 passed in 2.75s**.
  Después, `git status` solo muestra este informe.
- **Venv limpio** `[medido]`: `git archive 38c56fa` extraído en el directorio temporal del verificador,
  `py -3.12 -m venv` (Python 3.12.10), `pip install ./tree "pydantic==2.13.4" pytest` (instalación normal).
  Quedaron pydantic 2.13.4 y numpy 2.5.4, y `find_spec` sitúa `mainpipe_transient.schemas` en
  `venv\Lib\site-packages\`. Desde el árbol extraído: suite completa **145 passed in 2.93s** y
  `tests/test_profile.py` solo **30 passed**.
- Mis scripts (`rev.py`, `mv.py`) están en el directorio temporal, fuera del repositorio. Los mutantes se
  aplicaron a la copia instalada en el venv limpio y después se restauraron (`cmp` idéntico, 145 passed).

### Estado de los hallazgos

| ID | Estado | Evidencia |
|---|---|---|
| F3-01 (menor) | **cerrado** | `[leído]` `tests/test_profile.py:226-243`, `test_f301_global_extreme_on_a_vertex_that_is_not_a_node`, con dos casos: pico de 60 m en x = 520 y valle de −60 m en x = 970, ninguno en un nodo con N = 20. `[medido]` (`rev.py`): pico → `pressure_head_min_global_m` = −69.733 m en x = 520, frente a −37.899 m buscando solo en los nodos; valle → `pressure_head_max_global_m` = 302.598 m en x = 970, frente a 242.764 m solo en los nodos. Las dos diferencias superan con holgura los 10 m del aserto. Mutantes sobre `_moc.py:150`: M7 (los dos extremos solo en los nodos) → **2 failed**; solo el mínimo → **1 failed**; solo el máximo → **1 failed**. En la verificación anterior, M7 sobrevivía con 143 passed |
| F3-02 (menor) | **aceptado** (no corregido) | `[leído]` `portal/HANDOFF.md`, nota del 2026-11-14, y `CHANGELOG.md`: «aceptado por el dueño». Un verificador no puede comprobar una aceptación; solo consta que está anotada. `[medido]` el comportamiento no cambia: x = [0, 500, 500 + 1e-7, 1000], z = [0, 40, 0, 0] → 21 progresivas y `elevation_m(500)` = 0.0. Queda fuera del veredicto por la aceptación |
| F3-03 (menor) | **cerrado** | `[medido]` (`rev.py`, `mv.py`): «La progresiva del perfil (profile_x_m) debe ser estrictamente creciente: x[3] = 120 m (punto 4) es menor que x[2] = 300 m (punto 3).» y «…x[2] = 300 m (punto 3) es igual a x[1] = 300 m (punto 2).». Por la vía de FastAPI (`SolveRequest.model_validate`), el mismo texto con el prefijo «Value error, », 145 caracteres (menos de 400, `kit 02 §3`). El mismo punto con tipo erróneo sigue dando «profile_x_m (punto 4): debe ser un número.» y con NaN «…debe ser un número finito.»: la posición desde 1 coincide ahora en todos los mensajes del campo |

### Criterio de «hecho» de la fase, repasado

V-10 sigue en verde `[medido]` (`rev.py`, venv limpio): loma, p_min(500) − (p_min horizontal − 40) = **0.0**;
perfil plano de 2 puntos igual al horizontal, fuera de `geometry`, **igual bit a bit**. El commit no toca
el cálculo (`_moc.py`, `_geometry.py`, `_solve.py`), así que no repetí la transcripción independiente de 25
perfiles, la comparación con `excel_case.json` ni la medición de tiempo de la primera verificación. Los tests
que las cubren en la suite siguen en verde.

Conformidad con el kit: sin cambios respecto de la primera verificación. El único cambio en `src/` es un
texto para el usuario, que sigue en español, nombra el campo y el valor con unidades y no lleva trazas
(`kit 02 §3`). `portal/examples/` e `INTEGRATION.md` no se tocan.

### Hallazgos nuevos

Ninguno.

### Observaciones (sin ID, no cuentan para el veredicto)

- **Literal de HU-2.3 crit. 1** `[medido]`: la historia dice que el mensaje «señala que x[3] = 120 m es
  menor que x[2] = 300 m». Con «(punto 4)» intercalado, esa cadena ya no aparece seguida en el mensaje,
  aunque todos sus datos siguen ahí. Lo considero cumplido en su sentido. Si se quiere el literal exacto,
  lo decide `hie-product-owner` en la historia.
- **Trazabilidad** `[medido]`: `CHANGELOG.md` y `portal/HANDOFF.md` en `38c56fa` citan
  `doc/verification/04-fase-3.md`, pero ese archivo no está en ningún commit (`git status`: sin
  seguimiento). Hay que confirmarlo junto con esta reverificación para que las referencias resuelvan.
- La nota de `portal/HANDOFF.md` da F3-01 y F3-03 por «corregidos» antes de esta reverificación. Ahora
  coincide con lo medido.
- Sigue en pie la incoherencia interna del plan señalada en la primera verificación (la fila de la fase 3
  en §5 habla de interpolar Q en los vértices, M14 y U-07 dicen que no se hace). El plan no ha cambiado.

### Lo que no comprobé en la reverificación

- Todo lo listado en «Lo que no comprobé» de la primera verificación.
- No repetí la transcripción independiente, la comparación con el Excel, el tiempo del peor caso ni los
  mutantes M1–M10 distintos de M7, porque el commit no toca el código de cálculo. Solo lo comprobé con
  `git diff --stat` y la suite.
- No puedo comprobar la aceptación del dueño de F3-02: solo leí la nota.
- `pip install git+…` del commit: no está empujado.

### Veredicto de la reverificación

**Pasa**: V-10 en verde en el venv limpio, F3-01 y F3-03 cerrados y medidos, F3-02 aceptado por el dueño
según la nota; sin bloqueantes ni mayores, y sin hallazgos nuevos.
