# Plan 01 — Golpe de ariete por cierre de válvula (v1)

| | |
|---|---|
| estado | **congelado** — 2026-11-14, puerta G4. Contrato de Capa 1 (§1) con `SCHEMA_VERSION` = `"1.0"`. Antes: aprobado en G2 el 2026-11-14 y reaprobado el mismo día tras incorporar D-57 … D-62. Toda enmienda posterior sigue `kit 01 §8` y U-37 |
| kit | 3.0.0 |
| fecha | 2026-11-14 (congelado) |
| historias | `doc/stories/00-epica.md` … `04-serie-reproduccion.md` (reaprobadas en G1 el 2026-11-14 con D-57: HU-4.1 crit. 1 sin `frame_flow_lps`, HU-1.6 crit. 13) |
| pedidos al portal | `portal/DECISION-REQUESTS.md` (DR-1 … DR-6, **todos resueltos**: D-57 … D-62, commit `2466321` del portal) |
| propuesta de Capa 2 | `portal/API-PROPOSAL.md` |
| decisiones internas | `doc/DECISIONS.md` (U-01 … U-37) |

---

# Parte 1 — Para el dueño

## Qué se construye

Una «calculadora de golpe de ariete» que el portal Fluida llamará por detrás. Recibe los datos de
una aducción por gravedad (depósito, tubería, válvula y la tabla de cierre de la válvula) y
devuelve, para toda la tubería y cada instante, la altura piezométrica y la presión (el caudal,
en la válvula y en el depósito); las envolventes de máximos y mínimos; los avisos de timbraje y de depresión; y la referencia
teórica de Joukowsky / Michaud. Es lo mismo que hoy hace el Excel, pero:

- con cualquier número de tramos (10 a 200) y cualquier duración dentro de un tope;
- con el **perfil real** del trazado, de modo que la presión de cada punto alto sale con su cota
  (el Excel suponía la tubería horizontal y por eso subestimaba la depresión de las lomas);
- con mensajes de error y avisos en español que dicen qué, dónde y cuándo.

La pantalla (formularios, gráficos, el botón PLAY) **no** se construye aquí: la hace el portal. Este
repositorio entrega el motor y la ficha técnica para que el portal lo enchufe sin rediseñar nada.

## En qué orden

Como en una obra: primero se replantea, luego se hace la estructura y se prueba, y al final los
acabados.

| Fase | Qué se hace | Analogía | Cómo sabremos que está hecha |
|---|---|---|---|
| 0 | Andamiaje del paquete y **congelado de los números del Excel** (recalculados una vez con Excel) | Replanteo: fijar los puntos de referencia antes de excavar | El paquete se instala limpio y los resultados del Excel quedan guardados como referencia, con su procedencia |
| 1 | El **cálculo MOC** en tubería horizontal | La estructura: es lo que más riesgo tiene | Reproduce el Excel paso a paso (± 0.05 m) y Joukowsky exacto sin fricción |
| 2 | La **ficha de entrada**: validaciones, mensajes, topes de malla y duración, medición de tiempos | El control de recepción de materiales | Cada dato malo se rechaza con un mensaje claro; el caso más grande calcula en < 1 s |
| 3 | El **perfil real** (x, z) | Pasar del plano en planta al perfil longitudinal | La loma de 40 m baja la presión mínima exactamente 40 m |
| 4 | Las **verificaciones**: PN, depresión, separación de columna, Joukowsky / Michaud | La inspección final con su acta | Cada aviso aparece justo en su umbral, con su mensaje |
| 5 | La **serie para el PLAY** | Las fotos del avance de obra | La película coincide con las series, y la respuesta más grande posible **pesada en báscula** (no estimada) cabe en los 3,5 MB que fijó el portal |
| 6 | **Entrega** al portal | Planos «as built» y acta de entrega | Lista de chequeo de la puerta G5 completa, desde un entorno limpio |

## Qué riesgos hay y cómo se cubren

1. **Que el motor no coincida con el Excel por un detalle de fórmula** (cómo se escribe la fricción
   en cada paso). Una diferencia de esquema basta para mover algunos décimos de metro. **Ya
   cubierto**: las fórmulas del Excel se leyeron el 2026-11-14 y el plan copia ese esquema; una
   transcripción de prueba coincide con el Excel recalculado a 10⁻¹³ m. Como el Excel no guarda
   resultados calculados, la fase 0 los genera una vez con Excel y los congela como referencia.
2. **Inestabilidad numérica con mucha fricción y tramos largos.** Como un encofrado demasiado
   largo sin apuntalar: con tramos muy largos, mucha fricción y diámetro pequeño, el esquema puede
   oscilar. Esos casos se rechazan con un mensaje que dice cuántos tramos usar como mínimo
   (punto 1 de abajo, confirmado en G2).
3. **Tiempo de cálculo y tamaño de la respuesta.** El portal espera la respuesta antes de atender
   a otros usuarios, y en producción corta toda respuesta de más de 4,5 MB sin que ninguna prueba lo
   vea. El portal ya fijó las cotas (D-57): respuesta ≤ 3,5 MB en el peor caso, tope de 10 000
   pasos de cálculo, película de H y presión sin el caudal. Como un camión que tiene que pasar bajo
   un puente: la cuenta en papel da ≈ 3,3 MB, cerca del gálibo, así que en la fase 5 **se pesa la
   carga real** del peor caso antes de entregar. Si no cupiera, se quitan fotogramas a la película
   de las mallas más grandes (nunca precisión ni series); el dueño aceptó esa regla en G2 (punto 6
   de abajo).
4. **Que el resultado parezca válido cuando ya no lo es.** Bajo la presión de vapor el agua se
   separa y este método deja de valer. No se modela (fuera de v1), pero el aviso dirá desde qué
   instante y en qué punto los resultados dejan de ser físicos.

## Lo que el portal decidió (D-57 a D-62)

Los seis pedidos están resueltos (detalle en la Parte 2 §7). Lo que cambia el motor es **D-57**
(tamaño): la película lleva solo altura y presión (el caudal por fotograma sale), como mucho
min(1001, ⌊50 000 / progresivas⌋) fotogramas, tope de 10 000 pasos de cálculo, respuesta ≤ 3,5 MB
medida y petición ≤ 64 KiB medida. Los otros cinco (panel «Transitorio», layout, colores, fórmulas,
sin IA) son de la pantalla y se incorporaron en la etapa 3 (`portal/ui-spec.json` y
`portal/prototype.html`, G3 reaprobada el 2026-11-14); de ellos el motor solo recoge dos
detalles: que cada aviso lleve su instante para el botón «Ir a t = … s» (ya lo lleva) y devolver la
presión mínima admisible usada, para que la línea del límite y su cruce en rojo salgan del mismo
resultado que los avisos (U-35, U-36).

## Puntos que el dueño confirmó en G2

Todos confirmados al reaprobar G2 el 2026-11-14 (`portal/HANDOFF.md`, notas); con ellos el plan se
congeló en G4. Se conservan como registro de lo que se aceptó.

**Ya aprobados en G2 el 2026-11-14, sin cambios** (ratificados; detalle en `doc/DECISIONS.md`):

- **(1) Nuevo error por malla gruesa con mucha fricción** (U-03): si el número de fricción del
  tramo supera 0.5, error 422 con el número mínimo de tramos.
- **(2) La presión mínima admisible no puede ser positiva** (U-21): rango −10.33 a 0 m.c.a. Un
  criterio de presión mínima positiva no es separación de columna y daría un aviso engañoso.
- **(4) Con perfil, enviar también `length_m` o `pipe_elevation_m` es error** (U-22), igual que
  enviar perfil con geometría horizontal (HU-2.3 crit. 5).
- **(5) `pipe_elevation_m` y `pn_bar` son obligatorios, sin valor por defecto** (U-14).

**Cambiados por D-57** (la numeración se conserva para no confundir con la aprobación anterior):

