# Verificación: fase 7 (enmienda F5R-02: rango del PN y resultados no representables)

| | |
|---|---|
| Fase | 7 (plan 01 §5, fila 7; Parte 1, «En qué orden», fila 7) |
| Commit verificado | `1430873e93901380548561cc9ae197d572646a8e` (`git rev-parse HEAD`, árbol limpio, rama `main`) |
| Plan | `doc/plans/01-golpe-ariete-v1.md`, estado **congelado** (G4 del 2026-11-16, enmienda F5R-02, `SCHEMA_VERSION` = `"2.0"`) |
| Kit | Portal `C:\Dev\web_apps\doc\upstream-kit`, `KIT_VERSION` = `3.0.1`, el mismo que declaran el plan y `portal/HANDOFF.md` |
| Verificador | `hie-verifier`, 2026-11-16 |

## Entornos de ejecución

Los dos venvs se crearon desde cero con Python 3.12.10, fuera del repo, en el scratchpad de la sesión.
El paquete se instaló desde el repositorio local por commit (el commit no está en GitHub):
`pip install "git+file:///C:/Dev/MyApps/mainpipe_transient@<sha>"`.

| venv | Commit | numpy | pydantic | Para qué |
|---|---|---|---|---|
| F7 | `1430873` | 2.5.5 | **2.13.4** (pin del portal) | todo lo de esta fase |
| V01 | `a04431e` (v0.1.0) | 2.5.5 | 2.13.4 | comparar con la entrega anterior (V-20 (b), F7-01, tiempos) |

La suite se ejecutó contra el paquete instalado en F7. Un plugin de pytest imprimió al terminar
`mainpipe_transient.__file__` = `…\venv7\Lib\site-packages\mainpipe_transient\__init__.py` `[medido]`.
Los scripts de comprobación están en el scratchpad (`scripts/v12.py`, `v20b.py`, `fuzz.py`, `fuzz2.py`,
`hb.py`, `f701.py`, `ex.py`, `t16.py`, `warn.py`), fuera del repo.

## Criterio de «hecho» de la fase 7, punto por punto

| Criterio (plan §5, fila 7) | Resultado | Evidencia |
|---|---|---|
| V-12 en verde (rango del PN) | cumple | `[medido]` `scripts/v12.py` en F7: `pn_bar` = 1 y 100 calculan; `pn_head_m` = 10.193679918450561 y 1019.367991845056, iguales con `==` a PN·10⁵/(1000·9.81); 1019.37 ± 0.01. 100.5, 1e304, 0.5, 5e-324, 1e-320, 1e-300, 0, −1, −0.0, 150, ±1e308 dan `MainpipeTransientValidationError` 422. Los textos de 100.5, 0.5, 0 y −1 coinciden carácter a carácter con los literales de §1.3, escritos a mano en el script a partir del plan. `nextafter(100, ∞)` → «pn_bar = 100.00000000000001 bar…», 100.00000000001 → `repr`, 0.99999999999 → `repr`; nunca «= 100 bar supera» ni «= 1 bar es menor». El mismo texto, con el prefijo «Value error, », sale de `SolveRequest.model_validate` (lo que ve FastAPI) en todos los casos. `description` = «Pipe pressure rating PN (bar). 1 <= PN <= 100.» |
| V-20 en verde | cumple en los casos que enumera V-20 | Ver abajo y F7-01 |
| HU-1.6 crits. 7 y 14 (a–d) con su test y el mensaje literal | **no cumple el 14 d** | Tests presentes (`tests/test_amendment_f5r02.py`, `tests/test_contract.py::test_hu16_crit7_…`) `[leído]` y en verde `[medido]`. El crit. 14 d («cualquier `pn_bar` admitido y cualquier otra entrada admitida → no 500») tiene un contraejemplo medido: F7-01 |
| Los 12 ejemplos de `portal/examples/` idénticos a su `expected` sin regenerar | cumple | `[medido]` `scripts/ex.py` en F7: 12 de 12 `True` (éxito: salida de `solve()` pasada por JSON `==` `expected`; error: clase, `http_status` y `message` iguales). `git diff a04431e 1430873 -- portal/examples` vacío |
| Suite completa en verde | cumple | `[medido]` `python -m pytest -q tests` en F7: **507 passed, 11 warnings** (los 11 avisos son `RuntimeWarning` de numpy en los casos de desbordamiento). Ídem con `.venv` del repo (pydantic 2.14.3): 507 passed |
| Mediana de 5 del peor caso con fotogramas < 0.8 s (V-16), anotada en U-38 | cumple | `[medido]` `scripts/t16.py`, receta realista de U-34 (3) con fotogramas: 0.230, 0.244, 0.229, 0.241, 0.249 s → **mediana 0.241 s** (en otra tanda, 0.274 s). U-38 anota 0.247 s `[leído]`. Ver F7-04 sobre la receta adversaria |
| `SCHEMA_VERSION` sigue en `"2.0"` | cumple | `[medido]` `mainpipe_transient.SCHEMA_VERSION` = `"2.0"` en F7. `__version__` = 0.1.0 (sube a 0.2.0 en la fase 8, no aquí) |
| Parte 1, fila 7: «con cualquier PN admitido no hay ningún "error del servidor" causado por los datos, ni con los casos absurdos de la báscula» | **no cumple** | Las recetas de la báscula sí (V-20 (a)). Con «cualquier PN admitido» hay un 500 causado por los datos: F7-01 |

