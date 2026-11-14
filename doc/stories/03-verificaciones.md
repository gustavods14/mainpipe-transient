# F3 — Verificaciones del resultado (v1)

> Épica: `00-epica.md`. Kit 3.0.0. Vale para las dos geometrías (F1 y F2).
>
> **Resultado no conforme ≠ error** (`kit 01 §5`, `kit 02 §4`). Todo lo de esta página se
> **calcula** y se devuelve con `status` + `checks`; la pantalla dibuja el resultado con sus avisos.
> Lo que impide calcular (ley de cierre mal formada o que no termina en Q = 0, perfil inválido,
> duración insuficiente, rangos) es error 422 y está en HU-1.6 y HU-2.3.
>
> Los semáforos de validación de entradas del Excel **no son avisos en la API**: «Courant = 1» se
> cumple por construcción de la malla; «primer caudal de la ley = Q₀» y «tiempos de la ley
> crecientes» son errores 422 (HU-1.6).
>
> **Decisiones de G1 (2026-11-14)**: PN y presión mínima van como `checks` (P6); la comparación con
> Joukowsky / Michaud es solo dato informativo, sin aviso (P6); la presión mínima admisible la
> ingresa el usuario, −10 m.c.a. por defecto, sin ajuste por altitud (P7); la separación de
> columna se avisa con un mensaje claro y no se modela (P8).
>
> **Códigos y severidades**: propuestos aquí (los decide el upstream, regla central del kit);
> `hie-architect` fija en el plan su correspondencia con la paleta de estado del portal (D-13,
> `kit 01 §5`). Cada aviso lleva `code`, `severity`, `message` en español con unidades y
> decimales con punto, y los datos que lo localizan (valor, progresiva, instante).
>
> **Caso sin fricción** usado abajo: el de HU-1.1 criterio 3 (f = 0, L = 1000 m, a = 1000 m/s,
> D = 300 mm, Q₀ = 100 L/s, `n_reaches` = 20, `duration_s` = 5, cierre en un paso, tubería
> horizontal en z = 0). Su sobrepresión es exacta, ΔH = a·V₀/g = 144.21 m, y la presión en la
> válvula oscila entre H_dep + 144.21 y H_dep − 144.21.

## Entradas que usa

`pn_bar`, `density_kgm3`, `gravity_ms2`, `min_allowed_pressure_head_m` (F1), más las envolventes
y extremos calculados en F1/F2.

## Salidas

| Grupo | Campos |
|---|---|
| Estado | `status` (`ok` · `warning` · `error`), `checks[]` (`code`, `severity`, `message`, datos de localización) |
| Timbraje | `pn_head_m` (PN expresado en m.c.a. = PN·10⁵/(ρ·g)), `pressure_max_pn_ratio_pct` |
| Referencia teórica (informativa, sin aviso) | `maneuver_type` (`rapid` · `slow`), `theoretical_head_rise_m` (ΔH teórico), `moc_head_rise_valve_m` (ΔH MOC), `theory_deviation_pct` (diferencia en %); como desglose: `joukowsky_head_rise_m`, `michaud_head_rise_m` (`null` si la maniobra es rápida), `full_pulse_length_m` (`null` si la maniobra es lenta) |

## Avisos propuestos

| `code` | Severidad | Cuándo |
|---|---|---|
| `PN_NEAR_LIMIT` | `warning` | 80 % < presión máxima global / PN ≤ 100 % |
| `PN_EXCEEDED` | `error` | presión máxima global > PN |
| `SUBATMOSPHERIC_PRESSURE` | `warning` | presión mínima admisible ≤ presión mínima global < 0 |
| `COLUMN_SEPARATION_RISK` | `error` | presión mínima global < presión mínima admisible |
| `STEADY_NEGATIVE_PRESSURE` | `warning` / `error` | presión negativa en el régimen inicial (`error` si además baja de la mínima admisible) |

No hay aviso por desviación respecto de Joukowsky / Michaud ni por duración insuficiente (esta
última es error 422, HU-1.6 criterio 10).

---

## HU-3.1 — Comprobar la sobrepresión frente al timbraje de la tubería

