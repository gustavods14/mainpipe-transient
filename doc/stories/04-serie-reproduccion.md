# F4 — Serie temporal completa para reproducir el transitorio (v1)

> Épica: `00-epica.md`. Kit 3.0.0. **Entra en v1** por decisión del usuario en G1 (P4,
> 2026-11-14).
>
> Enmienda 2026-11-14 (D-57, resuelve DR-2): `frame_flow_lps` (Q por fotograma) se retira de v1;
> HU-4.1 queda sin caudal en el enunciado y su crit. 1 se verifica con H y p/γ; el tope de
> fotogramas respeta el presupuesto de celdas de D-57 (cifra en el plan, U-10). Etapa 1 reabierta
> para esta enmienda.
>
> Enmienda 2026-11-14 (D-58, resuelve DR-1; decisión del usuario en G1): la descripción del
> reproductor se alinea con el panel «Transitorio» aprobado en G3; se retiran la tubería coloreada
> por presión y el mapa de calor H(x, t), descartados.
>
> **Qué es de la API y qué no.** El usuario quiere poder dar PLAY en la pantalla y ver el
> transitorio avanzar. Esta funcionalidad cubre **solo la parte del paquete**: devolver, en la
> misma respuesta de `solve`, el estado de toda la tubería en cada instante. El **reproductor** es
> del portal: el panel «Transitorio» aprobado en G3 y admitido por el portal en D-58, con una barra
> de reproducción común (reproducir / pausa, paso a paso, cursor de tiempo, velocidad y bucle),
> cuatro pestañas de gráficos que comparten el mismo instante (altura H(x), presión p/γ(x), válvula
> y L/2, caudales), el texto de la fase de la onda y el salto al instante desde los avisos. Su
> historia la escribe el `product-owner` del portal.

## Salidas (además de F1–F3)

| Campo | Unidad | Contenido |
|---|---|---|
| `frame_time_s` | s | instantes de los fotogramas |
| `frame_x_m` | m | progresivas de los nodos de cálculo (y vértices del perfil con geometría `profile`, como en F2) |
| `frame_head_m` | m | H en cada fotograma y progresiva |
| ~~`frame_flow_lps`~~ | ~~L/s~~ | **Retirado de v1** (D-57, 2026-11-14): Q por fotograma no viaja en la respuesta. El caudal en el tiempo sigue disponible en la válvula y en el depósito por las series de F1 (`flow_valve_lps`, `flow_reservoir_lps`, HU-1.4) |
| `frame_pressure_head_m` | m.c.a. | p/γ = H − z en cada fotograma y progresiva |

La forma exacta de las matrices (por fotograma o por progresiva) y el tope de fotogramas los fija
`hie-architect` en el plan (preguntas 2 y 3 de la épica). El tope respeta el presupuesto de celdas
que fijó el portal para las dos matrices `frame_*` (D-57); la cifra la da el plan (U-10). Los
valores de los fotogramas no se redondean (D-57). Los tiempos característicos para el texto de
fase (L/a, 2L/a, 4L/a) ya vienen en F1 (`reflection_time_s`, `wave_period_s`).

---

## HU-4.1 — Recibir el estado de toda la tubería en cada instante

**Como** proyectista, **quiero** la altura piezométrica y la presión de todos los puntos de la
tubería en cada instante **para** que la pantalla pueda reproducir el transitorio y yo vea cómo
viaja y se refleja la onda.

**Criterios de aceptación**

1. Dado el caso del Excel (`n_reaches` = 20, `duration_s` = 20; 21 nodos × 401 instantes, sin
   submuestreo), cuando se calcula, entonces, en cada instante y con ± 1·10⁻⁹ m:
   `frame_head_m` en x = L coincide con `head_valve_m`, en x = L/2 con `head_midpoint_m` y en
   x = 0 con `reservoir_level_m` (depósito de nivel constante); y `frame_pressure_head_m` en x = L
   coincide con `pressure_head_valve_m` y en x = L/2 con `pressure_head_midpoint_m`.
   *(Enmendado 2026-11-14, D-57: sustituye la comparación de `frame_flow_lps` en x = 0 con
   `flow_reservoir_lps`.)*
2. Dado cualquier cálculo válido sin submuestreo, entonces el máximo y el mínimo en el tiempo de
   `frame_pressure_head_m` en cada progresiva coinciden con `pressure_head_max_m` y
   `pressure_head_min_m`.
3. Dado cualquier cálculo válido, entonces `frame_pressure_head_m` = `frame_head_m` − cota del
   punto en cada fotograma y progresiva.
4. Dado el caso sin fricción con cierre en un paso de HU-1.1, entonces en t = 0.55 s
   `frame_head_m` vale 100 ± 0.01 m para x < 500 m y 244.21 ± 0.01 m para x > 500 m (el frente
   de onda ha recorrido a·(t − 0.05) = 500 m desde la válvula).
5. Entregable `portal/` completo según el kit v3.0.0.

## HU-4.2 — Mantener la respuesta en un tamaño razonable

**Como** proyectista, **quiero** que la respuesta con la serie completa llegue en el mismo tiempo
que un cálculo normal **para** que la reproducción no vuelva lenta la herramienta, aunque aumente
la malla o la duración.

**Criterios de aceptación**

1. Dado el caso del Excel, entonces el cálculo completo, incluida la serie, se mantiene en < 1 s
   (`kit 01 §6`).
2. Dado el caso más grande admitido por los rangos de `n_reaches` y `duration_s` que fije el plan
   (HU-1.7), entonces el número de fotogramas no supera el tope fijado en el plan, el primero es
   t = 0, el último es `duration_s`, y las envolventes y extremos de F1 se calculan sobre **todos**
   los pasos, no sobre la serie submuestreada.
3. Entregable `portal/` completo según el kit v3.0.0.