### V-20, apartado por apartado

- **(a) PN admitido** — cumple. `[medido]` `scripts/t16.py`: con `pn_bar` = 1 y = 100, las recetas realista,
  adversaria y adversaria con datum negativo calculan; `pn_head_m` y `pressure_max_pn_ratio_pct` son
  finitos. El caso del Excel con 1 y 100, en `scripts/v12.py`.
- **(b) No representable → 422** — cumple. `[medido]` `scripts/v20b.py`, misma entrada en V01 y en F7:

  | Entrada | v0.1.0 (V01) | fase 7 (F7) |
  |---|---|---|
  | Excel, `pn_bar` = 1, `reservoir_level_m` = 1e308 | 500, causa `ValidationError` (inf en `Check`) | 422, mensaje de §1.6, sin `__cause__` |
  | Excel, H_dep = 1e308, `pipe_elevation_m` = −1e308 | 500 | 422, sin `__cause__` |
  | Q₀ = 1e158 L/s con f = 1e-200 | 500, causa `OverflowError` | 422, `__cause__` = `OverflowError` |
  | Q₀ = 5e-324 L/s | 500, causa `ZeroDivisionError` | 422, `__cause__` = `ZeroDivisionError` |

  La sustitución de f = 0.02 por f = 1e-200 en el caso de V₀² está justificada: con f = 0.02 la entrada
  ya era 422 en v0.1.0 por la regla de φ (U-03) `[medido]`, así que no reproducía el 500. La anotación
  que pide V-20 (b) está en el docstring del test `[leído]`.
- **(c) La guarda no salta** con los 12 ejemplos ni con las recetas de (a) — cumple (`[medido]`, los
  12 ejemplos idénticos y las recetas sin excepción).
- **(d) `NaN` sin desbordamiento sigue en 500** — cumple por los tests con `NaN` inyectado en un escalar
  y en una serie (`test_v20d_nan_without_overflow_is_still_500`) `[leído]` y `[medido]` (en verde).

### Fórmulas y unidades

- M18: `pn_head_m` = PN·10⁵/(ρ·g), ρ = 1000 kg/m³ y g = 9.81 m/s² de `_constants.py`; la razón,
  100·p_max/`pn_head_m`. Sin cambio respecto a v0.1.0 `[leído]` y bit a bit con `==` `[medido]`.
- Rango [1, 100] bar → `pn_head_m` ∈ [10.19, 1019.37] m.c.a. `[medido]` en los dos extremos.
- Conversión bar → m.c.a. (factor 10⁵/(ρ·g)) ejercida por `test_v12_limits_are_admitted` a rel. 10⁻¹²
  `[leído]` y por mi script con igualdad exacta `[medido]`.