- **(3) Tope de pasos de cálculo = 10 000** (U-09; antes 20 000, lo fijó el portal). Duración máxima
  = 10 000 · L/(N·a): en el caso del Excel, 500 s con 20 tramos y 50 s con 200. Si se pide más, o
  si la duración por defecto Tc + 5·(4L/a) no cabe (cierres lentos con malla fina), error 422 que
  da la duración máxima y propone acortar o usar menos tramos (HU-1.6 crit. 13). La duración por
  defecto **no se recorta en silencio** al tope: el usuario ve el 422 y elige (decisión del
  upstream, U-09; el dueño la aceptó en G2).
- **(6) Tamaño de la respuesta en el peor caso ≈ 3,3 MB calculado, techo 3,5 MB medido** (D-57):
  ≈ 1,3 MB de series temporales + ≈ 1,9 MB de película + ≈ 0,1 MB de envolventes. El margen es
  corto (≈ 5 %), así que se pesa en la fase 5 con un peor caso a propósito desfavorable (U-34). Si
  la báscula diera más de 3,5 MB, **el plan propone** bajar el presupuesto de fotogramas hasta que
  quepa (menos fotogramas en las mallas grandes; el caso del Excel no cambia), lo que respeta D-57
  porque sus cifras son techos, e informar al portal en `portal/INTEGRATION.md`. **El dueño aceptó
  esta regla en G2** en lugar de abrir un pedido nuevo al portal (DR-7), y la lectura
  3,5 MB = 3 500 000 B.

**Nuevos**:

- **(7) `frame_flow_lps` desaparece del contrato**, sin opción para pedirlo (U-33): el portal
  nunca la enviaría y la historia lo retiró de v1.
- **(8) La respuesta devuelve la presión mínima admisible usada** (`min_allowed_pressure_head_m`,
  U-35), para que la pantalla dibuje la línea del límite y su cruce desde el resultado (D-60).

---

# Parte 2 — Técnica

## 1. Contrato de Capa 1

### 1.1 API pública (`kit 01 §3`)

`src/mainpipe_transient/__init__.py` exporta únicamente:

| Símbolo | Tipo |
|---|---|
| `solve(data: dict) -> dict` | única función de cálculo |
| `SolveRequest`, `SolveResponse`, `Check` | modelos Pydantic v2 |
| `MainpipeTransientError`, `MainpipeTransientValidationError`, `MainpipeTransientComputationError` | excepciones (§1.6) |
| `__version__` | `importlib.metadata.version("mainpipe-transient")` |
| `SCHEMA_VERSION` | `"1.0"` |

`solve` sigue los tres pasos de `kit 01 §3`: `SolveRequest.model_validate(data)` (un
`pydantic.ValidationError` se envuelve en `MainpipeTransientValidationError` con mensaje en español,
`raise … from exc`), calcula, y devuelve `SolveResponse(...).model_dump(mode="json")`. Cualquier
excepción no prevista se envuelve en `MainpipeTransientComputationError` (`kit 02 §1`). Importar el
paquete no calcula ni toca disco o red (`kit 03 §1`, `/health`).

**`SCHEMA_VERSION`** (U-15): cadena `"MAYOR.MENOR"`, empieza en `"1.0"`. Sube la **menor** con un
cambio aditivo compatible (campo de entrada opcional nuevo, campo de salida nuevo, valor nuevo de
`scenario`); sube la **mayor** con un cambio que rompe (campo retirado o renombrado, unidad o tipo
cambiado). Añadir un escenario (p. ej. parada de bombas) es menor si los campos actuales no cambian
de significado.

**Versión congelada en G4 (2026-11-14): `SCHEMA_VERSION = "1.0"`**, la forma que describe este §1.
Desde aquí, cambiar la Capa 1 exige motivo, entrada en el changelog del plan, subir
`SCHEMA_VERSION` según la regla de arriba (`kit 01 §8`) y regenerar `portal/examples/` y
`portal/INTEGRATION.md`; si el cambio toca algo que decidió el portal (D-57 … D-62), es un `DR`
nuevo (U-37). Cambiar un número sin cambiar la forma (p. ej. la regla de ajuste de U-34) no sube
`SCHEMA_VERSION` (`kit 01 §3`).

### 1.2 Unidades del contrato (U-06)

Las del `kit 01 §4`, con la unidad en el nombre. Caudales en **L/s**, diámetro en **mm**,
longitudes, cotas y alturas en **m**, alturas de presión en **m.c.a.** (sufijo `_m`, p/γ = H − z),
tiempos en **s**, PN en **bar**, densidad en **kg/m³**, gravedad en **m/s²**. Internamente se
trabaja en SI (m³/s, m). La pantalla muestra estas mismas unidades; si quisiera otras, la
conversión es del portal (`kit 01 §4`).

### 1.3 `SolveRequest`

`model_config = ConfigDict(extra="forbid")` (U-23). Todas las restricciones de rango se escriben
como validadores propios con mensaje en español (U-13), no como `Field(gt=…)`, para que el 422 de
FastAPI llegue en español (`kit 02 §3`). Los rangos se repiten en `description`.

| Campo | Tipo | Unidad | Por defecto | Rango / regla (fuera → 422) | HU |
|---|---|---|---|---|---|
| `scenario` | `Literal["reservoir_pipe_valve"]` | — | `"reservoir_pipe_valve"` | único valor en v1 | épica P1 |
| `geometry` | `Literal["horizontal","profile"]` | — | `"horizontal"` | — | 1.1, 2.1 |
| `length_m` | `float \| None` | m | `None` | obligatorio y > 0 con `horizontal`; prohibido con `profile` | 1.6-7, 2.3-5 |
| `pipe_elevation_m` | `float \| None` | m | `None` | obligatorio y ≤ `reservoir_level_m` con `horizontal`; prohibido con `profile` | 1.6-8 |
| `profile_x_m` | `list[float] \| None` | m | `None` | obligatorio con `profile`, prohibido con `horizontal`; 2–500 puntos; `[0] = 0`; estrictamente creciente | 2.3 |
| `profile_z_m` | `list[float] \| None` | m | `None` | igual longitud que `profile_x_m`; `[0] ≤ reservoir_level_m` | 2.3 |
| `inner_diameter_mm` | `float` | mm | — | > 0 | 1.6-7 |
| `wave_speed_ms` | `float` | m/s | — | 0 < a ≤ 1500 | 1.6-7 |
| `darcy_friction_factor` | `float` | — | — | 0 ≤ f ≤ 0.1 | 1.6-7 |
| `initial_flow_lps` | `float` | L/s | — | > 0 | 1.6-7 |
| `reservoir_level_m` | `float` | m | — | cualquiera (mismo datum que la tubería) | 1.1 |
| `density_kgm3` | `float` | kg/m³ | `1000.0` | > 0 | 3.1 |
| `gravity_ms2` | `float` | m/s² | `9.81` | 9.7 ≤ g ≤ 9.9 | 1.6-7 |
| `pn_bar` | `float` | bar | — | > 0 | 3.1 |
| `min_allowed_pressure_head_m` | `float` | m.c.a. | `-10.0` | −10.33 ≤ valor ≤ 0 (U-21) | 3.2 |
| `closure_time_s` | `list[float]` | s | — | 2–20 puntos; `[0] = 0`; estrictamente creciente | 1.2, 1.6 |
| `closure_flow_lps` | `list[float]` | L/s | — | igual longitud; `|[0] − Q₀| ≤ 0.1 %·Q₀`; 0 ≤ Q ≤ Q₀; último = 0 | 1.2, 1.6 |
| `n_reaches` | `int` | — | `20` | par; 10 ≤ N ≤ 200 | 1.7 |
| `duration_s` | `float \| None` | s | `None` → Tc + 5·(4L/a) | ≥ Tc + 2L/a; `n_steps` ≤ `MAX_STEPS` = 10 000 (U-09, D-57), también con la duración por defecto | 1.6-10, 1.6-13, 1.7 |
| `include_frames` | `bool` | — | `True` | `False` → campos `frame_*` y `frame_stride` en `null` (U-24) | 4.2 |

Reglas cruzadas adicionales, todas 422 y en el validador del modelo:

