# Épica — Golpe de ariete por cierre de válvula en una aducción por gravedad

> Kit con el que se redacta: **3.0.0**. Estado: borrador para la puerta **G1** (`/hie-flow approve 1`),
> con las decisiones de alcance del usuario del 2026-11-14 ya aplicadas.
> Material previo: `doc/archive/2026-11-pre-hie/Transitorio_MOC_Animado.xlsx`. Es materia prima,
> no alcance acordado.
>
> Enmienda 2026-11-14 (D-57, resuelve DR-2): F4 deja de incluir el caudal por fotograma Q(x, t)
> (`frame_flow_lps`), que pasa a «Fuera de v1»; preguntas 2 y 3 anotadas con lo que fijó el
> portal. Etapa 1 reabierta para esta enmienda.
>
> Enmienda 2026-11-14 (D-58, resuelve DR-1; decisión del usuario en G1): el reproductor se describe
> como el panel «Transitorio» aprobado en G3 (barra de reproducción común y cuatro pestañas de
> gráficos con un instante compartido); se retiran la tubería coloreada por presión y el mapa de
> calor, descartados. Afecta al corte R3, a «Fuera de v1» (portal) y a la pregunta 1.
>
> Enmienda 2026-11-15 (decisiones del dueño tras G4; etapa 1 reabierta). Las tres primeras salen
> del desglose del tamaño de la respuesta (peor caso de 3,16 MB: fotogramas 57 %, series 40 %,
> perfiles 3 %; unos 18 B por número):
> (1) las listas de salida en m y L/s se redondean a 3 decimales al serializar; `time_s`,
> `frame_time_s` y los escalares no (F1, «Precisión de las listas de salida»; F4);
> (2) se retira `frame_pressure_head_m`: el portal obtiene p/γ(x, t) como `frame_head_m` −
> `elevation_m` (F4, HU-4.1);
> (3) el texto de la fase de la onda del reproductor sale de v1 (F4); los escalares
> `reflection_time_s`, `wave_period_s` y `closure_duration_s` se mantienen;
> (4) la densidad y la gravedad dejan de ser entradas: ρ = 1000 kg/m³ y g = 9.81 m/s² quedan como
> constantes fijas (F1, «Constantes fijas»; F3).
> Estimado del dueño: peor caso de 3,16 MB a ≈ 0,96 MB; caso del Excel con fotogramas de 356 KB a
> ≈ 89 KB. Afecta a la tabla de funcionalidades (F4), a «Fuera de v1» y a las preguntas 1, 2 y 10.

## Problema de ingeniería

En una aducción por gravedad (depósito → tubería → válvula), la maniobra de cierre de la válvula
genera un transitorio de presión (golpe de ariete) que puede superar el timbraje de la tubería o
llevar puntos del trazado por debajo de la presión de vapor. El proyectista necesita conocer, para
una ley de cierre dada, la sobrepresión y la depresión máximas a lo largo de toda la tubería
—**en presión** (p/γ = H − z), no solo en altura piezométrica— para decidir si la clase de
tubería (PN) es suficiente, si la maniobra es demasiado rápida y si hay riesgo de cavitación o
separación de columna en los puntos altos del perfil. La API resuelve el transitorio con el
**Método de las Características (MOC) en H y Q**, fricción de Darcy-Weisbach constante, y lo
contrasta con las fórmulas de **Joukowsky** (maniobra rápida) y **Michaud** (maniobra lenta).

## Quién la usa

- **Proyectista de aducciones y conducciones** que dimensiona la clase de tubería y la ley de
  cierre de la válvula.
- **Ingeniero revisor** que comprueba un diseño ajeno frente al timbraje y a la presión mínima
  admisible.

## Escenario

v1 tiene **un único escenario**, `reservoir_pipe_valve`: depósito de nivel constante + tubería de
diámetro único + válvula aguas abajo con caudal impuesto por una ley de cierre total Q(t). La
geometría de la tubería se describe de una de dos formas: **horizontal** (una cota única) o
**perfil** (tabla de puntos x, z). No son escenarios distintos: es el mismo cálculo con otra
cota en cada punto.

