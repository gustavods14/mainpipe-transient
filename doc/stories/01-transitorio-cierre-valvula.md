# F1 — Transitorio por cierre de válvula en tubería horizontal (v1)

> Épica: `00-epica.md`. Kit 3.0.0. Escenario único `reservoir_pipe_valve`, geometría
> `horizontal`. La geometría `profile` está en `02-perfil-tuberia.md`; los avisos, en
> `03-verificaciones.md`.
>
> Enmienda 2026-11-14 (D-57, resuelve DR-2; decisión del usuario en G1): HU-1.6 gana el crit. 13,
> error 422 cuando la duración pedida con la malla elegida supera el tope de pasos de cálculo (la
> cifra del tope la fija el plan, U-09). Etapa 1 reabierta para esta enmienda.
>
> Enmienda 2026-11-14 (restaura HU-1.7; hallazgo F1-01 de `doc/verification/02-fase-1.md`,
> decisión del dueño): se añade al final HU-1.7 (malla y duración configurables), que la épica
> (decisión P5 y pregunta 3), el plan 01 (§1.3, fases 1 y 2), `doc/DECISIONS.md` (U-08, U-09) y
> HU-1.6 crit. 13 ya citaban y que faltaba en este archivo. No cambia el alcance: recoge la
> decisión P5 de G1, la tabla de entradas de este archivo y lo que el plan fijó (U-08, U-09,
> D-57). Los errores de N y de la duración siguen en HU-1.6 (crits. 9, 10 y 13).
>
> **Método**: Método de las Características en H y Q, malla con número de Courant = 1
> (Δx = L/N, Δt = Δx/a), fricción de Darcy-Weisbach con f constante. Contornos: depósito de nivel
> constante (H = H_dep) aguas arriba; caudal impuesto Q(t) en la válvula aguas abajo. Régimen
> inicial permanente: Q = Q₀ y H(x) = H_dep − h_f·x/L.
>
> **Nombres de campos y unidades**: propuestos con la unidad en el nombre (`kit 01 §4`); el
> contrato definitivo, incluida la elección de L/s y mm, lo fija `hie-architect` en el plan. Los
> decimales van con punto, como en pantalla.

## Entradas

| Campo | Unidad | Valor del Excel | Rango válido (fuera → error 422) |
|---|---|---|---|
| `scenario` | — | `reservoir_pipe_valve` | único valor en v1 (campo reservado para escenarios futuros) |
| `geometry` | — | `horizontal` | `horizontal` · `profile` |
| `length_m` | m | 1000 | > 0 (solo con geometría `horizontal`; con perfil, L = x final) |
| `inner_diameter_mm` | mm | 300 (0.3 m en el Excel) | > 0 |
| `wave_speed_ms` | m/s | 1000 | 0 < a ≤ 1500 |
| `darcy_friction_factor` | — | 0.02 | 0 ≤ f ≤ 0.1 (f = 0 admitido: caso sin fricción) |
| `initial_flow_lps` | L/s | 100 (0.1 m³/s en el Excel) | > 0 |
| `reservoir_level_m` | m | 100 | cualquier cota, en el mismo datum que la tubería |
| `pipe_elevation_m` | m | 0 | ≤ `reservoir_level_m` (solo con geometría `horizontal`) |
| `density_kgm3` | kg/m³ | 1000 | > 0 |
| `gravity_ms2` | m/s² | 9.81 | 9.7 ≤ g ≤ 9.9 |
| `pn_bar` | bar | 25 | > 0 (lo usa F3) |
| `min_allowed_pressure_head_m` | m.c.a. | −10 (por defecto) | ≥ −10.33 (lo usa F3); sin ajuste por altitud |
| `closure_time_s` | s | 0, 0.5, 1, 1.5, 2, 5, 10, 20 | 2 a 20 puntos; empieza en 0; estrictamente creciente |
| `closure_flow_lps` | L/s | 100, 50, 20, 0, 0, 0, 0, 0 | misma longitud que `closure_time_s`; primer valor = Q₀; 0 ≤ Q ≤ Q₀; **último valor = 0** (cierre total) |
| `n_reaches` | — | 20 | entero par, 10 ≤ N ≤ 200; por defecto 20 (tope propuesto; lo confirma el plan) |
| `duration_s` | s | 20 (= 400·Δt en el Excel) | ≥ Tc + 2L/a; por defecto Tc + 5·(4L/a); tope lo fija el plan |

