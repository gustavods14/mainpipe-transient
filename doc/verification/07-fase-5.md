# Verificación — fase 5 rehecha (contrato 2.0 y serie para el reproductor)

| | |
|---|---|
| Fase | 5 — Contrato 2.0 y serie para el reproductor, rehecha tras la enmienda del 2026-11-15 (plan 01 §5, fila 5) |
| Commit verificado | `32a98fd21f36df9b66519e393dea8c920a4b6cac` (`git rev-parse HEAD`, árbol limpio) |
| Plan | `doc/plans/01-golpe-ariete-v1.md`, estado **congelado** (nueva G4, 2026-11-15, `SCHEMA_VERSION` = `"2.0"`) |
| Kit | Portal `C:\Dev\web_apps\doc\upstream-kit`, `KIT_VERSION` = `3.0.1`; `portal/HANDOFF.md` y el plan dicen `3.0.0`. La 3.0.1 es un *patch* que solo reescribe `kit 03 §3` (IA). Esta app no tiene IA (D-62), así que no afecta a esta fase. Adoptarla le toca a `hie-architect` (ya anotado en `HANDOFF.md`) |
| Verificador | `hie-verifier`, 2026-11-15. Sustituye a `06-fase-5.md` (contrato 1.0) para la fase 5 |

## Criterio de «hecho» de la fase (plan 01 §5, fila 5), literal

