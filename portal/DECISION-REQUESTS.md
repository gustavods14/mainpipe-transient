# mainpipe-transient — Pedidos de decisión al portal

> Formato y ciclo de vida: `doc/upstream-kit/08-decision-requests.md` en el portal.
> Lo escribe `hie-architect`. Los estados y las `D-NN` las copia el usuario al volver del portal.
> Plan de origen: `doc/plans/01-golpe-ariete-v1.md` (kit 3.0.0; aprobado en G2, reabierto y
> reaprobado el 2026-11-14 con D-57 … D-62; **congelado** el 2026-11-14 para G4, `SCHEMA_VERSION`
> `"1.0"`).
> 2026-11-14: DR-1 y DR-4 reformulados tras aprobar el prototipo (G3) para pedir exactamente lo
> que proponen `portal/ui-spec.json` y `portal/prototype.html` (U-30). DR-3: contexto y
> alternativas actualizados al panel aprobado en G3, misma pregunta. DR-2: añadida la palanca de
> `frame_flow_lps` (U-31).
> 2026-11-14: el portal resolvió los seis pedidos (commit `2466321` del portal, D-57 a D-62).
> D-57, D-58, D-59 y D-60 obligan a enmendar el plan, HU-4.1 y `portal/ui-spec.json` /
> `portal/prototype.html` antes de congelar en G4 (ver «Pendiente tras las decisiones» al final).
> 2026-11-14: historias enmendadas y reaprobadas en G1 (D-57). Plan enmendado con D-57 … D-62
> (`hie-architect`) y reaprobado en G2; el estado de cada punto está al final. Ningún pedido nuevo:
> los efectos de D-57 … D-62 caben en lo decidido (plan U-33 … U-36).
> 2026-11-14: `portal/ui-spec.json` y `portal/prototype.html` enmendados con D-57 … D-62 y G3
> reaprobada. Plan **congelado** (G4 pendiente de `/hie-flow approve 4`): todos los pedidos
> resueltos, ningún bloqueante abierto; lo único pendiente son las mediciones de D-57, programadas
> en las fases 5 y 6 de la construcción.

| DR | Pregunta | Categoría | Bloquea | Estado | Decisión |
|---|---|---|---|---|---|
| DR-1 | ¿Se construye en el portal el panel «Transitorio» del prototipo de G3: barra de reproducción común a cuatro gráficos ECharts en pestañas, con salto al instante desde los gráficos y los avisos? | funcionalidad | no | resuelto | D-58 |
| DR-2 | ¿Qué tamaño máximo admite el portal para la serie de fotogramas en la respuesta de `solve`? | funcionalidad | **sí** — Capa 1 (F4) | resuelto | D-57 |
| DR-3 | ¿Cabe la pantalla con el reproductor en `solver-2col`, o se quiere un lienzo dominante fuera de catálogo? | layout | no — integración de la pantalla (G3 aprobó `solver-2col`) | resuelto | D-59 |
| DR-4 | ¿Se admite la asignación de colores del panel «Transitorio» con tokens existentes, sin escala de color por presión, incluidos cuatro usos que se apartan del rol documentado del token? | gráfico | no — integración | resuelto | D-60 |
| DR-5 | ¿Cómo se muestran las fórmulas de Joukowsky y Michaud sin renderizador LaTeX? | dependencia | no — integración de la pantalla (etapa 3 aprobada) | resuelto | D-61 |
| DR-6 | ¿Tiene la app análisis de IA? | IA | no | resuelto | D-62 |

Dependencias entre pedidos: DR-4 aplica con cualquier resultado de DR-1 (envolventes, régimen,
límites y series se pintan igual); solo el color del instante t depende de que DR-1 admita
reproductor. DR-3 conserva su pregunta de la etapa 2 con el contexto del prototipo de G3, que usa
su alternativa (a): `solver-2col` con el panel «Transitorio» en la columna de resultados. Ya no
depende de DR-1: el panel cabe igual con reproductor, con `timeline` o con las cuatro pestañas
estáticas. DR-2 es independiente de DR-1: la serie viaja en el contrato aunque el reproductor se
retrase (corte R3 de la épica).

**No se pide**: ningún endpoint adicional (solo `POST /api/mainpipe-transient/solve`, `kit 03 §1`);
ninguna dependencia de backend (`numpy` y `pydantic` ya están, `kit 07 §1`); ningún servicio
externo; el presupuesto de tiempo cabe en < 1 s con los topes del plan (`kit 01 §6`, plan §2).
El gráfico del perfil con envolventes y las series temporales son series ECharts, dentro de la
regla (`kit 05 §3`). Tras G3 tampoco se piden la tubería coloreada por presión ni el mapa de calor
H(x, t): el prototipo aprobado no los usa (ver DR-1 y DR-4).

---

## DR-1 — ¿Se construye en el portal el panel «Transitorio» del prototipo de G3, con una barra de reproducción común a cuatro gráficos?

