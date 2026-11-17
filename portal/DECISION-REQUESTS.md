# mainpipe-transient — Pedidos de decisión al portal

> Formato y ciclo de vida: `doc/upstream-kit/08-decision-requests.md` en el portal.
> Lo escribe `hie-architect`. Los estados y las `D-NN` las copia el usuario al volver del portal.
> Plan de origen: `doc/plans/01-golpe-ariete-v1.md` (kit 3.0.0; aprobado en G2, reabierto y
> reaprobado el 2026-11-14 con D-57 … D-62; congelado el 2026-11-14 para G4, `SCHEMA_VERSION`
> `"1.0"`; **de vuelta a borrador** el 2026-11-15 por la enmienda tras G4, con `"2.0"` propuesta).
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
> 2026-11-15: **enmienda tras G4.** El dueño decide, a partir del desglose del tamaño medido en la
> fase 5 (peor caso 3 156 607 B: fotogramas 57 %, series 40 %; ≈ 18 B por número), redondear las
> listas de salida, quitar `frame_pressure_head_m`, retirar el texto de fase y fijar ρ y g. El plan
> vuelve a borrador con `SCHEMA_VERSION` `"2.0"` propuesta. Lo que toca decisiones del portal sale
> en **DR-7 … DR-10** (D-57 (9), D-57 (4), D-58). ρ y g fijos no se piden: los campos de entrada los
> decide el upstream (regla central del kit; plan U-40). **DR-7, DR-8 y DR-9 bloquean la nueva G4.**
> 2026-11-15: el portal resolvió DR-7 … DR-10 (D-63 … D-66, alternativa (a) en los cuatro;
> commit `29593af` del portal). Ningún bloqueante abierto. D-63, D-64 y D-65 añaden
> condiciones de verificación y D-66 retira U-32: obligan a enmendar el plan y `portal/ui-spec.json`
> antes de re-congelar (ver «Pendiente tras D-63 … D-66» al final).
> 2026-11-15: plan enmendado con D-63 … D-66 (`hie-architect`) y **congelado** con
> `SCHEMA_VERSION` `"2.0"` (nueva G4 pendiente de `/hie-flow approve 4`). Ningún pedido nuevo: las
> cuatro decisiones eligen la alternativa (a) y caben en el plan (U-36, U-42, U-34 (6)). Queda
> pendiente la frase del rojo en `portal/ui-spec.json` / `portal/prototype.html`
> (`hie-prototyper`) y lo de la construcción (`hie-api`), en la tabla del final.
> 2026-11-16: **enmienda F5R-02** (posterior a la entrega v0.1.0: `pn_bar` en [1, 100] bar,
> resultados no representables → 422, `SCHEMA_VERSION` sigue en `"2.0"`; plan U-43 … U-45).
> **Ningún pedido nuevo**: el rango de una entrada y los mensajes de error los decide el upstream
> (regla central del kit) y no se toca D-57 … D-66 (plan §7, U-45 (4)). Comprobado al re-congelar el
> plan (G4 del 2026-11-16): DR-1 … DR-10 `resuelto` con su `D-NN`, ninguno `abierto`.

| DR | Pregunta | Categoría | Bloquea | Estado | Decisión |
|---|---|---|---|---|---|
| DR-1 | ¿Se construye en el portal el panel «Transitorio» del prototipo de G3: barra de reproducción común a cuatro gráficos ECharts en pestañas, con salto al instante desde los gráficos y los avisos? | funcionalidad | no | resuelto | D-58 |
| DR-2 | ¿Qué tamaño máximo admite el portal para la serie de fotogramas en la respuesta de `solve`? | funcionalidad | **sí** — Capa 1 (F4) | resuelto | D-57 |
| DR-3 | ¿Cabe la pantalla con el reproductor en `solver-2col`, o se quiere un lienzo dominante fuera de catálogo? | layout | no — integración de la pantalla (G3 aprobó `solver-2col`) | resuelto | D-59 |
| DR-4 | ¿Se admite la asignación de colores del panel «Transitorio» con tokens existentes, sin escala de color por presión, incluidos cuatro usos que se apartan del rol documentado del token? | gráfico | no — integración | resuelto | D-60 |
| DR-5 | ¿Cómo se muestran las fórmulas de Joukowsky y Michaud sin renderizador LaTeX? | dependencia | no — integración de la pantalla (etapa 3 aprobada) | resuelto | D-61 |
| DR-6 | ¿Tiene la app análisis de IA? | IA | no | resuelto | D-62 |
| DR-7 | ¿Admite el portal que el paquete entregue a 3 decimales las listas de salida en m y L/s, frente a «sin redondeo» de D-57 (9)? | funcionalidad | **sí** — precisión de la Capa 1 2.0 (G4) | resuelto | D-63 |
| DR-8 | ¿Admite el portal retirar `frame_pressure_head_m` y que el panel derive p/γ(x, t) = `frame_head_m` − `elevation_m`, frente a las dos matrices de D-57 (4)? | funcionalidad | **sí** — forma de la Capa 1 2.0 (G4) | resuelto | D-64 |
| DR-9 | Con una sola matriz `frame_*`, ¿qué tope de fotogramas rige? | funcionalidad | **sí** — tope de la Capa 1 y guarda de D-57 (2) (G4) | resuelto | D-65 |
| DR-10 | ¿Acepta el portal que el panel «Transitorio» salga sin el texto de fase que aprobó D-58? | funcionalidad | no — pantalla; la Capa 1 no cambia | resuelto | D-66 |