| Criterio | Resultado | Evidencia |
|---|---|---|
| (5.1) Una única función privada redondea a 3 decimales las listas de §1.4 al construir `SolveResponse`, partiendo de los arrays a precisión completa. `time_s`, `frame_time_s`, los escalares y todos los campos de `checks` quedan intactos | cumple | `[leído]` `_solve.py:221` `_rounded` (`round(v, 3) + 0.0`) es el único redondeo de listas en `src/`: grep de `round(` da solo esa línea y `schemas.py:81`, que es la T_max del mensaje y no una lista. Se aplica a las 16 listas de U-39 (1); `time_s` y `frame_time_s` usan `_floats`. `[medido]` 137 casos aleatorios válidos (99 submuestreados, 128 con avisos): todas las listas son iguales a su propio redondeo y ninguna lleva `-0.0` en el JSON. `pressure_head_valve_m` = r(H − z) en 401/401 pasos frente a mi MOC independiente con z = 3.14159265; r(H) − r(z) habría diferido en 158/401, así que el redondeo se hace una sola vez y desde la precisión completa (U-39 (5)) |
| Pruebas de las fases 1–4 que leen listas por `solve()` ajustadas a §6 (nota de tolerancias) | cumple | `[leído]` `test_contract.py` V-05 ± (0.0005 + 10⁻⁶), `test_profile.py` con `DIFF_TOL` o igualdad exacta (V-19), `test_checks.py` con `r3`. No queda ninguna tolerancia de 10⁻⁶ sobre listas de `solve()` comparadas con una referencia sin redondear |
| (5.2) `_constants.py`; `density_kgm3` y `gravity_ms2` fuera de `SolveRequest`, con su 422 propio; `SCHEMA_VERSION` = `"2.0"`; entrada de la 2.0 en `CHANGELOG.md` | cumple | `[medido]` venv limpio: `{density_kgm3: 1000}`, `{gravity_ms2: 9.81}` y los dos juntos (incluso con valores `"x"` / `null`) dan `MainpipeTransientValidationError` 422 con el texto literal de §1.3. Por `SolveRequest.model_validate`, que es lo que valida FastAPI, sale `Value error, density_kgm3: …` en español. Un campo desconocido (`density`) mantiene el 422 genérico de `extra="forbid"`. `SCHEMA_VERSION` = `"2.0"`. `[leído]` `CHANGELOG.md` § «Fase 5 rehecha — contrato 2.0» |
| (5.3) Solo `frame_head_m` y `frame_x_m`, sin `frame_pressure_head_m` ni `frame_flow_lps`; tope de U-10 (D-65 (1)); invariantes de D-64 (3) probados | cumple | `[leído]` `_frames.py`: `FRAME_CELL_BUDGET` = 50 000, `MAX_FRAMES` = 1001 y la fórmula de U-10 sin cambios. `[medido]` en los 137 casos aleatorios: `frame_x_m == x_m`; `time_s[i_k] == frame_time_s[k]` con i_k = k·`frame_stride`, salvo el último fotograma, que es `n_steps`; nº de fotogramas ≤ min(1001, ⌊50 000/n⌋) (≤ tope − 1 con submuestreo) y ≤ 50 000 celdas; primer fotograma 0 y último `duration_s`; presión derivada en x = L y L/2 frente a las series en i_k, y `head_* − elevation_m` frente a `pressure_head_*`, ≤ 0.001 m + 10⁻⁹ m. Cero incumplimientos |
| V-13 (regla del rojo de D-63) en verde | cumple | `[medido]` la suite pasa, incluidos `test_v13_red_rule` (14 casos + la receta de U-34) y los cuatro `test_v13_band_cases`. Además, de forma independiente: (a) aviso ⇔ cruce a precisión completa, (b) campos del aviso == extremo global sin redondear, (c) `STEADY` en `error` ⇒ `COLUMN_SEPARATION_RISK` y (d) desacuerdo solo dentro de la banda, en los 137 casos aleatorios, sin incumplimientos. También construí un caso en la banda por cada lado del límite (sin fricción, H_dep ≈ 136 m): P = −8.211071, límite −8.2110354 → aviso sin tramo; P = −8.210941, límite −8.2109704 → tramo sin aviso. El aviso sigue a la precisión completa |
| V-17 en verde | cumple | `[medido]` `tests/test_frames.py` en verde. Caso del Excel: `frame_head_m` en la válvula frente a la referencia del Excel, 4.99·10⁻⁴ m (≤ 0.0005 + 10⁻⁶). Resto, ver la fila de 5.3 |
| V-19 en verde, comprobado sobre la salida de `solve()` | cumple | `[medido]` `tests/test_precision.py` en verde. HU-4.2 crit. 4 (L = 100 m, a = 1500 m/s, N = 200), recalculado por mi cuenta: `n_steps` = 8 500, máx \|Δt_k − `dt_s`\| = 4.1·10⁻¹⁶ s, 244 fotogramas (`frame_stride` 35), todos en `time_s`, estrictamente crecientes, y el último = `duration_s`. Escalares a precisión completa: `pn_head_m` == 25·10⁵/(1000·9.81) bit a bit, y `head_loss_m` y `joukowsky_head_rise_m` == mi fórmula |
| V-18 (i) receta realista **y** entrada adversaria ≤ 3 500 000 B (la mayor de las dos serializaciones); adversaria ≥ 20 B/número | cumple | `[medido]` venv limpio, `python tools/measure_payload.py`: receta 964 274 B; barrido, 694 progresivas → **965 887 B**; adversaria **2 819 475 B** (`json.dumps` = `model_dump_json`), **22.37 B/número**; cota analítica 3 285 874 B. Ver F5R-01 |
| V-18 (ii) petición del peor caso ≤ 65 536 B | cumple | `[medido]` 19 919 B con 17 cifras (19 311 B compacta) |
| V-18 (iii) caso del Excel con y sin fotogramas | cumple | `[medido]` 90 471 B con fotogramas, 24 039 B sin ellos; petición 374 B. Receta sin fotogramas: 620 431 B |
| Las cifras en bytes de las dos recetas en `doc/DECISIONS.md` (U-34), en lugar de las de la 1.0 | cumple | `[leído]` U-34, «Medición de la fase 5 rehecha». `[medido]` las nueve cifras coinciden byte a byte con mi ejecución en el venv limpio |
| Si (i) no cumple, detener y abrir DR (U-34 (6)) | no aplica | las dos mediciones están por debajo del techo |
| Tiempo del peor caso con fotogramas < 0.8 s (V-16) | cumple | `[medido]` venv limpio, mediana de 5: **0.247 s** (U-38 anota 0.243 s) |
| HU-1.6 crit. 7 sin ρ ni g | cumple | `[leído]` las filas de ρ y g salen de la parametrización. `[medido]` en verde |

## Cómo se ejecutó

- **`.venv` del repo** `[medido]`: `.venv\Scripts\python -m pytest -q -p no:cacheprovider` →
  **412 passed in 13.62s** (pydantic 2.14.3, numpy 2.5.4, instalación editable desde `src/`).
