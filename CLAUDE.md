# mainpipe_transient — API upstream para el portal Fluida

Paquete de cálculo hidráulico que se desarrolla aquí y se integra al portal Fluida
(`C:/Dev/web_apps`) como dependencia git pineada por commit.

| | |
|---|---|
| Slug del portal | `mainpipe-transient` |
| Paquete Python | `mainpipe_transient` (layout `src/`) |
| Repositorio | https://github.com/gustavods14/mainpipe-transient |
| Estado del flujo | `portal/HANDOFF.md` — o `/hie-flow` |

## Integración con Fluida

Las reglas de integración **no se copian aquí**: viven en el portal, en
`C:/Dev/web_apps/doc/upstream-kit/`, y las carga la skill `hie-kit`. Antes de redactar historias, planes,
contratos, pantallas o código del paquete, carga `hie-kit`.

- **El upstream propone, el portal decide.** Endpoints, dependencias, layouts, gráficos fuera de
  la regla y funcionalidades nuevas del portal se piden en `portal/DECISION-REQUESTS.md`.
- **Nunca se escribe en el repositorio del portal** desde esta sesión.
- **`portal/` es el contrato con el portal.** Lo que hay ahí lo consume el portal tal cual.

## Equipo

| Pieza | Tipo | Escribe en |
|---|---|---|
| `hie-product-owner` | agente | `doc/stories/` |
| `hie-architect` | agente | `doc/plans/`, `doc/DECISIONS.md`, `portal/DECISION-REQUESTS.md`, `portal/API-PROPOSAL.md` |
| `hie-prototyper` | skill | `portal/ui-spec.json`, `portal/prototype.html` |
| `hie-api` | skill | `src/`, `tests/`, `portal/INTEGRATION.md`, `portal/examples/` |
| `hie-verifier` | agente | `doc/verification/` (nunca edita código) |

Flujo y puertas: `/hie-flow`.

## Comandos

```powershell
python -m pytest -q
```

## Material previo

Archivado en `doc/archive/2026-11-pre-hie/` (materia prima para las historias; **no es alcance acordado**).

- `Transitorio_MOC_Animado.xlsx`: golpe de ariete por cierre de válvula en una aducción por
  gravedad (depósito → tubería → válvula), resuelto con el Método de las Características en
  fórmulas de Excel. Malla fija de 20 tramos × 400 pasos, Courant = 1, f constante, ley de cierre
  por tabla Q(t) interpolada linealmente, validación contra Joukowsky / Michaud y semáforos de
  PN y cavitación. Supuesto: tubería horizontal (una sola cota `z_tub`).

Antecedentes técnicos de la sesión del 2026-11-14 (contexto, no decisión):

- La malla del MOC se escribe en altura piezométrica H, por lo que **la cota no entra en el
  cálculo de H y Q**: con un perfil real el método es el mismo. Lo único que cambia es la
  presión de cada nodo, p/γ = H − z(x). Despreciar el término V·sen α cambia H como máximo
  ≈ V₀·Δz/a (≈ 0,1 m en el caso del Excel).
- El supuesto horizontal subestima la depresión en cada punto alto en exactamente su altura.
  Con los datos del Excel, p/γ mín. = −37,9 m (horizontal) frente a −50 a −61 m con perfiles
  descendentes o con loma.
- Por debajo de la presión de vapor hay separación de columna: el MOC simple deja de ser
  válido y puede subestimar los picos posteriores. Un modelo DVCM/DGCM queda fuera del MOC
  simple. El límite de −10 m.c.a. depende de la altitud (≈ −7 m a 3000 m).