El contrato lleva un campo `scenario` con un solo valor en v1 para poder añadir escenarios más
adelante (p. ej. parada de bombas), que **no** entran en este alcance.

## Funcionalidades

| # | Funcionalidad | Versión | Archivo |
|---|---|---|---|
| F1 | Transitorio por cierre de válvula en tubería horizontal: entradas del Excel (ρ y g como constantes fijas desde el 2026-11-15), ley de cierre, malla y duración, régimen inicial, series en válvula / punto medio / depósito y envolventes | **v1** | `01-transitorio-cierre-valvula.md` |
| F2 | Perfil real de la tubería (x, z) ingresado como tabla de puntos; presión p/γ = H − z(x) y envolventes de presión sobre el perfil | **v1** | `02-perfil-tuberia.md` |
| F3 | Verificaciones del resultado (`checks`): timbraje PN, presión mínima admisible / riesgo de separación de columna, presión negativa en régimen; referencia teórica Joukowsky / Michaud como dato informativo | **v1** | `03-verificaciones.md` |
| F4 | Serie temporal completa H(x, t) para que el portal pueda reproducir el transitorio (PLAY); el portal obtiene p/γ(x, t) = H − z. Sin Q(x, t) desde D-57 (2026-11-14) ni p/γ(x, t) en la respuesta desde el 2026-11-15; listas a 3 decimales | **v1** | `04-serie-reproduccion.md` |
| F5 | Otros escenarios (p. ej. parada de bombas, dispositivos de protección) | posterior, sin fecha | — |

**Corte (R3).** F1–F4 forman la v1. F1–F3 son el núcleo de ingeniería; F4 solo añade a la
respuesta datos que el cálculo ya produce. El reproductor que los usa es del portal (panel
«Transitorio», D-58): si su integración se retrasa, la API se entrega igual.

## Fuera de v1

- **Parada de bombas** y cualquier escenario con bombeo, y en general cualquier escenario distinto
  de depósito + tubería + válvula: chimeneas de equilibrio, calderines, válvulas de aire /
  ventosas, depósito de nivel variable, varias válvulas.
- **Separación de columna y cavitación modeladas** (DVCM / DGCM): v1 solo **avisa**, con un
  mensaje claro, cuando la presión baja del mínimo admisible, dónde y cuándo, y que desde ese
  instante los resultados del MOC simple dejan de ser físicos.
- **Cierres parciales y maniobras de apertura**: la ley de cierre termina siempre en Q = 0.
- Tubería compuesta (varios tramos con distinto diámetro, material o celeridad).
- Fricción variable con Reynolds o fricción no estacionaria: f de Darcy constante.
- Término de pendiente V·sen α en las características (efecto ≈ V₀·Δz/a; ≈ 0.1 m en el caso del
  Excel).
- Ley de la válvula por apertura relativa τ(t) con ecuación de orificio: v1 impone el caudal
  Q(t) en la válvula, como el Excel.
- Ajuste de la presión mínima admisible por altitud o temperatura: en v1 es un valor que ingresa
  el usuario (por defecto −10 m.c.a.).
- **Densidad y gravedad como datos del usuario** (`density_kgm3`, `gravity_ms2`): retiradas de la
  entrada el 2026-11-15; en v1 son constantes fijas, ρ = 1000 kg/m³ y g = 9.81 m/s².
- Carga del perfil desde un archivo: no pedida; queda solo como idea, sin pedido al portal.
- **Caudal en cada fotograma y progresiva**, Q(x, t) (`frame_flow_lps`): retirado de v1 por D-57
  (2026-11-14), ni por defecto ni detrás de una opción, porque la pantalla aprobada no lo usa y el
  portal no la enviaría. El caudal en el tiempo sigue en la válvula y en el depósito (HU-1.4).
- **Presión en cada fotograma y progresiva** como campo de la respuesta (`frame_pressure_head_m`):
  retirada el 2026-11-15. No se pierde información: el portal la obtiene como `frame_head_m` −
  `elevation_m`. Las series de presión en la válvula y en L/2 y las envolventes de presión siguen
  en la respuesta.
- **Precisión completa en las listas de salida**: desde el 2026-11-15 las listas en m y L/s salen
  redondeadas a 3 decimales (`time_s`, `frame_time_s` y los escalares, no).
