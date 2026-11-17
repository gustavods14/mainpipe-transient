# Verificación: fase 7, tercera pasada (enmienda F5R-02, tras la corrección F7R-01)

| | |
|---|---|
| Fase | 7 (plan 01 §5, fila 7; Parte 1, «En qué orden», fila 7) |
| Commit verificado | `dea8a8f4d23d7938699ed0fb5579ca6288471c8c` (`git rev-parse HEAD`, árbol limpio, rama `main`) |
| Plan | `doc/plans/01-golpe-ariete-v1.md`, estado **congelado** (G4 del 2026-11-16, enmienda F5R-02, `SCHEMA_VERSION` = `"2.0"`) |
| Kit | Portal `C:\Dev\web_apps\doc\upstream-kit`, `KIT_VERSION` = `3.0.1`, el mismo que declaran el plan y `portal/HANDOFF.md` |
| Informes anteriores | `doc/verification/10-fase-7.md` (`1430873`, no pasa por F7-01); `doc/verification/11-fase-7.md` (`6720689`, no pasa por F7R-01) |
| Verificador | `hie-verifier`, 2026-11-16 |

## Entorno de ejecución

He creado un venv nuevo, `v7c`, con Python 3.12.10, fuera del repo, en el scratchpad de la sesión
(`C:\Users\gusta\AppData\Local\Temp\claude\f98149e085510c81\88d573fc-1065-4fcb-8218-d1be25ea03d4\scratchpad`).
Instalé el paquete desde el repositorio local, por commit, porque el commit no está en GitHub:
`pip install "git+file:///C:/Dev/MyApps/mainpipe_transient@dea8a8f…" "pydantic==2.13.4" pytest`.
Versiones: numpy 2.5.5, pydantic **2.13.4** (el pin del portal), pydantic_core 2.46.4, pytest 9.2.0.
Para comprobar que los tests nuevos detectan el defecto, usé también el venv `v7b` del informe 11
(commit `6720689`).