- **Número de fricción del tramo** (U-03): φ = f·Δx·V₀ / (2·D·a) ≤ 0.5. El mensaje da φ y el
  `n_reaches` mínimo par que lo cumple. (Confirmado por el dueño en G2.)
- **Tope de pasos** (U-09, D-57, HU-1.6 crit. 13): `n_steps` = ⌈T/Δt − 10⁻⁹⌉ ≤ `MAX_STEPS`
  = 10 000, con T la duración pedida o, si falta, la de por defecto. El mensaje nombra
  `duration_s` y `n_reaches`, da los pasos necesarios, la **duración máxima admisible con esa
  malla** T_max = `MAX_STEPS`·Δt y el N par máximo con la duración pedida, e indica que se puede
  acortar la duración o usar una malla más gruesa. T_max se escribe **truncada** (no redondeada) a
  los decimales de U-26, para que enviar la cifra mostrada calcule sin error (HU-1.6 crit. 13).
  Variantes: si `duration_s` no se envió, el mensaje dice que la duración por defecto
  Tc + 5·(4L/a) = … s supera el tope y propone enviar `duration_s` ≤ T_max; si la duración mínima
  Tc + 2L/a ya supera T_max, no propone acortar sino el N máximo que la admite (y, si ni N = 10 la
  admite, dice que el cierre es demasiado lento para el tope de pasos). Ejemplo del caso del Excel:
  Δt = 1000/(N·1000) → T_max = 500 s con N = 20 y 50 s con N = 200.
- El primer caudal de la ley se sustituye internamente por Q₀ (U-18), tras validar la tolerancia.

Mensajes: en español, con unidades, decimales con punto y el punto exacto que falla (`kit 02 §3`;
textos de HU-1.6 y HU-2.3). Formato numérico común en U-26.

### 1.4 `SolveResponse`

`model_config = ConfigDict(allow_inf_nan=False)` (`kit 01 §4`). Todas las series van en columnas
paralelas. Un `null` solo aparece donde la tabla lo dice.

**Identidad y estado**

| Campo | Tipo | Unidad | Contenido |
|---|---|---|---|
| `schema_version` | `str` | — | igual a `SCHEMA_VERSION` |
| `scenario` | `Literal` | — | eco de la entrada |
| `geometry` | `Literal` | — | eco de la entrada |
| `status` | `Literal["ok","warning","error"]` | — | el más severo de `checks`; `ok` si no hay |
| `checks` | `list[Check]` | — | §1.5 |

**Derivados**

| Campo | Unidad | Fórmula |
|---|---|---|
| `length_m` | m | L (`length_m` o último `profile_x_m`) |
| `area_m2` | m² | A = π·D²/4 |
| `velocity_initial_ms` | m/s | V₀ = Q₀/A |
| `head_loss_m` | m | h_f = f·(L/D)·V₀²/(2g) |
| `dx_m`, `dt_s` | m, s | Δx = L/N, Δt = Δx/a |
| `n_reaches`, `n_steps` | — | N; ⌈T/Δt − 10⁻⁹⌉ |
| `duration_s` | s | duración efectiva = `n_steps`·Δt |
| `reflection_time_s` | s | 2L/a |
| `wave_period_s` | s | 4L/a |
| `closure_duration_s` | s | Tc = primer instante de la tabla con Q = 0 |
| `friction_number` | — | φ = f·Δx·V₀/(2·D·a) (informativo, U-03) |

**Series temporales** (longitud `n_steps + 1`, instante k = k·Δt)

`time_s` (s), `head_valve_m`, `head_midpoint_m` (m), `pressure_head_valve_m`,
`pressure_head_midpoint_m` (m.c.a.), `flow_reservoir_lps`, `flow_valve_lps` (L/s). «Punto medio» =
nodo x = L/2 (N par); su cota es z(L/2) interpolada del perfil.

**Envolventes por progresiva** (todas de la misma longitud, U-07)

| Campo | Unidad | Contenido |
|---|---|---|
| `x_m` | m | nodos de cálculo ∪ vértices del perfil, ordenados, sin duplicados |
| `x_is_node` | `list[bool]` | `true` si la progresiva es nodo de cálculo, `false` si es solo vértice |
| `elevation_m` | m | z(x) |
| `head_initial_m` | m | H de régimen |
| `pressure_head_initial_m` | m.c.a. | H de régimen − z |
| `head_max_m`, `head_min_m` | m | sobre **todos** los pasos (U-19) |
| `pressure_head_max_m`, `pressure_head_min_m` | m.c.a. | ídem, con la cota del punto |

**Extremos** (desempate: primer instante, luego menor x; U-25)

`head_valve_max_m`, `head_valve_max_time_s`, `head_valve_min_m`, `head_valve_min_time_s`,
`pressure_head_max_global_m`, `pressure_head_max_global_x_m`, `pressure_head_max_global_time_s`,
`pressure_head_min_global_m`, `pressure_head_min_global_x_m`, `pressure_head_min_global_time_s`.

**Timbraje y límite de depresión**

`pn_head_m` (m.c.a.) = PN·10⁵/(ρ·g); `pressure_max_pn_ratio_pct` (%) =
100·`pressure_head_max_global_m`/`pn_head_m`; `min_allowed_pressure_head_m` (m.c.a.) = eco del
límite usado (el enviado o −10.0 por defecto), siempre presente (U-35). Con `pn_head_m` es lo que
la pantalla necesita para dibujar las dos líneas de umbral y marcar sus cruces con el predicado de
§1.5 (D-60) sin leer el formulario, que puede haber cambiado tras el cálculo (D-58 (3)).

**Referencia teórica** (informativa: nunca genera aviso ni cambia `status`, HU-3.4)

| Campo | Unidad | Contenido |
|---|---|---|
| `maneuver_type` | `Literal["rapid","slow"]` | `rapid` si Tc ≤ 2L/a |
| `joukowsky_head_rise_m` | m | a·V₀/g (siempre) |
| `michaud_head_rise_m` | m \| `null` | 2·L·V₀/(g·Tc); `null` si la maniobra es rápida |
| `full_pulse_length_m` | m \| `null` | L − a·Tc/2; `null` si la maniobra es lenta |
| `theoretical_head_rise_m` | m | Joukowsky si rápida, Michaud si lenta |
| `moc_head_rise_valve_m` | m | `head_valve_max_m` − H de régimen en la válvula |
| `theory_deviation_pct` | % | 100·(MOC − teórico)/teórico (U-17; igual que `4_Validacion!C27`, que la da como fracción). Caso Excel: 3.712 % |

**Serie para el reproductor** (F4; todos `null` si `include_frames = false`; tope en U-10, D-57)

| Campo | Tipo | Unidad | Contenido |
|---|---|---|---|
| `frame_stride` | `int \| null` | — | pasos de cálculo entre fotogramas consecutivos (1 = sin submuestreo); el último intervalo puede ser más corto, porque el último paso siempre es fotograma |
| `frame_time_s` | `list[float] \| null` | s | instantes; el primero 0 y el último `duration_s`; cada uno es un valor de `time_s` |
| `frame_x_m` | `list[float] \| null` | m | idéntico a `x_m` |
| `frame_head_m` | `list[list[float]] \| null` | m | `[k][j]`: fotograma k, progresiva j (U-11) |
| `frame_pressure_head_m` | `list[list[float]] \| null` | m.c.a. | ídem, = H − z |

Tope de fotogramas (U-10, D-57 (4)): n_fotogramas ≤ min(1001, ⌊50 000 / n_progresivas⌋), con
n_progresivas = longitud de `x_m` (100 000 celdas entre las dos matrices). Valores sin redondear
(D-57 (9)). **No hay `frame_flow_lps`** ni opción para pedirlo (U-33, D-57 (3)): el caudal en el
tiempo está en `flow_valve_lps` y `flow_reservoir_lps` (HU-1.4). Caso del Excel: 401 fotogramas
× 21 progresivas, sin submuestreo (HU-4.1 crit. 1). Peor caso (N = 200, 500 vértices fuera de
nodo → 699 progresivas, 10 000 pasos): tope 71, `frame_stride` = ⌈10 000/69⌉ = 145, **70**
fotogramas (k = 0, 145, …, 9 860 y 10 000).