### Conformidad con el kit

- `kit 01 §3`: la API pública no cambia; `solve` valida, calcula y devuelve `model_dump(mode="json")`;
  `pydantic.ValidationError` envuelto `[leído]`.
- `kit 01 §5` / `kit 02 §1`: el resultado no representable es `MainpipeTransientValidationError`
  (422), con `raise … from exc` cuando hay causa; la clase concreta es la de §1.6 `[medido]`.
- `kit 02 §3`: los dos mensajes del PN, en español, con unidad, valor y límite, y viajan en el 422 de
  FastAPI `[medido]`. El mensaje de U-44 es literal al de §1.6 (lo compara el test y mi script)
  `[medido]`.
- `kit 01 §6`: sin `print`, disco, red ni variables de entorno en `src/` (búsqueda de `print(`,
  `open(`, `os.environ`, `global`) `[leído]`; el `logger.info` del 422 usa el logger del paquete.
  Ver F7-02 sobre los `RuntimeWarning` de numpy.
- La fase no toca `portal/` (`git show --stat 1430873`) `[medido]`: el punto 6 del encargo no aplica.

## Hallazgos

| ID | Severidad | Archivo:línea | Qué está mal | Evidencia |
|---|---|---|---|---|
| F7-01 | **mayor** | `src/mainpipe_transient/_solve.py:125-126` (extremos globales antes de la llamada a la guarda en `:197`); `src/mainpipe_transient/_moc.py:183-185`; `src/mainpipe_transient/_geometry.py:89` | **Queda un 500 causado por los datos con un PN admitido**, contra HU-1.6 crit. 14 d, U-44 (1) y (6) y el «cómo sabremos» de la fase 7 en la Parte 1. Con fricción nula (f = 0, admitida) y una longitud tal que L·(N−1) desborda `float64`, las progresivas de los nodos salen `inf` (`x = L * arange / N`), la línea piezométrica de régimen sale `NaN` en esas progresivas (0·inf) y la envolvente de presiones también. `_compute` llama a `pressure_head_max_global()` **antes** de `_ensure_representable`; con la envolvente en `NaN`, `np.flatnonzero(envelope == value)` queda vacío y `min()` lanza `ValueError`, que no es `ArithmeticError`, así que sale `MainpipeTransientComputationError` (500). La guarda habría dado 422: `x_m` va a la respuesta con `+inf` (U-44 (1) pide 422 si **algún** valor de la respuesta es ±inf), pero nunca llega a ejecutarse. Ya ocurría en v0.1.0; la fase 7 no lo cubre. V-20 (b) no lo detecta porque solo prueba las cuatro entradas que enumera | `[medido]` `scripts/f701.py`, en F7 y en V01, mismo resultado. Caso del Excel con `darcy_friction_factor` = 0 y `length_m` = 1e307 (N = 20, con o sin fotogramas, `pn_bar` = 1, 25 o 100) → `MainpipeTransientComputationError` 500, `__cause__` = `ValueError('min() iterable argument is empty')`. También con N = 200 y `length_m` = 1e306, y con perfil `profile_x_m` = [0, 5e306, 1e307]. Con `length_m` = 9e306 y N = 20 calcula (L·19 < 1.8e308). `[medido]` `scripts/sim.py`: `station_x_m` = [0, 5e305, …, inf, inf, 1e307]; `head_initial_m`, `pressure_max_m` y `pressure_min_m` con 2 `NaN` y 0 `inf`; `head_valve_m` con 400 `NaN`. Fuzzing de 2 000 entradas extremas con PN admitido (`scripts/fuzz.py`): 2 casos con 500, los dos de esta causa; con L ≤ 1e305 (`scripts/fuzz2.py`, 3 600 entradas) y en la búsqueda dirigida de desbordamientos de H (`scripts/hb.py`, 4 104 entradas), ningún 500. Cómo comprobarlo: `solve()` del caso del Excel con `darcy_friction_factor = 0.0`, `length_m = 1e307` y `pn_bar` en [1, 100] no debe lanzar `MainpipeTransientComputationError` |
| F7-02 | menor | `src/mainpipe_transient/_solve.py:85-90` | El 422 de U-44 depende de la configuración de avisos del proceso anfitrión. Las operaciones de numpy que desbordan emiten `RuntimeWarning`; con un filtro `warnings.simplefilter("error")` (o `pytest -W error`) ese aviso se lanza como excepción, no es `ArithmeticError`, y la misma entrada sale como 500. Con la configuración por defecto, cada 422 de este tipo deja además 2–3 `RuntimeWarning` en el `stderr` del backend. El backend del portal no tiene hoy `filterwarnings` = error (búsqueda en `backend/` sin resultados), así que no rompe nada ahora | `[medido]` `scripts/warn.py`, caso Excel con `pn_bar` = 1 y H_dep = 1e308: por defecto, 422 y 3 avisos («overflow encountered in add», «invalid value encountered in subtract»); con `simplefilter("error")`, `MainpipeTransientComputationError` 500, `__cause__` = `RuntimeWarning('overflow encountered in add')`. `[medido]` `pytest tests/test_amendment_f5r02.py -W error::RuntimeWarning`: 2 fallos (`pn_ratio_overflow`, `opposite_elevations`) |
| F7-03 | menor | `tests/test_amendment_f5r02.py:315` (`test_the_twelve_examples_of_v010_are_all_here`) | El test exige que `portal/examples/` tenga exactamente 12 archivos. La fase 8 añade tres (plan §5, fila 8), así que el test fallará en cuanto se regeneren los ejemplos, aunque los 12 de v0.1.0 sigan idénticos, que es lo que la fase 8 pide comprobar. El test fija el número de archivos y no los 12 identificadores | `[leído]` `assert len(EXAMPLES) == 12`, con `EXAMPLES` = todos los `*.json` de `portal/examples/` |
| F7-04 | menor | — (no es de esta fase) | La receta adversaria de U-34 (3b), que es una entrada admitida con el mismo tamaño de malla que el peor caso, tarda una mediana de **0.87–0.89 s** con fotogramas: por encima del objetivo interno de 0.8 s (plan §2) y por debajo de 1 s (`kit 01 §6`). No es una regresión de la fase 7 (v0.1.0 da 0.865 s en el mismo equipo) y V-16 define el peor caso como la receta realista (0.24–0.27 s). Se anota porque U-38 y los informes de fase 6 no registran el tiempo de la adversaria | `[medido]` `scripts/t16.py`: adversaria 0.811, 0.876, 0.916, 0.890, 0.970 s (mediana 0.890 s); con datum negativo, mediana 0.808 s; en V01, 0.865 y 0.859 s |

