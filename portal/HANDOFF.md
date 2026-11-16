# mainpipe-transient — Handoff al portal Fluida

| | |
|---|---|
| Slug del portal | `mainpipe-transient` |
| Paquete Python | `mainpipe_transient` |
| Distribución | `mainpipe-transient` |
| Repositorio | https://github.com/gustavods14/mainpipe-transient |
| Kit con el que se diseñó | `3.0.1` (adoptada el 2026-11-15 tras la entrega, F6-04; etapas 0–6 diseñadas con `3.0.0`) |
| Versión del contrato (`SCHEMA_VERSION`) | `2.0` (congelada en la nueva G4, 2026-11-15) — antes `1.0` |
| Commit a pinear | `a04431e1dc741acfce305c6f7cfca3cdfa57e96c` (etiqueta `v0.1.0`, rama `main`) |

## Etapas

| # | Etapa | Estado | Fecha | Artefacto | Kit |
|---|---|---|---|---|---|
| 0 | Inicio | aprobada | 2026-11-14 | `portal/HANDOFF.md` | 3.0.0 |
| 1 | Historias (G1) | aprobada | 2026-11-15 | `doc/stories/` | 3.0.0 |
| 2 | Plan (G2) | aprobada | 2026-11-15 | `doc/plans/` · `portal/DECISION-REQUESTS.md` · `portal/API-PROPOSAL.md` | 3.0.0 |
| 3 | Prototipo (G3) | aprobada | 2026-11-15 | `portal/ui-spec.json` · `portal/prototype.html` | 3.0.0 |
| 4 | Decisiones del portal (G4) | aprobada | 2026-11-15 | `D-NN` en el portal · plan `congelado` | 3.0.0 |
| 5 | Construcción (G5) | aprobada | 2026-11-15 | `src/` · `portal/INTEGRATION.md` · `portal/examples/` · `doc/verification/` | 3.0.0 |
| 6 | Entrega | aprobada | 2026-11-15 | commit `a04431e` + etiqueta `v0.1.0` | 3.0.0 |

Estados: `pendiente` · `en curso` · `aprobada` (puerta pasada) · `reabierta`.

## Checklist de entrega

Ver `doc/upstream-kit/04-handoff.md` §3 en el portal.

## Notas

(Cualquier desvío del kit, con su `DR-N`.)

- 2026-11-14: el portal resolvió DR-1..DR-6 (D-57 a D-62, commit `2466321` del portal). Se
  reabren las etapas 1–3 para incorporarlas: HU-4.1 crit. 1 (D-57), plan (D-57..D-62) y
  `ui-spec.json` / `prototype.html` (D-58..D-62). Detalle en `portal/DECISION-REQUESTS.md`,
  «Pendiente tras las decisiones».
- 2026-11-14: G1 aprobada de nuevo tras incorporar D-57 (HU-4.1 crit. 1 sin `frame_flow_lps`,
  HU-1.6 crit. 13: 422 al superar el tope de pasos) y alinear el reproductor con D-58.
- 2026-11-14: G2 aprobada de nuevo tras incorporar D-57..D-62 al plan (`MAX_STEPS` = 10 000,
  tope de fotogramas min(1001, ⌊50 000/n⌋), sin `frame_flow_lps` — U-33, eco
  `min_allowed_pressure_head_m` — U-35). El dueño acepta la regla de ajuste de U-34 (bajar el
  presupuesto de celdas si la medición supera 3,5 MB) en lugar de abrir un DR-7, el 422 para la
  duración por defecto fuera de tope (U-09) y la lectura 3,5 MB = 3 500 000 B.
- 2026-11-14: G3 aprobada de nuevo tras incorporar D-57 … D-62 a `portal/ui-spec.json` y
  `portal/prototype.html`: tope de 10 000 pasos y su 422 (D-57); instante como estado del panel,
  teclado y «Ir a t = … s» (D-58); barra de una fila, sticky solo ≥ lg con `lg:top-20` (D-59);
  colores con roles documentados y rojo solo en el cruce (D-60); fórmulas en HTML (D-61); sin
  sección `ai` (D-62); límite leído de `response.min_allowed_pressure_head_m` (U-35). Esquema
  validado con jsonschema; 73 `contract_path` presentes en el plan §1, sin huecos. Hallazgos para
  el kit: el esquema de `ui-spec.json` no tiene lugar para fórmulas (D-61) ni para acciones dentro
  de un aviso («Ir a t», descrito en `interactions`).