### 1.5 `checks` (`kit 01 §5`)

Modelo `Check`, misma forma para todos los códigos (U-25):

| Campo | Tipo | Unidad | Contenido |
|---|---|---|---|
| `code` | `Literal[…]` | — | tabla de abajo |
| `severity` | `Literal["warning","error"]` | — | |
| `message` | `str` | — | español, con unidades y decimales con punto |
| `value_m` | `float` | m.c.a. | valor que dispara el aviso |
| `limit_m` | `float` | m.c.a. | umbral cruzado |
| `x_m` | `float` | m | progresiva del valor (está en `x_m`) |
| `time_s` | `float` | s | instante del valor (está en `time_s`) |
| `first_x_m` | `float \| null` | m | solo `COLUMN_SEPARATION_RISK`: primera progresiva bajo el límite; `null` en los demás |
| `first_time_s` | `float \| null` | s | ídem, primer instante |
| `first_pressure_head_m` | `float \| null` | m.c.a. | ídem, presión en ese punto e instante |

| `code` | Severidad | Condición | `value_m` / `limit_m` / `x_m`, `time_s` |
|---|---|---|---|
| `PN_EXCEEDED` | `error` | p_max global > `pn_head_m` | p_max / `pn_head_m` / lugar del máximo |
| `PN_NEAR_LIMIT` | `warning` | 80 % < p_max/PN ≤ 100 % (U-16) | ídem |
| `COLUMN_SEPARATION_RISK` | `error` | p_min global < `min_allowed_pressure_head_m` | p_min / límite / lugar del mínimo; `first_*` = primer cruce (U-25) |
| `SUBATMOSPHERIC_PRESSURE` | `warning` | límite ≤ p_min global < 0 | p_min / 0 / lugar del mínimo |
| `STEADY_NEGATIVE_PRESSURE` | `warning` o `error` | p de régimen < 0 en algún x; `error` si además < límite | p mínima de régimen / 0 (warning) o límite (error) / su x, t = 0 |

Orden de `checks`: primero los `error`, luego los `warning`; dentro de cada severidad, en el orden de
la tabla. Los avisos son independientes: un régimen negativo puede dar a la vez
`STEADY_NEGATIVE_PRESSURE` y `SUBATMOSPHERIC_PRESSURE` o `COLUMN_SEPARATION_RISK`.

**Correspondencia con la paleta de estado del portal (D-13, `kit 01 §5`)** (U-20): `status` `ok` →
`success`; `warning` → `warning`; `error` → `danger`. `severity` `warning` → `warning`; `error` →
`danger`. `caution` no se usa. Sin niveles fuera de la paleta.

Mensajes modelo: los de HU-3.1 crit. 4 y HU-3.2 crit. 4 (literales, salvo el signo menos, que
es ASCII, U-26). El de
`COLUMN_SEPARATION_RISK` dice siempre, en este orden: valor y límite, dónde, cuándo, y que desde ahí
los resultados del MOC simple dejan de ser físicos.

**Uso en el panel «Transitorio» (D-58, D-60; U-36).** Sin campos nuevos en `Check`:

- **Botón «Ir a t = … s»** (D-58 (1)): todo aviso lleva instante (`time_s`, y en
  `COLUMN_SEPARATION_RISK` además `first_time_s`; `STEADY_NEGATIVE_PRESSURE` lleva t = 0). Son
  valores de `time_s`, múltiplos de Δt; con `frame_stride` > 1 pueden no coincidir con un
  fotograma, y elegir el fotograma (el más cercano, según `portal/ui-spec.json`) es de la pantalla.
  Con `include_frames: false` no hay fotogramas y el botón no aplica.
- **Predicado del cruce en rojo** (D-60 (1), «el mismo predicado que el aviso `danger`»): en la
  progresiva j hay cruce del PN si `pressure_head_max_m[j]` > `pn_head_m`, y del límite si
  `pressure_head_min_m[j]` < `min_allowed_pressure_head_m` (desigualdades estrictas, como
  `PN_EXCEEDED` y `COLUMN_SEPARATION_RISK`). Como los extremos globales son el máximo y el mínimo
  exactos de esas envolventes (mismos `float`), el aviso `danger` existe **si y solo si** algún j
  cumple su predicado; lo comprueba V-13. La pantalla compara dos listas con dos números: no
  recalcula hidráulica.

### 1.6 Excepciones (`kit 02 §1`)

Prefijo **`MainpipeTransient`** (U-12): único entre los paquetes del portal (`Mainpipe` queda para
`mainpipe-design`).

```python
class MainpipeTransientError(Exception):                        # http_status = 500
class MainpipeTransientValidationError(MainpipeTransientError, ValueError):   # 422
class MainpipeTransientComputationError(MainpipeTransientError):              # 500
```

No hay `MainpipeTransientServiceError`: el paquete no llama a ningún servicio externo (`kit 01 §6`,
`kit 02 §1`). Sin subclases más finas en v1: toda la validación ocurre en el modelo, así que el
nombre concreto que verá `examples/` es `MainpipeTransientValidationError`.

Un `NaN`/`inf` al construir la respuesta (no debería ocurrir: lo previene U-03) sale como
`MainpipeTransientComputationError`.

## 2. Pureza y presupuesto de tiempo (`kit 01 §6`)

- Sin disco, red, variables de entorno ni estado global. Sin `print`; `logging` con el logger
  `mainpipe_transient`.
- **Coste**: (N + 1 + vértices) × `n_steps` actualizaciones, con un bucle Python sobre el tiempo y
  operaciones `numpy` vectorizadas sobre los nodos. Envolventes, primer cruce y fotogramas se
  acumulan dentro del bucle (U-19): no se guarda la historia completa (con 699 progresivas y
  10 000 pasos, H y p/γ serían ≈ 112 MB en `float64`).
- **Presupuesto**: caso del Excel ≈ 400 pasos × 21 nodos → milisegundos. Peor caso admitido:
  N = 200, 500 vértices, `MAX_STEPS` = 10 000 pasos (D-57). Estimación ≈ 0.25–0.35 s (la de
  20 000 pasos era 0.5–0.7 s; el coste es lineal en `n_steps`); **se mide en la fase 2** y de nuevo
  con fotogramas en la fase 5. Si la mediana de 5 ejecuciones del peor caso supera 0.8 s en el
  equipo del upstream, primero se optimiza el bucle; `MAX_STEPS` ya no se baja por cuenta propia,
  porque lo fijó el portal (D-57 (5)): sería un pedido nuevo.
- **Tamaño** (D-57; detalle y protocolo de medición en U-34). Números de la respuesta en el peor
  caso: series temporales 7 × 10 001 = 70 007 (no se submuestrean, HU-1.4); fotogramas
  2 × 70 × 699 = 97 860 más 70 instantes y 699 progresivas; envolventes 8 × 699 = 5 592 más 699
  booleanos. Total ≈ 174 000 números. A ≈ 18–20 B por número en JSON (`float64` sin redondear, con
  su separador) son **≈ 3,1–3,5 MB, ≈ 3,3 MB como valor central** `[calculado]`, frente al techo de
  **3,5 MB** de D-57 (1). Margen ≈ 5 %: por eso la cifra se **mide** en la fase 5 (V-18), con un
  peor caso deliberadamente desfavorable, y se anota en `portal/INTEGRATION.md`. Sin fotogramas
  (`include_frames: false`) el peor caso queda en ≈ 1,4 MB. Caso del Excel: ≈ 0,35 MB con
  fotogramas y ≈ 60 kB sin ellos.
- **Petición** (D-57 (10), D-48): el peor caso (perfil de 500 filas, ley de 20) son ≈ 1 060
  números, ≈ 21–26 KB aun con 17 cifras significativas por número, frente a 64 KiB = 65 536 B
  `[calculado]`. También se mide (V-18).
