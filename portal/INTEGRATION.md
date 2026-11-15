# mainpipe_transient — Integration Reference

> **Qué es este documento.** El contrato de **Capa 1** del paquete `mainpipe_transient`, tal como
> está en el código del commit entregado (`src/mainpipe_transient/__init__.py`, `schemas.py`,
> `exceptions.py`). No documenta endpoints del portal (Capa 2) ni tipos de TypeScript (Capa 3).
> Lo redacta el upstream (`hie-api`, fase 6 del plan `doc/plans/01-golpe-ariete-v1.md`) leyendo
> el código; el portal lo copia a `doc/apps/mainpipe-transient/INTEGRATION.md` y lo verifica
> contra el paquete instalado.

| | |
|---|---|
| Slug del portal | `mainpipe-transient` |
| Paquete Python | `mainpipe_transient` (distribución `mainpipe-transient`) |
| Repositorio upstream | https://github.com/gustavods14/mainpipe-transient |
| Commit pineado | el de `portal/HANDOFF.md`, fila «Commit a pinear» (se fija en la entrega) |
| `__version__` | `0.1.0` |
| `SCHEMA_VERSION` | `"2.0"` (contrato congelado en G4 el 2026-11-15, D-63 … D-66) |

---

## Install

```
mainpipe-transient @ git+https://github.com/gustavods14/mainpipe-transient.git@<sha>
```

Dependencias transitivas: `numpy>=1.24` y `pydantic>=2.6` (ambas ya en el portal). Python
`>=3.12`. No las declares en `backend/requirements.txt`; se resuelven solas. Sin dependencias
nuevas para el portal (frontend tampoco).

---

## Import paths

```python
from mainpipe_transient import solve, SCHEMA_VERSION, __version__
from mainpipe_transient import SolveRequest, SolveResponse, Check            # o desde .schemas
from mainpipe_transient import (                                              # o desde .exceptions
    MainpipeTransientError,
    MainpipeTransientValidationError,
    MainpipeTransientComputationError,
)
```

Todo lo que no está en `mainpipe_transient.__all__` es privado. Importar el paquete no calcula
ni toca disco, red ni variables de entorno. Sin `print`; los fallos inesperados se registran con
`logging.getLogger("mainpipe_transient").exception(...)`.

---

## Funciones — firmas

| Función | Firma | Devuelve |
|---|---|---|
| `solve` | `solve(data: dict[str, Any]) -> dict[str, Any]` | `SolveResponse(...).model_dump(mode="json")`: un `dict` serializable con `json.dumps(..., allow_nan=False)`, ya con el redondeo de la salida aplicado |

`solve` valida con `SolveRequest.model_validate(data)`, calcula (Método de las Características,
malla de Courant 1) y devuelve la respuesta. Es pura y determinista. Tiempo medido del peor caso
admitido (N = 200, 699 progresivas, 10 000 pasos, con fotogramas): mediana 0.25 s (U-38).

### `solve` — claves de entrada (`SolveRequest`, `extra="forbid"`, sin `NaN`/`inf`)

| Clave | Requerida | Tipo | Unidad | Regla (fuera → 422) |
|---|---|---|---|---|
| `scenario` | no (`"reservoir_pipe_valve"`) | `"reservoir_pipe_valve"` | — | único valor en v1 |
| `geometry` | no (`"horizontal"`) | `"horizontal"` \| `"profile"` | — | — |
| `length_m` | con `horizontal` | `float \| null` | m | > 0; prohibido con `profile` |
| `pipe_elevation_m` | con `horizontal` | `float \| null` | m | ≤ `reservoir_level_m`; prohibido con `profile` |
| `profile_x_m` | con `profile` | `list[float] \| null` | m | 2–500 puntos, empieza en 0, estrictamente creciente; prohibido con `horizontal` |
| `profile_z_m` | con `profile` | `list[float] \| null` | m | misma longitud que `profile_x_m`; `[0]` ≤ `reservoir_level_m` |
| `inner_diameter_mm` | sí | `float` | mm | > 0 |
| `wave_speed_ms` | sí | `float` | m/s | 0 < a ≤ 1500 |
| `darcy_friction_factor` | sí | `float` | — | 0 ≤ f ≤ 0.1 |
| `initial_flow_lps` | sí | `float` | L/s | > 0 |
| `reservoir_level_m` | sí | `float` | m | cualquiera (mismo datum que la tubería) |
| `pn_bar` | sí | `float` | bar | > 0 |
| `min_allowed_pressure_head_m` | no (`-10.0`) | `float` | m.c.a. | −10.33 ≤ valor ≤ 0 |
| `closure_time_s` | sí | `list[float]` | s | 2–20 puntos, empieza en 0, estrictamente creciente |
| `closure_flow_lps` | sí | `list[float]` | L/s | misma longitud; `[0]` a ±0.1 % de Q₀ (se sustituye por Q₀); 0 ≤ Q ≤ Q₀; último = 0 |
| `n_reaches` | no (`20`) | `int` | — | par, 10 ≤ N ≤ 200 |
| `duration_s` | no (`null` → Tc + 5·(4L/a)) | `float \| null` | s | > 0; ≥ Tc + 2L/a; `n_steps` ≤ `MAX_STEPS` = 10 000, también con la duración por defecto |
| `include_frames` | no (`true`) | `bool` | — | `false` → `frame_*` y `frame_stride` en `null` |