**Como** proyectista, **quiero** que la presión máxima del transitorio se compare con el PN de la
tubería **para** saber si la clase elegida resiste la maniobra o si debo cambiar de clase o de ley
de cierre.

**Criterios de aceptación**

1. Dado ρ = 1000 kg/m³, g = 9.81 m/s² y `pn_bar` = 25, entonces `pn_head_m` = 254.84 ± 0.01.
2. Dado el caso sin fricción con H_dep = 100 m (presión máxima 244.21 m en toda la tubería) y
   `pn_bar` = 25, entonces `pressure_max_pn_ratio_pct` = 95.8 ± 0.1 y hay un aviso
   `PN_NEAR_LIMIT`.
3. El mismo caso con `pn_bar` = 20 (203.87 m) da `PN_EXCEEDED`, y con `pn_bar` = 40 no da
   ningún aviso de PN.
4. El mensaje de `PN_EXCEEDED` indica la presión máxima, el PN en bar y en m.c.a., la progresiva y
   el instante, p. ej. «La presión máxima (244.2 m.c.a. en x = 1000 m, t = 0.05 s) supera el
   PN 20 bar (203.9 m.c.a.). Aumente la clase de la tubería o alargue el cierre.»
5. Entregable `portal/` completo según el kit v3.0.0.

## HU-3.2 — Recibir un aviso claro cuando la presión cae bajo el límite admisible

**Como** proyectista, **quiero** saber si algún punto de la tubería baja de la presión mínima
admisible, dónde y cuándo ocurre por primera vez, y que se me diga sin ambigüedad que desde ese
instante el resultado ya no es físico, **para** decidir si hace falta protección (ventosas,
cierre más lento) y no tomar por buenos los picos posteriores.

El aviso `COLUMN_SEPARATION_RISK` lleva, además de `code`, `severity` y `message`: la primera
progresiva (`first_x_m`) y el primer instante (`first_time_s`) en que la presión baja del límite,
la presión en ese punto e instante, la presión mínima global y el límite usado.

**Criterios de aceptación**

1. Dado el caso del Excel (presión mínima −37.9 m.c.a., límite −10 m.c.a.), cuando se calcula,
   entonces hay un aviso `COLUMN_SEPARATION_RISK`, `status` = `error`, y el resultado se devuelve
   completo (no es un error 422).
2. Dado cualquier caso con `COLUMN_SEPARATION_RISK`, entonces `first_x_m` es una progresiva de
   `x_m`, `first_time_s` es un instante de `time_s`, la presión en ese punto e instante es menor
   que el límite, y en ningún punto de la tubería la presión es menor que el límite en un instante
   anterior.
3. Dado el caso sin fricción con H_dep = 100 m (presión mínima −44.21 m), entonces
   `first_x_m` = 1000 y `first_time_s` = 2.05 ± 0.05.
4. El `message` de `COLUMN_SEPARATION_RISK` dice, en este orden: que la presión cae por debajo del
   límite admisible (con ambos valores en m.c.a.), **dónde** (x en m) y **cuándo** (t en s) ocurre
   por primera vez, y que **a partir de ese instante los resultados del Método de las
   Características simple dejan de ser físicos** (puede haber separación de columna, que v1 no
   modela, y los picos posteriores pueden estar subestimados). Para el caso sin fricción:
   «La presión cae a −44.2 m.c.a., por debajo del límite admisible de −10.0 m.c.a., por primera
   vez en x = 1000 m y t = 2.05 s. A partir de ese instante puede haber separación de columna y
   los resultados del MOC simple dejan de ser físicos: las presiones y caudales posteriores no son
   fiables.»
5. Dado el caso sin fricción con H_dep = 136 m (presión mínima 136 − 144.21 = −8.21 m.c.a.) y el
   límite por defecto de −10 m.c.a., entonces hay `SUBATMOSPHERIC_PRESSURE` y no
   `COLUMN_SEPARATION_RISK`; su mensaje da la presión mínima, x y t.
6. Dado el mismo caso con `min_allowed_pressure_head_m` = −7, entonces hay
   `COLUMN_SEPARATION_RISK` y no `SUBATMOSPHERIC_PRESSURE`: el umbral es el valor que ingresa el
   usuario.