- Con esos topes **el dominio cabe en < 1 s** y no hace falta pedido de backend.

## 3. Dependencias (`kit 01 §7`, `kit 07`)

| Dependencia | Uso | Cota | ¿Pedido? |
|---|---|---|---|
| `pydantic` | modelos | `>=2.6` (admite 2.13.4) | no, está en el portal |
| `numpy` | bucle MOC vectorizado | `>=1.24` (debe funcionar con 2.x) | no, disponible (`kit 07 §1`) |
| `pytest` | tests | solo dev | no (`kit 07 §2`) |
| `pywin32` | recalcular el Excel por COM una sola vez para generar la referencia (fase 0, U-28) | solo dev y solo Windows; no se importa desde `src/` ni desde `tests/` | no (`kit 07 §2`) |
| `openpyxl` | leer las fórmulas del Excel para documentar el esquema (fase 0) | solo dev; no se importa desde `src/` ni desde `tests/` | no (`kit 07 §2`) |

Sin `scipy`. **No hay dependencias nuevas para el portal.** Frontend: ninguna; D-61 resolvió DR-5
con fórmulas en HTML semántico y Unicode, sin renderizador.

## 4. Método y fórmulas

Referencias: [WS] Wylie, E. B. & Streeter, V. L. (1993), *Fluid Transients in Systems*, Prentice
Hall, caps. 1–3. [Ch] Chaudhry, M. H. (2014), *Applied Hydraulic Transients*, 3.ª ed., Springer,
caps. 2–3. [Jk] Joukowsky, N. (1898/1904). [Mi] Michaud, J. (1878). [Al] Allievi, L. (1902/1913),
ecuaciones encadenadas, en [WS] cap. 1 y [Ch] cap. 2.

| # | Elemento | Fórmula | Ref. |
|---|---|---|---|
| M1 | Geometría | D = `inner_diameter_mm`/1000; A = πD²/4; Q₀ = `initial_flow_lps`/1000; V₀ = Q₀/A | — |
| M2 | Pérdida de régimen | h_f = f·(L/D)·V₀²/(2g) (Darcy-Weisbach) | [WS] §3, [Ch] §2 |
| M3 | Régimen inicial | Q(x) = Q₀; H(x) = H_dep − h_f·x/L. Sin pérdida de entrada ni altura de velocidad (U-04) | igual que el Excel |
| M4 | Malla | Δx = L/N, Δt = Δx/a (Courant = 1, sin interpolación); x_i = L·i/N | [WS] §3.2, [Ch] §3.4 |
| M5 | Constantes | B = a/(g·A); R = f·Δx/(2·g·D·A²) | [WS] §3.2 |
| M6 | Característica C⁺ | C_P = H_{i−1} + B·Q_{i−1} − R·Q_{i−1}·\|Q_{i−1}\|; H_P = C_P − B·Q_P | [WS] ec. 3.3.x, [Ch] §3.4 |
| M7 | Característica C⁻ | C_M = H_{i+1} − B·Q_{i+1} + R·Q_{i+1}·\|Q_{i+1}\|; H_P = C_M + B·Q_P | ídem |
| M8 | Nodo interior | H_P = (C_P + C_M)/2; Q_P = (C_P − C_M)/(2B) | ídem |
| M9 | Depósito (x = 0) | H_P = H_dep; Q_P = (H_dep − C_M)/B | [WS] §3.4 |
| M10 | Válvula (x = L) | Q_P = Q_ley(t_{k+1}) (ley evaluada en el instante que se calcula); H_P = C_P − B·Q_P | [WS] §3.4 (caudal impuesto); igual que `2_Malla_MOC` |
| M11 | Ley de cierre | interpolación lineal en la tabla; Q = 0 para t ≥ último punto; Tc = primer t_i con Q_i = 0 | HU-1.2 |
| M12 | Fricción | primer orden explícita con el caudal del punto de partida (M6–M7), **confirmada contra `2_Malla_MOC`** (U-02; en el Excel B = Cₐ, R = C_f); estabilidad φ = R·Q₀/B = f·Δx·V₀/(2Da) ≤ 0.5 (U-03) | [WS] §3.5, [Ch] §3.6 |
| M13 | Presión | p/γ = H − z(x); el término V·sen α se desprecia (efecto ≤ V₀·Δz/a) (U-05) | antecedente `CLAUDE.md` |
| M14 | Puntos que no son nodo | H interpolada linealmente entre los dos nodos vecinos en cada paso; z del vértice (U-07). Q en los vértices no se calcula: desde D-57 ninguna salida lo usa | — |
| M15 | Joukowsky | ΔH_J = a·V₀/g | [Jk], [WS] §1.2 |
| M16 | Michaud | ΔH_M = 2·L·V₀/(g·Tc), maniobra lenta (Tc > 2L/a) | [Mi], [Ch] §1 |
| M17 | Pulso completo | L_pulso = L − a·Tc/2, maniobra rápida | HU-3.4 |
| M18 | PN en m.c.a. | H_PN = PN·10⁵/(ρ·g) | HU-3.1 |
| M19 | Allievi (solo verificación, f = 0) | H_v(t) + H_v(t − 2L/a) − 2·H_dep = B·[Q(t − 2L/a) − Q(t)], con H_v = H_dep y Q = Q₀ para t ≤ 0 | [Al], [WS] cap. 1 |

Notas:

- Con fricción explícita (M6–M7) el régimen M3 es punto fijo exacto del esquema
  (N·R·Q₀² = h_f), así que antes de la maniobra H y Q no se mueven (prueba V-15).
- Con f = 0 y Courant = 1 el MOC es exacto en los nodos; M19 da la solución exacta en la válvula
  para cualquier ley Q(t) y sirve de referencia independiente del Excel (V-03).

### Estructura interna (U-01; privada, `kit 01 §2`)

```
src/mainpipe_transient/
  __init__.py       API pública (§1.1)
  schemas.py        SolveRequest, SolveResponse, Check + validadores
  exceptions.py     §1.6
  py.typed
  _solve.py         orquestación y envoltorio de errores
  _closure.py       ley de cierre (M11)
  _geometry.py      malla, perfil, unión de progresivas, pesos de interpolación (M4, M14)
  _moc.py           régimen y bucle MOC con acumuladores (M3–M10, M12)
  _theory.py        Joukowsky, Michaud, pulso (M15–M17)
  _checks.py        checks, status, mensajes (§1.5)
  _format.py        formato numérico de los mensajes (U-26)
tools/extract_excel_reference.py   (fase 0; recalcula una COPIA del Excel por COM con pywin32 y
                                    vuelca los valores; fuera del paquete, se ejecuta una vez)
tools/make_examples.py             (fase 6, llama al paquete instalado)
tests/reference/excel_case.json    (fase 0, generado una vez y versionado con su procedencia;
                                    los tests solo leen este JSON, U-28)
```

## 5. Fases

Orden: primero lo que más riesgo tiene (fidelidad al Excel, unidades, estabilidad), luego el
contrato, y al final lo que dimensionó el portal (F4, D-57), con su medición de tamaño.

