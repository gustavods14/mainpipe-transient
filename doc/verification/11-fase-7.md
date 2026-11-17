# Verificación: fase 7, segunda pasada (enmienda F5R-02, tras las correcciones F7-01 a F7-03)

| | |
|---|---|
| Fase | 7 (plan 01 §5, fila 7; Parte 1, «En qué orden», fila 7) |
| Commit verificado | `67206894b83f4c9abfe9eb26e34bd8f2e65c0a62` (`git rev-parse HEAD`, árbol limpio, rama `main`) |
| Plan | `doc/plans/01-golpe-ariete-v1.md`, estado **congelado** (G4 del 2026-11-16, enmienda F5R-02, `SCHEMA_VERSION` = `"2.0"`) |
| Kit | Portal `C:\Dev\web_apps\doc\upstream-kit`, `KIT_VERSION` = `3.0.1`, el mismo que declaran el plan y `portal/HANDOFF.md` |
| Informe anterior | `doc/verification/10-fase-7.md` (commit `1430873`, «no pasa» por F7-01) |
| Verificador | `hie-verifier`, 2026-11-16 |

## Entornos de ejecución

Tres venvs nuevos con Python 3.12.10, fuera del repo, en el scratchpad de la sesión
(`C:\Users\gusta\AppData\Local\Temp\claude\f98149e085510c81\88d573fc-1065-4fcb-8218-d1be25ea03d4\scratchpad`).
Instalación desde el repositorio local por commit (los commits no están en GitHub):
`pip install "git+file:///C:/Dev/MyApps/mainpipe_transient@<sha>" "pydantic==2.13.4"`.

| venv | Commit | numpy | pydantic | Para qué |
|---|---|---|---|---|
| `v7b` | `6720689` | 2.5.5 | **2.13.4** (pin del portal) | todo lo de esta fase |
| `v743` | `1430873` | 2.5.5 | 2.13.4 | comparar con la primera pasada (F7R-01, tiempos) |
| `v010` | `a04431e` (v0.1.0) | 2.5.5 | 2.13.4 | comprobar si F7R-01 es anterior a la fase |