Reglas cruzadas, todas 422 con mensaje en español: número de fricción del tramo
φ = f·Δx·V₀/(2·D·a) ≤ 0.5 (el mensaje da el `n_reaches` par mínimo que lo cumple); tope de pasos
⌈T/Δt − 10⁻⁹⌉ ≤ 10 000 (el mensaje da la duración máxima admisible con esa malla, truncada para
que reenviarla calcule, y la malla más gruesa que admite la duración pedida); magnitudes que
desbordan en esas reglas. Campos retirados en la 2.0: `density_kgm3` y `gravity_ms2` (abajo,
«Cambios 1.0 → 2.0»).

---

## Modelos

> **Las unidades son parte del contrato.** La unidad va en el nombre: caudales en **L/s**,
> diámetro en **mm**, longitudes, cotas y alturas piezométricas en **m**, alturas de presión en
> **m.c.a.** (sufijo `_m`, p/γ = H − z), tiempos en **s**, PN en **bar**, porcentajes en **%**.
> Si la pantalla muestra otras unidades, la conversión es del portal.

**Constantes del cálculo** (desde la 2.0, U-40): densidad **ρ = 1000 kg/m³** y gravedad
**g = 9.81 m/s²**. No son campos de entrada ni de salida. Intervienen en `head_loss_m`,
`pn_head_m` (PN·10⁵/(ρ·g)), `joukowsky_head_rise_m` y `michaud_head_rise_m`.

### `SolveResponse` (`allow_inf_nan=False`)

**Identidad y estado**

| Campo | Tipo | Unidad / notas |
|---|---|---|
| `schema_version` | `str` | `"2.0"` |
| `scenario`, `geometry` | `str` | eco de la entrada |
| `status` | `"ok"` \| `"warning"` \| `"error"` | la severidad más alta de `checks`; `ok` sin avisos |
| `checks` | `list[Check]` | errores primero, después avisos (ver `Check`) |

**Derivados** (escalares, precisión completa)

| Campo | Unidad | Contenido |
|---|---|---|
| `length_m` | m | L (`length_m` o última `profile_x_m`) |
| `area_m2` | m² | π·D²/4 |
| `velocity_initial_ms` | m/s | V₀ = Q₀/A |
| `head_loss_m` | m | f·(L/D)·V₀²/(2g) |
| `dx_m`, `dt_s` | m, s | Δx = L/N, Δt = Δx/a |
| `n_reaches`, `n_steps` | — | N; ⌈T/Δt − 10⁻⁹⌉ |
| `duration_s` | s | duración efectiva `n_steps`·Δt (puede ser algo mayor que la pedida) |
| `reflection_time_s`, `wave_period_s` | s | 2L/a, 4L/a |
| `closure_duration_s` | s | Tc: primer instante de la ley con Q = 0 |
| `friction_number` | — | φ (≤ 0.5) |

**Series temporales** (longitud `n_steps + 1`; columnas paralelas)

| Campo | Unidad | Precisión |
|---|---|---|
| `time_s` | s | completa (k·Δt) |
| `head_valve_m`, `head_midpoint_m` | m | 3 decimales |
| `pressure_head_valve_m`, `pressure_head_midpoint_m` | m.c.a. | 3 decimales |
| `flow_reservoir_lps`, `flow_valve_lps` | L/s | 3 decimales |

«Midpoint» = nodo x = L/2 (N es par); su cota es z(L/2) interpolada del perfil.

