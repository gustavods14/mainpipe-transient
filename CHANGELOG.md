# Changelog

Una entrada por cambio de contrato (`kit 01 §8`). `SCHEMA_VERSION` es la versión de la forma del
contrato; `__version__`, la del código.

## [0.1.0] — sin publicar

Contrato objetivo: `SCHEMA_VERSION = "2.0"` (plan `doc/plans/01-golpe-ariete-v1.md`, congelado de nuevo
en G4 el 2026-11-15 tras la enmienda; antes `"1.0"`). Las fases 0–4 se construyeron sobre la 1.0 y
siguen valiendo; la fase 5 se rehizo con la 2.0 (abajo).

### Fase 0 — andamiaje y referencia

- Paquete `mainpipe_transient` con layout `src/`, `py.typed` y dependencias `numpy>=1.24` y
  `pydantic>=2.6`.
- API pública: `solve` (provisional: siempre lanza `MainpipeTransientComputationError`),
  `__version__`, `SCHEMA_VERSION = "1.0"` y la jerarquía `MainpipeTransientError`,
  `MainpipeTransientValidationError` (422), `MainpipeTransientComputationError` (500).
  `SolveRequest`, `SolveResponse` y `Check` llegan en la fase 2.
- Referencia del Excel `tests/reference/excel_case.json` (U-28), generada una vez con
  `tools/extract_excel_reference.py`.

### Fase 1 — núcleo MOC horizontal

- Módulos privados `_closure` (ley de cierre, M11, U-18), `_geometry` (malla de Courant 1 solo con
  nodos, `n_steps` de U-08, duración por defecto) y `_moc` (régimen M3, bucle MOC M6–M10 con la
  fricción explícita de U-02, envolventes y extremos acumulados en el bucle, U-19, desempate U-25).
  Sin cambios en la API pública: `solve` sigue siendo provisional hasta la fase 2.

### Fase 2 — contrato y topes

- `schemas.py`: `SolveRequest` (`extra="forbid"`, sin `NaN`/`inf`), `SolveResponse`
  (`allow_inf_nan=False`) y `Check` con la forma completa del plan §1.3–§1.5. Se exportan desde
  `mainpipe_transient`.
- Validadores propios con mensajes en español (U-13) para HU-1.6 crit. 1–10 y 13, el número de
  fricción φ ≤ 0.5 (U-03) y el tope `MAX_STEPS` = 10 000 (U-09, D-57) con sus variantes: duración
  pedida, duración por defecto (no se recorta) y duración mínima fuera de tope. T_max se muestra
  truncada a 3 decimales y siempre calcula al reenviarla.
- `solve` real para geometría `horizontal`: valida, calcula y devuelve
  `SolveResponse(...).model_dump(mode="json")`. Un `pydantic.ValidationError` sale como
  `MainpipeTransientValidationError` (422); cualquier otra excepción, como
  `MainpipeTransientComputationError` (500) con mensaje genérico.
- `_format` (U-26) y `_theory` (M15–M17; su verificación V-11 es de la fase 4).
- Pendiente por fase: geometría `profile` (fase 3; hoy `solve` responde
  `MainpipeTransientComputationError`), `checks` (fase 4; hoy lista vacía y `status` = `ok`) y
  fotogramas (fase 5; hoy `frame_*` = `null`).
- Correcciones de la verificación (`doc/verification/03-fase-2.md`): las magnitudes extremas que
  desbordan en las reglas cruzadas salen como 422 y no como excepción ajena (F2-01); test de ρ y g
  en `pn_head_m` (F2-02); si la T_max mostrada queda por debajo de la duración mínima mostrada, el
  422 solo propone engrosar la malla (F2-03); mensajes de validación sin «or», posiciones de lista
  desde 1, magnitudes enormes en notación científica y como máximo 400 caracteres (F2-04).

### Fase 3 — perfil

