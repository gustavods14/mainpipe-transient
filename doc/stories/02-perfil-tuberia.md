# F2 — Perfil real de la tubería (v1)

> Épica: `00-epica.md`. Kit 3.0.0. Geometría `profile` del escenario único
> `reservoir_pipe_valve`. Todo lo de F1 (entradas, salidas, ley de cierre, malla, errores) vale
> igual; aquí solo lo que cambia.
>
> **Método**: el MOC se escribe en altura piezométrica H, así que el perfil **no cambia** H ni Q
> (se desprecia el término V·sen α, efecto ≈ V₀·Δz/a; fuera de v1). Lo que cambia es la presión de
> cada punto: **p/γ = H − z(x)**, con z interpolada linealmente entre los vértices del perfil.
>
> **Decisiones de G1 (2026-11-14)**: el perfil se ingresa como tabla de puntos (x, z) y el portal
> lo muestra en un gráfico del perfil (P2); x es la progresiva a lo largo del eje de la tubería y
> L = x final del perfil (P3).
>
> Enmienda 2026-11-15 (decisión del dueño tras G4): las columnas por progresiva se redondean a
> 3 decimales al serializar, con la regla de F1 («Precisión de las listas de salida»); los
> extremos escalares y sus progresivas no. Se ajustan las tolerancias que el redondeo hace
> inverificables: HU-2.1 crit. 2 y HU-2.2 crits. 1, 2 y 3. No cambia el cálculo ni el resto del
> alcance. Etapa 1 reabierta para esta enmienda.
>
> Enmienda 2026-11-15, posterior a la entrega v0.1.0 (observación «Literal de HU-2.3 crit. 1» de
> `doc/verification/04-fase-3.md`, tras la corrección F3-03; decisión del dueño del 2026-11-15):
> HU-2.3 crit. 1 pasa a citar el mensaje literal que da el paquete, con la numeración
> «(punto N)» desde 1 que F3-03 intercaló. **No es un cambio de comportamiento**: el mensaje ya es
> ese desde F3-03 y la verificación daba el criterio por cumplido en su sentido.

## Entradas (además de las de F1)

| Campo | Unidad | Rango válido (fuera → error 422) |
|---|---|---|
| `geometry` | — | `profile` |
| `profile_x_m` | m | 2 a 500 puntos; progresiva a lo largo del eje; empieza en 0; estrictamente creciente. L = último valor |
| `profile_z_m` | m | misma longitud que `profile_x_m`; mismo datum que `reservoir_level_m`; z(0) ≤ `reservoir_level_m` |

Con geometría `profile` no se usan `length_m` ni `pipe_elevation_m`.

## Salidas (cambios respecto de F1)

- `x_m` de las envolventes incluye los nodos de cálculo **y todos los vértices del perfil**, para
  no perder un punto alto que caiga entre dos nodos.
- `elevation_m` es la cota del perfil en cada progresiva de `x_m`.
- `pressure_head_*` (series, envolventes y extremos) se calculan con la cota del punto.
- Las columnas `x_m`, `elevation_m`, `head_initial_m`, `head_max_m`, `head_min_m`,
  `pressure_head_max_m` y `pressure_head_min_m` están alineadas, para que el portal dibuje el
  perfil, la piezométrica inicial y las envolventes en un mismo gráfico de serie sin
  transformarlas (`kit 01 §4`, `kit 05 §3`).
- Esas columnas salen redondeadas a 3 decimales (enmienda 2026-11-15; regla y excepciones en F1,
  «Precisión de las listas de salida»). Las presiones se calculan con precisión completa y se
  redondean al final, igual que las alturas.

---

## HU-2.1 — Describir el trazado de la tubería con puntos (x, z)

**Como** proyectista, **quiero** ingresar el perfil longitudinal de la tubería como una tabla de
puntos progresiva–cota **para** que las presiones del transitorio correspondan al trazado real y
no a una tubería horizontal.

**Criterios de aceptación**

1. Dado el caso del Excel con geometría `profile` y un perfil cualquiera de x final 1000 m que
   quede bajo la piezométrica inicial, cuando se calcula, entonces todas las series de H y Q y las
   envolventes de H en los nodos de cálculo son idénticas (± 1·10⁻⁶) a las del mismo caso con
   geometría `horizontal` y `length_m` = 1000.
2. Dado un perfil (0; 0), (500; 40), (1000; 0), cuando se calcula, entonces `elevation_m` = 20 en
   x = 250 m, y en cada progresiva `pressure_head_min_m` = `head_min_m` − `elevation_m` y
   `pressure_head_max_m` = `head_max_m` − `elevation_m` con |diferencia| ≤ 0.001 m + 1·10⁻⁹ m.
   *(Enmendado 2026-11-15: antes ± 1·10⁻⁶ m; las tres columnas salen redondeadas a 3 decimales.)*