N es par para que el punto medio (x = L/2) sea un nodo de cálculo (propuesta; el plan puede
cambiarla). Tc (`closure_duration_s`) es el instante en que la ley llega a Q = 0.

## Salidas

| Grupo | Campos (unidad en el nombre) |
|---|---|
| Estado | `status`, `checks` (F3) |
| Derivados | `area_m2`, `velocity_initial_ms`, `head_loss_m` (h_f), `dx_m`, `dt_s`, `n_reaches`, `n_steps`, `duration_s` (duración efectiva = `n_steps`·`dt_s`), `reflection_time_s` (2L/a), `wave_period_s` (4L/a), `closure_duration_s` (Tc) |
| Series temporales (columnas paralelas) | `time_s`, `head_valve_m`, `head_midpoint_m`, `pressure_head_valve_m`, `pressure_head_midpoint_m`, `flow_reservoir_lps`, `flow_valve_lps` |
| Envolventes (columnas paralelas por progresiva) | `x_m`, `elevation_m`, `head_initial_m`, `head_max_m`, `head_min_m`, `pressure_head_max_m`, `pressure_head_min_m` |
| Extremos | `head_valve_max_m` + `head_valve_max_time_s`, `head_valve_min_m` + `head_valve_min_time_s`, `pressure_head_max_global_m` + su `x_m` y `time_s`, `pressure_head_min_global_m` + su `x_m` y `time_s` |

«Punto medio» = progresiva x = L/2. «Presión» = altura de presión p/γ = H − z, en m.c.a.

---

## HU-1.1 — Calcular el golpe de ariete de una maniobra de cierre

**Como** proyectista de una aducción por gravedad, **quiero** calcular el transitorio que produce
el cierre de la válvula a partir de los datos de la tubería, el depósito y la ley de cierre,
**para** decidir si la maniobra prevista es admisible para la tubería.

**Criterios de aceptación**

1. **Caso del Excel.** Dado el caso de referencia (valores de la tabla de entradas, con
   `n_reaches` = 20 y `duration_s` = 20), cuando se calcula, entonces `velocity_initial_ms` =
   1.415 ± 0.001, `head_loss_m` = 6.80 ± 0.01, `dx_m` = 50, `dt_s` = 0.05, `n_steps` = 400,
   `duration_s` = 20, `reflection_time_s` = 2.0, `wave_period_s` = 4.0, `head_valve_max_m` =
   242.8 ± 0.1 y `head_valve_min_m` = −37.9 ± 0.1.
2. **Fidelidad al Excel.** Dado el mismo caso, cuando se calcula, entonces H y Q en la válvula, el
   punto medio y el depósito coinciden con la hoja `2_Malla_MOC` en cada paso con una tolerancia
   de ± 0.05 m y ± 0.05 L/s. (El caso se extrae del Excel como caso de referencia en
   `portal/examples/`, `kit 01 §9`.)
3. **Joukowsky exacto sin fricción.** Dado f = 0, L = 1000 m, a = 1000 m/s, D = 300 mm,
   Q₀ = 100 L/s, H_dep = 100 m, `n_reaches` = 20, `duration_s` = 5 y un cierre en un solo paso
   (ley (0 s; 100 L/s), (0.05 s; 0)), cuando se calcula, entonces `head_valve_m` = 244.21 ± 0.01 m
   para 0.05 s < t < 2.0 s, `head_valve_m` = −44.21 ± 0.01 m para 2.05 s < t < 4.0 s, y
   `flow_reservoir_lps` = −100 ± 0.1 para 1.05 s < t < 3.0 s.
4. **Cota de la tubería.** Dado el caso del Excel con `pipe_elevation_m` = 50 y
   `reservoir_level_m` = 150, cuando se calcula, entonces todas las alturas piezométricas son las
   del caso original + 50 m y todas las presiones son idénticas (± 1·10⁻⁶ m).