| Fase | Contenido | Hecho cuando (comprobable) | HU / V |
|---|---|---|---|
| **0. Andamiaje y referencia** | `pyproject.toml` (layout `src/`, `requires-python >=3.12`, `numpy>=1.24`, `pydantic>=2.6`), `py.typed`, `CHANGELOG.md`, excepciones, `solve` vacío. **Referencia del Excel (U-28)**: el `.xlsx` no guarda valores calculados (con `openpyxl` y `data_only=True` toda celda con fórmula sale `None`), así que `tools/extract_excel_reference.py` abre por COM (pywin32, solo dev, solo Windows) una **copia temporal** del libro, la recalcula en Excel y vuelca a `tests/reference/excel_case.json` las entradas, H y Q de todos los nodos en los 401 instantes (hoja `2_Malla_MOC`) y los valores de `4_Validacion`. El JSON se versiona con su bloque de procedencia (fecha, versión de Excel, SHA-256 del `.xlsx`, commit del script); el original no se modifica. Los tests solo leen el JSON | `pip install .` en un venv limpio de Python 3.12 funciona; `import mainpipe_transient` sin efectos; el JSON tiene 401 instantes × 21 nodos de H y Q sin ningún `null`, su SHA-256 de origen coincide con el `.xlsx` archivado, y reproduce los valores de control de V-05 (p. ej. H_v máx = 242.76384 m en t = 2.00 s); la suite corre sin Excel ni pywin32 instalados | — |
| **1. Núcleo MOC horizontal** | `_closure`, `_geometry` (solo nodos), `_moc`, series, envolventes y extremos, llamados con argumentos internos (sin Pydantic todavía) | V-01 … V-09, V-14, V-15 en verde. En particular: Excel paso a paso ± 10⁻⁶ m / ± 10⁻⁶ L/s (U-29); Joukowsky ± 0.01 m; Allievi ± 10⁻⁶ m | HU-1.1 (1–4), 1.2, 1.3, 1.4, 1.5, 1.7 (1–4) |
| **2. Contrato y topes** | `schemas.py` completo, validadores en español, `solve` con envoltorio, φ (U-03), `MAX_STEPS` = 10 000 (U-09, D-57) con sus variantes de mensaje; benchmark del peor caso | Cada criterio de HU-1.6 tiene su test con el mensaje esperado; para el crit. 13, en el caso del Excel con N = 200: `duration_s` = 50 calcula con `n_steps` = 10 000, `duration_s` = 50.001 da 422 con «50 s», y la cifra que muestra el mensaje en un caso con Δt no redondo, reenviada, calcula sin error; la duración por defecto que no cabe da la variante «por defecto»; `solve` nunca deja salir una excepción ajena (test con fallo inyectado); mediana de 5 ejecuciones del peor caso < 0.8 s, anotada en `DECISIONS.md` (V-16) | HU-1.6 (1–13), 1.7 (5) |
| **3. Perfil** | unión de progresivas, interpolación de z, H y Q en vértices, presiones con la cota | V-10 en verde | HU-2.1, 2.2, 2.3 |
| **4. Verificaciones** | `_theory`, `_checks`, `status`, mensajes | V-11 … V-13 en verde; textos de HU-3.1-4 y HU-3.2-4 literales | HU-3.1 … 3.5 |
| **5. Serie para el reproductor** | fotogramas H y p/γ con el tope de U-10 (D-57), sin `frame_flow_lps` (U-33), `include_frames`; `tools/measure_payload.py` (fuera del paquete) con el protocolo de U-34 | V-17 en verde; **mediciones obligatorias, no estimaciones** (V-18, U-34): (i) JSON de la respuesta del peor caso con `include_frames: true` **≤ 3 500 000 B**, la mayor de las dos serializaciones de U-34; (ii) petición del peor caso (perfil de 500 filas, ley de cierre de 20) **≤ 65 536 B** (D-48); (iii) tamaño del caso del Excel con y sin fotogramas. Las cifras en bytes, con la entrada usada, quedan en `doc/DECISIONS.md` (U-34) para pasar a `portal/INTEGRATION.md` en la fase 6. Si (i) no cumple, se aplica la regla de U-34 antes de seguir. Tiempo total del peor caso con fotogramas < 0.8 s (V-16) | HU-4.1, 4.2 |
| **6. Entrega** | `tools/make_examples.py`, `portal/examples/`, `portal/INTEGRATION.md`, etiqueta | Checklist `kit 04 §3` completo, con suite, ejemplos **y las mediciones de V-18** ejecutados **desde el paquete instalado en un venv limpio** (kit 2.0.0); `portal/INTEGRATION.md` lleva una sección de tamaño con las dos cifras medidas en bytes (respuesta ≤ 3,5 MB, petición ≤ 64 KiB), la receta determinista de la entrada del peor caso (para que la guarda de D-57 (2) en `backend/tests/` mida lo mismo) y el aviso de que producción corta cuerpos > 4,5 MB sin que el CI ni `TestClient` lo detecten | HU-x.y «entregable» |

Ejemplos previstos para `portal/examples/` (`kit 04 §2`; los genera `hie-api` ejecutando el
paquete): `solve-excel-horizontal` (camino feliz, `status: error` con `COLUMN_SEPARATION_RISK` y
`PN_NEAR_LIMIT`, con fotogramas), `solve-perfil-loma` (perfil), `solve-sin-friccion-ok`
(`status: ok`), `solve-subatmosferica-warning`, `solve-regimen-negativo`, y errores
`MainpipeTransientValidationError`: ley no creciente, ley que no termina en 0, perfil no creciente,
duración insuficiente, más pasos que `MAX_STEPS` (HU-1.6 crit. 13). **Solo el primero lleva la
serie** (`include_frames: true`, ≈ 0,35 MB); todos los demás van con `include_frames: false`
(D-57 (8)). El peor caso de tamaño **no** es un ejemplo: pesaría ≈ 3,3 MB como caso dorado; su
entrada se publica como receta en `portal/INTEGRATION.md` (fase 6, U-34).

## 6. Estrategia de verificación hidráulica (`kit 01 §9`)

`hie-verifier` la usa tal cual. «Caso Excel» = entradas de la tabla de F1 con N = 20, T = 20 s.
«Caso sin fricción» = HU-1.1 crit. 3.