- 2026-11-14: G4 aprobada. DR-1 … DR-6 resueltos (D-57 … D-62), ninguno bloqueante abierto; plan
  `doc/plans/01-golpe-ariete-v1.md` congelado con `SCHEMA_VERSION` = `"1.0"` (U-37). El dueño
  acepta U-03, U-14, U-21, U-22, U-34 (6) y U-35 como vigentes y el riesgo de U-34: si la respuesta
  del peor caso supera 3 500 000 B en la fase 5, se bajan fotogramas sin abrir pedido y el tope
  efectivo se publica en `portal/INTEGRATION.md`.
- 2026-11-14: etapa 5 en curso. Fase 0 del plan (andamiaje y referencia del Excel, U-28)
  entregada en `905e53a` y verificada por `hie-verifier`: **pasa**
  (`doc/verification/01-fase-0.md`). Menores: F0-01 y F0-02 aceptados por el dueño; F0-03
  (este estado) corregido.
- 2026-11-14: fase 1 entregada en `9d1d9b4`; `hie-verifier` **no pasa** solo por F1-01 (faltaba
  HU-1.7, `doc/verification/02-fase-1.md`). `hie-product-owner` restaura HU-1.7 sin cambiar el
  alcance y G1 se aprueba de nuevo con ella: el dueño acepta el crit. 4 (`duration_s` devuelta =
  duración efectiva, 20.01 → 20.05 s) y que el crit. 5 (< 1 s con N = 200 y 10 000 pasos) se
  mide en la fase 2. Tests de HU-1.7 crit. 1, 2 y 4 añadidos y F1-03 corregido (referencia de
  Allievi con interpolación propia). F1-02 pasa a la fase 2.
- 2026-11-14: reverificación de la fase 1 sobre `a870561`: **pasa** (F1-01 y F1-03 cerrados).
  Pasan a la fase 2: F1-02 (V-05 vía `solve()`), F1-04 (ningún test ejerce la tolerancia 10⁻⁹
  de U-08; corregir el comentario «400.000…1») y F1-05 (n_reaches por defecto, eco en la
  respuesta y 422 de la duración por defecto, probados a través de `solve()`).
- 2026-11-14: fase 2 del plan (contrato y topes) entregada en `61d9756`; `hie-verifier` no pasa
  por F2-01 (excepciones ajenas con magnitudes extremas), corregido con F2-02 … F2-04 en `f29ae4d`
  y reverificado: **pasa** (`doc/verification/03-fase-2.md`). Menores nuevos F2-05 (test de F2-03
  con el Tc equivocado) y F2-06 (φ = inf en el mensaje) corregidos después. Provisionales hasta su
  fase: `profile` (3), `checks` (4), `frame_*` (5).
- 2026-11-14: fase 3 del plan (perfil) entregada en `2febc3f`; `hie-verifier` **pasa**
  (`doc/verification/04-fase-3.md`), sin bloqueantes ni mayores. Menores: F3-01 (test del extremo
  global en un vértice fuera de nodo) y F3-03 (mensaje con «(punto N)» además del literal de
  HU-2.3 crit. 1) corregidos; F3-02 (dos vértices a menos de 10⁻⁹·L del mismo nodo: el nodo toma la
  cota del último) **aceptado por el dueño**, por ser un escalón vertical sin sentido físico.
- 2026-11-14: fase 4 del plan (verificaciones) entregada en `92a3ded`; `hie-verifier` **pasa**
  (`doc/verification/05-fase-4.md`), sin bloqueantes ni mayores. Menores: F4-02 (instante del
  extremo de presión con empate de p/γ y H distinta en 1 ulp) y F4-03 (test de igualdad con el
  límite) corregidos; F4-01 (mensajes contradictorios por el redondeo a 1 decimal de U-26 cerca
  del umbral) **aceptado por el dueño**.