La suite corrió contra el paquete instalado: un plugin de pytest imprimió al terminar
`mainpipe_transient.__file__` = `…\scratchpad\v7b\Lib\site-packages\mainpipe_transient\__init__.py` `[medido]`.
Mis scripts están en `…\scratchpad\scripts\` (`ex.py`, `v7.py`, `fuzz.py`, `fuzz2.py`, `fuzz3.py`,
`bzero.py`, `bzero2.py`, `t16.py`, `t16b.py`, `prof.py`), fuera del repo.

## Qué cambia el commit

`git show --stat 6720689` `[medido]`: `src/mainpipe_transient/_solve.py`, `tests/test_amendment_f5r02.py`
y el informe 10. No toca `portal/` (`git diff e90e572 HEAD --stat -- portal` vacío `[medido]`), así que
el punto 6 del encargo no aplica. `_solve.py` `[leído]`: la búsqueda de ±inf se parte en dos pasadas,
una con las listas (`:148`) antes de buscar los extremos globales (`:150-155`) y otra con los escalares
y los campos de `checks` (`:206`); el cálculo corre dentro de `np.errstate(... "ignore")` (`:84`).

## Criterio de «hecho» de la fase 7, punto por punto

| Criterio (plan §5, fila 7) | Resultado | Evidencia |
|---|---|---|
| V-12 en verde (rango del PN) | cumple | `[medido]` `scripts/v7.py` en `v7b`: `pn_bar` = 1 y 100 calculan; `pn_head_m` = 10.193679918450561 y 1019.367991845056, iguales con `==` a PN·10⁵/(1000·9.81). 100.5, 1e304, 0.5, 5e-324, 1e-320, 1e-300, 0 y −1 dan `MainpipeTransientValidationError` 422. Para 100.5, 1e304, 0.5, 5e-324, 1e-300, 0 y −1, el texto coincide carácter a carácter con el literal de §1.3, que escribí a mano en el script (con 1e-320, «9.999888672e-321», que es el eco de U-26). 100.00000000001, 0.99999999999 y `nextafter(100, ∞)` escriben `repr`; ninguno dice «= 100 bar supera» ni «= 1 bar es menor». `SolveRequest.model_validate` da el mismo texto con el prefijo «Value error, » en todos los casos |
| V-20 en verde | cumple en los casos que enumera V-20 | Ver abajo |
| HU-1.6 crits. 7 y 14 (a–d) con su test y el mensaje literal | **no cumple el 14 d** | Los tests existen y están en verde `[medido]`. El crit. 14 d («cualquier `pn_bar` admitido y cualquier otra entrada admitida → ningún 500») tiene un contraejemplo medido nuevo: F7R-01. El de F7-01 está corregido |
| Los 12 ejemplos de `portal/examples/`, idénticos a su `expected` sin regenerar | cumple | `[medido]` `scripts/ex.py` en `v7b`: 12 de 12 (éxito: `json` de `solve()` `==` `expected`; error: clase, `http_status` y `message` de nivel superior iguales). `git diff a04431e HEAD -- portal/examples` vacío |
| Suite completa en verde | cumple | `[medido]` `python -m pytest -q -p whereplug tests` en `v7b`: **521 passed**. Con `-W error`: 521 passed. Con `.venv` del repo (pydantic 2.14.3): 521 passed |
| Mediana de 5 del peor caso con fotogramas < 0.8 s (V-16), anotada en U-38 | cumple | `[medido]` `scripts/t16.py` y `t16b.py`, receta realista de U-34 (3) con fotogramas (699 progresivas, 10 000 pasos, 70 fotogramas): medianas 0.256, 0.244 y 0.241 s con PN 16. Con PN 1 y 100 salieron 0.349 y 0.409 s, en una tanda con ruido. U-38 anota 0.247 s `[leído]`. Ver F7R-02 sobre la receta adversaria |
| `SCHEMA_VERSION` sigue en `"2.0"` | cumple | `[medido]` `mainpipe_transient.SCHEMA_VERSION` = `"2.0"`; `__version__` = 0.1.0 (pasa a 0.2.0 en la fase 8) |
| Parte 1, fila 7: «con cualquier PN admitido no hay ningún "error del servidor" causado por los datos, ni con los casos absurdos de la báscula» | **no cumple** | Las recetas de la báscula, sí. Con cualquier PN admitido queda un 500 causado por los datos: F7R-01 |

### Cierre de los hallazgos del informe 10

| ID | Estado | Evidencia |
|---|---|---|
| F7-01 | **cerrado** | `[medido]` `scripts/v7.py` en `v7b`: caso del Excel con f = 0 y `length_m` = 1e307, con PN 1, 25 y 100 y con y sin fotogramas → 422 con el mensaje literal de §1.6, sin `__cause__`. También N = 200 con L = 1e306, N = 20 con L = 9.5e306, y el perfil [0, 5e306, 1e307] → 422. Los casos límite que no desbordan calculan sin error: N = 20 con L = 9.4e306, N = 10 con L = 1.7e307, N = 50 con L = 3.6e306 y N = 200 con L = 8.95e305. En el repo, `tests/test_amendment_f5r02.py` añade estos casos a `OVERFLOW_CASES` `[leído]` |
| F7-02 | **cerrado** | `[medido]` `scripts/v7.py`: los 24 casos de desbordamiento dan el mismo 422 con `warnings.simplefilter("error")` y emiten 0 avisos con `"always"`. `np.geterr()` del llamador queda restaurado tras la llamada, también si el llamador tenía `np.seterr(all="raise")` (en ese modo la respuesta también es el 422). La suite pasa con `-W error` (521). En el repo, `test_v20b_422_does_not_depend_on_the_caller_warning_filters` lo comprueba `[leído]` |
| F7-03 | **cerrado** | `[leído]` `test_the_twelve_examples_of_v010_are_all_here` compara los 12 identificadores de v0.1.0 por nombre, y `EXAMPLES` solo carga esos 12 |
| F7-04 | aceptado por el dueño, según el mensaje del commit `6720689`. Ese registro solo está en el mensaje del commit | Ver F7R-02 |

### V-20, apartado por apartado

- **(a) PN admitido**: cumple. `[medido]` `scripts/t16.py`: con `pn_bar` = 1 y 100, las recetas realista,
  adversaria y adversaria con datum negativo calculan, y `pn_head_m` y `pressure_max_pn_ratio_pct` son
  finitos. El caso del Excel con 1 y 100 se comprueba en `scripts/v7.py`.
- **(b) No representable → 422**: cumple. `[medido]` `scripts/v7.py`: H_dep = 1e308 con PN 1 → 422 sin
  `__cause__`; cotas opuestas ±1e308 → 422 sin `__cause__`; Q₀ = 1e158 L/s con f = 1e-200 → 422 con
  `__cause__` = `OverflowError`; Q₀ = 5e-324 L/s → 422 con `__cause__` = `ZeroDivisionError`. En los cuatro,
  el mensaje es el literal de §1.6.
- **(c) La guarda no salta** con los 12 ejemplos ni con las recetas de (a): cumple `[medido]`.
- **(d) Un `NaN` sin desbordamiento sigue en 500**: cumple, por `test_v20d_nan_without_overflow_is_still_500`
  (escalar y serie), en verde `[medido]`.

### Fórmulas y unidades

- M18: `pn_head_m` = PN·10⁵/(ρ·g), con ρ = 1000 kg/m³ y g = 9.81 m/s²; la razón es 100·p_max/`pn_head_m`.
  Sin cambio en este commit `[leído]`. Bit a bit con `==` en PN 1 y 100 `[medido]`.
- Conversión bar → m.c.a. (10⁵/(ρ·g)): la ejercen `test_v12_limits_are_admitted` `[leído]` y mi script
  (igualdad exacta) `[medido]`.
- El commit no toca ninguna fórmula del MOC ni de la teoría: el diff de `src/` solo reordena la guarda y
  añade `np.errstate` `[leído]`. Los 12 ejemplos idénticos lo confirman `[medido]`.

### Conformidad con el kit

- `kit 01 §3`: la API pública no cambia `[leído]`.
- `kit 01 §4`: `allow_inf_nan=False` sigue haciendo fallar un `NaN` al construir la respuesta, y ese fallo
  sale envuelto como `MainpipeTransientComputationError` `[medido]` (F7R-01 lo muestra).
- `kit 01 §5` / `kit 02 §1`: un resultado no representable es `MainpipeTransientValidationError` (422), con
  `raise … from exc` cuando hay causa `[medido]`. Ninguna excepción ajena se escapa: en 34 000 entradas de
  fuzzing, 0 casos de la categoría `foreign` `[medido]`.
- `kit 01 §6`: no hay `print`, `open`, `os.environ`, `getenv`, `global` ni `warnings.` en `src/`
  (`grep`) `[leído]`. `np.errstate` es un gestor de contexto que restaura el estado al salir, también
  tras una excepción (`np.geterr()` igual antes y después) `[medido]`: no deja estado global mutado.
- `kit 02 §3`: los mensajes del PN y de U-44 están en español y coinciden con los literales del plan
  `[medido]`.

## Hallazgos

| ID | Severidad | Archivo:línea | Qué está mal | Evidencia |
|---|---|---|---|---|
| F7R-01 | **mayor** | `src/mainpipe_transient/_moc.py:70` (B = a/(g·A)), `:296` y `:299` (divisiones por `two_b` y por `b`); `src/mainpipe_transient/_solve.py:84` (`errstate` en `ignore`) y `:236-245` (la guarda solo busca ±inf) | **Queda un 500 causado por los datos con un PN admitido**, contra HU-1.6 crit. 14 d, U-44 (6) y el «cómo sabremos» de la fase 7 en la Parte 1. Con una celeridad diminuta y un diámetro enorme, ambos admitidos (0 < a ≤ 1500 y D > 0), la constante B = a/(g·A) subdesborda a 0.0. El bucle del MOC divide entonces por cero en numpy: `(cp − cm)/two_b` y `(h_dep − cm[0])/b` dan 0/0 = `NaN`, sin `ZeroDivisionError` (es aritmética de numpy y el `errstate` la silencia) y sin ningún ±inf. Las series de H y Q y los extremos en la válvula salen `NaN`. Las dos pasadas de la guarda no ven ningún infinito, y `SolveResponse` falla con `allow_inf_nan=False` → `MainpipeTransientComputationError` (500). Es el mismo mecanismo que U-44 (1) da como causa de 422 («`ZeroDivisionError` por un valor que subdesborda a 0»), pero en una división de numpy, que no lanza la excepción. Además contradice la premisa de U-44 (3) («sin desbordamiento, un `NaN` solo puede venir de un fallo del paquete»): aquí el `NaN` viene de un subdesbordamiento provocado por la entrada. Ya ocurría en v0.1.0 y en `1430873`, así que no es una regresión de este commit. Hace falta a < ≈3·10⁻¹⁶⁹ m/s (porque A ≤ 1.3·10¹⁵⁴ m², si no `area**2` lanza `OverflowError` → 422), y Joukowsky debe ser distinto de 0 (si es 0, la desviación teórica lanza `ZeroDivisionError` → 422). Decidir si el defecto está en el código o en la premisa del plan corresponde a `hie-architect` con el dueño | `[medido]` `scripts/bzero2.py` en `v7b`: caso del Excel con `wave_speed_ms` = 1e-190, `inner_diameter_mm` = 1e73, `initial_flow_lps` = 1e143 (la ley de cierre escalada a ese Q₀) y `duration_s` = null (A = 7.85·10¹³⁹ m², B = 0.0, V₀ = 1.27 m/s, Joukowsky = 1.3·10⁻¹⁹¹ m). Da `MainpipeTransientComputationError` 500 con `__cause__` = `pydantic.ValidationError` (`finite_number`), con `pn_bar` = 1, 25 y 100, con y sin fotogramas, con f = 0 y f = 1e-200 (φ ≤ 0.5), y con perfil [0, 400, 1000] / [0, 30, 0]: 13 de 13. Espiando `_ensure_representable`: 1.ª pasada, 0 inf y 9 976 `NaN` en las listas; 2.ª pasada, 0 inf y 4 escalares `NaN`. Mismo resultado en `v743` (`1430873`) y en `v010` (v0.1.0: 500, causa `ValidationError`). Encontrado por fuzzing (`scripts/fuzz.py` y `fuzz2.py`, 4 × 1 500 + 6 × 5 000 entradas extremas): 2 casos de 500, los dos con B = 0.0. Con `scripts/fuzz3.py` (6 × 3 000 perturbaciones de 1 a 4 campos del caso del Excel), 0 casos de 500. Cómo comprobarlo: `solve()` de la entrada anterior con cualquier `pn_bar` en [1, 100] no debe lanzar `MainpipeTransientComputationError` |
| F7R-02 | menor | — (no es de esta fase) | La receta adversaria de U-34 (3b), una entrada admitida con el tamaño de malla del peor caso, ha tardado hoy una mediana de **1.15–1.42 s** con fotogramas, por encima del objetivo de 1 s de `kit 01 §6`. El informe 10 midió 0.87–0.89 s (F7-04). No es una regresión de este commit: en la misma tanda, alternando, `1430873` da 1.23–1.25 s. El kit fija el objetivo para «un caso típico» y V-16 mide la receta realista, que cumple (0.24–0.26 s), así que no incumple ninguna regla. Se anota por dos motivos: la cifra registrada para F7-04 ya no describe el equipo, y la aceptación del dueño solo consta en el mensaje del commit `6720689`, en ningún artefacto del repo (`doc/DECISIONS.md`, `portal/HANDOFF.md`) | `[medido]` `scripts/t16.py`: adversaria con PN 16, 1 y 100 → medianas 1.306, 1.249 y 1.421 s; con datum negativo → 1.185, 1.398 y 1.408 s. `scripts/t16b.py`, alternando `v7b` y `v743`: 1.153 / 1.228 / 1.259 / 1.250 s. `scripts/prof.py` (cProfile, una ejecución, 0.86 s): el 67 % del tiempo es `round` de Python sobre ≈ 115 000 valores de magnitud enorme (U-39 (4)). `grep F7-04` en los `*.md` del repo (sin contar el informe 10): sin resultados |

## Observaciones fuera del alcance de la fase (no son hallazgos)

- `portal/INTEGRATION.md` sigue diciendo `pn_bar` > 0 y no recoge el 422 de U-44. Es lo previsto: el plan
  lo deja para la fase 8.
- Con `np.seterr(all="raise")` en el llamador, los desbordamientos dan el mismo 422 que antes del commit:
  ahora la guarda los detecta por el valor ±inf, y antes se detectaban por el `FloatingPointError` `[medido]`.

## Lo que no comprobé

- La fase 8: la regeneración de `portal/examples/`, los tres ejemplos nuevos, `INTEGRATION.md`,
  `CHANGELOG.md`, `__version__` 0.2.0 y la etiqueta.
- La instalación desde GitHub: los commits no están publicados, así que instalé desde el repositorio local
  por commit.
- V-16 en un equipo distinto del del upstream: medí en el mismo equipo, con ruido entre tandas.
- Que no haya más causas de `NaN` sin ±inf aparte de la de F7R-01. El análisis del código `[leído]`
  descarta B = inf (A tendría que estar por debajo de 8.5·10⁻³⁰⁷ m² y por encima de 2.2·10⁻¹⁶² m² a la
  vez) y un desbordamiento de `r·Q·|Q|` (lo acota φ ≤ 0.5). El fuzzing no encontró otras causas, pero eso
  no demuestra que no existan.
- Las fases 0–6 no se reverificaron. Con la suite completa en verde y los 12 ejemplos idénticos, este
  commit no cambia sus números.

## Veredicto

**No pasa**: F7R-01 (mayor) está abierto. Con un PN admitido aún hay un 500 causado por los datos:
B = a/(g·A) subdesborda a 0, y el `NaN` resultante no lleva ningún ±inf. Va contra HU-1.6 crit. 14 d y
U-44 (6). F7-01, F7-02 y F7-03 están cerrados.
