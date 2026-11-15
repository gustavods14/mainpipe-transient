# Verificación — fase 5 (serie para el reproductor)

| | |
|---|---|
| Fase | 5 — Serie para el reproductor (plan 01 §5) |
| Commit verificado | `2c51470c69e5d27e8c6119e4ecd688a51e756b2c` |
| Plan | `doc/plans/01-golpe-ariete-v1.md`, estado **congelado** (G4, 2026-11-14) |
| Kit | `3.0.0` (portal `C:\Dev\web_apps\doc\upstream-kit`); `portal/HANDOFF.md` dice `3.0.0`: coinciden |
| Verificador | `hie-verifier`, 2026-11-15 |

## Criterio de «hecho» de la fase (plan 01 §5, fila 5), literal

| Criterio | Resultado | Evidencia |
|---|---|---|
| V-17 en verde | cumple | `[medido]` `tests/test_frames.py` en verde en el `.venv` del repo y en un venv limpio (abajo). Además, comprobación independiente de todas las progresivas (abajo, punto 2) |
| (i) respuesta del peor caso con `include_frames: true` ≤ 3 500 000 B, la mayor de las dos serializaciones de U-34 | cumple con la receta de U-34 | `[medido]` venv limpio, `python tools/measure_payload.py`: receta 3 156 607 B (`json.dumps` compacto = `model_dump_json`); barrido, 694 progresivas → **3 167 900 B**. Ver F5-01 sobre qué es «el peor caso» |
| (ii) petición del peor caso ≤ 65 536 B | cumple | `[medido]` 19 919 B con 17 cifras (19 311 B compacta) |
| (iii) caso del Excel con y sin fotogramas | cumple | `[medido]` 355 716 B con fotogramas, 48 149 B sin ellos, petición 374 B |
| Cifras en bytes y entrada usada en `doc/DECISIONS.md` (U-34) | cumple | `[leído]` U-34 lleva la receta, el barrido y las ocho cifras; `[medido]` las ocho coinciden byte a byte con mi ejecución en el venv limpio |
| Si (i) no cumple, regla de U-34 (6) | no aplica | 3 167 900 B ≤ 3 500 000 B |
| Tiempo del peor caso con fotogramas < 0.8 s (V-16) | cumple | `[medido]` venv limpio, mediana de 5 por `solve()`: **0.215 s** (U-38 anota 0.147 s en el equipo del upstream con pydantic 2.14.3) |

## Cómo se ejecutó

- **`.venv` del repo** `[medido]`: `.venv\Scripts\python -m pytest -q` → **376 passed in 17.97s**
  (pydantic 2.14.3, numpy 2.5.4, paquete importado de `src/`).