| | |
|---|---|
| Estado | resuelto |
| Bloquea | no — la Capa 1 entrega la serie (F4) igual; condiciona la integración de la pantalla |
| Categoría | funcionalidad (incluye interacción sobre el gráfico que ECharts no trae de serie, `kit 05 §3`) |
| Decisión del portal | D-58 — (a), panel «Transitorio» como en G3; clic/arrastre con getZr() + convertFromPixel solo en las dos pestañas de tiempo; la barra llega a cualquier instante con teclado |

> Reformulado el 2026-11-14 tras aprobar el prototipo (G3). La versión de la etapa 2 preguntaba
> por un reproductor genérico con «tubería coloreada por presión» y un mapa de calor H(x, t); el
> prototipo concretó el alcance y ambas cosas quedan fuera (ver «Qué ya no se pide»).

**Contexto.** El usuario quiere dar PLAY y ver viajar y reflejarse la onda (épica, P4; historia
`04-serie-reproduccion.md`). Un reproductor no existe en ninguna app ni en el catálogo del kit: es
funcionalidad de portal nueva (regla central del `README`; `kit 05 §2–3`). El prototipo aprobado
en G3 (`portal/ui-spec.json`, gráficos `perfil-envolventes`, `presiones-progresiva`,
`series-temporales-h` y `series-temporales-q`; `portal/prototype.html`, panel «Transitorio») lo
concreta así, dentro de la columna de resultados de `solver-2col` (DR-3 a):

1. **Barra de reproducción** fija arriba del panel (`position: sticky`), en HTML con tokens:
   reproducir / pausa, fotograma anterior / siguiente, cursor sobre `frame_time_s` con lectura
   «t = … s», velocidad ×0.1 · ×0.25 · ×0.5 · ×1 (×1 = tiempo real; ×0.25 por defecto) y repetir
   en bucle.
2. **Texto de fase** bajo la barra (cierre en curso; onda hacia el depósito; reflexión en el
   depósito; reflexión en la válvula cerrada; depresión que vuelve, con el número de ciclo),
   calculado en el frontend con `reflection_time_s`, `wave_period_s` y `closure_duration_s`, que ya
   están en la Capa 1 (U-32).
3. **Cuatro pestañas ECharts a todo el ancho del panel**, un gráfico a la vez: «Altura H(x)»,
   «Presión p/γ(x)», «Válvula y L/2» (con conmutador H | p/γ) y «Caudales». En las dos primeras el
   instante t es la fila k de `frame_head_m` / `frame_pressure_head_m`; en las dos de tiempo, un
   cursor vertical. Cambiar de pestaña conserva el instante y la reproducción; la leyenda muestra
   solo las series de la pestaña visible.
4. **Saltar a un instante**: clic o arrastre sobre las dos pestañas de tiempo (en el prototipo,
   eventos de bajo nivel de ECharts —`getZr()` + `convertFromPixel`—, no el evento `click` de
   serie), y un botón «Ir a t = … s en el transitorio» en cada aviso de `checks` que lleva instante.
5. **Nota de submuestreo**: si `frame_stride` > 1, «Un fotograma cada N pasos de cálculo» bajo el
   panel.

Lo nuevo para el portal: el componente de reproducción (1), un instante compartido entre varios
gráficos y pestañas (3) y el salto desde los avisos (4). El arrastre sobre el gráfico es
interacción que ECharts no trae de serie, que `kit 05 §3` manda pedir. Lo demás está dentro de la
regla: series `line` y una serie `custom` (el polígono de la banda de envolventes) de ECharts
(`kit 05 §3`), sin dependencias nuevas (`kit 07 §1`). No se usa el componente `timeline` de
ECharts que proponía la etapa 2: es un control por gráfico y no sirve para cuatro gráficos en
pestañas con un instante común.

**Qué ya no se pide.** La tubería coloreada por presión, el mapa de calor H(x, t) (antigua
alternativa b) y el tubo dibujado en SVG / canvas (antigua d). Si el portal los quiere más
adelante, son un pedido nuevo (el mapa de calor, además, uno de color: ver DR-4).

**Alternativas.**