**Envolventes por progresiva** (todas de la longitud de `x_m`)

| Campo | Unidad | Contenido (3 decimales salvo `x_is_node`) |
|---|---|---|
| `x_m` | m | nodos de cálculo ∪ vértices del perfil, ordenados, sin duplicados a precisión completa. A 3 decimales es **no decreciente**: dos progresivas a menos de 1 mm pueden mostrar el mismo valor |
| `x_is_node` | `list[bool]` | `true` = nodo de cálculo, `false` = solo vértice (H interpolada linealmente entre nodos) |
| `elevation_m` | m | z(x) |
| `head_initial_m`, `pressure_head_initial_m` | m, m.c.a. | régimen permanente |
| `head_max_m`, `head_min_m` | m | sobre todos los pasos |
| `pressure_head_max_m`, `pressure_head_min_m` | m.c.a. | ídem, con la cota del punto |

**Extremos** (escalares, precisión completa; desempate: primer instante, luego menor x)

`head_valve_max_m`, `head_valve_max_time_s`, `head_valve_min_m`, `head_valve_min_time_s`,
`pressure_head_max_global_m`, `pressure_head_max_global_x_m`, `pressure_head_max_global_time_s`,
`pressure_head_min_global_m`, `pressure_head_min_global_x_m`, `pressure_head_min_global_time_s`.

**Timbraje y límite de depresión**

| Campo | Unidad | Contenido |
|---|---|---|
| `pn_head_m` | m.c.a. | PN·10⁵/(ρ·g) |
| `pressure_max_pn_ratio_pct` | % | 100·`pressure_head_max_global_m`/`pn_head_m` |
| `min_allowed_pressure_head_m` | m.c.a. | eco del límite usado (el enviado o −10.0); la pantalla dibuja la línea con este valor, no con el formulario |

**Referencia teórica** (informativa: nunca genera aviso ni cambia `status`)

| Campo | Unidad | Contenido |
|---|---|---|
| `maneuver_type` | `"rapid"` \| `"slow"` | `rapid` si Tc ≤ 2L/a |
| `joukowsky_head_rise_m` | m | a·V₀/g |
| `michaud_head_rise_m` | m \| `null` | 2·L·V₀/(g·Tc); `null` si la maniobra es rápida |
| `full_pulse_length_m` | m \| `null` | L − a·Tc/2; `null` si la maniobra es lenta |
| `theoretical_head_rise_m` | m | Joukowsky si rápida, Michaud si lenta |
| `moc_head_rise_valve_m` | m | `head_valve_max_m` − H de régimen en la válvula |
| `theory_deviation_pct` | % | 100·(MOC − teórico)/teórico |

**Serie para el reproductor** (todos `null` con `include_frames: false`)

| Campo | Tipo | Unidad / notas |
|---|---|---|
| `frame_stride` | `int \| null` | pasos entre fotogramas consecutivos (1 = sin submuestreo); el último intervalo puede ser más corto |
| `frame_time_s` | `list[float] \| null` | s, precisión completa; cada valor es exactamente uno de `time_s`; el primero 0 y el último `duration_s`. Como mucho min(1001, ⌊50 000 / len(`x_m`)⌋) fotogramas |
| `frame_x_m` | `list[float] \| null` | m, 3 decimales; idéntica a `x_m` |
| `frame_head_m` | `list[list[float]] \| null` | m, 3 decimales; `[k][j]` = fotograma k, progresiva j |

No hay `frame_pressure_head_m` ni `frame_flow_lps`: la presión por fotograma la deriva la
pantalla (invariantes abajo) y el caudal en el tiempo está en `flow_valve_lps` y
`flow_reservoir_lps`.

### `Check`

| Campo | Tipo | Unidad / notas |
|---|---|---|
| `code` | `str` | uno de la tabla de abajo (estable) |
| `severity` | `"warning"` \| `"error"` | paleta del portal (D-13): `warning` → warning, `error` → danger |
| `message` | `str` | en español, con unidades y decimales con punto |
| `value_m` | `float` | m.c.a., valor que dispara el aviso (precisión completa) |
| `limit_m` | `float` | m.c.a., umbral cruzado |
| `x_m` | `float` | m, progresiva del valor (precisión completa; redondeada a 3 decimales está en `x_m`) |
| `time_s` | `float` | s, instante del valor (está en `time_s`) |
| `first_x_m`, `first_time_s`, `first_pressure_head_m` | `float \| null` | solo `COLUMN_SEPARATION_RISK`: primer cruce del límite (m, s, m.c.a.); `null` en los demás |