- Geometría `profile`: L = última progresiva; z(x) lineal entre vértices (M13); `x_m` = nodos ∪
  vértices, ordenados, con fusión de un vértice a menos de 10⁻⁹·L de un nodo, que conserva la cota
  del vértice (U-07); `x_is_node` marca los nodos. En los vértices que no son nodo, H se interpola
  linealmente entre los nodos vecinos en cada paso y las envolventes y extremos se acumulan sobre
  todas las progresivas (M14, U-19); Q no se interpola (U-07, D-57). H y Q en los nodos no
  dependen de la cota.
- Validación del perfil con mensajes en español (HU-2.3 crit. 1–5): 2–500 puntos, misma longitud,
  empieza en x = 0 m, estrictamente creciente con el punto que falla, toma no más alta que el
  depósito, y datos de cada geometría; con `profile`, `length_m` y `pipe_elevation_m` son 422
  (U-22). Los topes de malla y duración (U-03, U-09) usan la L del perfil.
- Sin cambio de forma del contrato (`SCHEMA_VERSION` sigue en `"1.0"`).
- Menores de la verificación (`doc/verification/04-fase-3.md`): test con el extremo global de
  presión en un vértice fuera de nodo (F3-01); el mensaje de progresiva no creciente añade la
  posición desde 1, «x[3] = 120 m (punto 4)…» (F3-03). F3-02 (dos vértices fundidos en el mismo
  nodo) aceptado por el dueño.

### Fase 4 — verificaciones

- `_checks`: los cinco avisos del plan §1.5 con `code`, `severity`, mensaje en español y
  localización (`value_m`, `limit_m`, `x_m`, `time_s`). `PN_EXCEEDED` (p_max > PN en m.c.a.) y
  `PN_NEAR_LIMIT` (80 % < p_max/PN, U-16); `COLUMN_SEPARATION_RISK` (p_min < límite) y
  `SUBATMOSPHERIC_PRESSURE` (límite ≤ p_min < 0); `STEADY_NEGATIVE_PRESSURE` (presión de régimen
  < 0, `error` si además < límite). Orden: errores y después avisos, en el orden de la tabla.
  `status` = la severidad más alta, `ok` sin avisos (HU-3.5).
- Primer cruce del límite (`first_x_m`, `first_time_s`, `first_pressure_head_m`) acumulado dentro
  del bucle MOC desde t = 0 (U-19): primer paso con alguna progresiva bajo el límite y, entre
  ellas, la de menor presión y después la de menor x (U-25). El mensaje de
  `COLUMN_SEPARATION_RISK` da la presión, el lugar y el instante de ese primer cruce.
- Mensajes literales de HU-3.1 crit. 4 y HU-3.2 crit. 4 con el signo menos ASCII (U-26). Una
  depresión que redondea a cero se escribe `-0.0` para no contradecir el aviso.
- Verificación de `_theory` contra `4_Validacion` (V-11) y del predicado por progresiva de D-60
  (V-13). La comparación con Joukowsky / Michaud no genera avisos (HU-3.4).
- Sin cambio de forma del contrato (`SCHEMA_VERSION` sigue en `"1.0"`).
- Menores de la verificación (`doc/verification/05-fase-4.md`): las envolventes de presión se
  acumulan sobre p/γ = H − z con su propio paso, de modo que, si dos alturas que difieren en 1 ulp
  dan la misma presión, el extremo global publica el primer instante (U-25, F4-02); test de que una
  presión igual al límite no es cruce (F4-03). F4-01 (redondeo a 1 decimal de U-26 cerca del
  umbral: «-10.0 por debajo de -10.0», «100.0 %» sin superar el PN) aceptado por el dueño.
  Test del mismo empate en el mínimo global (F4-04).

### Fase 5 — serie para el reproductor (contrato 1.0, sustituida por la fase 5 rehecha)