- **Texto de la fase de la onda en el reproductor** («Cierre en curso…», «La onda de sobrepresión
  viaja…», «Reflexión en el depósito…», «Reflexión en la válvula cerrada…», «La depresión se
  refleja… (ciclo N)»): retirado de v1 el 2026-11-15.
- **Del portal, no de esta API**: el reproductor del transitorio —panel «Transitorio» con barra de
  reproducción común y cuatro pestañas de gráficos con un instante compartido y salto al instante
  desde los avisos (D-58), sin texto de fase desde el 2026-11-15—, el gráfico del perfil, la
  exportación de resultados y el análisis de IA (sin IA en v1, D-62). Los escribe el
  `product-owner` del portal cuando la API se entregue, previa decisión del portal donde
  corresponda.

## Decisiones de alcance de G1 (resueltas el 2026-11-14)

| # | Pregunta | Respuesta del usuario (2026-11-14) | Dónde se aplica |
|---|---|---|---|
| P1 | ¿Cuántos escenarios en v1? | Un único escenario, depósito + tubería + válvula. Otros (p. ej. parada de bombas) quedan para más adelante, fuera de este alcance. Se mantiene el campo `scenario` para crecer. | «Escenario», F1 |
| P2 | ¿Qué es «dibujar el perfil»? | Tabla de puntos (x, z); el portal la muestra en un gráfico del perfil. **No** se propone dibujo con ratón, ni ahora ni después. | F2 |
| P3 | ¿Qué es la x del perfil? | Progresiva a lo largo del eje de la tubería; L = x final del perfil. | F2 |
| P4 | ¿Entra en v1 la serie completa para el PLAY? | Sí. El reproductor sigue siendo del portal (candidato a pedido de decisión). | F4 |
| P5 | ¿Malla y duración fijas? | N configurable (20 por defecto) y duración de la simulación como dato de entrada. | F1 (HU-1.7), F3 |
| P6 | ¿Joukowsky / Michaud como aviso? | No: solo dato informativo (ΔH teórico, ΔH MOC, diferencia en %). PN y presión mínima siguen como `checks`. | F3 (HU-3.4) |
| P7 | ¿Presión mínima por altitud? | La ingresa el usuario (−10 m.c.a. por defecto); sin ajuste por altitud en v1. | F1, F3 |
| P8 | ¿Separación de columna? | Se avisa, no se modela. El aviso debe decir que la presión cae bajo el límite, dónde (x), cuándo (t), y que desde ahí los resultados del MOC simple dejan de ser físicos. | F3 (HU-3.2) |
| P9 | ¿Qué maniobras? | Solo cierres totales: la ley termina en Q = 0, si no, error 422. Cierres parciales y aperturas, fuera. | F1 (HU-1.2, HU-1.6), F3 |

Nota: el propio caso del Excel cae a −37.9 m.c.a., por debajo de −10; su resultado sale con
`status` = `error` y el aviso de separación de columna (HU-3.2).

## Preguntas para el plan (para `hie-architect`)

No se resuelven aquí; se nombran para que se conviertan en pedidos de decisión (`kit 08`) o en
decisiones internas.

1. **Reproductor del transitorio** (barra de reproducción común —reproducir / pausa, paso a paso,
   cursor de tiempo, velocidad, bucle—, gráficos con un instante compartido, texto de fase): es
   funcionalidad de portal nueva y no está en el catálogo de gráficos ni de layouts (`kit 05 §2–3`,
   regla central del `README`). **Candidato a DR.** Comprobar qué parte cabe en ECharts y qué
   parte es nueva.
   *Resuelta por el portal (D-58, 2026-11-14): panel «Transitorio» de G3, barra común y cuatro
   pestañas ECharts con instante compartido.*
   *Anotada 2026-11-15: el texto de fase sale de v1 (decisión del dueño), lo que toca D-58 (4) y
   U-32 (DR-1 punto 2); ver pregunta 10.*