| `code` | Severidad | Condición (precisión completa) | `value_m` / `limit_m` / lugar |
|---|---|---|---|
| `PN_EXCEEDED` | `error` | p_max global > `pn_head_m` | p_max / `pn_head_m` / lugar del máximo global |
| `PN_NEAR_LIMIT` | `warning` | 80 % < p_max/PN ≤ 100 % | ídem |
| `COLUMN_SEPARATION_RISK` | `error` | p_min global < `min_allowed_pressure_head_m` | p_min / límite / lugar del mínimo global; `first_*` = primer cruce |
| `SUBATMOSPHERIC_PRESSURE` | `warning` | límite ≤ p_min global < 0 | p_min / 0 / lugar del mínimo global |
| `STEADY_NEGATIVE_PRESSURE` | `warning` o `error` | presión de régimen < 0 en algún x; `error` si además < límite | p mínima de régimen / 0 o límite / su x, t = 0 |

Orden: `error` antes que `warning`; dentro de cada severidad, el de la tabla. `status` `ok` →
`success`, `warning` → `warning`, `error` → `danger`; `caution` no se usa.

---

## Excepciones → HTTP

| Excepción | Status del portal | Cuándo ocurre |
|---|---|---|
| `MainpipeTransientValidationError` (hereda de `MainpipeTransientError` y `ValueError`) | 422 | Toda entrada inválida: tipos, rangos, reglas cruzadas, campo desconocido o retirado. Mensaje en español, ≤ 400 caracteres, con el punto que falla. `__cause__` = el `pydantic.ValidationError` |
| `MainpipeTransientComputationError` | 500 | Fallo interno no previsto (no debería ocurrir con entradas válidas). Mensaje genérico en español; la traza va al `__cause__` y al log |

No existe `MainpipeTransientServiceError`: el paquete no llama a servicios externos. Ninguna
otra excepción sale de `solve`. Cada clase lleva `http_status`, así que el router mapea con una
línea:

```python
except MainpipeTransientError as exc:
    raise HTTPException(status_code=exc.http_status, detail=str(exc))
# golden_cases.py, http_status_for:
lambda exc: exc.http_status if isinstance(exc, MainpipeTransientError) else None
```

---

## Contrato de respuesta

```
{
  schema_version, scenario, geometry, status,
  checks: [ { code, severity, message, value_m, limit_m, x_m, time_s,
              first_x_m, first_time_s, first_pressure_head_m } ],
  length_m, area_m2, velocity_initial_ms, head_loss_m, dx_m, dt_s, n_reaches, n_steps,
  duration_s, reflection_time_s, wave_period_s, closure_duration_s, friction_number,
  time_s[], head_valve_m[], head_midpoint_m[], pressure_head_valve_m[],
  pressure_head_midpoint_m[], flow_reservoir_lps[], flow_valve_lps[],          // n_steps + 1
  x_m[], x_is_node[], elevation_m[], head_initial_m[], pressure_head_initial_m[],
  head_max_m[], head_min_m[], pressure_head_max_m[], pressure_head_min_m[],    // len(x_m)
  head_valve_max_m, head_valve_max_time_s, head_valve_min_m, head_valve_min_time_s,
  pressure_head_max_global_m, pressure_head_max_global_x_m, pressure_head_max_global_time_s,
  pressure_head_min_global_m, pressure_head_min_global_x_m, pressure_head_min_global_time_s,
  pn_head_m, pressure_max_pn_ratio_pct, min_allowed_pressure_head_m,
  maneuver_type, joukowsky_head_rise_m, michaud_head_rise_m, full_pulse_length_m,
  theoretical_head_rise_m, moc_head_rise_valve_m, theory_deviation_pct,
  frame_stride, frame_time_s[], frame_x_m[], frame_head_m[][]                  // null sin frames
}
```

Campos que pueden venir `null`: `michaud_head_rise_m` (maniobra rápida), `full_pulse_length_m`
(maniobra lenta), `frame_stride`, `frame_time_s`, `frame_x_m`, `frame_head_m`
(`include_frames: false`), y en cada `Check` los tres `first_*` salvo en
`COLUMN_SEPARATION_RISK`.

### (b) Precisión y regla de comparación (U-39, D-63)

