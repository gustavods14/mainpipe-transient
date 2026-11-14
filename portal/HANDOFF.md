# mainpipe-transient — Handoff al portal Fluida

| | |
|---|---|
| Slug del portal | `mainpipe-transient` |
| Paquete Python | `mainpipe_transient` |
| Distribución | `mainpipe-transient` |
| Repositorio | https://github.com/gustavods14/mainpipe-transient |
| Kit con el que se diseñó | `3.0.0` |
| Versión del contrato (`SCHEMA_VERSION`) | — |
| Commit a pinear | — (se llena en la entrega) |

## Etapas

| # | Etapa | Estado | Fecha | Artefacto | Kit |
|---|---|---|---|---|---|
| 0 | Inicio | aprobada | 2026-11-14 | `portal/HANDOFF.md` | 3.0.0 |
| 1 | Historias (G1) | aprobada | 2026-11-14 | `doc/stories/` | 3.0.0 |
| 2 | Plan (G2) | aprobada | 2026-11-14 | `doc/plans/` · `portal/DECISION-REQUESTS.md` · `portal/API-PROPOSAL.md` | 3.0.0 |
| 3 | Prototipo (G3) | aprobada | 2026-11-14 | `portal/ui-spec.json` · `portal/prototype.html` | 3.0.0 |
| 4 | Decisiones del portal (G4) | en curso | 2026-11-14 | `D-NN` en el portal · plan `congelado` | |
| 5 | Construcción (G5) | pendiente | | `src/` · `portal/INTEGRATION.md` · `portal/examples/` · `doc/verification/` | |
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
