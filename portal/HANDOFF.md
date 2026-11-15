# mainpipe-transient — Handoff al portal Fluida

| | |
|---|---|
| Slug del portal | `mainpipe-transient` |
| Paquete Python | `mainpipe_transient` |
| Distribución | `mainpipe-transient` |
| Repositorio | https://github.com/gustavods14/mainpipe-transient |
| Kit con el que se diseñó | `3.0.0` |
| Versión del contrato (`SCHEMA_VERSION`) | `1.0` (congelada en G4) |
| Commit a pinear | — (se llena en la entrega) |

## Etapas

| # | Etapa | Estado | Fecha | Artefacto | Kit |
|---|---|---|---|---|---|
| 0 | Inicio | aprobada | 2026-11-14 | `portal/HANDOFF.md` | 3.0.0 |
| 1 | Historias (G1) | aprobada | 2026-11-14 | `doc/stories/` | 3.0.0 |
| 2 | Plan (G2) | aprobada | 2026-11-14 | `doc/plans/` · `portal/DECISION-REQUESTS.md` · `portal/API-PROPOSAL.md` | 3.0.0 |
| 3 | Prototipo (G3) | aprobada | 2026-11-14 | `portal/ui-spec.json` · `portal/prototype.html` | 3.0.0 |
| 4 | Decisiones del portal (G4) | aprobada | 2026-11-14 | `D-NN` en el portal · plan `congelado` | 3.0.0 |
| 5 | Construcción (G5) | en curso | 2026-11-14 | `src/` · `portal/INTEGRATION.md` · `portal/examples/` · `doc/verification/` | 3.0.0 |
| 6 | Entrega | pendiente | | commit + etiqueta | |

Estados: `pendiente` · `en curso` · `aprobada` (puerta pasada) · `reabierta`.

## Checklist de entrega

Ver `doc/upstream-kit/04-handoff.md` §3 en el portal.

## Notas

(Cualquier desvío del kit, con su `DR-N`.)

- 2026-11-14: el portal resolvió DR-1..DR-6 (D-57 a D-62, commit `2466321` del portal). Se
  reabren las etapas 1–3 para incorporarlas: HU-4.1 crit. 1 (D-57), plan (D-57..D-62) y
  `ui-spec.json` / `prototype.html` (D-58..D-62). Detalle en `portal/DECISION-REQUESTS.md`,
  «Pendiente tras las decisiones».
- 2026-11-14: G1 aprobada de nuevo tras incorporar D-57 (HU-4.1 crit. 1 sin `frame_flow_lps`,
  HU-1.6 crit. 13: 422 al superar el tope de pasos) y alinear el reproductor con D-58.
- 2026-11-14: G2 aprobada de nuevo tras incorporar D-57..D-62 al plan (`MAX_STEPS` = 10 000,
  tope de fotogramas min(1001, ⌊50 000/n⌋), sin `frame_flow_lps` — U-33, eco
  `min_allowed_pressure_head_m` — U-35). El dueño acepta la regla de ajuste de U-34 (bajar el
  presupuesto de celdas si la medición supera 3,5 MB) en lugar de abrir un DR-7, el 422 para la
  duración por defecto fuera de tope (U-09) y la lectura 3,5 MB = 3 500 000 B.
- 2026-11-14: G3 aprobada de nuevo tras incorporar D-57 … D-62 a `portal/ui-spec.json` y
  `portal/prototype.html`: tope de 10 000 pasos y su 422 (D-57); instante como estado del panel,
  teclado y «Ir a t = … s» (D-58); barra de una fila, sticky solo ≥ lg con `lg:top-20` (D-59);
  colores con roles documentados y rojo solo en el cruce (D-60); fórmulas en HTML (D-61); sin
  sección `ai` (D-62); límite leído de `response.min_allowed_pressure_head_m` (U-35). Esquema
  validado con jsonschema; 73 `contract_path` presentes en el plan §1, sin huecos. Hallazgos para
  el kit: el esquema de `ui-spec.json` no tiene lugar para fórmulas (D-61) ni para acciones dentro
  de un aviso («Ir a t», descrito en `interactions`).
- 2026-11-14: G4 aprobada. DR-1 … DR-6 resueltos (D-57 … D-62), ninguno bloqueante abierto; plan
  `doc/plans/01-golpe-ariete-v1.md` congelado con `SCHEMA_VERSION` = `"1.0"` (U-37). El dueño
  acepta U-03, U-14, U-21, U-22, U-34 (6) y U-35 como vigentes y el riesgo de U-34: si la respuesta
  del peor caso supera 3 500 000 B en la fase 5, se bajan fotogramas sin abrir pedido y el tope
  efectivo se publica en `portal/INTEGRATION.md`.
- 2026-11-14: etapa 5 en curso. Fase 0 del plan (andamiaje y referencia del Excel, U-28)
  entregada en `905e53a` y verificada por `hie-verifier`: **pasa**
  (`doc/verification/01-fase-0.md`). Menores: F0-01 y F0-02 aceptados por el dueño; F0-03
  (este estado) corregido.
- 2026-11-14: fase 1 entregada en `9d1d9b4`; `hie-verifier` **no pasa** solo por F1-01 (faltaba
  HU-1.7, `doc/verification/02-fase-1.md`). `hie-product-owner` restaura HU-1.7 sin cambiar el
  alcance y G1 se aprueba de nuevo con ella: el dueño acepta el crit. 4 (`duration_s` devuelta =
  duración efectiva, 20.01 → 20.05 s) y que el crit. 5 (< 1 s con N = 200 y 10 000 pasos) se
  mide en la fase 2. Tests de HU-1.7 crit. 1, 2 y 4 añadidos y F1-03 corregido (referencia de
  Allievi con interpolación propia). F1-02 pasa a la fase 2.
- 2026-11-14: reverificación de la fase 1 sobre `a870561`: **pasa** (F1-01 y F1-03 cerrados).
  Pasan a la fase 2: F1-02 (V-05 vía `solve()`), F1-04 (ningún test ejerce la tolerancia 10⁻⁹
  de U-08; corregir el comentario «400.000…1») y F1-05 (n_reaches por defecto, eco en la
  respuesta y 422 de la duración por defecto, probados a través de `solve()`).