- **Venv limpio** `[medido]`: `git clone` del repo a un directorio temporal fuera del repo y
  `git checkout 32a98fd`; `python -m venv` (Python 3.12.10);
  `pip install "pydantic==2.13.4" numpy pytest ./src32`, una instalación normal, no editable
  (numpy 2.5.5, pydantic 2.13.4 = pin del portal). `mainpipe_transient.__file__` apunta a
  `venv\Lib\site-packages\` y `SCHEMA_VERSION` = `2.0`. Desde el árbol clonado:
  `pytest -q -p no:cacheprovider` → **412 passed in 13.74s**; `python tools/measure_payload.py` →
  cifras de arriba, código de salida 0.
- Mis scripts (`verify_f5.py`, `verify_f5b.py` y `adv_variants.py`) están en el scratchpad del
  verificador, fuera del repositorio, y se ejecutaron contra el venv limpio.

## Comprobaciones independientes

1. **Fórmulas y fidelidad (M1–M12, V-05 por `solve()`)** `[medido]`: escribí un MOC propio a partir
   de §4 del plan (B = a/(gA), R = fΔx/(2gDA²), C⁺/C⁻ con fricción explícita, depósito con H fija y
   válvula con Q(t_{k+1}) de la ley). Frente a `tests/reference/excel_case.json`: H a 4.6·10⁻¹³ m y
   Q a 3.4·10⁻¹³ L/s. Frente a `solve()` (caso del Excel): desviación máxima de las listas respecto
   a la referencia, H_v 4.99·10⁻⁴, H_mid 4.99·10⁻⁴, Q_dep 4.97·10⁻⁴, H inicial 4.92·10⁻⁴,
   envolventes 5.00·10⁻⁴, todo ≤ 0.0005 + 10⁻⁶. Escalares: H_v máx = 242.76384038… en t = 2.0 s
   (2.8·10⁻¹⁴ frente a la referencia), H_v mín = −37.89904017… en t = 4.0 s, y `head_valve_m[0]` =
   93.199.
2. **Unidades de extremo a extremo** `[medido]`: L/s → m³/s (÷1000) a la entrada y m³/s → L/s (×1000)
   a la salida. `flow_valve_lps` frente a mi MOC: 1.4·10⁻¹⁴ L/s. mm → m en D: `head_loss_m`
   coincide bit a bit con f·(L/D)·V₀²/(2g). PN bar → m.c.a. con las constantes de U-40: bit a bit.
   La única constante g del cálculo es `_constants.GRAVITY_MS2`: un grep de `9.81` / `1000.0` en
   `src/` solo devuelve `_constants.py`, las conversiones de unidades y `description`.
3. **HU-1.5 crit. 3 (enmendado en la 2.0)** `[medido]`: horizontal con z = 3.14159265. `elevation_m`
   = r(z) en todas las progresivas, y \|`pressure_head_*_m` − (`head_*_m` − z)\| ≤ 0.000593 m
   ≤ 0.001 m + 10⁻⁹ m en los tres pares. Ver F5R-03.
4. **Entradas adversarias distintas de la receta** `[medido]`: ver F5R-01 y F5R-02.
5. **Conformidad con el kit** `[leído]`:
   - Layout `src/` y API pública de §1.1: `__init__.py` exporta solo lo que dice el plan
     (`kit 01 §2–3`).
   - `allow_inf_nan=False` en `SolveResponse` y en `Check`, y `null` documentado en `frame_*`
     (`§4`).
   - Sin `print`, disco, red, entorno ni estado global en `src/`, solo `logging` (`§6`).
   - Excepciones de `kit 02` sin cambios. El mensaje nuevo está en español, nombra el campo y dice
     qué hacer.
   - `portal/` no cambia en este commit (`git show --stat`), así que el punto 6 del encargo no
     aplica en esta fase.

## Hallazgos

| ID | Severidad | Archivo:línea | Qué está mal | Evidencia |
|---|---|---|---|---|
| F5R-01 | menor | `tools/measure_payload.py:118` (`adversarial_recipe`) | La receta adversaria publicada **no es la entrada de más bytes**. La misma receta desplazada a un datum negativo (H_dep y z − 9.8765432109876543·10¹⁵⁰) da más. No incumple ningún criterio de la fase: D-65 (3) pide una receta determinista con ≥ 20 B/número, y las dos mediciones quedan bajo el techo. Pero en la fase 6, `portal/INTEGRATION.md` no puede presentar 2 819 475 B como el máximo. La garantía «para toda entrada admitida» se apoya en la cota analítica (3 285 874 B), que mi variante respeta. Es el mismo fenómeno que F5-01 en la 1.0 | `[medido]` `adv_variants.py` en el venv limpio: publicada 2 819 475 B (22.37 B/n.º); datum negativo **2 844 325 B** (22.57 B/n.º), 126 033 hojas, 699 progresivas, 70 fotogramas; z × 10¹⁵⁰ (≈ 10³⁰⁰) 2 578 762 B. Las tres ≤ 3 285 874 B < 3 500 000 B |
| F5R-02 | menor (anterior a esta fase: está igual en `2c51470` y viene de la fase 2/4) | `src/mainpipe_transient/_solve.py:111-112` | Un `pn_bar` admitido (> 0) pero extremo hace que `pn_head_m` o `pressure_max_pn_ratio_pct` salgan `inf`. La respuesta falla al construirse y `solve` devuelve `MainpipeTransientComputationError` (500). Está bien envuelta, sin excepción ajena, pero `kit 02 §1` dice que esa clase «no debería ocurrir con entradas válidas», y el plan §1.6 atribuye la prevención de `NaN`/`inf` a U-03, que no cubre el PN. Con datos sin sentido físico | `[medido]` caso del Excel con `pn_bar` = 5·10⁻³²⁴ y 10⁻³²⁰ → 500 (`pressure_max_pn_ratio_pct` = inf); con 10³⁰⁴ y 1.7·10³⁰⁸ → 500 (`pn_head_m` = inf). Mismo efecto en la adversaria con `pn_bar` = 10⁻³⁰⁰. Comprobación: `solve({..., "pn_bar": 5e-324})` |
| F5R-03 | menor | `tests/` (falta el test) | HU-1.5 crit. 3, enmendado en la 2.0 (`elevation_m` = r(`pipe_elevation_m`) y \|`pressure_head_*_m` − (`head_*_m` − `pipe_elevation_m`)\| ≤ 0.001 m + 10⁻⁹ m), está en la lista de HU de la fase 5, pero ningún test lo ejerce por `solve()` con una cota horizontal no redonda. Los que hay usan z = 0 o z = 50, donde r(z) = z, o comparan con `elevation_m` y no con `pipe_elevation_m` | `[leído]` grep en `tests/`: el único `pipe_elevation_m` no redondo (`test_checks.py:81`) no comprueba este criterio. `[medido]` el código cumple: desviación 0.000593 m con z = 3.14159265 |
| F5R-04 | menor (del texto del plan, no del código) | `src/mainpipe_transient/schemas.py:45,49`; plan §1.3, l. 289-290 | Los dos mensajes de campo retirado tratan de usted («Quite el campo de la petición»), y el resto de mensajes del paquete tutea («revisa el nombre», «usa n_reaches…», «envía duration_s…», «acorta…», «informa del caso»). El código copia literalmente el texto del plan, así que corregirlo requiere enmendar el plan. `kit 02 §3` no fija el tratamiento | `[leído]` |

Sin hallazgos **bloqueantes** ni **mayores**.

## Lo que no comprobé

- Que FastAPI, en el portal, serialice el 422 del campo retirado tal cual (con el prefijo
  `Value error, `). Solo lo comprobé a través de `SolveRequest.model_validate`, que es lo que valida
  FastAPI. FastAPI no está instalado en el venv.
- Que la pantalla aplique la regla del rojo (tramo solo con aviso). Es del portal (V-13, último
  párrafo).
- Que la receta adversaria o mi variante sean el máximo absoluto en bytes. Solo comprobé que
  ninguna de las tres que medí supera la cota analítica (F5R-01).
- Los riesgos de empate de redondeo con otra versión de `numpy` en los casos dorados (plan §5, nota
  para el portal). No hay `portal/examples/` todavía: es de la fase 6.
- `portal/INTEGRATION.md`, `portal/examples/` y la checklist de `kit 04 §3`: son de la fase 6 y G5.
- Que mis 137 casos aleatorios incluyeran algún valor bruto en (−0.0005, 0) de una lista, que es
  donde aparecería `-0.0`. La ausencia de `-0.0` en esos casos sí está medida, y
  `test_rounding_helper_follows_u39_4` ejerce −0.0004 → 0.0.

## Veredicto

**Pasa**: sin hallazgos bloqueantes ni mayores. Quedan cuatro menores (F5R-01 … F5R-04) para que el
dueño los acepte o los corrija.

## Decisión del dueño sobre los menores (2026-11-15)

- **F5R-01 — aceptado.** En la fase 6, `portal/INTEGRATION.md` presenta 2 819 475 B como la medición
  de la receta adversaria publicada, no como el máximo, y la cota analítica de U-34 (3b)
  (3 285 874 B) como el techo para toda entrada admitida; cita también la variante con datum
  negativo (2 844 325 B).
- **F5R-02 — aceptado, para `hie-architect`.** Devolver un 422 exige acotar `pn_bar` en el contrato
  (enmienda del plan, `kit 01 §8`); no se corrige en `hie-api`. Mientras tanto, esas entradas sin
  sentido físico siguen dando `MainpipeTransientComputationError` (500), bien envuelta.
- **F5R-03 — corregido** tras `32a98fd`, sin cambios en `src/`:
  `tests/test_precision.py::test_hu15_crit3_horizontal_elevation_with_a_non_round_datum`
  (z = 3.14159265; `elevation_m` = r(z) y las cinco parejas `pressure_head_*` / `head_*` − z dentro
  de 0.001 m + 10⁻⁹ m). Suite: 413 en verde.
- **F5R-04 — aceptado.** El tratamiento de usted es literal del plan §1.3 (U-40); cambiarlo sería
  una enmienda del plan.
