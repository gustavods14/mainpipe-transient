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