La suite corrió contra el paquete instalado. Un plugin de pytest escribió al terminar
`INSTALLED_FROM=…\scratchpad\v7c\Lib\site-packages\mainpipe_transient\__init__.py` `[medido]`.
Mis scripts están en `…\scratchpad\vc\`, fuera del repo: `check7.py`, `f7r01.py`, `fuzz7.py`,
`fuzzreal.py`, `t16c.py`, `tinyb_obs.py`, `common.py` y `wherec.py`. Todos se ejecutaron con
`python -I`.

## Qué cambia el commit

`git show --stat dea8a8f` `[medido]`: el commit toca `src/mainpipe_transient/_moc.py` (+8/−2),
`tests/test_amendment_f5r02.py` (+32), `doc/DECISIONS.md` (U-38) y añade el informe 11. No toca
`portal/`: `git diff e90e572 HEAD --stat -- portal` sale vacío `[medido]`, así que el punto 6 del
encargo no aplica.

En `_moc.py:66-71` `[leído]`, `derive()` calcula B = a/(g·A) y, si da `0.0`, lanza
`FloatingPointError`. Como `solve` captura `ArithmeticError` (`_solve.py:89-91`), eso sale como el
422 de U-44 (1). La fórmula de B no cambia: es M5. `derive()` solo se llama desde `simulate()`
(`_moc.py:228`, `grep`) `[leído]`, así que esta excepción no puede salir por otro camino sin
envolver.

## Criterio de «hecho» de la fase 7, punto por punto

| Criterio (plan §5, fila 7) | Resultado | Evidencia |
|---|---|---|
| V-12 en verde (rango del PN) | cumple | `[medido]` `vc/check7.py` en `v7c`. `pn_bar` = 1 y 100 calculan. `pn_head_m` sale 10.193679918450561 y 1019.367991845056, iguales con `==` a PN·10⁵/(1000·9.81), y 1019.37 ± 0.01. Los valores 100.5, 1e304, 0.5, 5e-324, 1e-320, 1e-300, 0 y −1 dan `MainpipeTransientValidationError` 422. En 100.5, 1e304, 0.5, 1e-300, 0 y −1, el texto es igual carácter a carácter al literal de §1.3, que copié del plan al script. En 5e-324 y 1e-320, el eco es «4.940656458e-324» y «9.999888672e-321» (U-26, 10 cifras) y el resto del texto coincide. Con 100.00000000001 y 0.99999999999 el valor sale con `repr`, y ningún mensaje dice «= 100 bar supera» ni «= 1 bar es menor». `SolveRequest.model_validate` da el mismo texto con el prefijo «Value error, » en los 10 casos. `description` = «Pipe pressure rating PN (bar). 1 <= PN <= 100.» |
| V-20 en verde | cumple | Ver «V-20, apartado por apartado» |
| HU-1.6 crits. 7 y 14 (a–d) con su test y el mensaje literal | cumple | Los tests existen `[leído]`: `test_amendment_f5r02.py:94` (14 a), `:119` (7, 14 b, 14 c), `:168` (14 d) y `test_contract.py:278-279` (crit. 7, PN). Están en verde `[medido]`. Para el 14 d («cualquier `pn_bar` admitido y cualquier otra entrada admitida → ningún 500»), el contraejemplo F7R-01 da ahora 422 y el fuzzing no encuentra ningún 500 (abajo) |
| Los 12 ejemplos de `portal/examples/`, idénticos a su `expected` sin regenerar | cumple | `[medido]` `vc/check7.py`: 12 de 12. En los 6 de éxito, la salida de `solve()` pasada por JSON es `==` a `expected`. En los 6 de error coinciden clase, `http_status` y `message`, y ninguno es el mensaje de U-44 |
| Suite completa en verde | cumple | `[medido]` `python -m pytest -q -p wherec tests` en `v7c`: **531 passed**. Con `-W error`: 531 passed. Con el `.venv` del repo (pydantic 2.14.3): 531 passed |
| Mediana de 5 ejecuciones del peor caso con fotogramas < 0.8 s (V-16), anotada en U-38 | cumple | `[medido]` `vc/t16c.py`, receta realista de U-34 (3) con fotogramas (699 progresivas, 10 000 pasos, 70 fotogramas): **mediana 0.234 s** (0.285, 0.231, 0.234, 0.228, 0.238). Con PN 1 y 100: 0.233 s y 0.233 s. Sin fotogramas: 0.227 s. Caso del Excel con fotogramas: 0.011 s. U-38 anota 0.240 s tras las correcciones `[leído]` |
| `SCHEMA_VERSION` sigue en `"2.0"` | cumple | `[medido]` `"2.0"`. `__version__` = 0.1.0; pasa a 0.2.0 en la fase 8 |
| Parte 1, fila 7: «con cualquier PN admitido no hay ningún "error del servidor" causado por los datos, ni con los casos absurdos de la báscula» | cumple, hasta donde se puede comprobar ejecutando | Las recetas de la báscula calculan con PN 1 y 100 (V-20 (a)). Fuzzing: 0 casos de 500 en 126 000 entradas (abajo). Que no exista ningún otro caso no se puede demostrar ejecutando (ver «Lo que no comprobé») |

### Cierre de los hallazgos del informe 11

| ID | Estado | Evidencia |
|---|---|---|
| F7R-01 | **cerrado** | `[medido]` `vc/f7r01.py` en `v7c`, con la entrada del informe 11: caso del Excel con `wave_speed_ms` = 1e-190, `inner_diameter_mm` = 1e73, `initial_flow_lps` = 1e143 (ley escalada) y `duration_s` = null. Probé 24 combinaciones: PN 1, 25 y 100; f = 0 y f = 1e-200; con y sin fotogramas; horizontal y perfil [0, 400, 1000] / [0, 30, 0]. Las 24 dan `MainpipeTransientValidationError` 422, con el mensaje literal de §1.6 y `__cause__` = `FloatingPointError`. Con la f = 0.02 por defecto, esa entrada ya la rechaza antes la regla de φ, con su propio 422. En el repo hay 5 casos nuevos en `OVERFLOW_CASES`, que dan 10 tests parametrizados. Esos 10 tests fallan contra `6720689` (`v7b`: «10 failed») y pasan contra `dea8a8f`, así que detectan el defecto `[medido]` |
| F7R-02 | **cerrado** | U-38 recoge ahora la medición de la receta adversaria (mediana 0.812 s) y que el dueño aceptó F7-04 el 2026-11-16 `[leído]` (`doc/DECISIONS.md`, fila U-38). Mi medición coincide: **0.801 s** de mediana (0.767–0.844 s) `[medido]` (`vc/t16c.py`). Está por debajo del 1 s del kit y V-16 no mide esta receta |

### V-20, apartado por apartado

- **(a) PN admitido**: cumple `[medido]`. Con `pn_bar` = 1 y 100 calculan el caso del Excel, la
  receta realista, la adversaria y la adversaria con datum negativo (las recetas son las de
  `tools/measure_payload.py`). `pn_head_m` y `pressure_max_pn_ratio_pct` son finitos; en la
  adversaria con PN 1, la razón es 5.536·10¹⁵¹ %.
- **(b) Resultado no representable → 422**: cumple `[medido]`. Los siete casos dan 422 con el mensaje
  literal de §1.6:
  - H_dep = 1e308 con PN 1, sin `__cause__`;
  - un perfil con cotas ±1e308, sin `__cause__`;
  - Q₀ = 1e158 L/s con f = 1e-200, con `__cause__` = `OverflowError`;
  - Q₀ = 5e-324 L/s, con `__cause__` = `ZeroDivisionError`;
  - tres variantes de F7R-01, con `__cause__` = `FloatingPointError`.
- **(c) La guarda no salta** con los 12 ejemplos ni con las recetas de (a): cumple `[medido]`.
  Además, en 6 000 entradas con valores de proyecto (`vc/fuzzreal.py`: a entre 100 y 1500 m/s,
  D entre 10 y 3000 mm, L entre 10 y 10⁵ m, H entre −1000 y 5000 m, perfiles de hasta 22
  vértices, PN en [1, 100]) hubo **0** casos del 422 de U-44: 5 942 calculan y 58 son 422 de
  validación.
- **(d) Un `NaN` sin desbordamiento sigue en 500**: cumple `[medido]`. Inyecté un `NaN` en
  `theory_deviation_pct` y salió `MainpipeTransientComputationError` 500. El test del repo
  `test_v20d_nan_without_overflow_is_still_500` está en verde.

Con avisos convertidos en errores (`warnings.simplefilter("error")`) y `np.seterr(all="raise")` en el
llamador, los siete casos de (b) dan el mismo 422, y `np.geterr()` queda como estaba `[medido]`.

### Búsqueda de otros 500 causados por la entrada

`vc/fuzz7.py` probó 120 000 entradas, 40 000 en cada uno de tres modos:

- **`tinyB`**: B = a/(g·A) entre 10⁻³³⁵ y 10⁻²⁸⁰, es decir, subnormal o cerca de serlo, con
  A ≤ 1.3·10¹⁵⁴ m²;
- **`wide`**: magnitudes log-uniformes en todo el rango de `float64`;
- **`near`**: el caso del Excel con campos sustituidos por valores extremos.

En los tres modos varié también el signo y la magnitud de las cotas, la geometría, N, la presencia de
fotogramas y el PN en [1, 100]. Resultado `[medido]`: **0** casos de 500, **0** excepciones ajenas
y 0 fallos del generador. Hubo 27 418 respuestas calculadas (10 618 de ellas con B subnormal),
33 293 casos del 422 de U-44 y 59 339 casos de 422 de validación. Añadiendo las 6 000 de
`fuzzreal.py`, son 126 000 entradas.

`[leído]` Dos razones por las que, con B > 0, no espero otro `NaN` sin ±inf:

- Las envolventes usan comparaciones estrictas (`_moc.py:332-347`). Un `NaN` no las cambia, y un
  ±inf de una progresiva sí queda registrado en ellas, así que la guarda lo ve.
- Las series de la válvula, el punto medio y el depósito guardan todos los pasos.

El único camino que veo hacia un `NaN` sin ±inf exige que el caudal desborde en un nodo interior,
que no se guarda. Eso pide |ΔH|/B > 1.8·10³⁰⁸. Con los topes del modelo (V₀ < 1.34·10¹⁵⁴ m/s,
porque si no `v0**2` lanza `OverflowError`; Q₀ ≤ 1.8·10³⁰⁵ m³/s; φ ≤ 0.5), las variaciones de H
están acotadas por B·Q y no llegan a ese valor. El fuzzing en `tinyB` es coherente con esto.

### Fórmulas y unidades

- M5: el commit no cambia la fórmula, B = a/(g·A) con g = 9.81 m/s² (`_moc.py:66`) `[leído]`. Lo único
  nuevo es comprobar B = 0. Como a > 0 y D > 0 por validación, B = 0 solo puede salir por
  subdesbordamiento.
- M18 y la razón al PN no cambian. Con PN 1 y 100, `pn_head_m` es igual bit a bit a PN·10⁵/(ρ·g)
  `[medido]`. El factor bar → m.c.a. lo ejerce `test_v12_limits_are_admitted`.
- Las conversiones L/s ↔ m³/s y mm ↔ m de `_solve.py:43-44, 98-114` no cambian `[leído]`. Las ejercen
  los 12 ejemplos, que salen idénticos `[medido]`.

### Conformidad con el kit

- `kit 01 §3`: la API pública es la de §1.1 y no cambia (`__init__.py`, `__all__`) `[leído]`.
- `kit 01 §4`: un `NaN` sigue haciendo fallar la respuesta por `allow_inf_nan=False`, y ese fallo se
  envuelve como `MainpipeTransientComputationError` `[medido]`.
- `kit 01 §5` y `kit 02 §1`: un resultado no representable da `MainpipeTransientValidationError` 422,
  con `raise … from exc` cuando hay causa. En 126 000 entradas no se escapó ninguna excepción ajena
  `[medido]`. El texto de `FloatingPointError` está en inglés, pero es interno: solo queda en
  `__cause__` y en el log, y el usuario ve el mensaje de §1.6 en español.
- `kit 01 §6`: `grep` en `src/` no encuentra `print(`, `open(`, `os.environ`, `getenv`, `global`,
  `warnings.` ni `np.seterr` (la única coincidencia es la palabra «Errors» en una `description`)
  `[leído]`. `np.errstate` restaura el estado `[medido]`.
- `kit 02 §3`: los mensajes del PN y de U-44 están en español y coinciden con los literales del plan
  `[medido]`.

## Hallazgos

No hay hallazgos bloqueantes, mayores ni menores en esta fase.

## Observaciones fuera del alcance de la fase (no son hallazgos)

- **Con B subnormal, el resultado es representable pero no tiene sentido físico.** `[medido]`
  `vc/tinyb_obs.py`: A = 10¹⁵⁰ m², a = 10⁻¹⁶⁰ m/s, V₀ = 1 m/s, f = 0, H_dep = 100 m, con lo que
  B = 1.02·10⁻³¹¹ s/m². `solve()` devuelve `status: ok`, pero `flow_reservoir_lps` cae de Q₀ a 0 en
  el primer paso, cuando debería seguir en Q₀ hasta t = L/a (paso 20). Es decir, V-07 (causalidad)
  no se cumple con esa entrada. La causa es que B·Q queda por debajo de la ulp de H. El plan no lo
  cubre: U-44 solo trata los valores no representables, y ningún criterio de la fase 7 lo pide. Se
  anota para que `hie-architect` decida si las entradas de magnitud absurda que calculan necesitan
  algún aviso. Cómo comprobarlo: con esa entrada, `flow_reservoir_lps[1]` debería ser Q₀.
- `portal/INTEGRATION.md` sigue diciendo `pn_bar` > 0 y no recoge el 422 de U-44. Está previsto: el
  plan lo deja para la fase 8.
- El mensaje del commit habla de «siete casos nuevos en V-20 (b)», pero `OVERFLOW_CASES` tiene 5
  entradas nuevas (10 tests parametrizados) `[leído]`. Afecta solo al mensaje del commit, no a un
  artefacto del repo.

## Lo que no comprobé

- La fase 8: regenerar `portal/examples/`, los tres ejemplos nuevos, `INTEGRATION.md`,
  `CHANGELOG.md`, `__version__` 0.2.0 y la etiqueta.
- La instalación desde GitHub: el commit no está publicado, así que instalé desde el repositorio local
  por commit.
- Que no exista ninguna otra entrada admitida que dé un 500. El fuzzing (126 000 entradas) y el
  análisis `[leído]` no encontraron ninguna, pero eso no lo demuestra.
- V-16 en un equipo distinto del del upstream: medí en el mismo equipo.
- No volví a verificar las fases 0–6. La suite completa está en verde y los 12 ejemplos salen
  idénticos, y este commit solo añade la comprobación de B = 0 en `derive()`.

## Veredicto

**Pasa**: no hay hallazgos bloqueantes ni mayores abiertos. F7R-01 y F7R-02 están cerrados, y
F7-01 a F7-03 ya lo estaban.