- 2026-11-14: reverificación de la fase 4 sobre `60e19c1`: **pasa** (F4-02 y F4-03 cerrados, F4-01
  aceptado). Menor nuevo F4-04 (sin test del empate de p/γ en el mínimo) cubierto con un test, sin
  cambios en `src/`.
- 2026-11-15: fase 5 del plan (serie para el reproductor) entregada en `2c51470`; `hie-verifier`
  **pasa** (`doc/verification/06-fase-5.md`), sin bloqueantes ni mayores. Medido: peor respuesta
  3 167 900 B ≤ 3 500 000 B, peor petición 19 919 B ≤ 65 536 B, peor caso con fotogramas < 0.8 s;
  no se aplica la regla de ajuste de U-34. Menor F5-01 (la receta no es el máximo en bytes: datum
  negativo 3 284 238 B; entradas extremas sin sentido físico hasta 4 129 794 B, por debajo de
  4,5 MB) **aceptado por el dueño**, con la condición de documentarlo en `portal/INTEGRATION.md`
  en la fase 6.
- 2026-11-15: **enmienda tras G4**; se reabren las etapas 1–4 y la 5 vuelve a `pendiente`. El
  dueño decide, a partir del desglose del tamaño de la respuesta (fotogramas 57 %, series 40 % del
  peor caso de 3,16 MB; unos 18 B por número): (1) redondear a 3 decimales las listas de salida en
  m y L/s, con `time_s` y los escalares sin redondear (choca con D-57 (9)); (2) quitar
  `frame_pressure_head_m`, porque p/γ = H − z se deriva de `frame_head_m` y `elevation_m` (choca
  con D-57 (4); cambio de forma: `SCHEMA_VERSION` 2.0); (3) retirar el texto de fase del
  reproductor (U-32; DR-1 punto 2 / D-58). Estimado: peor caso de 3,16 MB a ≈ 0,96 MB. Las fases
  0–4 siguen valiendo; la 5 y su verificación se rehacen tras la nueva G4. Orden: historias
  (`hie-product-owner`) → plan y DR nuevos (`hie-architect`) → prototipo (`hie-prototyper`) →
  decisión del portal → re-congelar → construir y verificar.
- 2026-11-15: la enmienda suma una cuarta decisión del dueño: (4) la densidad y la gravedad
  pasan a ser constantes de código, ρ = 1000 kg/m³ y g = 9.81 m/s² (los valores por defecto
  actuales, que el dueño confirma). Se quitan `density_kgm3` y `gravity_ms2` de la entrada y del
  formulario. Es un cambio de forma de la petición, ya cubierto por el paso a `SCHEMA_VERSION`
  2.0. Los nombres y campos de entrada los decide el upstream (regla central del kit), así que no
  requiere pedido al portal.
- 2026-11-15: G1 aprobada de nuevo con la enmienda: `doc/stories/` recoge las decisiones 1–4. El
  dueño acepta la tolerancia de 0.001 m + 1·10⁻⁹ m para comparar presiones derivadas con listas
  redondeadas y el caso nuevo de HU-4.2 crit. 4 (dt = 1/3000 s). Queda para `hie-architect` o
  `hie-api` confirmar que HU-2.1 crit. 1 y HU-1.3 crit. 1 siguen valiendo con el redondeo.
- 2026-11-15: G2 aprobada de nuevo con la enmienda: plan `doc/plans/01-golpe-ariete-v1.md`
  (borrador, contrato propuesto `SCHEMA_VERSION` 2.0, U-39 … U-41) y DR-7 … DR-10 abiertos. El
  dueño acepta las dos recomendaciones de la Parte 1: la banda de ±0.0005 m entre el tramo rojo
  y el aviso con las envolventes al milímetro (DR-7 (a); si el portal no la admite, envolventes de
  presión sin redondear y retoque de historias) y mantener min(1001, ⌊50 000 / n⌋) fotogramas
  (DR-9 (a), cierra F5-01).