| # | Alternativa | A favor | En contra |
|---|---|---|---|
| a | **Panel «Transitorio» como en G3** (puntos 1–5) | Es lo aprobado por el dueño; un solo control para los cuatro gráficos; el instante se lee a la vez en el espacio y en el tiempo; cada aviso lleva al momento en que ocurre | Componente nuevo (barra) y estado compartido entre gráficos; el arrastre usa eventos de bajo nivel de ECharts, sin precedente en el portal |
| b | (a) **sin saltar desde los gráficos**: el instante solo se mueve con la barra y con «Ir a t» de los avisos | Toda la interacción sobre el gráfico queda en lo que ECharts trae de serie (tooltip); misma barra y mismo contrato | Llegar a un pico obliga a buscarlo con el cursor de la barra; se pierde el gesto más directo en las series de tiempo |
| c | `timeline` nativo de ECharts en cada gráfico, sin barra común (planteamiento de la etapa 2) | Dentro de la regla de gráficos sin componente HTML nuevo | Cuatro controles, uno por pestaña; conservar el instante al cambiar de pestaña exige código propio igual; velocidad y bucle limitados a lo que ofrece `timeline`; estilado con tokens a resolver |
| d | **Sin reproductor en v1**: las cuatro pestañas estáticas (envolventes, régimen, límites, series), sin curva ni cursor del instante | Ningún componente nuevo; la API se integra igual | No cumple P4; la serie F4 no se usa (el portal llamaría con `include_frames: false`, U-24) |

**Recomendación del upstream.** (a), lo aprobado en G3. Si el portal prefiere no abrir el
precedente de interacción de bajo nivel sobre un gráfico, (b) conserva todo lo demás con el mismo
contrato.

**Qué cambia en el contrato o la pantalla según lo que se decida.** Contrato: nada en ninguna
alternativa. La pantalla consume `frame_time_s`, `frame_head_m`, `frame_pressure_head_m`,
`frame_stride`, `reflection_time_s`, `wave_period_s` y `closure_duration_s`; `frame_flow_lps` no lo
usa ninguna pestaña («Caudales» dibuja las series `flow_valve_lps` y `flow_reservoir_lps`), sigue en
la Capa 1 por HU-4.1 y su peso cuenta en DR-2 (U-31). En (d) el portal envía
`include_frames: false`. Pantalla: (a) es `ui-spec.json` tal cual, más el botón «Ir a t» de los
avisos, que hoy está solo en el prototipo; (b) quita «clic o arrastre» de las dos pestañas de
tiempo; (c) sustituye la barra por un `timeline` en cada gráfico; (d) quita la barra, el texto de
fase, la curva del instante y los cursores.

---

## DR-2 — ¿Qué tamaño máximo admite el portal para la serie de fotogramas en la respuesta de `solve`?

| | |
|---|---|
| Estado | resuelto |
| Bloquea | **sí** — fija el tope de fotogramas y por tanto la forma de los campos `frame_*` de la Capa 1 (G4) |
| Categoría | funcionalidad (tamaño de respuesta; el kit no tiene categoría propia, hallazgo en el plan §8) |
| Decisión del portal | D-57 — (a) con techo total ≤ 3,5 MB en el peor caso; fotogramas por presupuesto de 100 000 celdas entre las matrices frame_* (con H y p/γ: n_fotogramas ≤ min(1001, ⌊50 000 / n_progresivas⌋)); MAX_STEPS = 10 000; frame_flow_lps sale de la respuesta por defecto (confirmado por el dueño) |

**Contexto.** F4 añade a la respuesta tres matrices (H, Q, p/γ) de fotogramas × progresivas. Las
progresivas son los nodos (11 a 201) más los vértices del perfil (hasta 500). El kit no fija un
tamaño máximo de respuesta, pero el tamaño afecta al portal: el router es síncrono (`kit 01 §6`), el
navegador parsea el JSON, y los `examples/` se convierten en casos dorados del portal (`kit 04 §2`).
Con valores `float64` sin redondear, cada número ocupa ≈ 18 bytes en JSON. Medidas del plan
(U-10): caso del Excel, 401 fotogramas × 21 progresivas × 3 ≈ 25 000 números ≈ **0.45 MB**, sin
submuestreo; peor caso con el tope propuesto ≈ 150 000 números ≈ **2.7 MB**. No se pueden redondear
los fotogramas sin cambiar HU-4.1 (igualdad a 10⁻⁹ con las series). Con submuestreo fuerte (muchos
pasos y muchas progresivas) el frente de onda salta varios tramos entre fotogramas; la respuesta lo
declara con `frame_stride` para que la pantalla pueda advertirlo. Independiente de lo que se decida,
el paquete ofrece `include_frames: false` (U-24) para llamadas sin la serie.

Ojo, aparte de los fotogramas: las **series temporales** de F1 (7 columnas de `n_steps + 1`
valores, HU-1.4) no se submuestrean. Con el tope de 20 000 pasos (U-09) suman ≈ 140 000 números
(≈ 2.5 MB) en el peor caso, también con `include_frames: false`. Peor caso total con la
alternativa (a): ≈ 5 MB. Si el portal quiere un techo total menor, la palanca es bajar `MAX_STEPS`
(10 000 pasos → series ≈ 1.3 MB, a costa de duraciones máximas más cortas con mallas finas): dígase
en la decisión.