Dependencias entre los pedidos de la enmienda (2026-11-15): **DR-9 depende de DR-8**: solo tiene
objeto si sale `frame_pressure_head_m` (DR-8 (a), (c) o (d)); con DR-8 (b) rige D-57 (4) tal cual.
DR-7 es independiente de DR-8 y DR-9, pero sus cifras de tamaño suponen DR-8 (a) y DR-9 (a); la
cota absoluta de DR-9 no depende de DR-7. DR-7 (a) suaviza una condición de **D-60 (1)** (el
predicado del cruce en rojo, ver su contexto); no se abre un pedido aparte porque lo que la decide
es qué listas se redondean, que es la pregunta de DR-7. DR-10 es independiente de los otros tres.

Dependencias entre pedidos (DR-1 … DR-6): DR-4 aplica con cualquier resultado de DR-1 (envolventes, régimen,
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
H(x, t): el prototipo aprobado no los usa (ver DR-1 y DR-4). En la enmienda del 2026-11-15
tampoco se pide nada por fijar ρ = 1000 kg/m³ y g = 9.81 m/s²: quitar campos de entrada lo decide
el upstream (regla central del kit). Si una petición los trae, el paquete responde 422 con un
mensaje en español que lo explica (plan U-40); el portal solo tiene que dejar de mostrarlos en el
formulario (etapa 3).

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

## DR-7 — ¿Admite el portal que el paquete entregue a 3 decimales las listas de salida en m y L/s, frente a «sin redondeo» de D-57 (9)?

| | |
|---|---|
| Estado | resuelto |
| Bloquea | **sí** — fija la precisión de la Capa 1 2.0 y lo que congelan los casos dorados (G4) |
| Categoría | funcionalidad (tamaño de respuesta; el kit no tiene categoría propia, hallazgo en el plan §8) |
| Decisión del portal | D-63 — (a) listas en m, m.c.a. y L/s a 3 decimales, redondeadas por el paquete; el marcador del cruce y el extremo en `critical` se leen del aviso `danger` de `checks` (x_m, time_s, value_m) y el tramo rojo solo se dibuja si ese aviso existe (enmienda D-57 (9) y D-60 (1)) |

**Contexto.** D-57 (9) dejó dicho: «Sin redondeo en el router […]. Bajar peso redondeando sería
una enmienda de HU-4.1 aguas arriba, con su propio pedido». Este es ese pedido. La medición de la
fase 5 (plan U-34) dio 3 156 607 B en la receta del peor caso, con ≈ 18 B por número porque cada
`float64` sale con todas sus cifras; fotogramas 57 %, series 40 %, perfiles 3 %, `checks` y
escalares < 0,1 %. El dueño decidió (historias reaprobadas en G1 el 2026-11-15):

- **Se redondean a 3 decimales** (1 mm de columna, 0.001 L/s) todas las listas en m, m.c.a. y L/s:
  seis series temporales, ocho columnas por progresiva, `frame_x_m` y `frame_head_m`.
- **No se redondean** `time_s` ni `frame_time_s` (Δt puede ser menor que 1 ms, p. ej. 1/3000 s, o
  no múltiplo de él) ni ningún escalar (extremos con su progresiva e instante, PN, límite,
  referencia teórica, campos de `checks`).
- **El redondeo lo hace el paquete** al construir la respuesta, no el router (`kit 03 §1`, D-57
  (h)); el cálculo, los extremos y los `checks` siguen con precisión completa (plan U-39).

HU-4.1 ya está enmendada en consecuencia (el desglose a 10⁻⁹ que citaba D-57 (h) se mantiene donde
dos listas llevan el mismo valor y pasa a 0.001 m donde la pantalla resta dos listas). Un efecto
sobre **D-60 (1)** («`--color-chart-critical` solo donde una envolvente cruza un umbral, con el
mismo predicado que el aviso `danger`»): con `pressure_head_max_m` / `pressure_head_min_m` a
3 decimales y `pn_head_m`, el límite y los `checks` con precisión completa, el predicado de la
pantalla coincide con el aviso **salvo si el extremo global queda a menos de 0.0005 m del umbral**;
en esa banda puede haber aviso sin tramo rojo o tramo rojo sin aviso, y manda el aviso. Es del
mismo orden que el roce que el dueño ya aceptó en los mensajes (hallazgo F4-01: valores a
1 decimal cerca del umbral).

Tamaños `[calculado]` sobre la medición del dueño con un prototipo del redondeo (963 538 B), con
DR-8 (a) y DR-9 (a), a ≈ 6,7 B por número redondeado:

| | Peor caso realista | Caso del Excel con fotogramas |
|---|---|---|
| Contrato 1.0 (medido) | 3 167 900 B | 355 716 B |
| (a) | ≈ 0,96 MB (medido por el dueño) | ≈ 89 kB (medido por el dueño) |
| (b) | ≈ 0,98 MB | ≈ 89 kB |
| (c) | ≈ 1,7 MB | ≈ 0,1 MB |
| (d) | ≈ 2,3 MB | ≈ 0,2 MB |

La cota para entradas de magnitud absurda (≈ 3,2 MB, DR-9) no depende de este pedido: con números
enormes el redondeo no acorta nada.

**Alternativas.**

| # | Alternativa | A favor | En contra |
|---|---|---|---|
| a | **3 decimales en todas las listas en m, m.c.a. y L/s** (decisión del dueño, plan U-39) | −70 % en el peor caso y −75 % en el caso típico sin quitar un dato; regla única y sencilla de documentar; router intacto | El predicado de D-60 (1) admite la banda de ±0.0005 m; una lista ya no se compara con igualdad con un escalar (hay que redondear el escalar; reglas en `INTEGRATION.md`) |
| b | (a) **salvo `pressure_head_max_m` y `pressure_head_min_m`**, que salen con precisión completa | D-60 (1) se cumple sin banda: el aviso existe si y solo si alguna progresiva cumple el predicado; solo +≈ 16 kB | Regla con excepción; envolventes de presión con 17 cifras junto a todo lo demás al milímetro; obliga a enmendar otra vez las historias (lista de F1, HU-2.2 crit. 2, HU-4.2 crit. 3) |
| c | **Solo los fotogramas** (`frame_head_m`, `frame_x_m`) | Series, envolventes y el predicado de D-60 intactos | Deja sin tocar el 40 % de la respuesta (series): ≈ 1,7 MB; obliga a enmendar las historias |
| d | **Sin redondeo** (D-57 (9) tal cual); solo se adelgaza con DR-8 | Nada cambia en la precisión | ≈ 2,3 MB en el peor caso y ≈ 0,2 MB en el típico; se pierde la mayor palanca; obliga a enmendar las historias |

**Recomendación del upstream.** (a). 1 mm de columna y 0.001 L/s están muy por debajo de la
incertidumbre del modelo (f constante, celeridad, ley de cierre); la banda de D-60 (1) es de medio
milímetro, en ella manda el aviso calculado con precisión completa, y se documenta. Si el portal
exige la igualdad lógica exacta de D-60 (1), (b) la da por 16 kB.

**Qué cambia en el contrato o la pantalla según lo que se decida.** (a): plan §1.4 y U-39 tal cual;
U-36 y V-13 con la banda; `ui-spec.json` cambia una frase del predicado («sin j que lo cumpla […]
tampoco hay aviso», salvo en la banda); `INTEGRATION.md` documenta la regla de precisión y cómo
comparar. (b): las dos envolventes de presión salen de la lista de U-39 y U-36 vuelve a la
igualdad exacta; enmienda de historias. (c): U-39 se reduce a `frame_*`. (d): U-39 se retira. En
todas, el router sigue sin transformar la respuesta.

---

## DR-8 — ¿Admite el portal retirar `frame_pressure_head_m` y que el panel derive p/γ(x, t) = `frame_head_m` − `elevation_m`?

| | |
|---|---|
| Estado | resuelto |
| Bloquea | **sí** — forma de la Capa 1 2.0 (campo de salida retirado) |
| Categoría | funcionalidad |
| Decisión del portal | D-64 — (a) sale `frame_pressure_head_m`; p/γ = `frame_head_m` − `elevation_m` en una función pura de `lib/mainpipe-transient/` con test contra `pressure_head_valve_m` (tolerancia 0.0015 m); `INTEGRATION.md` declara como contrato `frame_x_m == x_m` y p/γ = H − z (enmienda D-57 (4)) |

**Contexto.** D-57 (4) dimensionó la película con **dos** matrices, H y p/γ («Con dos matrices (H y
p/γ) es la fórmula de (a)»). La presión de cada fotograma es, por definición, la altura menos la
cota de la progresiva: el paquete la calcula exactamente así (`frame_head_m` − `elevation_m`; el
dueño midió diferencia 0.0 entre las dos matrices de la 1.0), y el prototipo de G3 ya la deriva en
el navegador (`portal/prototype.html`, función `updateInstant`). El dueño decidió retirarla (F4,
HU-4.1 crits. 1–3 enmendados en G1). Es una **resta de dos columnas alineadas**, sin celeridad,
fricción ni nada que dé el método: no duplica lógica hidráulica en el sentido de D-58 (4), pero sí
pone una operación en el frontend, y D-57 contaba con la matriz; por eso se pide. Con DR-7 (a) la
presión derivada se aparta como mucho 0.001 m de la redondeada que daba la 1.0. Las series de
presión en la válvula y en L/2 y las envolventes de presión **siguen** en la respuesta (con ellas
se dibujan los umbrales, los cruces en rojo de D-60 y los avisos). Es un cambio de forma que rompe:
`SCHEMA_VERSION` pasa a `"2.0"` (plan U-15), junto con la retirada de `density_kgm3` y `gravity_ms2`
de la entrada (plan U-40, sin pedido).

**Alternativas.**

| # | Alternativa | A favor | En contra |
|---|---|---|---|
| a | **Retirar `frame_pressure_head_m`**; la pestaña «Presión p/γ(x)» dibuja `frame_head_m[k][j]` − `elevation_m[j]` | −0,33 MB en el peor caso (con DR-7 (a)) o, si se quisiera, el doble de fotogramas con el mismo tamaño (DR-9); el prototipo aprobado ya lo hace; menos superficie de contrato | Una resta por fotograma en el frontend (≤ 699 progresivas); la película ya no trae p/γ «hecha» |
| b | **Mantener las dos matrices** (a 3 decimales si DR-7 lo admite) | D-57 (4) tal cual; la pantalla no resta nada | ≈ +0,33 MB en el peor caso; con magnitudes absurdas la cota sube a ≈ 4,4 MB, por encima de 3,5 MB (hallazgo F5-01 sigue abierto y documentado) |
| c | **Mantener solo la presión** y retirar `frame_head_m`; la pestaña «Altura H(x)» suma la cota | Mismo tamaño que (a); la presión, que es lo que mira el ingeniero, llega sin operar | H es la variable del método y la que se compara con las series (HU-4.1 crit. 1); obligaría a reescribir F4 y la pestaña H(x) |
| d | **Matriz de presión opcional**, detrás de una entrada `include_frame_pressure` (falso por defecto) | Por defecto igual que (a); quien la quiera la pide | El portal nunca la enviaría (como `frame_flow_lps`, D-57 (3)): superficie de contrato y pruebas sin consumidor (plan U-33) |

**Recomendación del upstream.** (a). Pierde cero información, es lo que ya hace el prototipo
aprobado y, con DR-9 (a), deja la respuesta dentro de 3,5 MB para toda entrada admitida.

**Qué cambia en el contrato o la pantalla según lo que se decida.** (a): `SolveResponse` sin
`frame_pressure_head_m` (plan §1.4, U-11, U-24); en `ui-spec.json` la serie «p/γ en el instante t»
deja de apuntar a `response.frame_pressure_head_m[]` y se declara como `frame_head_m` −
`elevation_m`; DR-9 decide el tope. (b): la Capa 1 conserva el campo (a la precisión que diga
DR-7), DR-9 queda sin objeto y rige D-57 (4) literal; la pantalla no cambia. (c): sale
`frame_head_m`, se enmiendan F4 y la pestaña H(x). (d): entrada nueva y campo anulable; la pantalla
como en (a).

---

## DR-9 — Con una sola matriz `frame_*`, ¿qué tope de fotogramas rige?

| | |
|---|---|
| Estado | resuelto |
| Bloquea | **sí** — fija el tope de fotogramas de la Capa 1 (plan U-10) y la entrada de la guarda de D-57 (2) |
| Categoría | funcionalidad (tamaño de respuesta) |
| Decisión del portal | D-65 — (a) tope min(1001, ⌊50 000 / n⌋) = 50 000 celdas en la única matriz; la guarda de D-57 (2) mide dos recetas (peor caso realista y magnitudes extremas), ambas ≤ 3,5 MB, y el techo vale para toda entrada solo con esa guarda en verde (enmienda D-57 (4), precisa D-57 (1)-(2)) |

**Depende de DR-8**: solo tiene objeto si sale `frame_pressure_head_m` (DR-8 (a), (c) o (d)).

**Contexto.** D-57 (4) fija «presupuesto de fotogramas = 100 000 celdas entre todas las matrices
`frame_*` que viajan por defecto» y da la fórmula para dos matrices, min(1001, ⌊50 000 /
n_progresivas⌋); su razón dice que quitar una matriz «se convierte en resolución temporal». Leído
al pie de la letra con una sola matriz, el tope pasaría a min(1001, ⌊100 000 / n⌋). El upstream
propone **no** hacerlo, por un hecho que la medición de la fase 5 sacó a la luz (hallazgo F5-01,
aceptado por el dueño): con entradas admitidas pero de magnitud absurda (cotas o caudales de
10¹⁵⁰; `reservoir_level_m` no tiene rango) la respuesta del contrato 1.0 llegó a 4 129 794 B, por
encima de los 3,5 MB de D-57 (1). Con números así el redondeo de DR-7 no acorta nada: cada número
puede ocupar 25 B (`-1.2345678901234567e+150` y su coma). La cota absoluta es entonces
(números de la respuesta) × 25 B:

| Tope | Peor caso realista: fotogramas, `frame_stride` | Peor caso realista, tamaño | Cota absoluta |
|---|---|---|---|
| min(1001, ⌊50 000 / n⌋) | 70, 145 | ≈ 0,96 MB | ≤ 127 300 números → **≈ 3,2 MB** |
| min(1001, ⌊60 000 / n⌋) | 84, 121 | ≈ 1,03 MB | ≤ 137 300 números → ≈ 3,45 MB |
| min(1001, ⌊100 000 / n⌋) | 142, 71 | ≈ 1,30 MB | ≤ 177 300 números → ≈ 4,4 MB |

(Peor caso realista: N = 200, 500 vértices, 699 progresivas, 10 000 pasos; con L/a = 1,12 s, un
fotograma cada 0,81 s con el primer tope y cada 0,40 s con el último. Caso del Excel: 401
fotogramas con cualquiera de los tres, sin submuestreo.)

**Alternativas.**

| # | Alternativa | A favor | En contra |
|---|---|---|---|
| a | **Mantener la fórmula de hoy**, min(1001, ⌊50 000 / n⌋): ≤ 50 000 celdas en la única matriz | D-57 (1) se cumple para **toda** entrada admitida (≤ 3,2 MB), lo que cierra F5-01; los mismos fotogramas que hoy; es el estimado del dueño | Usa la mitad del presupuesto de D-57 (4); en las mallas más grandes la película sigue siendo gruesa |
| b | **D-57 (4) al pie de la letra**: min(1001, ⌊100 000 / n⌋) | El doble de fotogramas en las mallas grandes; sigue la razón de D-57 (más resolución en vez de menos peso) | Con magnitudes absurdas, ≈ 4,4 MB: por encima del techo y a un paso de los 4,5 MB de producción; F5-01 sigue abierto |
| c | **El mayor presupuesto que respeta la cota**: min(1001, ⌊60 000 / n⌋) | +20 % de fotogramas con D-57 (1) cumplido para toda entrada | Margen de la cota ≈ 1,5 %: cualquier campo nuevo o cambio de formato lo rompe |
| d | (b) **acotando las entradas** (p. ej. cotas, longitudes y caudales con un máximo físico) para que ningún número pase de ≈ 11 B | El doble de fotogramas y una cota absoluta ≈ 2 MB | Topes de entrada arbitrarios y nuevos 422 que el usuario puede encontrar con datos reales extremos; enmienda de historias (HU-1.6, HU-2.3) |

**Recomendación del upstream.** (a). La enmienda nació para alejarse del techo; con (a) el techo
deja de depender de que la entrada sea sensata y la regla de D-57 (1) se cumple sin excepción. Si
el portal prefiere resolución, (b) es viable con la documentación de F5-01 que ya aceptó el dueño.

**Qué cambia en el contrato o la pantalla según lo que se decida.** (a): U-10 conserva su fórmula
(el presupuesto efectivo se describe como 50 000 celdas en una matriz); `INTEGRATION.md` publica
la cota absoluta y la guarda de D-57 (2) mide la misma receta. (b) / (c): cambia la constante de U-10
y el número de fotogramas del peor caso; con (b), `INTEGRATION.md` mantiene el aviso de F5-01. (d):
además, rangos nuevos en `SolveRequest`. La pantalla no cambia en ninguna (lee `frame_stride`).

---

## DR-10 — ¿Acepta el portal que el panel «Transitorio» salga sin el texto de fase que aprobó D-58?

| | |
|---|---|
| Estado | resuelto |
| Bloquea | no — pantalla; la Capa 1 no cambia |
| Categoría | funcionalidad |
| Decisión del portal | D-66 — (a) sin texto de fase en v1; D-58 (4) queda sin efecto. Una guía de fase futura entraría como dato de la Capa 1, con su pedido |

**Contexto.** D-58 (1) incluyó en el alcance del panel el «texto de fase» y D-58 (4) lo fijó como
función pura en `lib/mainpipe-transient/`, con tests, a partir de `reflection_time_s`,
`wave_period_s`, `closure_duration_s` y el instante (DR-1, punto 2; plan U-32). El dueño lo retira
de v1 (épica, «Fuera de v1»; F4). Es una reducción de alcance, pero el portal aprobó el panel con
ese texto, así que se le pide. Los tres tiempos **siguen** en la respuesta (se muestran como
indicadores). Observación técnica del upstream: las cinco frases describen el ciclo ideal de un
cierre rápido; con un cierre lento (Tc > 2L/a) la regla del prototipo dice «Reflexión en el
depósito» mientras la válvula sigue cerrando, así que el texto puede confundir justo en los casos
de Michaud.

**Alternativas.**

| # | Alternativa | A favor | En contra |
|---|---|---|---|
| a | **Sin texto de fase en v1** | Menos código y pruebas en el frontend; ninguna frase engañosa en cierres lentos; la Capa 1 no cambia | El usuario pierde una guía de lectura de la onda mientras reproduce |
| b | **Mantenerlo como fijó D-58 (4)** | Lo aprobado; ayuda a leer la animación | Contra la decisión del dueño; habría que reabrir otra vez las historias (F4, épica); el texto es impreciso en cierres lentos |
| c | **Nota estática** bajo el panel: qué pasa en 0–L/a, L/a–2L/a… con los valores de 2L/a, 4L/a y Tc, sin cambiar con el instante | Conserva la explicación sin lógica por fotograma | Otro elemento de pantalla que nadie pidió; no dice en qué fase está el instante actual |
| d | **Fase como dato de la Capa 1**: un código por fotograma (`frame_phase`, `Literal`) que el paquete calcula teniendo en cuenta Tc, y el portal traduce | Correcto también en cierres lentos; el portal no razona sobre la onda | Campo nuevo, historia nueva, ≈ 1–8 kB más; textos de dominio que fijar; contradice la decisión del dueño |

**Recomendación del upstream.** (a), la decisión del dueño; si el portal quiere conservar una ayuda,
(c) no toca el contrato.

**Qué cambia en el contrato o la pantalla según lo que se decida.** Contrato: nada en (a), (b) y
(c); en (d), campo nuevo `frame_phase` (aditivo, dentro de la 2.0 antes de congelarla). Pantalla:
(a) quita de `ui-spec.json` y de `prototype.html` el texto de fase (y la función que lo calcula) y
U-32 se retira; (b) nada; (c) sustituye el texto por una nota fija; (d) el texto sale del código
por fotograma.

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

---

## Pendiente tras D-63 … D-66 (antes de la nueva G4)

Copiado de las decisiones del portal (2026-11-15). Estado al 2026-11-15, tras la enmienda del
plan (`hie-architect`): **hecho en el plan** todo lo de `hie-architect`; **pendiente** lo de
`hie-prototyper` (frase del rojo) y lo de `hie-api` (construcción, fases 5 y 6), cada uno en su
etapa.

| Punto | Qué | Dónde | Quién | Estado |
|---|---|---|---|---|
| D-63 (3)-(4) | Marcador del cruce y extremo en `critical` desde el aviso `danger` de `checks` (`x_m`, `time_s`, `value_m`); tramo rojo opcional sobre la envolvente redondeada, **solo si existe el aviso**. Nunca rojo sin aviso; el único desacuerdo admitido es aviso y marcador sin tramo a < 0.0005 m del umbral | plan §1.5, U-36, V-13; frase del predicado en `ui-spec.json` y `prototype.html` | `hie-architect`, `hie-prototyper` | plan: **hecho** (§1.5 reescrito: PN ↔ `PN_EXCEEDED`, límite ↔ `COLUMN_SEPARATION_RISK`, campos del aviso idénticos al extremo global; U-36; V-13 reescrita). `ui-spec.json` / `prototype.html`: **hecho** el 2026-11-15 (`hie-prototyper`: criterio del rojo y marcadores de `presiones-progresiva`, nota en colores de `perfil-envolventes`; el prototipo dibuja tramo y marcador en `critical` solo con el aviso) |
| D-63 (5) | Regla de precisión y de comparación (redondear el escalar a 3 decimales o tolerancia 0.0005 m) | `portal/INTEGRATION.md` (fase 6) | `hie-api` | plan: **hecho** (§1.4, regla de comparación; fase 6 (b)). `INTEGRATION.md`: **pendiente** (`hie-api`, fase 6) |
| D-63 (6) | Los casos dorados congelan los valores redondeados | fase 5 | `hie-api` | plan: **hecho** (fase 5: V-19 sobre la salida de `solve()`; fase 6: V-19 sobre cada ejemplo). Construcción: **pendiente** (`hie-api`, fases 5–6) |
| D-64 (3) | Declarar como contrato `frame_x_m == x_m` y p/γ(x_j, t_k) = `frame_head_m[k][j]` − `elevation_m[j]` con la misma cota z que `pressure_head_*`; mantenerlo probado (`tests/test_frames.py`) | plan §1.4; `portal/INTEGRATION.md` | `hie-architect`, `hie-api` | plan: **hecho** (§1.4, invariantes 1–3; V-17; U-42). Pruebas e `INTEGRATION.md`: **pendiente** (`hie-api`, fases 5–6) |
| D-65 (3)-(4) | Medir dos recetas (peor caso realista y magnitudes extremas, ≈ 25 B por número), ambas ≤ 3 500 000 B; publicar cota absoluta y las dos cifras medidas | plan U-34 / §2; fase 5; `portal/INTEGRATION.md` | `hie-architect`, `hie-api` | plan: **hecho** (§2, fase 5 (5.4), V-18; U-34 (3), (3b), (5) y (6) enmendadas: receta adversaria determinista con ≥ 20 B por número; si una medición supera el techo, se detiene y se pide). Mediciones e `INTEGRATION.md`: **pendiente** (`hie-api`, fases 5–6). F5-01 se cierra cuando las dos estén en verde |
| D-66 | Retirar U-32 (texto de fase) | plan; `ui-spec.json` ya lo retiró en G3 | `hie-architect` | **hecho** (U-32 retirada; plan §7) |
| Opcional | `frame_x_m` repite `x_m` (≈ 5 kB); el portal sugiere que podría quitarse. No registrado como decisión | plan, si el dueño lo quiere | dueño | **cerrado**: el dueño decide **mantenerlo** (U-42); el contrato lo declara idéntico a `x_m` |

Nota para el portal (no cambia ninguna decisión): D-64 (2) indexa la serie de la válvula con
k·`frame_stride`. Es exacto en el fixture que nombra (caso del Excel, sin submuestreo); con
submuestreo el último fotograma es el paso `n_steps` (en la receta del peor caso, 69·145 = 10 005
≠ 10 000). La regla general, que publicará `portal/INTEGRATION.md`, es el índice i_k con
`time_s[i_k]` == `frame_time_s[k]` (plan §1.4, invariante 3).