2. **Tamaño de la respuesta** de F4: (nodos + vértices) × fotogramas × 3 variables. Con la malla
   del Excel son ≈ 25 000 números; con N y duración configurables crece. Fijar un tope de
   fotogramas o un submuestreo, y si hace falta, un pedido al portal.
   *Resuelta por el portal (D-57, 2026-11-14): son 2 variables (H y p/γ; Q sale de F4), con un
   presupuesto de celdas entre las dos matrices y sin redondeo; la cifra del tope la fija el plan
   (U-10).*
   *Anotada 2026-11-15: queda 1 variable (H; p/γ la deriva el portal) y las listas se redondean a
   3 decimales, contra D-57 (4) y D-57 (9); ver pregunta 10.*
3. **Rangos de N y de la duración** y **presupuesto de tiempo** (`kit 01 §6`, < 1 s): trivial con
   N = 20 × 400 pasos; el número de pasos crece con N y con la duración (N·a·T/L). Fijar los topes
   que garanticen el presupuesto (HU-1.7 propone 10 ≤ N ≤ 200).
   *Anotada 2026-11-14 (D-57): el portal bajó el tope de pasos respecto del propuesto; con malla
   fina la duración máxima admitida se acorta y superarla es error 422 que da la duración máxima
   (HU-1.6 crit. 13). Las cifras las fija el plan (U-09).*
4. **Layout**: verificar que entradas + tabla de perfil + ley de cierre + gráficos + reproductor
   caben en `solver-2col` o `solver-3col`; si el reproductor exige un lienzo dominante, es DR
   (`kit 05 §2`).
5. **Fórmulas** (Joukowsky, Michaud) mostradas en LaTeX implican dependencia de frontend
   (`kit 05 §6`) → DR si el prototipo las muestra renderizadas.
6. **Dependencias**: no se prevé ninguna nueva (cálculo numérico simple); confirmar contra
   `kit 07` si se usa `numpy`.
7. **IA**: no pedida por el usuario; propuesta: sin análisis de IA en v1 (si se quisiera, es
   pedido, `kit 03 §3`).
8. **Extensibilidad del contrato**: campo `scenario` con un único valor en v1 y cómo se versiona
   al añadir escenarios (`SCHEMA_VERSION`, `kit 01 §3`).
9. **Unidades de entrada**: las historias proponen L/s y mm (el Excel usa m³/s y m); el usuario no
   las objetó. Las fija el plan.
10. **Enmienda del 2026-11-15 frente a lo que ya decidió el portal** *(añadida 2026-11-15)*. Lo
    que el upstream no puede cerrar solo:
    a. **Redondeo a 3 decimales** de las listas en m y L/s (`frame_head_m` y `frame_x_m`
       incluidas): choca con D-57 (9), «sin redondeo». Candidato a DR.
    b. **Retirar `frame_pressure_head_m`**: choca con D-57 (4) y cambia la forma de la respuesta
       (`SCHEMA_VERSION`, `kit 01 §3`; el `HANDOFF.md` anota 2.0). El panel «Transitorio» pasa a
       derivar p/γ en el navegador; el prototipo de G3 ya lo hace. Candidato a DR.
    c. **Retirar el texto de fase**: D-58 (4) y U-32 lo daban como función del frontend; el
       portal debe saber que sale de v1. Candidato a DR o nota en el mismo DR.
    d. **Presupuesto de celdas con una sola matriz `frame_*`**: el tope U-10 (min(1001,
       ⌊50 000/n⌋), 100 000 celdas entre dos matrices) se escribió para dos matrices. El dueño no
       pide cambiar el tope y su estimado (≈ 0,96 MB) lo supone igual; si se reinterpreta, lo
       decide el plan con el portal.
    e. **Densidad y gravedad fijas**: quitar `density_kgm3` y `gravity_ms2` de la entrada es otro
       cambio de forma del contrato (`SCHEMA_VERSION`). Queda por fijar qué pasa si una petición
       aún los trae (rechazo 422 o se ignoran), según la política de campos extra del contrato
       (`kit 01`), y si ρ y g se devuelven como eco en la respuesta. El panel de entradas aprobado
       en G3 debe dejar de mostrarlos.
    f. **Medición de tamaños** (U-34): rehacerla con la respuesta nueva; las cifras medidas en la
       fase 5 (3 167 900 B; F5-01 hasta 4 129 794 B) dejan de ser las del contrato.