Segunda palanca, solo para los fotogramas: **la pantalla aprobada en G3 no consume
`frame_flow_lps`** (ninguna pestaña del panel «Transitorio» lo dibuja; «Caudales» usa las series
`flow_valve_lps` y `flow_reservoir_lps`, ver DR-1). Es una de las tres matrices, ≈ 1/3 del peso de
los fotogramas: ≈ 0.15 MB de 0.45 MB en el caso del Excel y ≈ 0.9 MB de 2.7 MB en el peor caso de
la alternativa (a). Sacarlo de la respuesta por defecto deja el peor caso de fotogramas en
≈ 1.8 MB sin quitar un solo fotograma a la pantalla (o, con el mismo techo, admite ≈ 1.5 veces más
fotogramas). Pero **HU-4.1 crit. 1 lo exige hoy** y el upstream lo mantiene (U-31, provisional):
quitarlo cambia la historia aprobada en G1 y la forma de F4, así que no lo decide el upstream. Si el
portal lo quiere, dígase en la decisión y el dueño lo confirma al enmendar HU-4.1 antes de G4.

**Alternativas.**

| # | Alternativa | A favor | En contra |
|---|---|---|---|
| a | **Tope por celdas**: n_fotogramas ≤ min(1001, ⌊50 000 / n_progresivas⌋), siempre en `solve` (propuesta U-10) | Una sola llamada; caso típico < 0.5 MB; peor caso acotado ≈ 2.7 MB | En el peor caso, pocos fotogramas (≈ 70 con 701 progresivas) |
| b | Tope más alto: ⌊100 000 / n_progresivas⌋, máx. 2001 fotogramas | Más resolución temporal en mallas grandes | Peor caso ≈ 5.4 MB por respuesta |
| c | Tope más bajo: ⌊20 000 / n_progresivas⌋, máx. 501, y fotogramas solo en los nodos (sin vértices) | Peor caso ≈ 1 MB | Se pierde la presión animada en los puntos altos entre nodos; cambia HU-4.1 crit. 2 y la historia F4 (`frame_x_m` ≠ `x_m`) |
| d | Serie fuera de `solve`: endpoint `POST /api/mainpipe-transient/frames` que recalcula con los mismos datos | `solve` queda ligero siempre | Endpoint fuera de convención (`kit 03 §2`); calcula dos veces; dos estados de error en pantalla |

**Recomendación del upstream.** (a). Mantiene una sola llamada y una respuesta del orden de lo que
ya mueven otras apps en el caso típico, con un techo explícito. Los casos dorados llevarán la
serie solo en un ejemplo (el caso del Excel, ≈ 0.5 MB); los demás con `include_frames: false`.

**Qué cambia en el contrato o la pantalla según lo que se decida.** (a) / (b): solo la constante
del tope (U-10). (c): `frame_x_m` pasa a ser solo los nodos y se enmienda F4. (d): los campos
`frame_*` salen de `SolveResponse` a una función nueva `frames(data)` con su propio
`FramesResponse`, y `SCHEMA_VERSION` lo refleja; la pantalla hace dos llamadas. Con cualquiera de
ellas, si se acepta la palanca de `frame_flow_lps`: el campo sale de la respuesta por defecto, se
enmiendan HU-4.1 crit. 1, F4 y V-17, y la pantalla no cambia (no lo usa).

---

## DR-3 — ¿Cabe la pantalla con el reproductor en `solver-2col`, o se quiere un lienzo dominante?

| | |
|---|---|
| Estado | resuelto |
| Bloquea | no — integración de la pantalla; la etapa 3 está aprobada con la alternativa (a) y el contrato no cambia |
| Categoría | layout |
| Decisión del portal | D-59 — (a), solver-2col; barra sticky solo en ≥ lg (en < lg estática) |

> Contexto actualizado el 2026-11-14 tras aprobar el prototipo (G3). La pregunta es la de la
> etapa 2; ahora se pregunta por la pantalla concreta que el dueño aprobó.

**Contexto.** El prototipo aprobado en G3 (`portal/ui-spec.json`, `"layout": "solver-2col"`;
`portal/prototype.html`) usa la rejilla `2fr 3fr` del catálogo (`kit 05 §2`, D-34):

- **Columna de entradas (2/5, sticky)**, con tres pestañas: «Datos» (≈ 17 campos y el
  interruptor «Usar perfil del trazado»), «Ley de cierre» (tabla de 2–20 filas) y «Perfil» (tabla de
  2–500 filas, bloqueada si el interruptor está apagado), con sus vistas previas de entrada.
- **Columna de resultados (3/5)**: estado y `checks`, indicadores (extremos con progresiva e
  instante, PN, Joukowsky / Michaud), la tabla de envolventes y **un solo panel «Transitorio»**:
  barra de reproducción fija arriba del panel (`position: sticky`) y debajo cuatro pestañas ECharts
  —«Altura H(x)», «Presión p/γ(x)», «Válvula y L/2» y «Caudales»—, un gráfico a la vez **a todo el
  ancho de la columna**. El detalle del panel está en DR-1.