- **A 3 decimales** (redondeo del paquete al construir la respuesta, `round(x, 3)` de Python,
  sin `-0.0`): todas las listas en m, m.c.a. y L/s — las seis series temporales salvo `time_s`;
  `x_m`, `elevation_m`, `head_initial_m`, `pressure_head_initial_m`, `head_max_m`, `head_min_m`,
  `pressure_head_max_m`, `pressure_head_min_m`; `frame_x_m` y `frame_head_m`. Cada lista se
  redondea una sola vez desde la precisión completa (`pressure_head_valve_m` es r(H − z), no
  r(H) − r(z)). El router no debe transformar nada.
- **A precisión completa**: `time_s`, `frame_time_s` y **todos los escalares** (derivados,
  extremos con su progresiva y su instante, PN, eco del límite, referencia teórica) y **todos
  los campos de `checks`**. El cálculo, los extremos, el primer cruce y los `checks` usan
  precisión completa.
- **Una lista no se compara con igualdad estricta con un escalar.** O se redondea el escalar a
  3 decimales con la misma regla y la igualdad es exacta (p. ej. `head_max_m[-1]` ==
  `round(head_valve_max_m, 3)`), o se compara con tolerancia **0.0005 m** (en la práctica
  0.0005 m + 10⁻⁹ m).
- **Diferencia de listas redondeadas** (p. ej. `frame_head_m[k][j] − elevation_m[j]`): se aparta
  como mucho **0.001 m** (+ 10⁻⁹ m) de la lista redondeada equivalente.
- Igualdades que se conservan exactas entre listas (mismo valor → mismo redondeo):
  `head_valve_m[0]` == `head_initial_m[-1]`; `frame_head_m[k]` en x = L y x = L/2 ==
  `head_valve_m[i_k]` y `head_midpoint_m[i_k]`.
- **Progresivas escalares** (`checks[].x_m`, `first_x_m`, `pressure_head_*_global_x_m`): se
  localizan en `x_m` **redondeándolas a 3 decimales** (U-41). Los instantes escalares están en
  `time_s` tal cual.
- Una desigualdad lista-umbral (el tramo rojo) no es una igualdad: se evalúa tal cual y la
  gobierna la regla del rojo.

### (c) Regla del rojo en el gráfico de presiones (D-63 (3)-(4), D-60)

Cada umbral tiene **un único aviso que lo gobierna**: la línea del PN, `PN_EXCEEDED`; la línea de
la presión mínima admisible, `COLUMN_SEPARATION_RISK`. Ningún otro código da rojo:
`PN_NEAR_LIMIT` y `SUBATMOSPHERIC_PRESSURE` son `warning`, y `STEADY_NEGATIVE_PRESSURE` con
`error` siempre llega acompañado de `COLUMN_SEPARATION_RISK` (la envolvente incluye t = 0), cuyo
marcador es el que se dibuja.

1. **Marcador del cruce y extremo global en `--color-chart-critical` (obligatorio): se leen del
   aviso**, nunca de comparar una lista con el umbral. Si el aviso existe, el marcador va en
   (`x_m`, `value_m`) del aviso, instante `time_s`, y sustituye al marcador del extremo global de
   ese lado, que sin aviso va en `--color-chart-operating`. Esos campos son, por construcción, los
   mismos `float` que el extremo global: en `PN_EXCEEDED`, `value_m` =
   `pressure_head_max_global_m`, `x_m` = `pressure_head_max_global_x_m`, `time_s` =
   `pressure_head_max_global_time_s`, `limit_m` = `pn_head_m`; en `COLUMN_SEPARATION_RISK`, los
   del mínimo global y `limit_m` = `min_allowed_pressure_head_m`. El marcador no usa `first_*`
   (son para el mensaje y para «Ir a t»).
2. **Tramo coloreado (opcional)**: sobre las envolventes redondeadas — la progresiva j cumple si
   `pressure_head_max_m[j] > pn_head_m` o `pressure_head_min_m[j] < min_allowed_pressure_head_m`,
   desigualdades estrictas con el umbral sin redondear — **pero solo se dibuja si existe el aviso
   de ese umbral. Nunca hay rojo sin aviso.**
3. **Único desacuerdo admitido**: aviso y marcador **sin tramo** (ninguna j redondeada cumple).
   Solo ocurre si el extremo queda a ≤ 0.0005 m del umbral. La situación inversa (alguna j
   redondeada cumple sin aviso) solo ocurre en esa misma banda y la pantalla no la dibuja por (2).