5. El tiempo de cálculo del caso del Excel es < 1 s medido en el upstream (`kit 01 §6`).
6. Entregable `portal/` completo según el kit v3.0.0.

## HU-1.2 — Definir la ley de cierre como tabla tiempo–caudal

**Como** proyectista, **quiero** describir la maniobra de la válvula como una tabla de puntos
(t, Q) que termina con la válvula cerrada **para** probar cierres rápidos, lentos o escalonados
sin tocar el resto de datos.

**Criterios de aceptación**

1. Dada la ley del Excel, cuando se calcula, entonces `flow_valve_lps` en t = 0.25 s vale
   75 ± 0.01 (interpolación lineal entre (0; 100) y (0.5; 50)) y en t = 0.75 s vale 35 ± 0.01.
2. Dada una ley cuyo último punto es (1.5 s; 0), cuando se calcula con una duración mayor, entonces
   `flow_valve_lps` = 0 para todo t ≥ 1.5 s (constante tras el último punto).
3. Dada la ley del Excel, entonces `closure_duration_s` = 1.5 (primer instante con Q = 0, aunque la
   tabla siga con puntos en Q = 0 hasta 20 s).
4. Dada la ley lineal (0 s; 100 L/s), (3 s; 0), entonces `flow_valve_lps` en t = 1.5 s vale
   50 ± 0.01 y `closure_duration_s` = 3.
5. Entregable `portal/` completo según el kit v3.0.0.

## HU-1.3 — Conocer el régimen inicial y los tiempos característicos

**Como** proyectista, **quiero** ver el régimen permanente antes de la maniobra y los tiempos
2L/a y 4L/a **para** clasificar la maniobra y comprobar que el punto de partida es el que espero.

**Criterios de aceptación**

1. Dado el caso del Excel, entonces `head_initial_m` vale 100.00 en x = 0, 96.60 ± 0.01 en
   x = 500 m y 93.20 ± 0.01 en x = 1000 m, y `head_valve_m[0]` = `head_initial_m` en la válvula.
2. Dado el caso del Excel, entonces `flow_reservoir_lps[0]` = `flow_valve_lps[0]` = 100.
3. Entregable `portal/` completo según el kit v3.0.0.

## HU-1.4 — Ver la evolución en la válvula, el punto medio y el depósito

**Como** proyectista, **quiero** las series temporales de altura piezométrica y presión en la
válvula y en el punto medio, y de caudal en el depósito y en la válvula, **para** ver la forma del
pulso, su periodo y su amortiguamiento.

**Criterios de aceptación**

1. Dado cualquier cálculo válido, entonces las series tienen `n_steps + 1` valores,
   `time_s[0]` = 0, `time_s[-1]` = `duration_s` (efectiva) y el paso entre instantes es `dt_s`.
2. Dado el caso del Excel, entonces `head_midpoint_m` corresponde a x = 500 m y
   `pressure_head_valve_m` = `head_valve_m` − `pipe_elevation_m` en cada instante.
3. Dado el caso del Excel, entonces `flow_reservoir_lps` no cambia antes de t = L/a = 1.0 s (la
   onda aún no ha llegado al depósito), con tolerancia 1·10⁻⁶ L/s.
4. Entregable `portal/` completo según el kit v3.0.0.

## HU-1.5 — Obtener las envolventes de presión a lo largo de la tubería

**Como** proyectista, **quiero** las envolventes máxima y mínima de altura piezométrica y de
presión en toda la tubería, con el valor y el lugar e instante de los extremos, **para** elegir la
clase de tubería tramo a tramo y localizar dónde puede haber depresión.

**Criterios de aceptación**

1. Dado cualquier cálculo válido, entonces en cada progresiva `head_max_m` ≥ `head_initial_m` ≥
   `head_min_m` y `pressure_head_max_m` ≥ `pressure_head_min_m`.
2. Dado el caso del Excel, entonces `head_max_m` y `head_min_m` en x = L coinciden con
   `head_valve_max_m` y `head_valve_min_m`, y `pressure_head_max_global_m` /
   `pressure_head_min_global_m` y sus instantes coinciden con los de la hoja `4_Validacion`
   (± 0.1 m, ± `dt_s`).