Las pestañas del panel resuelven lo que la etapa 2 temía de esta alternativa: los cuatro gráficos
ya no se apilan en la columna junto a los indicadores, sino que ocupan un solo hueco con el ancho
mayor de la rejilla. Lo que el kit no describe es un elemento sticky **dentro** de la columna de
resultados: `kit 05 §2` solo fija sticky la columna de entradas. Por eso, y porque el catálogo es
cerrado, se pide al portal que confirme que el panel cabe en `solver-2col` sin convertirse en un
layout fuera de catálogo. Un lienzo dominante sigue siendo pedido y requiere dictamen de
`ux-ui-expert` (`kit 05 §2`).

**Alternativas.**

| # | Alternativa | A favor | En contra |
|---|---|---|---|
| a | **`solver-2col` como en G3**: entradas con pestañas (Datos · Ley de cierre · Perfil) a la izquierda; a la derecha resultados y el panel «Transitorio» con barra sticky y cuatro pestañas a todo el ancho de la columna (3/5) | Dentro del catálogo; es lo aprobado por el dueño; un gráfico a la vez con el ancho mayor de la rejilla, sin competir con otros gráficos; la barra sigue visible al desplazarse por el panel; las pestañas de entrada absorben las dos tablas | Hay que desplazarse desde los indicadores hasta el panel; la barra sticky dentro de la columna de resultados no está descrita en `kit 05 §2` (convive con la columna de entradas, también sticky) |
| b | `solver-3col`: entradas · resultados · panel «Transitorio» en la tercera columna | Dentro del catálogo; indicadores y panel visibles a la vez, sin desplazamiento | Columna de entradas de 320 px estrecha para la tabla del perfil (x, z, hasta 500 filas); panel en la mitad del ancho restante, con poco sitio para la barra (reproducir, paso a paso, cursor con lectura de t, cuatro velocidades y bucle) y para curvas de hasta 701 progresivas; obliga a rehacer el prototipo aprobado |
| c | Layout nuevo: lienzo central dominante para el panel con paneles laterales | El transitorio luce más; cabrían dos gráficos a la vez | Fuera de catálogo; dictamen de `ux-ui-expert`; componente de layout nuevo en el portal; el prototipo aprobado no lo necesita |

**Recomendación del upstream.** (a), lo aprobado en G3. Si al portal no le conviene la barra
sticky dentro de la columna, (a) con la barra estática encabezando el panel conserva todo lo demás
(el panel es corto: un gráfico a la vez).

**Qué cambia en el contrato o la pantalla según lo que se decida.** Contrato: nada. Pantalla: (a)
es `ui-spec.json` tal cual (o, con la barra estática, solo pierde `position: sticky`); (b) cambia
el `layout` y redistribuye resultados y panel; (c) es un layout nuevo que espera al dictamen de
`ux-ui-expert` y se reprototipa.

---

## DR-4 — ¿Se admite la asignación de colores del panel «Transitorio» con tokens existentes, sin escala por presión?

| | |
|---|---|
| Estado | resuelto |
| Bloquea | no — integración de la pantalla; contrato sin cambios |
| Categoría | gráfico (color / token: `kit 05 §3–4`, D-17, `DESIGN.md` §6.2) |
| Decisión del portal | D-60 — (a) con la corrección (b) en los cuatro usos fuera de rol; sin tokens nuevos |

> Reformulado el 2026-11-14 tras aprobar el prototipo (G3). La etapa 2 preguntaba con qué escala
> colorear la tubería según la presión; el prototipo no usa escala: la tubería es acromática y la
> presión se lee en la pestaña «Presión p/γ(x)» contra las líneas de PN y de límite.

**Contexto.** El prototipo no introduce tokens nuevos ni hex sueltos: todo sale de `.theme-light`
de `frontend/src/index.css` (`kit 05 §4`, T-1.6, T-1.8). Asignación, igual en las cuatro pestañas:

| Elemento | Token | Trazo | Rol del token en `DESIGN.md` §6.2 |
|---|---|---|---|
| Tubería (cota del eje) | `--color-chart-neutral` | continuo | sección del canal / lecho (`ia-channel`): coherente |
| Envolventes mín.–máx. | `--color-chart-zone` | banda (polígono), sin borde | banda de zona BEP, con patrón de dos capas: relleno + borde 1 px `series-1` al 40 % |
| H y p/γ de régimen | `--color-chart-series-3` | discontinuo, 1.5 px | serie |
| Instante t | `--color-chart-marker` | curva continua de 2.5 px en H(x) y p/γ(x); cursor vertical discontinuo en las de tiempo | marcador BEP / «marcador destacado» |
| Válvula · L/2 · depósito | `series-1` · `series-2` · `series-3` | series de tiempo; en H(x) y p/γ(x), verticales punteadas en x = L, L/2 y 0, rotuladas con el color de su serie | series |
| PN y presión mínima admisible | `--color-chart-critical` | discontinuo; rótulo «PN …» / «límite …» en `--color-chart-label`, sin entrada en la leyenda | reservado: violación real (p. ej. NPSH insuficiente) |
| Máximo y mínimo globales de p/γ | `--color-chart-operating` | punto con rótulo en `--color-chart-label` | punto de operación, capa de anotación acromática (D-17): coherente |
| Q = 0 en «Caudales» | `--color-chart-neutral` | discontinuo | — |