- Fotogramas `frame_time_s`, `frame_x_m` (= `x_m`), `frame_head_m` y `frame_pressure_head_m`
  (`[k][j]`, U-11) y `frame_stride`, acumulados dentro del bucle MOC sin guardar la historia
  completa (U-19). Tope U-10 / D-57 (4): como mucho min(1001, ⌊50 000 / n_progresivas⌋)
  fotogramas; sin submuestreo si caben todos los pasos, si no paso s = ⌈n_steps / (tope − 2)⌉ y
  siempre el último paso. Valores sin redondear (D-57 (9)); p/γ = H − z con la misma operación
  que las envolventes. Sin `frame_flow_lps` (U-33).
- `include_frames: false` deja `frame_*` y `frame_stride` en `null` (U-24); el resto de la
  respuesta es idéntico con y sin fotogramas.
- `tools/measure_payload.py` (fuera del paquete): protocolo de U-34. Peor respuesta medida
  3 167 900 B ≤ 3 500 000 B; peor petición 19 919 B ≤ 65 536 B; caso del Excel 355 716 B con
  fotogramas y 48 149 B sin ellos. No se aplica la regla de ajuste de U-34. Cifras y receta en
  `doc/DECISIONS.md` (U-34); tiempo del peor caso con fotogramas, mediana 0.147 s (U-38, V-16).
- Sin cambio de forma del contrato (`SCHEMA_VERSION` sigue en `"1.0"`); solo se amplía la
  `description` de `frame_time_s` con el tope.

### Fase 5 rehecha — contrato 2.0 (enmienda del 2026-11-15; D-63 … D-66)

Cambio de forma del contrato: **`SCHEMA_VERSION` = `"2.0"`** (subida mayor, U-15). Rompe con la 1.0
en tres puntos:

- **Entrada** (U-40): `density_kgm3` y `gravity_ms2` salen de `SolveRequest`; el cálculo usa
  ρ = 1000 kg/m³ y g = 9.81 m/s², constantes privadas en `_constants.py`. Una petición que los
  envíe recibe 422 con un mensaje propio en español por campo, desde un
  `model_validator(mode="before")`, de modo que llega en español también a través de FastAPI;
  cualquier otro campo desconocido sigue con el 422 genérico (U-23). Las `description` de
  `pn_head_m`, `head_loss_m`, `joukowsky_head_rise_m` y `michaud_head_rise_m` citan las constantes.
- **Precisión** (U-39, D-63 (1)-(2)): todas las listas en m, m.c.a. y L/s (seis series, ocho
  columnas por progresiva, `frame_x_m` y `frame_head_m`) salen redondeadas a 3 decimales con una
  única función privada (`_solve._rounded`: `round(x, 3)` de Python, sin `-0.0`), aplicada una sola
  vez desde la precisión completa al construir la respuesta. `time_s`, `frame_time_s`, los
  escalares y todos los campos de `checks` salen completos. El cálculo, las envolventes, los
  extremos, el primer cruce y los `checks` no cambian.
- **Serie** (D-64, D-65, U-42): se retira `frame_pressure_head_m`; la presión del fotograma k en la
  progresiva j es `frame_head_m[k][j]` − `elevation_m[j]`. `frame_x_m` se mantiene, idéntico a
  `x_m`. Tope de fotogramas min(1001, ⌊50 000 / n_progresivas⌋) sin cambios: el presupuesto pasa a
  50 000 celdas en la única matriz (`FRAME_CELL_BUDGET`).
- Pruebas: invariantes de D-64 (3) (V-17) en el caso del Excel, un perfil genérico y la receta
  submuestreada; regla del rojo de D-63 (V-13) con cuatro casos construidos en la banda de
  ±0.0005 m; precisión de la serialización (V-19, `tests/test_precision.py`), con el caso de
  HU-4.2 crit. 4 (Δt = 1/3000 s). Las pruebas de las fases 1–4 que leían listas de `solve()` se
  ajustan a la nota de tolerancias del plan §6; el caso del empate F4-02 se rehízo con g = 9.81.