- **Venv limpio** `[medido]`: `git archive 2c51470` a un directorio temporal fuera del repo,
  `py -3.12 -m venv` (Python 3.12.10), `pip install ./tree "pydantic==2.13.4" pytest` (instalación
  normal, no editable). `mainpipe_transient.__file__` y `find_spec("mainpipe_transient._frames")`
  apuntan a `venv\Lib\site-packages\` (el módulo nuevo entró en la distribución). Desde el árbol
  extraído: `pytest -q -p no:cacheprovider` → **376 passed in 15.44s**; `python tools/measure_payload.py`
  → cifras de la tabla de arriba.
- Mis scripts de comprobación (`indep.py`, `adversarial.py`, `adversarial2.py`) están en el directorio
  temporal del verificador, fuera del repositorio, y se ejecutaron contra el venv limpio.

## Comprobaciones independientes

1. **Tope y paso de U-10** `[medido]`: reimplementé la fórmula desde el texto de U-10
   (n_max = min(1001, ⌊50 000/n⌋); s = 1 si `n_steps` + 1 ≤ n_max, si no ⌈`n_steps`/(n_max − 2)⌉;
   k = 0, s, 2s, … < `n_steps` y el último) y la comparé con `_frames.plan_frames` para cada
   n_progresivas ∈ [11, 699] y `n_steps` ∈ {1, 2, 3, n_max − 2, n_max − 1, n_max, n_max + 1, 2·n_max,
   4321, 9999, 10 000}: **7 579 combinaciones, 0 discrepancias**, siempre n_fotogramas ≤ n_max y
   2·n_fotogramas·n ≤ 100 000. Peor caso del plan §1.4 (699, 10 000) → s = 145, 70 fotogramas
   (k = 0 … 9 860 y 10 000): coincide. El `raise` de `cap < 3` es inalcanzable: con el contrato hay
   como mucho 699 progresivas (201 nodos + 498 vértices), n_max ≥ 71 `[leído]`.
2. **Valores de los fotogramas en todas las progresivas** `[medido]`: los tests comparan solo las
   columnas de válvula, punto medio y depósito. Reconstruí H en todos los nodos con el `observer` de
   `simulate`, en los pasos de `frame_time_s`, interpolé con `np.interp` en `x_m` y comparé cada celda
   de `frame_head_m` y `frame_pressure_head_m` (= H − `elevation_m`). Receta de U-34 (70 fotogramas,
   s = 145): máx. |ΔH| = 7.1·10⁻¹⁵ m; barrido 694 (71, s = 143): 7.1·10⁻¹⁵ m; Excel (401, s = 1):
   0; loma de 5 puntos con vértice fuera de nodo (321, s = 1): 2.8·10⁻¹⁴ m. Todo ≤ 10⁻⁹ m: no hay
   desfase de paso ni de progresiva.
3. **Unidades** `[leído]`: `frame_time_s` sale de `time_s` (s), `frame_x_m` de `station_x_m` (m),
   `frame_head_m` de las alturas de estación (m) y `frame_pressure_head_m` = H − z (m.c.a.), con la
   misma operación que las envolventes. No hay conversión de unidades en la fase (no se devuelve
   caudal por fotograma); los `description` llevan la unidad y documentan el `null`.
4. **JSON estricto** `[medido]`: un `NaN` o un `inf` inyectado en `frame_head_m[3][4]` hace fallar
   `SolveResponse.model_validate` (`ValidationError`): `allow_inf_nan=False` cubre las listas anidadas.
5. **`include_frames` y U-33** `[medido]`: tests en verde; con `false` los cinco campos van `null` y el
   resto de la respuesta es idéntico; `frame_flow_lps` no existe en ningún caso.
6. **Conformidad con el kit** `[leído]`: `__init__.py` sin cambios (API pública intacta); `_frames.py`
   privado, sin disco, red, `print`, entorno ni estado global mutable (constantes y un array de solo
   lectura); los `ValueError` internos de `_frames`/`_moc` (en inglés) los envuelve `solve` como
   `MainpipeTransientComputationError` con el mensaje genérico en español (`kit 02 §1`).
   `SCHEMA_VERSION` sigue en `"1.0"`: solo cambia un `description`. `tools/measure_payload.py` está
   fuera del paquete.

## Hallazgos

| ID | Severidad | Archivo:línea | Qué está mal | Evidencia |
|---|---|---|---|---|
| F5-01 | menor | `doc/DECISIONS.md` U-34 (3); `tools/measure_payload.py:86-106, 151-162` | La receta y el barrido de U-34 no son el máximo en bytes del dominio que admite el contrato: el tamaño depende de cuántos caracteres ocupa cada número (signo, exponente), y el barrido solo varía el **recuento** de números. (a) Con entradas realistas, desplazar el datum a cotas negativas da respuestas mayores que la «peor» medida: 3 284 238 B (receta 694 con cota del depósito −1234.57 m y el perfil desplazado igual), 3 256 745 B (−412 m, cota del mar Muerto) frente a los 3 167 900 B publicados; el margen real sobre 3,5 MB es ≈ 6 %, no ≈ 9.5 %. (b) Con entradas válidas pero sin sentido físico (L = 1.2 cm, Q₀ ≈ 10⁻⁶ L/s, cotas ≈ −2·10⁻⁵ m, todo en notación exponencial y negativo) la respuesta llega a **4 129 794 B** (`model_dump_json`; `json.dumps` 4 059 734 B), **por encima de 3 500 000 B**. Cota superior `[calculado]`: 24 caracteres + separador por número × 175 566 números ≈ 4.39 MB más claves y `checks`, por debajo de los 4,5 MB de producción. D-57 (1) habla de «el peor caso que admiten los topes del paquete»; D-57 reserva el margen de 3,5 a 4,5 MB para signos y exponentes, así que producción no se rompe, pero la frase «la respuesta más grande posible cabe en 3,5 MB» (plan, Parte 1, fase 5) no es cierta en sentido estricto. Que se acepte, se acote la entrada o se pida al portal lo deciden `hie-architect` y el dueño; como mínimo, `portal/INTEGRATION.md` (fase 6) debería decir que la cifra vale para la receta y no para cualquier formato de número | `[medido]` venv limpio: `adversarial.py` / `adversarial2.py` sobre `case_with_stations(694)`: «E-shift -1234.567 … max=3284238», «D-dead-sea … max=3256745», «B-tiny-scale … pyd=4123080», «C-tiny-long … json=4059734 pyd=4129794 > 3.5MB». Longitudes de formato `[medido]`: `-0.000023457010241839345` (pydantic, 24 caracteres), `-2.2250738585072014e-308` (24) |

Sin hallazgos bloqueantes ni mayores.

Observación (no es hallazgo): el `description` de `frame_time_s` (`schemas.py:673-677`) escribe el
tope con la constante literal 50 000. Hoy es correcto; si algún día se aplica la regla de U-34 (6),
habrá que cambiar también ese texto, además de `FRAME_CELL_BUDGET`.

## Lo que no comprobé

- `portal/examples/` y `portal/INTEGRATION.md`: son de la fase 6; la fase 5 no toca `portal/`
  (`portal/examples/` solo tiene `.gitkeep`). No aplica `kit 04 §2–3`.
- Que la guarda de D-57 (2) en `backend/tests/` del portal mida lo mismo: el portal no forma parte de
  este repositorio y no lo ejecuté.
- La serialización real del router del portal (FastAPI con `response_model`): medí las dos de U-34
  (`json.dumps` compacto y `model_dump_json`), no un `TestClient`.
- Tiempos en otro equipo que el del verificador; la cifra de 0.215 s es de este equipo y de este venv.
- Entradas con magnitudes extremas (exponentes de tres cifras) para el tamaño: probablemente llevan a
  desbordamiento antes que a una respuesta; la cota de F5-01 no depende de ellas.
- El estado de `portal/HANDOFF.md` para la fase 5 (se actualiza tras esta verificación).

## Veredicto

**pasa** — sin bloqueantes ni mayores; un menor abierto (F5-01) para decisión de `hie-architect` y el
dueño antes de la fase 6.

## Decisión del dueño sobre F5-01 (2026-11-15)

**Aceptado y documentado.** No se cambian el código ni la receta de U-34. En la fase 6,
`portal/INTEGRATION.md` dirá que 3 167 900 B es la cifra de la receta publicada (y su barrido),
añadirá el caso con datum negativo (3 284 238 B, margen ≈ 6 %) y advertirá que entradas válidas
extremas, sin sentido físico, pueden superar 3 500 000 B (medido 4 129 794 B) sin llegar al corte
de 4,5 MB de producción (cota ≈ 4.39 MB `[calculado]`).