Cuatro usos se apartan del rol documentado y piden el dictamen de `ux-ui-expert` (`kit 05 §4`):

1. **`--color-chart-critical` permanente** para PN y límite, que §6.2 reserva para una violación
   real. La corrección del 2026-08-16 de §6.2 descartó un rojo permanente porque choca con el rojo
   condicional del estado; aquí lo condicional son los avisos `danger` de `checks`.
2. **`--color-chart-zone` sin el borde de 1 px** que §6.2 pide para que la banda se vea sobre
   blanco. Con borde `series-1` chocaría con la válvula, y los bordes de la banda son las propias
   envolventes.
3. **`--color-chart-series-3` con dos significados** en H(x) y p/γ(x): régimen (discontinuo) y
   depósito (vertical punteada).
4. **Rótulos de las verticales con matiz** (el color de su serie), cuando D-17 pide una capa de
   anotación acromática.

**Alternativas.**

| # | Alternativa | A favor | En contra |
|---|---|---|---|
| a | **Asignación del prototipo de G3** tal cual (tabla de arriba) | Es lo aprobado por el dueño; sin tokens nuevos; el violeta del instante no tiene otro uso en el gráfico; rojo = lo que no se debe cruzar | Los cuatro usos de arriba se apartan de §6.2 o de D-17 |
| b | (a) **ajustada a los roles documentados**: PN y límite acromáticos (`--color-chart-label` discontinuo) y `--color-chart-critical` solo en el tramo o el punto donde una envolvente los cruza; régimen acromático (`--color-chart-neutral` con trazo distinto del de la tubería) para dejar `series-3` solo al depósito; banda con un borde que no sea `series-1`; rótulos de las verticales en `--color-chart-label` | Respeta §6.2 y D-17 sin tokens nuevos; el rojo aparece solo si hay violación, como en los avisos | Más dibujo en el frontend (tramos de cruce); tubería y régimen comparten tono y solo los separa el trazo |
| c | **Escala de color por presión** (`visualMap`) sobre la curva del instante en p/γ(x), con la paleta de estado D-13 (planteamiento de la etapa 2) | Se ve en cada instante qué tramo está en peligro | Paleta de severidad usada como color de serie: choca con D-13 y D-17; repite lo que ya dicen las líneas de PN y límite; el prototipo aprobado la retiró |
| d | **Tokens nuevos de gráfico** genéricos (p. ej. banda de envolvente, umbral, instante), validados por `ux-ui-expert` | Roles propios, sin reinterpretar los de `pump-analysis`; reutilizables por otros motores de transitorios | Cambio del sistema de diseño (T-1.8, `kit 05 §4`); más plazo |

**Recomendación del upstream.** (a), con el dictamen de `ux-ui-expert` sobre los cuatro puntos. Si
alguno no se admite, la corrección de (b) para ese punto, sin tokens nuevos.

**Qué cambia en el contrato o la pantalla según lo que se decida.** Contrato: nada en ninguna
alternativa (`pn_head_m`, `min_allowed_pressure_head_m`, las envolventes y la posición de los
extremos ya están en la Capa 1; los tramos de cruce de (b) los calcula el frontend con ellos).
Pantalla: colores y trazos de los cuatro gráficos del panel en `ui-spec.json` (línea «colores
coherentes en las cuatro pestañas» de `perfil-envolventes`) y en el prototipo; en (d), además,
esperar a los tokens nuevos.

---

## DR-5 — ¿Cómo se muestran las fórmulas de Joukowsky y Michaud sin renderizador LaTeX?

| | |
|---|---|
| Estado | resuelto |
| Bloquea | no — integración de la pantalla; la etapa 3 está aprobada y el contrato no cambia |
| Categoría | dependencia (frontend) |
| Decisión del portal | D-61 — (a), fórmulas de una línea en HTML (<var>, <sub>) y Unicode con desglose de unidades, sin dependencia |

**Contexto.** La referencia teórica (HU-3.4) se entiende mejor con su fórmula: ΔH = a·V₀/g y
ΔH = 2·L·V₀/(g·Tc). `DESIGN.md` §9 pide fórmulas en LaTeX con desglose, pero el portal no tiene
renderizador (`kit 05 §6`); mostrarlas renderizadas sería una dependencia nueva de frontend
(`kit 07 §2–3`).

**Alternativas.**

