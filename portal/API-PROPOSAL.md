# mainpipe-transient — Propuesta de Capa 2

> **Propuesta**, no contrato. La Capa 2 la fija `software-architect` del portal en
> `doc/apps/mainpipe-transient/API.md`. Convención vigente: `doc/upstream-kit/03-portal-api.md`.
> Contrato de Capa 1 en el que se apoya: `doc/plans/01-golpe-ariete-v1.md` §1 (kit 3.0.0,
> `SCHEMA_VERSION` propuesto `"1.0"`; G2 reabierta el 2026-11-14 para incorporar D-57 … D-62,
> pendiente de reaprobación; se congela en G4).
> 2026-11-14: actualizada con D-57 (sin `frame_flow_lps`, `MAX_STEPS` = 10 000, tamaños), D-60
> (eco `min_allowed_pressure_head_m`) y D-62 (sin IA).

## Endpoints

| Método | Ruta | Función del paquete | Request | Response | ¿Fuera de convención? |
|---|---|---|---|---|---|
| `POST` | `/api/mainpipe-transient/solve` | `solve` | `SolveRequest` | `SolveResponse` | no |

Todo endpoint con "sí" en la última columna tiene su `DR-N`.

No se propone ningún otro endpoint. La serie para el reproductor (F4) viaja en la misma respuesta
de `solve`, con el tamaño que fijó **D-57** (DR-2; el endpoint `/frames` quedó descartado). Router
delgado según `kit 03 §1`, sin redondear ni transformar la respuesta (D-57 (9)):

```python
from mainpipe_transient import solve, MainpipeTransientError
# ...
except MainpipeTransientError as exc:
    raise HTTPException(status_code=exc.http_status, detail=str(exc))
```

`http_status_for` de los casos dorados:
`lambda exc: exc.http_status if isinstance(exc, MainpipeTransientError) else None`.

Distribución en `backend/requirements.txt`:
`mainpipe-transient @ git+https://github.com/gustavods14/mainpipe-transient.git@<sha>`.

## Mapeo de errores

| Excepción | HTTP | Cuándo |
|---|---|---|
| `MainpipeTransientValidationError` | 422 | Entrada que no permite calcular: rangos (diámetro, celeridad ≤ 1500 m/s, f ≤ 0.1, g, PN, presión mínima admisible en [−10.33, 0]), ley de cierre mal formada (no empieza en 0 s, no creciente, primer caudal ≠ Q₀, caudal fuera de 0–Q₀, no termina en Q = 0), perfil mal formado (no empieza en 0 m, no creciente, toma sobre el depósito, 2–500 puntos), datos de geometría cruzados, `n_reaches` impar o fuera de 10–200, duración < Tc + 2L/a, más de 10 000 pasos de cálculo con la duración pedida o la de por defecto (D-57; el mensaje da la duración máxima admisible con esa malla, HU-1.6 crit. 13), número de fricción del tramo > 0.5. Por la validación de FastAPI estos casos llegan normalmente como el 422 del framework con el mensaje del validador en español (`kit 02 §3`); la excepción cubre las llamadas directas |
| `MainpipeTransientComputationError` | 500 | Fallo interno no previsto (incluido un `NaN` al construir la respuesta). No debería ocurrir con entradas válidas |
| `MainpipeTransientServiceError` | — | No existe: el paquete no llama a servicios externos |

Un resultado que calcula pero no cumple (PN superado, depresión, riesgo de separación de columna,
presión negativa en régimen) **no** es error: es `200` con `status` = `warning` / `error` y `checks`
(`kit 01 §5`).

## Ejemplo de llamada

Caso del Excel (tubería horizontal). Valores de la respuesta **ilustrativos**, abreviados con `…`;
los reales los genera `hie-api` ejecutando el paquete en `portal/examples/solve-excel-horizontal.json`.

```json
POST /api/mainpipe-transient/solve
{
  "scenario": "reservoir_pipe_valve",
  "geometry": "horizontal",
  "length_m": 1000,
  "pipe_elevation_m": 0,
  "inner_diameter_mm": 300,
  "wave_speed_ms": 1000,
  "darcy_friction_factor": 0.02,
  "initial_flow_lps": 100,
  "reservoir_level_m": 100,
  "density_kgm3": 1000,
  "gravity_ms2": 9.81,
  "pn_bar": 25,
  "min_allowed_pressure_head_m": -10,
  "closure_time_s": [0, 0.5, 1, 1.5, 2, 5, 10, 20],
  "closure_flow_lps": [100, 50, 20, 0, 0, 0, 0, 0],
  "n_reaches": 20,
  "duration_s": 20,
  "include_frames": true
}
```