| ID | Método | Caso de referencia | Fuente | Tolerancia |
|---|---|---|---|---|
| V-01 | Darcy-Weisbach, régimen (M2–M3) | Caso Excel: V₀, h_f, H(x) | analítica [WS] §3; hoja del Excel | V₀ ± 0.001 m/s; h_f ± 0.01 m; H(500) = 96.60 ± 0.01 m; además rel. 10⁻¹² contra la fórmula |
| V-02 | MOC + contornos, sin fricción | Caso sin fricción, cierre en un paso | Joukowsky [Jk], [WS] §1.2 | H_v = 244.21 ± 0.01 m (0.05 < t < 2.0 s); −44.21 ± 0.01 m (2.05 < t < 4.0 s); Q_dep = −100 ± 0.1 L/s (1.05 < t < 3.0 s) |
| V-03 | MOC, sin fricción, ley arbitraria | Ley del Excel y ley lineal 3 s con f = 0 | Allievi M19 [Al], [WS] cap. 1 | H_v en todos los pasos ± 10⁻⁶ m |
| V-04 | Independencia de malla sin fricción | Caso sin fricción con N = 20 y N = 40 | idem V-02 | `head_valve_max_m` ± 0.01 m en ambos |
| V-05 | MOC con fricción (fidelidad) | Caso Excel | `tests/reference/excel_case.json` (hojas `2_Malla_MOC` y `4_Validacion` recalculadas en Excel, U-28) | **H ± 10⁻⁶ m y Q ± 10⁻⁶ L/s** en los 21 nodos y los 401 pasos (U-29); extremos ± 10⁻⁶ m e instante exacto: H_v máx = 242.76384 m en t = 2.00 s, H_v mín = −37.89904 m en t = 4.00 s, H_v(0) = 93.19944 m; máximo y mínimo de toda la tubería = los de la válvula. Las tolerancias de HU-1.1 crit. 1–2 (± 0.1 m, ± 0.05 m) siguen siendo el criterio de aceptación de la historia; esta es la de verificación, más estricta |
| V-06 | Celeridad / posición del frente | Caso sin fricción, t = 0.55 s | cinemática: frente a a·(t − Δt) de la válvula | H = 100 ± 0.01 m para x < 500 m; 244.21 ± 0.01 m para x > 500 m |
| V-07 | Causalidad | Caso Excel, t < L/a | — | Q_dep sin cambio ± 10⁻⁶ L/s |
| V-08 | Ley de cierre (M11) | HU-1.2 crit. 1–4 | interpolación lineal | ± 0.01 L/s; Tc exacto |
| V-09 | Invariancia de datum | Caso Excel con z = 50, H_dep = 150 | M13 | H = original + 50; presiones iguales, ± 10⁻⁶ m |
| V-10 | Perfil (M13–M14) | HU-2.1 y HU-2.2 (perfil plano de 2 puntos, loma 40 m, vértice en 520 m, L = 1250 m) | identidades | ± 10⁻⁶ m; loma: p_min(500) = p_min horizontal − 40 ± 10⁻⁶ m |
| V-11 | Joukowsky / Michaud / pulso | HU-3.4 crit. 1–2 | [Jk], [Mi]; `4_Validacion` (C11, C22, C27) | Caso Excel contra el JSON de referencia: ΔH_J = 144.2111 m, ΔH_MOC = 149.56440 m, `theory_deviation_pct` = 100·C27 = 3.712 %, todos a rel. 10⁻⁹ (U-29); `maneuver_type` = `rapid`, L_pulso = 250 m ± 10⁻⁹. Caso lento (sin hoja de referencia): ΔH_M contra la fórmula M16 a rel. 10⁻¹², y 28.84 ± 0.01 (HU-3.4 crit. 2) |
| V-12 | PN | HU-3.1 crit. 1–3 | M18 | `pn_head_m` ± 0.01; ratio ± 0.1 % |
| V-13 | Umbrales de checks | HU-3.2 crit. 3–7, HU-3.3, HU-3.5; además el predicado por progresiva de §1.5 (D-60) en el caso Excel, la loma de V-10 y un caso sin avisos | tabla §1.5 | presencia / ausencia exacta del código; `first_time_s` ± Δt; `PN_EXCEEDED` presente ⇔ ∃j `pressure_head_max_m[j]` > `pn_head_m`, y `COLUMN_SEPARATION_RISK` presente ⇔ ∃j `pressure_head_min_m[j]` < `min_allowed_pressure_head_m` (igualdad lógica exacta); `min_allowed_pressure_head_m` de la respuesta = el enviado o −10.0 |
| V-14 | Amortiguamiento con fricción | Caso Excel | propiedad física [WS] §3 | máx. \|H_v − H_dep\| de cada periodo 4L/a ≤ el del periodo anterior (después de Tc) |
| V-15 | Régimen como punto fijo | Ley (0; Q₀), (5 s; Q₀), (6 s; 0) | M3 | H y Q sin cambio para t < 5 s, ± 10⁻⁹ |
| V-16 | Presupuesto de tiempo | Caso Excel y peor caso admitido (N = 200, 500 vértices, `MAX_STEPS` = 10 000), con y sin fotogramas | `kit 01 §6` | < 1 s (objetivo interno < 0.8 s, mediana de 5) |
| V-17 | Fotogramas | HU-4.1 crit. 1–4, HU-4.2 crit. 2 (enmendadas por D-57) | coherencia interna | Caso Excel, 401 fotogramas sin submuestreo, ± 10⁻⁹ m: `frame_head_m` en x = L, L/2 y 0 frente a `head_valve_m`, `head_midpoint_m` y `reservoir_level_m`; `frame_pressure_head_m` en x = L y L/2 frente a `pressure_head_valve_m` y `pressure_head_midpoint_m` (crit. 1). Sin submuestreo, máx./mín. en el tiempo de `frame_pressure_head_m` = envolventes (crit. 2). p/γ = H − z en cada celda (crit. 3). Frente de onda a t = 0.55 s como V-06, sobre `frame_head_m` (crit. 4). Con submuestreo: n_fotogramas ≤ min(1001, ⌊50 000 / n_progresivas⌋), primer y último fotograma exactos, cada `frame_time_s` está en `time_s`, envolventes sobre todos los pasos. La clave `frame_flow_lps` **no existe** en la respuesta, con `include_frames` verdadero o falso |
| V-18 | Tamaño de petición y respuesta | Peor caso de U-34 (receta determinista y barrido) y caso Excel | D-57 (1), (10); D-48 | Medido en bytes, sin tolerancia: respuesta del peor caso con `include_frames: true` ≤ 3 500 000 B en la mayor de las dos serializaciones de U-34; petición del peor caso ≤ 65 536 B. Desde el paquete instalado en la fase 6 |

## 7. Decisiones que se solicitan al portal

Detalle en `portal/DECISION-REQUESTS.md`. Todos resueltos el 2026-11-14 (commit `2466321` del
portal); **ningún pedido bloqueante abierto**.

| DR | Pregunta | Bloquea | Estado | Efecto en este plan |
|---|---|---|---|---|
| DR-1 | ¿Se construye en el portal el panel «Transitorio» del prototipo de G3: barra de reproducción común a cuatro gráficos ECharts en pestañas, con salto al instante desde los gráficos y los avisos? | no — pantalla; el contrato F4 se entrega igual (corte R3) | resuelto — **D-58** (a) | Capa 1 sin cambios: los avisos ya llevan instante (§1.5, U-36). Texto de fase en el frontend como función pura con los tres tiempos (D-58 (4), U-32). Resto: etapa 3 |
| DR-2 | ¿Qué tamaño máximo admite el portal para la serie de fotogramas en la respuesta de `solve`? | **sí** — fija topes y forma de F4 en la Capa 1 | resuelto — **D-57** (a) con techo 3,5 MB, 100 000 celdas, `MAX_STEPS` = 10 000, sin `frame_flow_lps` | Sí: §1.3, §1.4, §2, fases 2, 5 y 6, V-16 … V-18; U-09, U-10, U-33, U-34 |
| DR-3 | ¿Cabe la pantalla con el reproductor en `solver-2col`, o se quiere un lienzo dominante fuera de catálogo? | no — integración de la pantalla | resuelto — **D-59** (a), sticky solo en ≥ lg | Ninguno (etapa 3) |
| DR-4 | ¿Se admite la asignación de colores del panel «Transitorio» con tokens existentes, sin escala de color por presión, incluidos cuatro usos que se apartan del rol documentado del token? | no — integración de la pantalla | resuelto — **D-60** (a) + corrección (b) en los cuatro usos | Rojo solo en el cruce, con el predicado de los avisos `danger`: §1.5, V-13; eco de `min_allowed_pressure_head_m` (U-35). Colores: etapa 3 |
| DR-5 | ¿Cómo se muestran las fórmulas de Joukowsky / Michaud, sin renderizador LaTeX en el portal? | no — integración de la pantalla | resuelto — **D-61** (a), HTML semántico y Unicode | §3: ninguna dependencia de frontend. Resto: etapa 3 |
| DR-6 | ¿Tiene la app análisis de IA? | no | resuelto — **D-62** (a), sin IA en v1 | Ninguno en la Capa 1; sección `ai` de `ui-spec.json` ausente o vacía (etapa 3) |

### Correspondencia con las «Preguntas para el plan» de la épica

| # | Pregunta | Resolución |
|---|---|---|
| 1 | Reproductor | DR-1 → D-58 (y DR-3 → D-59, DR-4 → D-60) |
| 2 | Tamaño de F4 | DR-2 → D-57; U-10, U-33, U-34 |
| 3 | Rangos de N, duración, presupuesto | U-09 (`MAX_STEPS` = 10 000, D-57), §2; N par 10–200 confirmado |
| 4 | Layout | DR-3 → D-59: `solver-2col` |
| 5 | Fórmulas LaTeX | DR-5 → D-61: HTML y Unicode |
| 6 | Dependencias | §3: ninguna nueva (`numpy` disponible, `kit 07 §1`) |
| 7 | IA | DR-6 → D-62: sin IA en v1 |
| 8 | Extensibilidad / `scenario` | U-15, §1.1 |
| 9 | Unidades de entrada | U-06: L/s y mm |

## 8. Hallazgos para el kit

(Se siguen las reglas tal cual; se anotan para `software-architect` del portal.)

- **`kit 01 §4`** no dice cómo van las series bidimensionales (fotogramas × progresivas). El plan
  usa listas de filas por fotograma alineadas con un eje `x_m` (U-11). Convendría una regla.
- **`kit 08 §2`** no tiene categoría para «tamaño / transporte de la respuesta»; DR-2 usa
  `funcionalidad`.