El paquete prueba (V-13): aviso ⇔ cruce a precisión completa; campos del aviso = extremo global
sin redondear; toda discrepancia con las listas redondeadas cae en la banda de 0.0005 m.

### (d) Invariantes de la serie del reproductor (D-64 (3), U-42)

Con `include_frames: true`, contrato de Capa 1 probado en la suite del paquete (V-17):

1. **`frame_x_m` == `x_m`**, elemento a elemento (mismos `float`).
2. **p/γ(x_j, t_k) = `frame_head_m[k][j]` − `elevation_m[j]`**, con `elevation_m[j]` la misma
   cota con que el paquete calcula todos los `pressure_head_*`. La presión es H − z, sin otro
   término. Tolerancia garantizada frente al redondeo de la presión a precisión completa:
   **0.001 m + 10⁻⁹ m** (con magnitudes de proyecto).
3. **Fotograma k ↔ paso i_k**: i_k es el índice con `time_s[i_k] == frame_time_s[k]` (igualdad
   exacta). Vale i_k = k·`frame_stride` para todos los fotogramas **salvo el último**, que es
   siempre i = `n_steps`. Sin submuestreo (`frame_stride` = 1) también el último cumple
   i_k = k·`frame_stride`. En x = L y x = L/2, la presión derivada del fotograma k y
   `pressure_head_valve_m[i_k]` / `pressure_head_midpoint_m[i_k]` difieren como mucho
   0.001 m + 10⁻⁹ m (más estricto que los 0.0015 m del test del portal, D-64 (2)).

**Nota para el test de D-64 (2)**: indexar la serie de la válvula con k·`frame_stride` es exacto
en el fixture del Excel (sin submuestreo), pero con submuestreo el último fotograma no está ahí
(receta de tamaño: 69·145 = 10 005 ≠ 10 000, índice fuera de rango). La regla general es la del
invariante 3.

### (a) Tamaño de la respuesta y de la petición (D-57 (1)-(2), (10); D-65 (3)-(4))

Medido con `tools/measure_payload.py` **desde el paquete instalado en un venv limpio** (kit 04
§3). Unidades: 3,5 MB = 3 500 000 B; 64 KiB = 65 536 B. Se miden dos serializaciones de la
respuesta y cuenta la mayor: `json.dumps(out, ensure_ascii=False, allow_nan=False,
separators=(",", ":"))` (lo que emite `JSONResponse`) y
`SolveResponse.model_validate(out).model_dump_json()`; la petición, compacta.

| Medición | Bytes | Techo |
|---|---|---|
| Respuesta, receta realista (699 progresivas, 10 000 pasos, 70 fotogramas, `frame_stride` 145) | **964 274 B** | 3 500 000 B |
| Respuesta, peor caso del barrido (694 progresivas, 71 fotogramas, `frame_stride` 143) | **965 887 B** | 3 500 000 B |
| Respuesta, entrada adversaria de magnitud (699 progresivas, 10 000 pasos; 22.37 B por número) | **2 819 475 B** | 3 500 000 B |
| Cota analítica: 126 328 números × 25 B + 127 674 B de estructura | **3 285 874 B** | 3 500 000 B |
| Petición, receta realista con 17 cifras significativas (compacta: 19 311 B) | **19 919 B** | 65 536 B |
| Caso del Excel: respuesta con fotogramas / sin fotogramas / petición | 90 471 / 24 039 / 374 B | — |

Las dos serializaciones dan los mismos bytes en todas las mediciones.

**Receta realista** (U-34 (3), `worst_case_recipe()` en `tools/measure_payload.py`):
`geometry` = `profile`, perfil x_j = 1234.5·j/499 m (j = 0…499, 500 vértices, los 498 interiores
fuera de nodo), z_j = 62·sen(π·x_j/1234.5) − 0.01·x_j m; `inner_diameter_mm` = 287.3,
`wave_speed_ms` = 1100, `darcy_friction_factor` = 0.0173, `initial_flow_lps` = 87.654321,
`reservoir_level_m` = 60, `pn_bar` = 16; ley t_0 = 0, t_i = 50·(i/19)^1.3 s (i = 1…19),
Q_i = Q₀·(1 − (t_i/50)^0.7), Q_19 = 0; `n_reaches` = 200, `duration_s` = 56.113,
`include_frames` = true. El peor caso del barrido es la misma receta con 493 vértices interiores
en x_j = 1234.5·j/494 (el que cae en el nodo L/2, j = 247, se desplaza +10⁻⁴·L):
`case_with_stations(694)`.