7. Dado el caso sin fricción con H_dep = 150 m (presión mínima +5.79 m), entonces no hay ningún
   aviso de presión mínima.
8. Entregable `portal/` completo según el kit v3.0.0.

## HU-3.3 — Detectar presión negativa ya en el régimen inicial

**Como** proyectista, **quiero** que se me avise si la piezométrica de régimen queda por debajo del
perfil en algún punto **para** saber que el problema existe antes de la maniobra y que el
trazado o el caudal de diseño no son viables.

**Criterios de aceptación**

1. Dado el caso del Excel con un perfil (0; 0), (300; 98), (1000; 0) (la piezométrica inicial en
   x = 300 m es 97.96 m), entonces hay `STEADY_NEGATIVE_PRESSURE` con severidad `warning` en
   x = 300 m.
2. Dado el mismo caso con el vértice a 110 m de cota, entonces `STEADY_NEGATIVE_PRESSURE` tiene
   severidad `error` (−12.04 m.c.a. < −10 m.c.a.).
3. En ambos casos el resultado se calcula y se devuelve completo (no es un error 422).
4. Entregable `portal/` completo según el kit v3.0.0.

## HU-3.4 — Contrastar el resultado con Joukowsky y Michaud

**Como** ingeniero revisor, **quiero** ver la sobrepresión teórica de la maniobra (Joukowsky si es
rápida, Michaud si es lenta), la del MOC y su diferencia en % **para** juzgar de un vistazo si el
resultado numérico es razonable.

Es **dato informativo**: nunca genera un aviso ni cambia `status`.

**Criterios de aceptación**

1. Dado el caso del Excel, entonces `maneuver_type` = `rapid` (Tc = 1.5 s ≤ 2L/a = 2.0 s),
   `theoretical_head_rise_m` = `joukowsky_head_rise_m` = 144.2 ± 0.1 (a·V₀/g),
   `michaud_head_rise_m` = `null`, `full_pulse_length_m` = 250 ± 0.1 (L − a·Tc/2),
   `moc_head_rise_valve_m` = 149.6 ± 0.1 (242.8 − 93.2) y `theory_deviation_pct` = 3.7 ± 0.1. Los
   valores se contrastan con la hoja `4_Validacion`; si su definición de la diferencia difiere,
   manda la del Excel y se anota en el plan.
2. Dada la ley lineal (0 s; 100 L/s), (10 s; 0) con los demás datos del Excel, entonces
   `maneuver_type` = `slow`, `theoretical_head_rise_m` = `michaud_head_rise_m` = 28.84 ± 0.01
   (2·L·V₀/(g·Tc)) y `full_pulse_length_m` = `null`.
3. Dado un caso con `theory_deviation_pct` > 5 %, entonces no aparece ningún aviso por ese motivo
   en `checks` y `status` no cambia.
4. Entregable `portal/` completo según el kit v3.0.0.

## HU-3.5 — Ver el estado global del cálculo

**Como** proyectista, **quiero** un estado global del resultado **para** saber sin leer cada aviso
si el diseño cumple, cumple con reservas o no cumple.

**Criterios de aceptación**

1. Dado un resultado sin avisos (p. ej. caso sin fricción con H_dep = 150 m y `pn_bar` = 40),
   entonces `status` = `ok` y `checks` = [].
2. Dado un resultado cuyo aviso más severo es `warning`, entonces `status` = `warning`; si hay
   algún `error`, `status` = `error`.
3. Dado el caso del Excel, entonces `checks` contiene al menos `COLUMN_SEPARATION_RISK` y
   `PN_NEAR_LIMIT` (242.8 m.c.a. = 95.3 % de 254.84 m.c.a., si la presión máxima global es la de
   la válvula; se confirma con la hoja `4_Validacion`).
4. Todos los `message` están en español, con unidades y decimales con punto (`kit 01 §5`).
5. Entregable `portal/` completo según el kit v3.0.0.

> La antigua HU-3.6 («la simulación no cubre la maniobra») se retiró: con la duración como dato de
> entrada (P5) es el error 422 de HU-1.6 criterio 10.