- **`kit 02 §1`** dice «el mismo prefijo en las cuatro clases» y a la vez que `ServiceError` es
  «solo si» hay servicio externo; el plan define tres clases. Una aclaración evitaría dudas.
- **Tamaño de respuesta**: el kit no lo regula y producción corta cuerpos > 4,5 MB (D-47) sin que
  el CI lo vea; D-57 lo resolvió para esta app. Una regla general en `kit 01 §6` (techo, cómo se
  mide, con qué serializador) evitaría repetir el pedido. D-57 expresa el techo en «MB» sin decir
  si son 10⁶ o 2²⁰ B; el plan toma 10⁶ B, lo más estricto (U-34).
- **`06-ui-spec.schema.json` no tiene dónde declarar fórmulas ni cómo se presentan** (etapa 3).
  D-61 fijó ΔH = a·V₀/g y ΔH = 2·L·V₀/(g·T_c) en HTML con `<var>` / `<sub>` y desglose de variables
  con unidades, pero el esquema no tiene un campo para la fórmula ni para su desglose: quedaron solo
  como `symbol` Unicode en los `kpis` de `portal/ui-spec.json` y, completas, en
  `portal/prototype.html`, que es desechable (`kit 04 §1`). El frontend tendrá que leerlas del
  prototipo o de D-61. Convendría un campo `formula` (expresión y variables con unidad) en los kpis
  o un bloque propio.
- **`06-ui-spec.schema.json` no tiene dónde declarar acciones dentro de un aviso de `checks`**
  (etapa 3). El botón «Ir a t = … s en el transitorio» que D-58 mandó añadir (qué instante usa cada
  código, a qué fotograma salta, qué pestaña abre, cuándo no se muestra) quedó descrito en texto
  libre en `charts[].interactions` del gráfico `perfil-envolventes`, lejos de la sección de
  `checks` donde vive el botón. Convendría un campo `actions` por código en la sección de `checks`
  del esquema.

---

## Changelog

| Fecha | Cambio |
|---|---|
| 2026-11-14 | Borrador inicial para G2 (`hie-architect`, kit 3.0.0). |
| 2026-11-14 | Lectura del Excel (fórmulas con openpyxl; copia recalculada en Excel por COM, original intacto). U-02 y U-17 pasan a vigentes (M10, M12, `theory_deviation_pct`). Fase 0 reescrita: el `.xlsx` no tiene valores en caché, la referencia se genera una vez por COM y se versiona con su procedencia (U-28, `pywin32` solo dev). V-05 y V-11 endurecidas a 10⁻⁶ m / rel. 10⁻⁹ (U-29). Retirado de las confirmaciones de G2 el punto 6 de entonces, que dependía de la lectura del Excel; la lista se renumeró y el punto 6 actual (tamaño de la respuesta) es otro, vigente (aclaración del 2026-11-14, ver la última entrada). Sin cambio de contrato. |
| 2026-11-14 | Coherencia tras G3 (prototipo aprobado). Cabecera: decisiones internas hasta U-32 (U-30 reformulación de DR-1 y DR-4; U-31 `frame_flow_lps` provisional; U-32 texto de fase calculado en el frontend). §7: preguntas de DR-1 y DR-4 alineadas con su redacción nueva en `portal/DECISION-REQUESTS.md`; DR-3 y DR-4 ya no dependen de DR-1 ni de la etapa 3 (aprobada) y pasan a «integración de la pantalla»; DR-2 cita sus dos palancas (`MAX_STEPS`, `frame_flow_lps`); fila 4 de la correspondencia con la épica anota el layout de G3. Estado del plan y Capa 1 sin cambios; DR-1 … DR-6 siguen `abierto`. |
| 2026-11-14 | Más coherencia tras G3. Estado: de «borrador (para la puerta G2)» a **aprobado** (G2 del 2026-11-14), pendiente de congelarse en G4; misma corrección en la cabecera de `portal/DECISION-REQUESTS.md`. §7: DR-5 pasa de «etapa 3» a «integración de la pantalla», como DR-3 y DR-4 (también en `DECISION-REQUESTS.md`). Parte 1, punto 6 de las confirmaciones de G2: se mantiene, porque es el punto que el dueño aprobó en G2 (el retirado era el 6 de antes de renumerar, que dependía de la lectura del Excel), y ahora cita también la palanca `frame_flow_lps` (U-31); se aclara la redacción de la entrada del changelog que lo retiraba. Capa 1 sin cambios. |
| 2026-11-14 | **G2 reabierta: incorporación de D-57 (DR-2).** Estado a **borrador**, pendiente de reaprobación. Capa 1: `frame_flow_lps` retirado de `SolveResponse` sin opción para pedirlo (U-33, sustituye a U-31); tope de fotogramas min(1001, ⌊50 000 / n_progresivas⌋) con dos matrices (U-10 vigente); `MAX_STEPS` = 10 000 (U-09 vigente) con 422 de HU-1.6 crit. 13, T_max truncada y variantes de mensaje (duración por defecto, duración mínima mayor que T_max). §2 recalculado: tiempo del peor caso ≈ 0.25–0.35 s (antes 0.5–0.7 s); respuesta del peor caso ≈ 3,3 MB `[calculado]` (antes ≈ 5 MB) frente al techo de 3,5 MB; petición ≈ 21–26 KB frente a 64 KiB; caso del Excel ≈ 0,35 MB (antes ≈ 0,5 MB). Fase 5 con las mediciones obligatorias de D-57 (1) y (10) y protocolo U-34; fase 6 vuelca las cifras y la receta del peor caso a `portal/INTEGRATION.md`; V-17 enmendada (HU-4.1 crit. 1 sin caudal; sin clave `frame_flow_lps`), V-18 nueva. Ejemplos: solo el del Excel con serie (D-57 (8)), nuevo ejemplo de error por `MAX_STEPS`. M14 y U-07: Q ya no se interpola en los vértices. |
| 2026-11-14 | **Incorporación de D-58 … D-62.** Capa 1: eco `min_allowed_pressure_head_m` en `SolveResponse` (U-35) y predicado por progresiva del cruce en rojo, igual al de los avisos `danger` (D-60, U-36, V-13); los avisos ya llevan instante para «Ir a t = … s» (D-58), sin campos nuevos. §3: D-61 sin dependencia. §7: DR-1 … DR-6 resueltos, con su efecto en el plan. §8: hallazgo sobre el tamaño de respuesta. Parte 1 reescrita en «Lo que el portal decidió» y «Puntos que el dueño debe confirmar al reaprobar G2» (3 y 6 cambiados por D-57; 7 y 8 nuevos). `SCHEMA_VERSION` sigue en `"1.0"`: el contrato no está congelado. Lo de pantalla (D-58 … D-62 en `ui-spec.json` / `prototype.html`) queda para la etapa 3. |
| 2026-11-14 | **Congelado (G4), `hie-architect`, kit 3.0.0.** Comprobado antes de congelar: DR-1 … DR-6 `resuelto` con su D-NN (D-57 … D-62) y ningún `DR` bloqueante `abierto` (`kit 08 §1`); G1, G2 y G3 reaprobadas el 2026-11-14 con D-57 … D-62; los 73 `contract_path` de `portal/ui-spec.json` están en §1, y el límite se lee de `response.min_allowed_pressure_head_m` (U-35). Estado a **congelado**; **`SCHEMA_VERSION = "1.0"` confirmado como versión congelada** (§1.1), con la regla de enmienda posterior (U-37, `kit 01 §8`). Puestos al día los textos que G2 ya había resuelto, sin cambiar el contrato: Parte 1, riesgos 2 y 3 y la sección de confirmaciones, que pasa a «Puntos que el dueño confirmó en G2» (U-03, U-09 sin recorte de la duración por defecto, U-14, U-21, U-22, regla de ajuste de U-34, U-33, U-35); §1.3, la nota de φ ya no dice «punto abierto». §8: dos hallazgos de la etapa 3 sobre `06-ui-spec.schema.json` (fórmulas de D-61; acciones dentro de un aviso, «Ir a t» de D-58). Capa 1 sin cambios respecto a la reaprobación de G2. |
