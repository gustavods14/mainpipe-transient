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
> Enmienda 2026-11-15 (decisiones del dueño tras G4, a partir del desglose del tamaño de la
> respuesta: fotogramas 57 % y series 40 % del peor caso de 3,16 MB, unos 18 B por número). Etapa 1
> reabierta para esta enmienda. Tres cambios, sin tocar el resto del alcance:
> (1) `frame_head_m` y `frame_x_m` se redondean a 3 decimales al serializar; `frame_time_s` no
> (sustituye la frase «los valores de los fotogramas no se redondean», D-57 (9));
> (2) se retira `frame_pressure_head_m`: la presión de cada fotograma es `frame_head_m` −
> `elevation_m` y la obtiene el portal (choca con D-57 (4)); HU-4.1 crits. 1–3 se reformulan;
> (3) el texto de la fase de la onda del reproductor sale de v1 (U-32, D-58 (4)). Se añaden los
> crits. 3 y 4 de HU-4.2 (precisión de la serialización e instantes sin redondear). Estimado del
> dueño: peor caso de 3,16 MB a ≈ 0,96 MB; caso del Excel con fotogramas de 356 KB a ≈ 89 KB.
>
> **Qué es de la API y qué no.** El usuario quiere poder dar PLAY en la pantalla y ver el
> transitorio avanzar. Esta funcionalidad cubre **solo la parte del paquete**: devolver, en la
> misma respuesta de `solve`, la altura piezométrica de toda la tubería en cada instante. El
> **reproductor** es del portal: el panel «Transitorio» aprobado en G3 y admitido por el portal en
> D-58, con una barra de reproducción común (reproducir / pausa, paso a paso, cursor de tiempo,
> velocidad y bucle), cuatro pestañas de gráficos que comparten el mismo instante (altura H(x),
> presión p/γ(x), válvula y L/2, caudales) y el salto al instante desde los avisos. La presión
> p/γ(x) de cada fotograma la obtiene el portal como `frame_head_m` − `elevation_m`, como ya hace el
> prototipo de G3. El texto de la fase de la onda («Cierre en curso…», «La onda de sobrepresión
> viaja…», «Reflexión en el depósito…», «Reflexión en la válvula cerrada…», «La depresión se
> refleja… (ciclo N)») **ya no forma parte de v1** (enmienda 2026-11-15). La historia del
> reproductor la escribe el `product-owner` del portal.

## Salidas (además de F1–F3)

| Campo | Unidad | Contenido |
|---|---|---|
| `frame_time_s` | s | instantes de los fotogramas; **sin redondear** (como `time_s`: `dt_s` puede no ser múltiplo de 1 ms, o ser menor) |
| `frame_x_m` | m | progresivas de los nodos de cálculo (y vértices del perfil con geometría `profile`, como en F2); las mismas que `x_m`, alineadas con `elevation_m`; redondeadas a 3 decimales |
| `frame_head_m` | m | H en cada fotograma y progresiva; redondeada a 3 decimales |
| ~~`frame_flow_lps`~~ | ~~L/s~~ | **Retirado de v1** (D-57, 2026-11-14): Q por fotograma no viaja en la respuesta. El caudal en el tiempo sigue disponible en la válvula y en el depósito por las series de F1 (`flow_valve_lps`, `flow_reservoir_lps`, HU-1.4) |
| ~~`frame_pressure_head_m`~~ | ~~m.c.a.~~ | **Retirado de v1** (enmienda 2026-11-15): p/γ = H − z por fotograma no viaja en la respuesta; el portal la obtiene como `frame_head_m` − `elevation_m` de la misma progresiva, que es exactamente como la calcula el paquete. Las series `pressure_head_valve_m` / `pressure_head_midpoint_m` y las envolventes de presión de F1–F2 **se mantienen** |

La forma exacta de la matriz (por fotograma o por progresiva) y el tope de fotogramas los fija
`hie-architect` en el plan (preguntas 2 y 3 de la épica). El tope respeta el presupuesto de celdas
que fijó el portal (D-57); la cifra la da el plan (U-10). Esta enmienda no pide cambiar el tope; si
al quedar una sola matriz `frame_*` hay que reinterpretar el presupuesto, lo decide el plan
(pregunta 10 de la épica).