**Receta adversaria de magnitud** (U-34 (3b), `adversarial_recipe()`): la geometría de la receta
realista escalada a L = 1.2345678901234567·10¹⁵⁰ m, x_j = L·j/499;
`reservoir_level_m` = 3.1415926535897932·10¹⁵⁰; z_j = 2.7182818284590452·10¹⁵⁰·sen(π·x_j/L + 0.3)
− 1.4142135623730951·10¹⁵⁰·x_j/L; `inner_diameter_mm` = 1000, `wave_speed_ms` =
1234.5678901234567, `darcy_friction_factor` = 0, `initial_flow_lps` = 1.6180339887498949·10¹⁵¹;
con Δt = (L/200)/a, Tc = 0.9599·9599·Δt, ley t_i = Tc·(i/19)^1.3, Q_i = Q₀·(1 − (t_i/Tc)^0.7),
Q_19 = 0; `n_reaches` = 200, `duration_s` = 9999.5·Δt, `pn_bar` = 16, `include_frames` = true.
Entrada admitida sin sentido físico: el redondeo a 3 decimales no acorta ningún número.

**Lectura** (D-65 (4)): el techo de 3 500 000 B vale **para toda entrada admitida** con las dos
mediciones en verde —receta realista y adversaria—, y así queda cerrado F5-01. La cota analítica
se publica como apoyo pero no sustituye a las mediciones. La guarda de D-57 (2) en
`backend/tests/` debe medir **exactamente estas dos recetas** (copiar las funciones de
`tools/measure_payload.py`, que no forman parte del paquete instalado). **Aviso**: producción corta
cuerpos > 4,5 MB (D-47) sin que el CI ni `TestClient` lo detecten; esa guarda es lo único que lo
vigila.

### (e) Cambios 1.0 → 2.0 (U-40, D-63, D-64)

`SCHEMA_VERSION` sube de `"1.0"` a `"2.0"` (cambio mayor). Una integración escrita contra la 1.0
debe cambiar:

| Cambio | 1.0 | 2.0 |
|---|---|---|
| Densidad y gravedad | `density_kgm3`, `gravity_ms2` en la entrada | **retirados**; ρ = 1000 kg/m³ y g = 9.81 m/s² fijas. Enviarlos da 422 con mensaje propio por campo: «density_kgm3: la densidad ya no es un dato de entrada; el cálculo usa ρ = 1000 kg/m³. Quite el campo de la petición.» (y el equivalente de `gravity_ms2`; ambos si llegan los dos). Otro campo desconocido sigue con el 422 genérico |
| Presión por fotograma | `frame_pressure_head_m` | **retirado**; p/γ = `frame_head_m[k][j]` − `elevation_m[j]` (invariantes arriba) |
| Precisión de las listas | sin redondeo | listas en m, m.c.a. y L/s a 3 decimales; tiempos, escalares y `checks` completos |
| Tope de fotogramas | min(1001, ⌊50 000/n⌋) con dos matrices | misma fórmula, una sola matriz (`frame_head_m`) |

Tipos, unidades y el resto de nombres no cambian. Ningún caso dorado de la 1.0 sigue valiendo:
los de `portal/examples/` son de la 2.0 y congelan los valores redondeados (D-63 (6)).

---

## Ejemplo mínimo

```python
from mainpipe_transient import solve, MainpipeTransientError

result = solve({
    "geometry": "horizontal", "length_m": 1000.0, "pipe_elevation_m": 0.0,
    "inner_diameter_mm": 300.0, "wave_speed_ms": 1000.0, "darcy_friction_factor": 0.02,
    "initial_flow_lps": 100.0, "reservoir_level_m": 100.0, "pn_bar": 25.0,
    "closure_time_s": [0.0, 0.5, 1.0, 1.5, 2.0, 5.0, 10.0, 20.0],
    "closure_flow_lps": [100.0, 50.0, 20.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    "n_reaches": 20, "duration_s": 20.0, "include_frames": True,
})
# result["status"]                      → "error"
# [c["code"] for c in result["checks"]] → ["COLUMN_SEPARATION_RISK", "PN_NEAR_LIMIT"]
# result["head_valve_max_m"]            → 242.76384038253607 (t = 2.0 s)
# result["pressure_head_min_global_m"]  → -37.89904017427625 (x = 1000.0 m, t = 4.0 s)
# result["head_valve_m"][:3]            → [93.199, 100.41, 107.621]
# len(result["frame_time_s"]), len(result["x_m"]) → 401, 21
```

