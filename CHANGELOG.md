# Changelog

Una entrada por cambio de contrato (`kit 01 §8`). `SCHEMA_VERSION` es la versión de la forma del
contrato; `__version__`, la del código.

## [0.1.0] — sin publicar

Contrato objetivo: `SCHEMA_VERSION = "1.0"` (plan `doc/plans/01-golpe-ariete-v1.md`, congelado en G4).

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