| # | Alternativa | A favor | En contra |
|---|---|---|---|
| a | **Texto con HTML y Unicode** (subíndices `<sub>`, «·», «Δ») y desglose de variables con unidades | Sin dependencias; suficiente para fórmulas de una línea | No es LaTeX como pide `DESIGN.md` §9 |
| b | KaTeX (MIT, mantenido; peso y último release a comprobar por el portal, `kit 07 §3`) en el componente `Formula` de `DESIGN.md` §7.2 | Cumple `DESIGN.md`; reutilizable por otras apps | Dependencia nueva: entrada en `DECISIONS.md` del portal con ≥ 3 alternativas |
| c | MathJax (Apache-2.0, más pesado) | Cobertura LaTeX completa | Más peso que KaTeX para el mismo uso |
| d | Sin fórmulas: solo valores y el nombre del método | Nada que decidir | El revisor (HU-3.4) pierde el contexto de qué se comparó |

**Recomendación del upstream.** (a) en v1; si el portal implementa `Formula` con KaTeX para todas
las apps, la app lo adopta sin cambiar el contrato.

**Qué cambia en el contrato o la pantalla según lo que se decida.** Contrato: nada. Pantalla: el
bloque de referencia teórica en `ui-spec.json`.

---

## DR-6 — ¿Tiene la app análisis de IA?

| | |
|---|---|
| Estado | resuelto |
| Bloquea | no |
| Categoría | IA |
| Decisión del portal | D-62 — (a), sin IA en v1 |

**Contexto.** El usuario no lo pidió (épica, pregunta 7). Habilitar IA añade un valor de `domain`
en `POST /api/ai/analyze` y un prompt de dominio redactado por el portal (`kit 03 §3`, D-26, D-33),
y el upstream declararía los campos de contexto en `ui-spec.json` (`ai`). Es decisión del portal
(regla central del `README`).

**Alternativas.**

| # | Alternativa | A favor | En contra |
|---|---|---|---|
| a | **Sin IA en v1** | Cero trabajo de portal; la lectura del resultado ya la guían `status`, `checks` y la referencia teórica | — |
| b | IA en v1 con contexto: extremos, PN, `checks`, tipo de maniobra y desviación teórica | Comentario de ingeniería sobre la maniobra y las protecciones | Nuevo `domain` y prompt en el portal; no pedido por el usuario |
| c | Dejar el hueco previsto en `ui-spec.json` (`ai` vacío) para decidir tras la entrega | No cierra la puerta | Decisión aplazada; el prototipo no la muestra |

**Recomendación del upstream.** (a). Si más adelante se quiere, (b) no cambia la Capa 1: todos los
campos de contexto ya están en la respuesta.

**Qué cambia en el contrato o la pantalla según lo que se decida.** Contrato: nada. Pantalla:
sección `ai` de `ui-spec.json` y el panel de IA.

---

## Pendiente tras las decisiones (antes de G4)

Lo que el portal pidió al upstream con D-57 a D-62 (commit `2466321` del portal), copiado de su
respuesta.

**Estado de la incorporación (2026-11-14).** Plan = `doc/plans/01-golpe-ariete-v1.md`.

| Punto | Estado | Dónde |
|---|---|---|
| D-57: HU-4.1 crit. 1 y F4 sin `frame_flow_lps` | hecho (G1 reaprobada) | `doc/stories/04-serie-reproduccion.md` |
| D-57: F4 y V-17 sin `frame_flow_lps`; sin opción explícita | hecho en el plan | §1.4, §6 V-17; U-33 (se quita del todo: el portal nunca enviaría la opción) |
| D-57: U-10, tope min(1001, ⌊50 000 / n_progresivas⌋) | hecho en el plan | §1.4; U-10 vigente |
| D-57: U-09, `MAX_STEPS` = 10 000 y 422 con la duración máxima | hecho en el plan (HU-1.6 crit. 13 en G1) | §1.3, fase 2; U-09 vigente |
| D-57: medir JSON del peor caso ≤ 3,5 MB | programado: fase 5 (medición), fase 6 (cifra en `portal/INTEGRATION.md`) | §2, §5, V-18; protocolo U-34 |
| D-57: medir petición del peor caso ≤ 64 KiB (D-48) | programado: fases 5 y 6, junto a la anterior | §2, §5, V-18; U-34 |
| D-57: sin redondeo; `frame_stride` se mantiene | hecho en el plan | §1.4; U-10 |
| D-57: `examples/` con la serie solo en el caso del Excel | hecho en el plan | §5, ejemplos previstos |
| D-58: botón «Ir a t = … s» | Capa 1 sin cambios (los avisos llevan instante; U-36). **Hecho** en `ui-spec.json` / `prototype.html` el 2026-11-14 (G3) | plan §1.5; `ui-spec.json`, `charts[perfil-envolventes].interactions` (el esquema no tiene sitio para acciones en un aviso: hallazgo, plan §8) |
| D-58 (resto): instante como estado del panel, reinicio con cada resultado, clic/arrastre solo en «Válvula y L/2» y «Caudales», teclado | **hecho** el 2026-11-14 (G3) | `ui-spec.json` / `prototype.html` |
| D-59: barra de una fila, opaca, sticky solo ≥ lg con `lg:top-20`, estática por debajo | **hecho** el 2026-11-14 (G3) | `ui-spec.json` / `prototype.html` |
| D-60: rojo solo en el cruce, mismo predicado que `danger` | predicado fijado y verificado en el plan; eco `min_allowed_pressure_head_m` en la respuesta (U-35). Colores (PN y límite en `--color-chart-label`, banda con bordes de 1 px, régimen neutral, `series-3` solo depósito, rótulos con nombre): **hechos** el 2026-11-14 (G3) | plan §1.4, §1.5, V-13; `ui-spec.json` / `prototype.html` |
| D-61: fórmulas en HTML con `<var>` / `<sub>` y desglose | **hecho** el 2026-11-14 (G3); en `ui-spec.json` solo como `symbol` Unicode de los kpis (el esquema no tiene sitio para fórmulas: hallazgo, plan §8) | `prototype.html`; `ui-spec.json` kpis |
| D-62: sin IA | Capa 1 sin cambios. Sección `ai` **eliminada** de `ui-spec.json` el 2026-11-14 (G3) | `portal/API-PROPOSAL.md`; `ui-spec.json` |