3. Dado un perfil de dos puntos (0; 0), (1000; 0), cuando se calcula, entonces el resultado es
   idéntico al de la geometría `horizontal` con `length_m` = 1000 y `pipe_elevation_m` = 0.
4. Dado un perfil cuyo último punto es x = 1250 m, entonces la longitud de cálculo es 1250 m:
   `dx_m` = 62.5 con `n_reaches` = 20 y `reflection_time_s` = 2.5 con a = 1000 m/s.
5. Con geometría `profile`, `pressure_head_midpoint_m` usa la cota del perfil en x = L/2.
6. Entregable `portal/` completo según el kit v3.0.0.

## HU-2.2 — Ver dónde se dan la sobrepresión y la depresión máximas sobre el perfil

**Como** proyectista, **quiero** las envolventes de presión evaluadas también en los vértices del
perfil, con la ubicación del mínimo y del máximo global, **para** saber qué punto alto del trazado
es el crítico y dónde haría falta protección.

**Criterios de aceptación**

1. Dado un perfil con un vértice en x = 520 m (entre los nodos de 500 y 550 m con
   `n_reaches` = 20), cuando se calcula, entonces `x_m` contiene 520 y `elevation_m` en esa
   progresiva es la cota del vértice redondeada a 3 decimales.
   *(Enmendado 2026-11-15: «redondeada a 3 decimales».)*
2. Dado cualquier perfil, cuando se calcula, entonces `pressure_head_min_global_m` redondeado a
   3 decimales es el menor valor de `pressure_head_min_m`, `pressure_head_max_global_m` redondeado
   a 3 decimales es el mayor de `pressure_head_max_m`, y sus progresivas informadas, redondeadas a
   3 decimales, están en `x_m`.
   *(Enmendado 2026-11-15: los extremos escalares no se redondean y las columnas sí.)*
3. Dado el caso del Excel con el perfil con loma (0; 0), (500; 40), (1000; 0), cuando se calcula,
   entonces `pressure_head_min_m` en x = 500 m es 40 m menor (|diferencia| ≤ 0.001 m + 1·10⁻⁹ m)
   que en el mismo punto del caso horizontal: el supuesto horizontal subestima la depresión de cada
   punto alto en su altura (antecedente técnico de `CLAUDE.md`).
   *(Enmendado 2026-11-15: antes «exactamente», ± 1·10⁻⁶ m.)*
4. Entregable `portal/` completo según el kit v3.0.0.

## HU-2.3 — Recibir un error claro cuando el perfil no es válido

**Como** proyectista, **quiero** que un perfil mal formado se rechace con el punto exacto que
falla **para** corregirlo en la tabla.

Son **errores** (422): el paquete no puede construir la geometría. Una piezométrica inicial por
debajo del perfil **no** es error: se calcula y se avisa (F3, `STEADY_NEGATIVE_PRESSURE`).

**Criterios de aceptación** (mensajes en español, con unidades, `kit 02 §3`)

1. Dado `profile_x_m` = [0, 150, 300, 120, 600], cuando se llama a `solve`, entonces error 422
   cuyo mensaje es exactamente:
   «La progresiva del perfil (profile_x_m) debe ser estrictamente creciente: x[3] = 120 m
   (punto 4) es menor que x[2] = 300 m (punto 3).»
   (en una sola línea). `x[i]` es el índice de `profile_x_m` contado desde 0 y «punto N» es la fila
   de la tabla del perfil contada desde 1.
   *(Enmendado 2026-11-15: antes «señala que x[3] = 120 m es menor que x[2] = 300 m»; el literal
   pasa a coincidir con el mensaje real tras F3-03. No cambia el comportamiento.)*
2. Dado un perfil con menos de 2 o más de 500 puntos, o con `profile_x_m` y `profile_z_m` de
   distinta longitud, entonces error 422.
3. Dado `profile_x_m[0]` ≠ 0, entonces error 422 que pide que el perfil empiece en x = 0 m (el
   depósito).
4. Dado `profile_z_m[0]` > `reservoir_level_m`, entonces error 422: la toma queda por encima del
   nivel del depósito, con ambos valores en m.
5. Dada la geometría `profile` sin perfil, o la geometría `horizontal` con perfil, entonces error
   422 que indica qué datos corresponden a cada geometría.
6. Entregable `portal/` completo según el kit v3.0.0.