- 2026-11-15: G3 aprobada de nuevo con la enmienda: `portal/ui-spec.json` y
  `portal/prototype.html` sin `density_kgm3` ni `gravity_ms2` en el formulario (ρ y g
  constantes), curva p/γ del instante derivada en pantalla como `frame_head_m[k][j] −
  elevation_m[j]` (DR-8), sin texto de fase (U-32, DR-10) y con la banda de redondeo de
  ±0.0005 m entre el tramo rojo y los avisos, en la que manda el aviso (U-39, DR-7). Esquema
  validado con jsonschema contra `06-ui-spec.schema.json` (kit 3.0.0). Siguiente:
  `/hie-flow requests` para llevar DR-7 … DR-10 al portal.
- 2026-11-15: el portal resolvió DR-7 … DR-10 con la alternativa (a) en los cuatro (D-63 … D-66;
  sin commit en el portal al registrarlo). `hie-architect` los incorporó y dejó el plan
  `doc/plans/01-golpe-ariete-v1.md` **congelado** con `SCHEMA_VERSION` = `"2.0"`: §1.5, U-36 y V-13
  con el rojo leído del aviso `danger` (D-63); invariantes `frame_x_m == x_m` y p = H − z (U-42,
  D-64; `frame_x_m` se mantiene por decisión del dueño); dos mediciones de tamaño ≤ 3 500 000 B y
  U-34 (6) «detener y abrir DR» (D-65); U-32 retirada (D-66). Ningún DR abierto.
- 2026-11-15: `hie-prototyper` ajustó `portal/ui-spec.json` y `portal/prototype.html` a D-63
  (marcador del cruce desde el aviso, tramo solo con aviso) sin cambiar el uso aprobado en G3;
  esquema validado con jsonschema. El dueño lo revisa en G4.
- 2026-11-15: **G4 aprobada de nuevo.** D-63 … D-66 en el commit `29593af` del portal, con CI en
  verde según el dueño; ningún DR abierto; plan congelado con `SCHEMA_VERSION` = `"2.0"`. El dueño
  acepta U-34 (6) («detener la fase 5 y abrir DR» si una medición supera 3 500 000 B), el criterio
  de ≥ 20 B por número en la receta adversaria, la banda de < 0.0005 m (aviso y marcador sin tramo)
  y el riesgo de empate de redondeo en los casos dorados. Etapa 5: se rehace la fase 5 (contrato
  2.0) y sigue la 6.
- 2026-11-15: el portal publicó el kit 3.0.1 (`de21e5c`, *patch*, DT-33): solo reescribe la IA de
  `kit 03 §3`. Sin efecto en esta app (sin IA, D-62); el diseño sigue con 3.0.0 hasta que
  `hie-architect` adopte la versión nueva. El mismo commit abre en el portal DT-34 (columna de
  entradas sticky de `solver-2col` más alta que el viewport; nombra esta app, prioridad baja): es
  deuda del patrón del portal, no pide nada al upstream.
- 2026-11-15: **fase 5 rehecha (contrato 2.0)** entregada en `32a98fd`; `hie-verifier` **pasa**
  (`doc/verification/07-fase-5.md`, sustituye a `06-fase-5.md` de la 1.0), sin bloqueantes ni
  mayores; suite también en verde en un venv limpio con pydantic 2.13.4. Medido (D-65 (3)-(4)):
  receta realista 965 887 B, entrada adversaria 2 819 475 B (22.37 B por número), cota analítica
  3 285 874 B, petición 19 919 B: no se abre pedido y F5-01 queda cerrado. Menores: F5R-01 (la
  adversaria publicada no es el máximo en bytes; INTEGRATION.md la presenta como medición y la cota
  como techo) y F5R-04 (mensajes de ρ y g de usted, literales del plan) **aceptados por el dueño**;
  F5R-02 (`pn_bar` extremo da 500, anterior a esta fase) **aceptado** y pasa a `hie-architect`
  porque acotarlo es enmienda del contrato; F5R-03 (test de HU-1.5 crit. 3 con datum no redondo)
  corregido. Siguiente: fase 6.