```jsonc
200
{
  "schema_version": "1.0",
  "scenario": "reservoir_pipe_valve",
  "geometry": "horizontal",
  "status": "error",
  "checks": [
    { "code": "COLUMN_SEPARATION_RISK", "severity": "error",
      "message": "La presión cae a -37.9 m.c.a., por debajo del límite admisible de -10.0 m.c.a., por primera vez en x = … m y t = … s. A partir de ese instante puede haber separación de columna y los resultados del MOC simple dejan de ser físicos: las presiones y caudales posteriores no son fiables.",
      "value_m": -37.90, "limit_m": -10.0, "x_m": 1000, "time_s": 4.0,
      "first_x_m": …, "first_time_s": …, "first_pressure_head_m": … },
    { "code": "PN_NEAR_LIMIT", "severity": "warning", "message": "…",
      "value_m": 242.76, "limit_m": 254.84, "x_m": 1000, "time_s": 2.0,
      "first_x_m": null, "first_time_s": null, "first_pressure_head_m": null }
  ],
  "length_m": 1000, "area_m2": 0.0707, "velocity_initial_ms": 1.415, "head_loss_m": 6.80,
  "dx_m": 50, "dt_s": 0.05, "n_reaches": 20, "n_steps": 400, "duration_s": 20,
  "reflection_time_s": 2.0, "wave_period_s": 4.0, "closure_duration_s": 1.5, "friction_number": 0.0024,
  "time_s": [0, 0.05, …, 20],
  "head_valve_m": [93.2, …], "head_midpoint_m": [96.6, …],
  "pressure_head_valve_m": [93.2, …], "pressure_head_midpoint_m": [96.6, …],
  "flow_reservoir_lps": [100, …], "flow_valve_lps": [100, …],
  "x_m": [0, 50, …, 1000], "x_is_node": [true, …], "elevation_m": [0, …],
  "head_initial_m": [100, …, 93.2], "pressure_head_initial_m": [100, …, 93.2],
  "head_max_m": […], "head_min_m": […], "pressure_head_max_m": […], "pressure_head_min_m": […],
  "head_valve_max_m": 242.76, "head_valve_max_time_s": 2.0,
  "head_valve_min_m": -37.90, "head_valve_min_time_s": 4.0,
  "pressure_head_max_global_m": 242.76, "pressure_head_max_global_x_m": 1000, "pressure_head_max_global_time_s": 2.0,
  "pressure_head_min_global_m": -37.90, "pressure_head_min_global_x_m": 1000, "pressure_head_min_global_time_s": 4.0,
  "pn_head_m": 254.84, "pressure_max_pn_ratio_pct": 95.3, "min_allowed_pressure_head_m": -10.0,
  "maneuver_type": "rapid", "joukowsky_head_rise_m": 144.2, "michaud_head_rise_m": null,
  "full_pulse_length_m": 250, "theoretical_head_rise_m": 144.2,
  "moc_head_rise_valve_m": 149.56, "theory_deviation_pct": 3.71,
  "frame_stride": 1, "frame_time_s": [0, 0.05, …, 20], "frame_x_m": [0, 50, …, 1000],
  "frame_head_m": [[100, …, 93.2], …],
  "frame_pressure_head_m": [[100, …, 93.2], …]
}
```

La respuesta no tiene `frame_flow_lps` (D-57 (3)): el caudal en el tiempo está en
`flow_valve_lps` y `flow_reservoir_lps`. Con `"include_frames": false`, `frame_stride` y los
cuatro `frame_*` vienen `null`.

Con `"geometry": "profile"` se envían `profile_x_m` y `profile_z_m` en lugar de `length_m` y
`pipe_elevation_m`; `x_m` y `frame_x_m` incluyen entonces los vértices del perfil.

## Tamaño y tiempo de respuesta

Cotas de **D-57**: respuesta del peor caso ≤ 3,5 MB, fotogramas ≤ min(1001, ⌊50 000 /
n_progresivas⌋), `MAX_STEPS` = 10 000, sin `frame_flow_lps`, sin redondeo.

- Tiempo: < 1 s en el caso más grande admitido (N = 200, 500 vértices, 10 000 pasos), estimado
  ≈ 0.25–0.35 s y medido en el upstream en las fases 2 y 5 del plan (`kit 01 §6`). Sin necesidad de
  cambio en el backend.
- Respuesta, `[calculado]` (≈ 18–20 B por número): caso del Excel ≈ 0,35 MB con fotogramas y
  ≈ 60 kB sin ellos; peor caso ≈ 3,3 MB con fotogramas (series ≈ 1,3 MB + fotogramas ≈ 1,9 MB +
  envolventes ≈ 0,1 MB; 699 progresivas × 70 fotogramas) y ≈ 1,4 MB sin ellos.
- Petición del peor caso (perfil de 500 filas, ley de 20): ≈ 21–26 KB `[calculado]`, frente a los
  64 KiB de D-48.
- **Cifras medidas**: las dos de D-57 (1) y (10), en bytes y desde el paquete instalado, van a
  `portal/INTEGRATION.md` en la entrega, con la receta determinista de la entrada del peor caso
  para que la guarda de `backend/tests/` (D-57 (2)) mida la misma entrada (plan U-34).
- Casos dorados: solo `solve-excel-horizontal` lleva la serie; los demás, `include_frames: false`
  (D-57 (8)).

## Análisis de IA

No (D-62, resuelve DR-6): sin `aiDomain` en el registro de la app y sin sección `ai` en
`ui-spec.json`. Si se reabre, la Capa 1 no cambia: los campos de contexto ya están en la respuesta.