3. Con geometría `horizontal`, `elevation_m` = `pipe_elevation_m` en todas las progresivas y
   `pressure_head_*_m` = `head_*_m` − `pipe_elevation_m`.
4. Entregable `portal/` completo según el kit v3.0.0.

## HU-1.6 — Recibir un error claro cuando los datos no permiten calcular

**Como** proyectista, **quiero** que una entrada inválida se rechace con un mensaje que diga qué
campo, qué valor y qué límite, **para** corregirla sin adivinar.

Son **errores** (`<Pkg>ValidationError`, 422, `kit 02 §1–3`): entradas para las que el paquete
**no puede producir** un resultado. No se mezclan con los avisos de F3, que acompañan a un
resultado calculado.

**Criterios de aceptación** (mensajes en español, con unidades y accionables, `kit 02 §3`)

1. Dado `closure_time_s` = [0, 1, 1, 2], cuando se calcula, entonces error 422 cuyo mensaje indica
   que los tiempos de la ley deben ser estrictamente crecientes y señala el punto 3 (t = 1 s).
2. Dado `closure_time_s[0]` ≠ 0, entonces error 422 que pide que la ley empiece en t = 0 s.
3. Dado `closure_flow_lps[0]` que difiere de `initial_flow_lps` en más de 0.1 %, entonces error
   422 que muestra ambos valores en L/s.
4. Dada una ley cuyo último caudal no es 0 (p. ej. (0; 100), (2; 40)), entonces error 422 que
   indica que la ley debe terminar con la válvula cerrada (Q = 0 L/s) y que los cierres parciales
   no están admitidos.
5. Dado un caudal de la ley negativo o mayor que Q₀, entonces error 422 que indica el punto y el
   rango admitido (0 a Q₀ L/s).
6. Dadas `closure_time_s` y `closure_flow_lps` de distinta longitud, o menos de 2 o más de 20
   puntos, entonces error 422.
7. Dado `wave_speed_ms` > 1500, `darcy_friction_factor` > 0.1, `min_allowed_pressure_head_m` <
   −10.33 o cualquier longitud, diámetro, caudal o PN ≤ 0, entonces error 422 que nombra el campo y
   el límite.
8. Dado `pipe_elevation_m` > `reservoir_level_m`, entonces error 422: la tubería queda por encima
   del nivel del depósito.
9. Dado `n_reaches` impar o fuera de 10–200, entonces error 422 con el rango admitido.
10. Dado `duration_s` < Tc + 2L/a (p. ej. la ley lineal (0 s; 100 L/s), (30 s; 0) con
    `duration_s` = 20 en el caso del Excel), entonces error 422 cuyo mensaje da Tc, 2L/a y la
    duración mínima (32 s): la simulación no cubriría el cierre y su primera reflexión.
11. Dado un fallo interno no previsto, entonces el paquete lanza `<Pkg>ComputationError` (500) con
    un mensaje genérico en español, nunca una excepción ajena (`kit 02 §1`).
12. Entregable `portal/` completo según el kit v3.0.0.
13. Dados `n_reaches` y `duration_s` cuyo número de pasos (`n_steps` calculado como en HU-1.7
    crit. 4, con `dt_s` = L/(N·a)) supera el tope de pasos de cálculo que fija el plan (p. ej. el
    caso del Excel con `n_reaches` = 200 y una `duration_s` mayor que la máxima admisible con esa
    malla), cuando se llama a `solve`, entonces error 422 cuyo mensaje nombra `duration_s` y
    `n_reaches`, da en s la duración máxima admisible con esa malla (tope de pasos × `dt_s`) e
    indica que se puede acortar la duración o usar una malla más gruesa; y con `duration_s` igual a
    esa duración máxima el cálculo se resuelve sin error. *(Añadido 2026-11-14, D-57.)*

## HU-1.7 — Elegir la malla de cálculo y la duración de la simulación