**Precisión (enmienda 2026-11-15).** `frame_head_m` y `frame_x_m` se redondean a 3 decimales
(1 mm) solo al serializar, con la misma regla que las demás listas en m y L/s de F1–F2
(`01-transitorio-cierre-valvula.md`, «Precisión de las listas de salida»); `frame_time_s` sale sin
redondear. El cálculo, los extremos y los `checks` usan precisión completa. Antes (D-57 (9)) los
valores de los fotogramas no se redondeaban.

Los tiempos característicos `reflection_time_s`, `wave_period_s` y `closure_duration_s` siguen en
la respuesta (F1); en v1 ya no alimentan un texto de fase del reproductor.

---

## HU-4.1 — Recibir el estado de toda la tubería en cada instante

**Como** proyectista, **quiero** la altura piezométrica de todos los puntos de la tubería en cada
instante, con la que la pantalla obtiene también su presión (H − z), **para** que la pantalla
pueda reproducir el transitorio y yo vea cómo viaja y se refleja la onda.
*(Enmendado 2026-11-15: antes pedía «la altura piezométrica y la presión».)*

**Criterios de aceptación**

1. Dado el caso del Excel (`n_reaches` = 20, `duration_s` = 20; 21 nodos × 401 instantes, sin
   submuestreo), cuando se calcula, entonces, en cada instante y con ± 1·10⁻⁹ m:
   `frame_head_m` en x = L coincide con `head_valve_m`, en x = L/2 con `head_midpoint_m` (las dos
   listas se redondean desde el mismo valor) y en x = 0 con `reservoir_level_m` redondeado a
   3 decimales (depósito de nivel constante); y la presión derivada `frame_head_m` − `elevation_m`
   en x = L coincide con `pressure_head_valve_m` y en x = L/2 con `pressure_head_midpoint_m` con
   |diferencia| ≤ 0.001 m + 1·10⁻⁹ m (redondeo de tres listas distintas).
   *(Enmendado 2026-11-14, D-57: sustituye la comparación de `frame_flow_lps` en x = 0 con
   `flow_reservoir_lps`. Enmendado 2026-11-15: la presión se compara a partir de `frame_head_m` −
   `elevation_m` en lugar de `frame_pressure_head_m`, y x = 0 con el nivel redondeado.)*
2. Dado cualquier cálculo válido sin submuestreo, entonces en cada progresiva el máximo y el
   mínimo en el tiempo de `frame_head_m` − `elevation_m` coinciden con `pressure_head_max_m` y
   `pressure_head_min_m` con |diferencia| ≤ 0.001 m + 1·10⁻⁹ m.
   *(Enmendado 2026-11-15: antes se comparaba `frame_pressure_head_m`, sin tolerancia.)*
3. Dado cualquier cálculo válido con fotogramas, entonces la respuesta **no** contiene
   `frame_pressure_head_m` (ni `frame_flow_lps`), y `frame_x_m` tiene las mismas progresivas que
   `x_m`, en el mismo orden, de modo que la presión de cada fotograma y progresiva se obtiene como
   `frame_head_m` − `elevation_m` de esa progresiva.
   *(Enmendado 2026-11-15: antes exigía `frame_pressure_head_m` = `frame_head_m` − cota del punto
   en cada fotograma y progresiva.)*
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
3. **Precisión de la serialización.** Dado cualquier cálculo válido con fotogramas, cuando se
   serializa la respuesta, entonces cada valor de las listas en m y L/s (las de F1–F2 enumeradas
   en «Precisión de las listas de salida» de `01-transitorio-cierre-valvula.md`, más
   `frame_head_m` y `frame_x_m`) es igual a su redondeo a 3 decimales, y `time_s`,
   `frame_time_s` y los escalares (`dt_s`, `dx_m`, extremos y sus progresivas e instantes,
   referencia teórica, datos de los `checks`) salen con precisión completa.
   *(Añadido 2026-11-15.)*
4. **Instantes sin redondear.** Dado el caso del Excel con `length_m` = 100, `wave_speed_ms` =
   1500 y `n_reaches` = 200 (`dt_s` = 1/3000 s ≈ 0.000333 s, menor que 1 ms) y la duración por
   defecto, cuando se calcula con fotogramas, entonces el paso entre instantes consecutivos de
   `time_s` es `dt_s` (± 1·10⁻⁹ s), cada `frame_time_s` es exactamente un valor de `time_s`, y las
   dos listas son estrictamente crecientes, sin instantes repetidos.
   *(Añadido 2026-11-15.)*
5. Entregable `portal/` completo según el kit v3.0.0.