---

## Request / Response examples

Los ejemplos completos están en `portal/examples/` (formato de `kit 04 §2`), generados con
`tools/make_examples.py` **llamando al paquete instalado** desde el commit registrado en cada
uno (`commit`, con las versiones de Python, numpy y pydantic en `generated_with`):

| `id` | Qué cubre | Resultado |
|---|---|---|
| `solve-excel-horizontal` | camino feliz horizontal, caso del Excel; único con fotogramas (401 × 21) | `error`: `COLUMN_SEPARATION_RISK`, `PN_NEAR_LIMIT` |
| `solve-perfil-loma` | camino feliz con perfil (loma de 40 m) | `error`: `COLUMN_SEPARATION_RISK`, `PN_NEAR_LIMIT` |
| `solve-sin-friccion-ok` | sin avisos | `ok` |
| `solve-subatmosferica-warning` | presión negativa sobre el límite | `warning`: `SUBATMOSPHERIC_PRESSURE` |
| `solve-pn-superado` | aviso que gobierna la línea del PN | `error`: `PN_EXCEEDED`, `SUBATMOSPHERIC_PRESSURE` |
| `solve-regimen-negativo` | régimen con presión bajo el límite (vértice fuera de nodo) | `error`: `COLUMN_SEPARATION_RISK`, `STEADY_NEGATIVE_PRESSURE` (error), `PN_NEAR_LIMIT` |
| `error-ley-no-creciente` | tiempos de la ley no crecientes | `MainpipeTransientValidationError` 422 |
| `error-ley-sin-cierre` | ley que no termina en Q = 0 | 422 |
| `error-perfil-no-creciente` | progresiva del perfil no creciente | 422 |
| `error-duracion-insuficiente` | `duration_s` < Tc + 2L/a | 422 |
| `error-tope-de-pasos` | más de 10 000 pasos (N = 200, 50.001 s) | 422 |
| `error-campo-retirado-densidad` | `density_kgm3` en la petición (migración 1.0 → 2.0) | 422 |

Petición y respuesta del caso más pequeño, `solve-sin-friccion-ok` (respuesta abreviada; la
completa en el ejemplo):

```json
{
  "geometry": "horizontal", "length_m": 1000.0, "pipe_elevation_m": 0.0,
  "inner_diameter_mm": 300.0, "wave_speed_ms": 1000.0, "darcy_friction_factor": 0.0,
  "initial_flow_lps": 100.0, "reservoir_level_m": 150.0, "pn_bar": 40.0,
  "closure_time_s": [0.0, 0.05], "closure_flow_lps": [100.0, 0.0],
  "n_reaches": 20, "duration_s": 5.0, "include_frames": false
}
```

```json
{
  "schema_version": "2.0", "scenario": "reservoir_pipe_valve", "geometry": "horizontal",
  "status": "ok", "checks": [],
  "length_m": 1000.0, "dx_m": 50.0, "dt_s": 0.05, "n_steps": 100, "duration_s": 5.0,
  "time_s": [0.0, 0.05, 0.1, 0.15000000000000002, "…"],
  "frame_stride": null, "frame_time_s": null, "frame_x_m": null, "frame_head_m": null
}
```

Nota sobre `REL_TOL = 1e-9` (`golden_lib.py`): con listas al milímetro, un valor a menos de
≈ 10⁻¹³ m de un empate de redondeo podría salir 1 mm distinto con otra versión de `numpy` y
romper esa tolerancia. Probabilidad del orden de 10⁻⁶ por caso dorado; si ocurre, el diagnóstico
es inmediato (un valor que difiere exactamente 0.001) y se trata como hallazgo de integración
(`kit 04 §4`).

> Estos ejemplos son la base de los casos dorados de `backend/tests/golden/mainpipe-transient.json`.

---

## Changelog de integración

| Fecha | Commit pineado | Qué cambió en el contrato | Acción tomada en el portal |
|---|---|---|---|
| — | (el de `portal/HANDOFF.md`) | Integración inicial, `SCHEMA_VERSION` `"2.0"` | — |