## Observaciones fuera del alcance de la fase (no son hallazgos)

- `portal/INTEGRATION.md` sigue diciendo `pn_bar` > 0 y no recoge el 422 de U-44. Es lo previsto: el
  plan lo pone en la fase 8.
- `pn_bar: true` se admite como 1.0 (modo laxo de Pydantic para `bool` → `float`), igual que en v0.1.0
  y en todos los campos `float` `[medido]`. Queda dentro del rango y no produce ningún 500.

## Lo que no comprobé

- La regeneración de `portal/examples/`, `INTEGRATION.md`, `CHANGELOG.md`, `__version__` 0.2.0 y la
  etiqueta: son de la fase 8.
- La instalación desde GitHub: el commit `1430873` no está publicado; instalé desde el repositorio
  local por commit.
- V-16 en un equipo distinto del del upstream (medí en el mismo equipo).
- Que no haya otras causas de `NaN` sin `inf` en la salida además de la de F7-01: el fuzzing no
  encontró ninguna, pero no lo demuestra.
- Las fases 0–6 no se reverificaron. La suite completa en verde y los 12 ejemplos idénticos
  muestran que la fase 7 no cambia sus números.

## Veredicto

**No pasa**: F7-01 (mayor) sigue abierto. Con un PN admitido aún hay un 500 causado por los datos
(f = 0 y L ≳ 9.5·10³⁰⁶ m con N = 20), contra HU-1.6 crit. 14 d y U-44 (1).