**Como** proyectista, **quiero** fijar el número de tramos de la malla y la duración de la
simulación, o aceptar sus valores por defecto, **para** comprobar que el resultado no depende de
la malla y que la simulación cubre el cierre completo y los ciclos de la onda que necesito para
juzgar la maniobra.

Origen: decisión P5 de G1 (`00-epica.md`): N configurable, 20 por defecto, y duración como dato
de entrada. *(Restaurada 2026-11-14, F1-01.)*

La malla mantiene el número de Courant = 1 (ver «Método»): Δx = L/N y Δt = Δx/a = L/(N·a).
`n_reaches` (N) es un entero par entre 10 y 200, 20 por defecto, para que x = L/2 sea nodo (tabla
de entradas). `duration_s` (T) vale por defecto Tc + 5·(4L/a): el cierre más cinco periodos de la
onda. Los rangos y el tope de pasos los fija el plan (U-09; tope de 10 000 pasos, D-57).

Las entradas fuera de rango son **errores** ya descritos en HU-1.6 y no se repiten aquí: N impar o
fuera de 10–200 (crit. 9), duración menor que Tc + 2L/a (crit. 10) y número de pasos por encima del
tope, también con la duración por defecto (crit. 13). Elegir N o T no genera avisos en `checks`: la
malla y la duración no dan lugar a ningún resultado no conforme.

**Criterios de aceptación** (caso del Excel: L = 1000 m, a = 1000 m/s)

1. **Malla.** Dado el caso del Excel con `n_reaches` = 20, cuando se calcula, entonces
   `dx_m` = 50 y `dt_s` = 0.05, y con geometría `horizontal` `x_m` tiene N + 1 = 21 progresivas,
   de 0 a 1000 m cada 50 m (la última es 1000 exacto). Con `n_reaches` = 40, `dx_m` = 25,
   `dt_s` = 0.025 y hay 41 progresivas. La respuesta devuelve el `n_reaches` usado y, si la
   entrada no lo trae, se usa 20.
2. **Punto medio e independencia de la malla.** Dado cualquier `n_reaches` admitido (p. ej. 20 o
   40), entonces x = L/2 = 500 m es un nodo de cálculo (el N/2) y `head_midpoint_m` es la altura
   de ese nodo, sin interpolar. Dado el caso sin fricción de HU-1.1 crit. 3, calculado con
   `n_reaches` = 20 y con `n_reaches` = 40, entonces `head_valve_max_m` = 244.21 ± 0.01 m en los
   dos casos (Joukowsky): el resultado no depende de la malla.
3. **Duración por defecto.** Dado el caso del Excel sin `duration_s`, cuando se calcula, entonces
   la duración es Tc + 5·(4L/a) = 1.5 + 5·4.0 = 21.5 s, con `n_steps` = 430 y `duration_s` = 21.5
   en la respuesta. La duración por defecto no se recorta para que quepa en el tope de pasos: si no
   cabe, se aplica el error 422 de HU-1.6 crit. 13.
4. **Número de pasos y duración efectiva.** Dados `duration_s` = T y `dt_s` = Δt, entonces
   `n_steps` = ⌈T/Δt − 10⁻⁹⌉ (la tolerancia absorbe el redondeo de coma flotante) y la
   `duration_s` devuelta es la duración efectiva, `n_steps`·`dt_s`. Caso del Excel con
   `n_reaches` = 20: `duration_s` = 20 da `n_steps` = 400 (no 401) y `duration_s` = 20;
   `duration_s` = 20.01 da `n_steps` = 401 y `duration_s` = 20.05 (el paso que completa la
   duración pedida).
5. **Tiempo de cálculo con la malla más fina.** Dado el caso más grande que admiten los rangos,
   `n_reaches` = 200 con la duración máxima del tope de pasos (caso del Excel: `dt_s` = 0.005 s,
   `duration_s` = 50 s, `n_steps` = 10 000), cuando se llama a `solve`, entonces el cálculo se
   resuelve sin error y el tiempo de cálculo es < 1 s medido en el upstream (`kit 01 §6`). El peor
   caso exacto de la medición (geometría, vértices del perfil, fotogramas) y el objetivo interno
   los fija el plan (V-16).
6. Entregable `portal/` completo según el kit v3.0.0.