Para la etapa 3 además, **hecho** el 2026-11-14 (G3): el hint de `duration_s` en
`portal/ui-spec.json` y `portal/prototype.html` dice «tope de 10 000 pasos» (D-57), y la línea del
límite lee `response.min_allowed_pressure_head_m` (U-35), no el valor del formulario.

Con esto no queda nada pendiente antes de G4. Siguen programadas para la construcción las dos
mediciones de D-57 (respuesta ≤ 3,5 MB, petición ≤ 64 KiB): fases 5 y 6 del plan, V-18.

Lista original del portal:

1. **D-57 (DR-2)** — plan y historias:
   - Enmendar HU-4.1 crit. 1, F4 y V-17: `frame_flow_lps` sale de la respuesta por defecto. Si se
     conserva detrás de una opción explícita, el portal nunca la enviará.
   - U-10: tope de fotogramas = min(1001, ⌊50 000 / n_progresivas⌋) (presupuesto de 100 000 celdas
     entre las dos matrices `frame_*` que viajan por defecto).
   - U-09: `MAX_STEPS` = 10 000 (antes 20 000). Cierres lentos con malla fina → 422 con la duración
     máxima.
   - Medir (no estimar) el peor caso con `include_frames` activo (N máximo, 500 vértices,
     `n_steps` = `MAX_STEPS`): JSON ≤ 3,5 MB; anotar la cifra en `portal/INTEGRATION.md`
     (producción corta cuerpos > 4,5 MB; ni el CI ni TestClient lo detectan).
   - Medir que la petición del peor caso (perfil de 500 filas, ley de cierre de 20) cabe en 64 KiB
     (D-48) y anotarlo junto a la anterior.
   - Sin redondeo de fotogramas; `frame_stride` se mantiene.
   - `examples/`: solo el caso del Excel lleva la serie; los demás con `include_frames: false`.
2. **D-58 (DR-1)** — `ui-spec.json` / prototipo: el instante es estado del panel y se reinicia al
   cambiar el resultado; clic/arrastre de bajo nivel solo en «Válvula y L/2» y «Caudales», dentro de
   un único módulo; la barra llega a cualquier instante con teclado; añadir a `ui-spec.json` el botón
   «Ir a t = … s en el transitorio» de los avisos de `checks`.
3. **D-59 (DR-3)** — barra sticky solo desde `lg`, opaca, de una fila, con el mismo offset que la
   columna de entradas (`lg:top-20`); por debajo de `lg`, estática.
4. **D-60 (DR-4)** — colores en `ui-spec.json` y prototipo:
   - PN y presión mínima admisible: `--color-chart-label` discontinuo; `--color-chart-critical` solo
     en el tramo o punto donde una envolvente los cruza, con el mismo predicado que el aviso
     `danger` de `checks`.
   - Banda de envolventes sin borde propio solo si sus dos límites se dibujan como líneas de 1 px en
     `--color-chart-label`.
   - Régimen: `--color-chart-neutral` discontinuo (trazo distinto del de la tubería);
     `--color-chart-series-3` solo para el depósito.
   - Rótulos de las verticales en `--color-chart-label` y con nombre.
   - Lo demás de la tabla de DR-4 queda como en G3.
5. **D-61 (DR-5)** — referencia teórica: ΔH = a·V₀/g y ΔH = 2·L·V₀/(g·T_c) en HTML con
   `<var>`/`<sub>` y desglose de variables con unidades.
6. **D-62 (DR-6)** — sección `ai` de `ui-spec.json` vacía o ausente; sin panel de IA.