- `tools/measure_payload.py`: una sola matriz en el recuento y receta adversaria determinista de
  U-34 (3b). Medido (D-65 (3)-(4)): receta realista 964 274 B, peor del barrido 965 887 B;
  adversaria 2 819 475 B (22.37 B por número); cota analítica 3 285 874 B; petición 19 919 B; caso
  del Excel 90 471 B con fotogramas y 24 039 B sin ellos. Todo ≤ 3 500 000 B (y ≤ 65 536 B la
  petición): no se abre pedido (U-34 (6)). Peor caso con fotogramas, mediana 0.243 s (V-16).

### Fase 6 — entrega

- `tools/make_examples.py` (fuera del paquete): genera `portal/examples/*.json` llamando a
  `solve` del paquete importable, con el formato de `kit 04 §2` (`expected` = salida pasada por
  JSON; en error, clase concreta y `http_status`, con el mensaje aparte). Registra el commit del
  código y las versiones de Python, numpy y pydantic (`generated_with`). `--check` regenera en
  memoria y compara sin escribir. Sin `--commit`, se niega si `src/` difiere de `HEAD`.
- `portal/examples/`: 12 casos de la 2.0 — seis de éxito (`ok`, `warning`, `error`; horizontal y
  perfil; los cinco códigos de `checks`; solo el del Excel con fotogramas, D-57 (8)) y seis
  `MainpipeTransientValidationError` 422, entre ellos el de migración por `density_kgm3` (U-40).
  Generados desde el paquete instalado en un venv limpio de Python 3.12. Respecto a la lista del
  plan se añade `solve-pn-superado`, para que `PN_EXCEEDED` (el aviso que gobierna la línea del
  PN, D-63) tenga caso dorado.
- `tests/test_examples.py`: los ejemplos son exactamente los casos del script, tienen el formato
  de la plantilla, `solve()` los reproduce con `REL_TOL = 1e-9` (los de error, con la misma clase,
  status y mensaje), cubren lo que pide `kit 04 §2` y cada lista en m, m.c.a. y L/s de los casos
  de éxito es igual a su redondeo a 3 decimales (V-19 sobre los ejemplos, D-63 (6)).
- `portal/INTEGRATION.md` desde la plantilla del portal, leído del código: firmas, entrada,
  modelos, unidades, constantes ρ y g, excepciones, y lo que pide la fase 6 del plan — tamaño
  (cifras, dos recetas, cota y aviso de 4,5 MB), precisión y regla de comparación, regla del rojo,
  invariantes de la serie y cambios 1.0 → 2.0.
- Desde el paquete instalado en un venv limpio (Python 3.12.10, numpy 2.5.5, pydantic 2.14.3):
  suite en verde; ejemplos regenerados idénticos (también con numpy 2.5.4); mediciones de V-18
  iguales a las de la fase 5 (receta 964 274 B, barrido 965 887 B, adversaria 2 819 475 B,
  cota 3 285 874 B, petición 19 919 B; Excel 90 471 / 24 039 B); peor caso con fotogramas,
  mediana 0.243 s.
- Sin cambios en `src/`.
- Correcciones de la verificación (`doc/verification/08-fase-6.md`): el párrafo «Lectura» del
  tamaño en `portal/INTEGRATION.md` presenta 2 819 475 B como la medición de la receta adversaria
  publicada y no como el máximo, cita la variante con datum negativo (2 844 325 B), da la cota
  analítica (3 285 874 B) como techo para toda entrada admitida y recoge D-65 (4): D-57 (1) se
  cumple solo con la guarda del portal en verde (F6-02, condición de la aceptación de F5R-01).
  `tools/measure_payload.py` mide esa variante (`adversarial_negative_datum_recipe()`) y
  `test_v18_measured_sizes_fit_d57_d65` comprueba que pesa más que la publicada y no supera la
  cota. `make_examples.py --check` ignora `generated_with` y dice qué clave difiere (F6-03).