- 2026-11-15: **fase 6 del plan (entrega)** construida en `db613b7`: `tools/make_examples.py`, 12
  ejemplos de la 2.0 en `portal/examples/` (generados desde el paquete instalado en un venv limpio;
  se añade `solve-pn-superado` a la lista del plan), `tests/test_examples.py` y
  `portal/INTEGRATION.md`. `hie-verifier` **no pasa** (`doc/verification/08-fase-6.md`) por F6-01
  (commit sin empujar) y F6-02 (el párrafo del tamaño no recogía D-65 (4) ni la condición de
  F5R-01). Corregidos en `fcbff53` (con F6-03), empujado a `hie/etapas-0-3`, y reverificado
  instalando desde GitHub: **pasa** (`doc/verification/09-fase-6.md`). Menores F6-04 (kit 3.0.1 sin
  adoptar) y F6R-01 (U-34 en `doc/DECISIONS.md` dice «dos mediciones en verde» en vez de la guarda
  del portal de D-65 (4)) **aceptados por el dueño**, para `hie-architect`.
- 2026-11-15: **G5 aprobada** por el dueño (`/hie-flow approve 5`). Checklist de `kit 04 §3`
  recorrido sobre `fcbff53`: instalación desde GitHub, suite y ejemplos desde lo instalado,
  ningún DR abierto, `INTEGRATION.md` conforme al código, `src/` sin cambios desde los ejemplos
  (`a8a1675`), `ui-spec.json` válido, sin bloqueantes. Quedan para la entrega (etapa 6): etiqueta,
  commit a pinear en este archivo y estado de la etapa 6. Kit 3.0.0 frente al vigente 3.0.1:
  desvío aceptado (F6-04), sin efecto en esta app.
- 2026-11-15: **entrega (etapa 6).** Commit a pinear `a04431e1dc741acfce305c6f7cfca3cdfa57e96c` (el de la nota de G5; `src/` idéntico
  al verificado en `fcbff53`), etiqueta `v0.1.0`, rama `main` creada en ese commit y empujada
  junto con `hie/etapas-0-3`. Comprobado tras el push, en un venv nuevo de Python 3.12:
  `pip install "mainpipe-transient @ git+https://github.com/gustavods14/mainpipe-transient.git@a04431e1dc741acfce305c6f7cfca3cdfa57e96c"`,
  suite (446) importando desde `site-packages` y `tools/make_examples.py --check` sin diferencias.
  Línea para `backend/requirements.txt`:
  `mainpipe-transient @ git+https://github.com/gustavods14/mainpipe-transient.git@a04431e1dc741acfce305c6f7cfca3cdfa57e96c`.
  Este registro va en un commit posterior al pin. El portal integra con su flujo
  (`NEW_APP_GUIDE.md`) leyendo `portal/`. Pendientes para `hie-architect`: kit 3.0.1 (F6-04), U-34
  frente a D-65 (4) (F6R-01), `pn_bar` extremo (F5R-02) y los anotados en el plan.
- 2026-11-15: `hie-architect`, a encargo del dueño, cierra dos de esos pendientes como correcciones
  de registro, **sin cambio de la Capa 1, del código, de los ejemplos ni del pin** (`a04431e`,
  `SCHEMA_VERSION` `"2.0"`; sin DR). **F6-04**: se adopta el kit **3.0.1** (fila «Kit con el que
  se diseñó» y cabecera del plan). Revisado el changelog 3.0.0 → 3.0.1: *patch* (DT-33) que solo
  reescribe `kit 03 §1` y `§3` (IA) sin cambiar reglas para el upstream; las citas del plan a
  `kit 03 §1` siguen valiendo y la app no tiene IA (D-62): nada del plan cambia. La columna «Kit»
  de las etapas se deja en 3.0.0, que es con lo que se aprobó cada una. **F6R-01**: U-34 en
  `doc/DECISIONS.md`, y la misma formulación en el plan (Parte 1, §2, fase 6, V-18, §7 DR-9),
  leen ahora D-65 (4) como `portal/INTEGRATION.md`: el techo para toda entrada admitida es la cota
  de 3 285 874 B, las mediciones son de dos recetas y no el máximo (datum negativo 2 844 325 B) y
  D-57 (1) se da por cumplido solo con la guarda de D-57 (2) del portal en verde. Las erratas del
  plan (fase 3 «Q en vértices», rango de U-NN de la cabecera) ya estaban corregidas desde la
  enmienda del 2026-11-15. Queda pendiente F5R-02 (`pn_bar` extremo), que sí es enmienda del
  contrato.
