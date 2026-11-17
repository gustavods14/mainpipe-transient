# Plan 01 — Golpe de ariete por cierre de válvula (v1)

| | |
|---|---|
| estado | **borrador (enmienda F5R-02)** — 2026-11-15, tras la entrega v0.1.0 (pin `a04431e`), pendiente de G2 y de una nueva G4. La enmienda solo toca el rango de `pn_bar` (U-43), los resultados no representables (U-44) y el versionado y la entrega (U-45): §1.3 (fila `pn_bar` y sus mensajes), §1.4 (timbraje), §1.6, fases 7 y 8, V-12 y V-20. **Todo lo demás del contrato 2.0 sigue congelado** tal como quedó en la G4 del 2026-11-15, y `SCHEMA_VERSION` sigue en **`"2.0"`** (U-45). Antes: congelado el 2026-11-15 en la nueva G4 con `"2.0"` (DR-7 … DR-10 resueltos, D-63 … D-66); congelado el 2026-11-14 en G4 con `"1.0"`. Toda enmienda posterior sigue `kit 01 §8` y U-37 |
| kit | 3.0.1 (adoptada el 2026-11-15, F6-04; diseñado y congelado con 3.0.0. La 3.0.1 es un *patch* que solo reescribe `kit 03 §1` y `§3` (IA) sin cambiar ninguna regla para el upstream; las citas del plan a `kit 03 §1` siguen valiendo y la app no tiene IA, D-62). La enmienda F5R-02 se redacta con 3.0.1 |
| fecha | 2026-11-15 (enmienda F5R-02, borrador); 2026-11-15 (congelado 2.0); 2026-11-14 (congelado 1.0) |
| historias | `doc/stories/00-epica.md` … `04-serie-reproduccion.md` (reaprobadas en G1 el 2026-11-15 con la enmienda: precisión de las listas, sin `frame_pressure_head_m`, sin texto de fase, ρ y g constantes; y de nuevo el mismo día con la enmienda F5R-02: HU-1.6 crit. 14, fila `pn_bar`, épica pregunta 11, HU-2.3 crit. 1 con el literal del paquete) |
| pedidos al portal | `portal/DECISION-REQUESTS.md`: DR-1 … DR-6 resueltos (D-57 … D-62, commit `2466321` del portal); DR-7 … DR-10 resueltos (D-63 … D-66, alternativa (a) en los cuatro; commit `29593af` del portal). La enmienda F5R-02 **no abre pedidos** (U-45 (4)). Ningún pedido abierto |
| propuesta de Capa 2 | `portal/API-PROPOSAL.md` |
| decisiones internas | `doc/DECISIONS.md` (U-01 … U-45; U-43 … U-45 propuestas hasta G2) |

---

# Parte 1 — Para el dueño

## Qué se construye

Una «calculadora de golpe de ariete» que el portal Fluida llamará por detrás. Recibe los datos de
una aducción por gravedad (depósito, tubería, válvula y la tabla de cierre de la válvula) y
devuelve, para toda la tubería y cada instante, la altura piezométrica (de la que la pantalla saca
la presión restando la cota); en la válvula y en el punto medio, la altura y la presión, y el caudal
en la válvula y en el depósito; las envolventes de máximos y mínimos; los avisos de timbraje y de
depresión; y la referencia teórica de Joukowsky / Michaud. Es lo mismo que hoy hace el Excel, pero:

- con cualquier número de tramos (10 a 200) y cualquier duración dentro de un tope;
- con el **perfil real** del trazado, de modo que la presión de cada punto alto sale con su cota
  (el Excel suponía la tubería horizontal y por eso subestimaba la depresión de las lomas);
- con mensajes de error y avisos en español que dicen qué, dónde y cuándo.

La pantalla (formularios, gráficos, el botón PLAY) **no** se construye aquí: la hace el portal. Este
repositorio entrega el motor y la ficha técnica para que el portal lo enchufe sin rediseñar nada.

## En qué orden

Como en una obra: primero se replantea, luego se hace la estructura y se prueba, y al final los
acabados.

| Fase | Qué se hace | Analogía | Cómo sabremos que está hecha |
|---|---|---|---|
| 0 | Andamiaje del paquete y **congelado de los números del Excel** (recalculados una vez con Excel) | Replanteo: fijar los puntos de referencia antes de excavar | El paquete se instala limpio y los resultados del Excel quedan guardados como referencia, con su procedencia |
| 1 | El **cálculo MOC** en tubería horizontal | La estructura: es lo que más riesgo tiene | Reproduce el Excel paso a paso (± 0.05 m) y Joukowsky exacto sin fricción |
| 2 | La **ficha de entrada**: validaciones, mensajes, topes de malla y duración, medición de tiempos | El control de recepción de materiales | Cada dato malo se rechaza con un mensaje claro; el caso más grande calcula en < 1 s |
| 3 | El **perfil real** (x, z) | Pasar del plano en planta al perfil longitudinal | La loma de 40 m baja la presión mínima exactamente 40 m |
| 4 | Las **verificaciones**: PN, depresión, separación de columna, Joukowsky / Michaud | La inspección final con su acta | Cada aviso aparece justo en su umbral, con su mensaje |
| 5 | **Rehecha tras la enmienda del 2026-11-15**: la ficha 2.0 (ρ y g fijos, números a 3 decimales) y la **serie para el PLAY** con solo la altura | Las fotos del avance de obra, ahora en un formato más ligero | La película coincide con las series; cada número sale con su milímetro y nada más; el peor caso real y uno cargado con datos absurdos, **pesados en báscula** (no estimados), caben en los 3,5 MB que fijó el portal, y la cuenta de la respuesta más grande posible también |
| 6 | **Entrega** al portal | Planos «as built» y acta de entrega | Lista de chequeo de la puerta G5 completa, desde un entorno limpio |
| 7 | **Enmienda F5R-02**: el PN admite de 1 a 100 bar, y un resultado imposible de escribir en números del ordenador da un error claro en lugar de un «error del servidor» | Corregir el acta de recepción: un material fuera de catálogo se rechaza en la puerta con su motivo, no revienta en obra | Cada PN fuera de rango se rechaza con su mensaje; con cualquier PN admitido no hay ningún «error del servidor» causado por los datos, ni con los casos absurdos de la báscula |
| 8 | **Entrega 0.2.0** al portal | Planos «as built» revisados | Lista de chequeo de G5 otra vez completa desde un entorno limpio; los ejemplos de siempre dan los mismos números y hay tres nuevos |

Las fases 0 a 4 ya están construidas y verificadas y **no se rehacen**: la enmienda no cambia el
cálculo. Solo se ajustan, dentro de la fase 5, las pruebas que leían listas de la respuesta con
precisión de micras (ahora salen al milímetro). Las fases 0 a 6 están entregadas (v0.1.0); la
enmienda F5R-02 añade las fases 7 y 8 sin rehacer ninguna de las anteriores.

## Qué riesgos hay y cómo se cubren

1. **Que el motor no coincida con el Excel por un detalle de fórmula** (cómo se escribe la fricción
   en cada paso). Una diferencia de esquema basta para mover algunos décimos de metro. **Ya
   cubierto**: las fórmulas del Excel se leyeron el 2026-11-14 y el plan copia ese esquema; una
   transcripción de prueba coincide con el Excel recalculado a 10⁻¹³ m. Como el Excel no guarda
   resultados calculados, la fase 0 los genera una vez con Excel y los congela como referencia.
2. **Inestabilidad numérica con mucha fricción y tramos largos.** Como un encofrado demasiado
   largo sin apuntalar: con tramos muy largos, mucha fricción y diámetro pequeño, el esquema puede
   oscilar. Esos casos se rechazan con un mensaje que dice cuántos tramos usar como mínimo
   (punto 1 de abajo, confirmado en G2).
3. **Tiempo de cálculo y tamaño de la respuesta.** El portal espera la respuesta antes de atender
   a otros usuarios, y en producción corta toda respuesta de más de 4,5 MB sin que ninguna prueba lo
   vea. El portal ya fijó las cotas (D-57): respuesta ≤ 3,5 MB en el peor caso, tope de 10 000
   pasos de cálculo. Como un camión que tiene que pasar bajo un puente: con el contrato 1.0 la
   báscula dio 3,17 MB, cerca del gálibo, y con datos absurdos (cotas de billones de metros) hasta
   4,1 MB (hallazgo F5-01, aceptado). Con la enmienda la carga baja a ≈ 0,96 MB en el peor caso
   real, y, como el portal mantuvo la película con los mismos fotogramas (D-65), **ninguna
   entrada admitida, ni absurda, debería pasar de ≈ 3,2 MB** `[calculado]` (cota recalculada en la
   fase 5 con la estructura medida: 3 285 874 B, ≈ 3,3 MB): el riesgo deja de
   depender de que el usuario meta datos sensatos. El portal no se fía de la cuenta: en la fase 5
   se pesan **dos camiones**, el peor caso real y uno cargado con números absurdos, y el portal
   vuelve a pesar esos dos en su propia báscula de control (la guarda de D-57 (2)). El techo para
   toda entrada se da por cumplido solo con esa báscula del portal en verde (D-65 (3)-(4)); los dos
   camiones son dos cargas concretas, no la más pesada posible (otra carga absurda puede pesar algo
   más), y el máximo lo da la cuenta.
4. **Que el resultado parezca válido cuando ya no lo es.** Bajo la presión de vapor el agua se
   separa y este método deja de valer. No se modela (fuera de v1), pero el aviso dirá desde qué
   instante y en qué punto los resultados dejan de ser físicos.

## Enmienda F5R-02 (2026-11-15, tras la entrega v0.1.0): el rango del PN

**Qué pasaba.** El dato de timbraje (PN) solo exigía ser mayor que 0. Con un PN absurdo
—10³⁰⁴ bar, o 0.000…005 bar— la calculadora no puede escribir el resultado (la presión en metros
de columna o el porcentaje del PN salen «infinito») y el portal mostraría «error del servidor: el
cálculo falló en el servidor, no en tus datos», que es falso: fallan los datos.

**Qué se decide** (el tope lo decidió el dueño; lo demás lo propone el plan y el dueño lo acepta
en esta G2):

| # | Decisión | Por qué |
|---|---|---|
| 1 | El PN admite **de 1 a 100 bar, ambos incluidos** (U-43). Más de 100 o menos de 1 (incluidos 0 y negativos) es un error con mensaje: «pn_bar = 100.5 bar está fuera de rango: supera el máximo de 100 bar. El timbraje (PN) debe estar entre 1 y 100 bar.» y su gemelo «… es menor que el mínimo de 1 bar. …» | 1 bar son ≈ 10 m de columna de agua: no hay tubería a presión de clase menor (la normalizada más baja es PN 2.5, y 1 bar deja margen para un PN rebajado por temperatura). Con ese mínimo el porcentaje del PN nunca se dispara con datos reales |
| 2 | Si los **otros datos** son tan absurdos que el resultado no se puede escribir con los números del ordenador (cotas de 10³⁰⁸ m, caudales de 10⁻³²⁴ L/s…), la respuesta es un **error de datos** con mensaje («El resultado del cálculo queda fuera del rango numérico representable: revisa las magnitudes extremas del nivel del depósito…»), nunca un «error del servidor» (U-44) | Ningún mínimo de PN razonable lo evita: el porcentaje es presión / PN, y la presión puede ser tan grande como el usuario quiera porque las cotas no tienen límite. Es como una báscula: con un camión normal pesa; con uno de un millón de toneladas no debe romperse, debe decir «fuera de escala, revise la carga» |
| 3 | El contrato **no cambia de versión** (sigue la 2.0); el paquete pasa de **0.1.0 a 0.2.0** y se hace una entrega nueva (U-45). Sin pedido al portal | No cambia ningún campo, unidad ni tipo: solo qué valores de PN se admiten. Los doce ejemplos que ya tiene el portal dan los mismos números |

**Riesgo que se acepta.** El error de datos de la decisión 2 también saldría si un fallo del
propio programa produjera un «infinito» con datos normales; un fallo que dé «no es un número»
(`NaN`) sin infinitos sigue saliendo como error del servidor. Las pruebas comprueban que con todos
los ejemplos y las recetas de la báscula esa guarda no salta.

**Puntos que el dueño acepta en esta G2** (cada uno con su alternativa, si no lo acepta):

1. **Cota inferior de 1 bar, inclusiva** (U-43). Alternativas: 0.1 bar (misma garantía numérica,
   pero admite PN sin sentido) o 2.5 bar (la clase normalizada mínima, pero rechaza PN rebajados).
2. **Lectura de HU-1.6 crit. 14 d** (U-44 (6)): con un PN admitido, toda respuesta trae el PN en
   metros y el porcentaje finitos y nunca hay un «error del servidor» causado por los datos; si
   los otros datos hacen el resultado imposible de escribir, no hay respuesta, sino el error de
   datos de la decisión 2. **Pregunta para el dueño** si no la acepta: la otra salida es **acotar
   las demás entradas** (nivel del depósito, cotas, longitud, diámetro, caudal). Eso cambia el
   alcance aprobado en G1 («cualquier cota») y vuelve a las historias; y si la cota quedara por
   debajo de 10¹⁵⁰, dejaría fuera la receta absurda que el portal pesa en su báscula (D-65 (3)), lo
   que exige un pedido al portal. El plan no lo decide.
3. **Versionado** (U-45): `SCHEMA_VERSION` sigue en `"2.0"` y `__version__` pasa a 0.2.0, sin
   pedido. Si el dueño prefiere que lo confirme el portal, el plan redacta un pedido (DR-11) antes
   de la nueva G4.

**Qué se construye** (Parte 2 §5): la fase 7 (el rango, los mensajes, la guarda y sus pruebas) y
la fase 8 (entrega 0.2.0: ejemplos regenerados y tres nuevos, `portal/INTEGRATION.md`, etiqueta).
Además, `hie-prototyper` pone el rango 1–100 en el formulario (`portal/ui-spec.json`). Hasta la
nueva entrega, la v0.1.0 (`a04431e`) sigue siendo válida para el portal.

## La enmienda del 2026-11-15 y lo que decidió el portal (D-63 … D-66)

Cuatro decisiones del dueño, tomadas al ver de qué estaba hecha la respuesta (fotogramas 57 %,
series 40 %; unos 18 bytes por número porque cada uno salía con 17 cifras). El portal aceptó las
tres que le tocaban, cada una con la alternativa que recomendaba el plan:

| # | Decisión | Qué cambia en el motor | Portal |
|---|---|---|---|
| 1 | Las listas en m y L/s salen **al milímetro** (3 decimales); los tiempos y los valores sueltos, completos | Solo la escritura de la respuesta: el cálculo y los avisos siguen con toda la precisión (U-39) | **DR-7 → D-63 (a)**, con una condición sobre el rojo del gráfico (abajo) |
| 2 | La película lleva **solo la altura**; la presión de cada fotograma la saca la pantalla restando la cota | Se quita `frame_pressure_head_m`; contrato **2.0** | **DR-8 → D-64 (a)**: la resta pasa a ser parte del contrato y se prueba en los dos lados; **DR-9 → D-65 (a)**: los mismos fotogramas que hoy |
| 3 | Sin **texto de fase** en el reproductor | Nada en el motor: los tres tiempos siguen en la respuesta | **DR-10 → D-66 (a)** |
| 4 | ρ = 1000 kg/m³ y g = 9.81 m/s² **fijos** | Dejan de ser datos de entrada; si alguien los manda, error 422 que lo explica (U-40) | No se pidió: los campos de entrada los decide el upstream |

Analogía: es como entregar los planos con cotas al milímetro en lugar de a la micra. La obra es la
misma; los planos pesan la cuarta parte. Lo que el portal añadió:

- **El rojo del gráfico sale del aviso, no de la regla de medir.** El plan proponía tolerar que,
  con el pico a menos de medio milímetro del umbral, el gráfico y el aviso discreparan en los dos
  sentidos. El portal fue más estricto (D-63): el punto rojo y el extremo en rojo se dibujan **en
  el lugar que dice el aviso**, y el tramo rojo (opcional) solo se pinta si hay aviso. Resultado:
  **nunca hay rojo sin aviso**; lo único que puede pasar, y solo en ese medio milímetro, es aviso y
  punto rojo sin tramo. Es como el acta de inspección: si el acta dice «no conforme», el plano lo
  marca en el sitio que dice el acta; el plano nunca se adelanta al acta.
- **La resta de la presión es parte del contrato** (D-64): «presión = altura − cota, con la misma
  cota que el resto de presiones» queda escrito y probado aquí y en el portal. Si algún día el
  motor calculara la presión de otro modo, sería un cambio de contrato con pedido.
- **Dos pesajes** (D-65): el peor caso real y uno con números absurdos, los dos por debajo de
  3,5 MB, medidos y no calculados.
- `frame_x_m` repite `x_m` (≈ 5 kB). El portal sugirió que podía quitarse; **el dueño decide
  mantenerlo** y el contrato lo declara idéntico a `x_m` (U-42).

## Puntos que el dueño acepta en esta G4

1. **Regla de ajuste del tamaño** (U-34 (6)). La que se aceptó el 2026-11-14 decía: si la báscula
   supera 3,5 MB, se bajan fotogramas sin preguntar. Desde D-65 el número de fotogramas lo ha
   fijado el portal, así que el plan la cambia: si algún pesaje supera 3,5 MB, **la fase 5 se
   detiene y se abre un pedido** (el portal ya dijo cuál sería el camino: acotar las entradas,
   D-65 (5)). Con ≈ 9 % de margen calculado, no se espera.
2. **Medio milímetro sin tramo**: con el pico a menos de 0.0005 m del umbral puede haber aviso
   rojo y punto rojo sin tramo rojo (D-63 (4)). Es la única discrepancia que admite el contrato.
3. **`frame_x_m` se queda** (U-42), con su coste de ≈ 5 kB en el peor caso.

## Lo que el portal decidió antes (D-57 a D-62)

Los seis pedidos están resueltos (detalle en la Parte 2 §7); la enmienda del 2026-11-15 revisó
parte de D-57 y de D-58 (D-63 … D-66, arriba). Lo que cambia el motor es **D-57**
(tamaño): la película (desde D-64, solo altura; el caudal por fotograma sale), como mucho
min(1001, ⌊50 000 / progresivas⌋) fotogramas, tope de 10 000 pasos de cálculo, respuesta ≤ 3,5 MB
medida y petición ≤ 64 KiB medida. Los otros cinco (panel «Transitorio», layout, colores, fórmulas,
sin IA) son de la pantalla y se incorporaron en la etapa 3 (`portal/ui-spec.json` y
`portal/prototype.html`, G3 reaprobada el 2026-11-15); de ellos el motor solo recoge dos
detalles: que cada aviso lleve su instante para el botón «Ir a t = … s» (ya lo lleva) y devolver la
presión mínima admisible usada, para que la línea del límite y su cruce en rojo salgan del mismo
resultado que los avisos (U-35, U-36). El texto de fase que aprobó D-58 lo retiró D-66.

## Puntos que el dueño confirmó en G2

Todos confirmados al reaprobar G2 el 2026-11-14 (`portal/HANDOFF.md`, notas); con ellos el plan se
congeló en G4. Se conservan como registro de lo que se aceptó. La enmienda del 2026-11-15 deja
obsoletas las cifras del (6), y D-65 su regla de ajuste (sustituida por «detenerse y pedir»: punto
1 de la sección anterior, U-34 (6)); el (5) no cambia (los valores por defecto de ρ y g
desaparecen con los campos: U-14, U-40).

**Ya aprobados en G2 el 2026-11-14, sin cambios** (ratificados; detalle en `doc/DECISIONS.md`):

- **(1) Nuevo error por malla gruesa con mucha fricción** (U-03): si el número de fricción del
  tramo supera 0.5, error 422 con el número mínimo de tramos.
- **(2) La presión mínima admisible no puede ser positiva** (U-21): rango −10.33 a 0 m.c.a. Un
  criterio de presión mínima positiva no es separación de columna y daría un aviso engañoso.
- **(4) Con perfil, enviar también `length_m` o `pipe_elevation_m` es error** (U-22), igual que
  enviar perfil con geometría horizontal (HU-2.3 crit. 5).
- **(5) `pipe_elevation_m` y `pn_bar` son obligatorios, sin valor por defecto** (U-14).

**Cambiados por D-57** (la numeración se conserva para no confundir con la aprobación anterior):

- **(3) Tope de pasos de cálculo = 10 000** (U-09; antes 20 000, lo fijó el portal). Duración máxima
  = 10 000 · L/(N·a): en el caso del Excel, 500 s con 20 tramos y 50 s con 200. Si se pide más, o
  si la duración por defecto Tc + 5·(4L/a) no cabe (cierres lentos con malla fina), error 422 que
  da la duración máxima y propone acortar o usar menos tramos (HU-1.6 crit. 13). La duración por
  defecto **no se recorta en silencio** al tope: el usuario ve el 422 y elige (decisión del
  upstream, U-09; el dueño la aceptó en G2).
- **(6) Tamaño de la respuesta en el peor caso ≈ 3,3 MB calculado, techo 3,5 MB medido** (D-57):
  ≈ 1,3 MB de series temporales + ≈ 1,9 MB de película + ≈ 0,1 MB de envolventes. El margen es
  corto (≈ 5 %), así que se pesa en la fase 5 con un peor caso a propósito desfavorable (U-34). Si
  la báscula diera más de 3,5 MB, **el plan propone** bajar el presupuesto de fotogramas hasta que
  quepa (menos fotogramas en las mallas grandes; el caso del Excel no cambia), lo que respeta D-57
  porque sus cifras son techos, e informar al portal en `portal/INTEGRATION.md`. **El dueño aceptó
  esta regla en G2** en lugar de abrir un pedido nuevo al portal (DR-7), y la lectura
  3,5 MB = 3 500 000 B.

**Nuevos**:

- **(7) `frame_flow_lps` desaparece del contrato**, sin opción para pedirlo (U-33): el portal
  nunca la enviaría y la historia lo retiró de v1.
- **(8) La respuesta devuelve la presión mínima admisible usada** (`min_allowed_pressure_head_m`,
  U-35), para que la pantalla dibuje la línea del límite y su cruce desde el resultado (D-60).

---

# Parte 2 — Técnica

## 1. Contrato de Capa 1

### 1.1 API pública (`kit 01 §3`)

`src/mainpipe_transient/__init__.py` exporta únicamente:

| Símbolo | Tipo |
|---|---|
| `solve(data: dict) -> dict` | única función de cálculo |
| `SolveRequest`, `SolveResponse`, `Check` | modelos Pydantic v2 |
| `MainpipeTransientError`, `MainpipeTransientValidationError`, `MainpipeTransientComputationError` | excepciones (§1.6) |
| `__version__` | `importlib.metadata.version("mainpipe-transient")` |
| `SCHEMA_VERSION` | `"2.0"` (enmienda del 2026-11-15; antes `"1.0"`) |

`solve` sigue los tres pasos de `kit 01 §3`: `SolveRequest.model_validate(data)` (un
`pydantic.ValidationError` se envuelve en `MainpipeTransientValidationError` con mensaje en español,
`raise … from exc`), calcula, y devuelve `SolveResponse(...).model_dump(mode="json")`. Cualquier
excepción no prevista se envuelve en `MainpipeTransientComputationError` (`kit 02 §1`). Importar el
paquete no calcula ni toca disco o red (`kit 03 §1`, `/health`).

**`SCHEMA_VERSION`** (U-15): cadena `"MAYOR.MENOR"`, empieza en `"1.0"`. Sube la **menor** con un
cambio aditivo compatible (campo de entrada opcional nuevo, campo de salida nuevo, valor nuevo de
`scenario`); sube la **mayor** con un cambio que rompe (campo retirado o renombrado, unidad o tipo
cambiado). Añadir un escenario (p. ej. parada de bombas) es menor si los campos actuales no cambian
de significado.

**Versión congelada en G4 (2026-11-14): `SCHEMA_VERSION = "1.0"`.** Desde aquí, cambiar la Capa 1
exige motivo, entrada en el changelog del plan, subir `SCHEMA_VERSION` según la regla de arriba
(`kit 01 §8`) y regenerar `portal/examples/` y `portal/INTEGRATION.md`; si el cambio toca algo que
decidió el portal (D-57 … D-62), es un `DR` nuevo (U-37). Cambiar un número sin cambiar la forma
(p. ej. la regla de ajuste de U-34, hoy sustituida por «detenerse y pedir») no sube
`SCHEMA_VERSION` (`kit 01 §3`).

**Enmienda del 2026-11-15: `SCHEMA_VERSION = "2.0"`** (subida **mayor**, U-15), la forma que
describe este §1. Motivo: decisiones del dueño del 2026-11-15 a partir del desglose del tamaño de
la respuesta (changelog). Rompe con `"1.0"` en tres puntos: (1) `density_kgm3` y `gravity_ms2`
salen de `SolveRequest` (U-40); una petición 1.0 que los envíe recibe 422; (2)
`frame_pressure_head_m` sale de `SolveResponse` (DR-8 → D-64); (3) las listas en m y L/s salen
con 3 decimales (U-39, DR-7 → D-63), que no cambia tipos ni unidades pero sí lo que un consumidor
puede comparar con igualdad.

**Versión congelada en la nueva G4 (2026-11-15): `SCHEMA_VERSION = "2.0"`**, con DR-7 … DR-10
resueltos (D-63 … D-66) y ningún pedido abierto. La regla de enmienda posterior es la de arriba
(U-37), y las decisiones del portal que obligan a un `DR` nuevo si se tocan son ahora D-57 …
D-66.

### 1.2 Unidades del contrato (U-06)

Las del `kit 01 §4`, con la unidad en el nombre. Caudales en **L/s**, diámetro en **mm**,
longitudes, cotas y alturas en **m**, alturas de presión en **m.c.a.** (sufijo `_m`, p/γ = H − z),
tiempos en **s**, PN en **bar**. Internamente se trabaja en SI (m³/s, m). La pantalla muestra estas
mismas unidades; si quisiera otras, la conversión es del portal (`kit 01 §4`).

**Constantes del cálculo** (U-40, desde la 2.0): densidad ρ = **1000 kg/m³** y gravedad
g = **9.81 m/s²**. No son campos de entrada ni de salida; se citan en la `description` de los campos
que las usan (`pn_head_m`, `head_loss_m`, `joukowsky_head_rise_m`, `michaud_head_rise_m`) y en
`portal/INTEGRATION.md`.

**Precisión de la salida** (U-39, D-63 (1)-(2), desde la 2.0): las listas en m y L/s se redondean
a 3 decimales al construir la respuesta; `time_s`, `frame_time_s` y los escalares salen completos.
Detalle y regla de comparación en §1.4.

### 1.3 `SolveRequest`

`model_config = ConfigDict(extra="forbid")` (U-23). Todas las restricciones de rango se escriben
como validadores propios con mensaje en español (U-13), no como `Field(gt=…)`, para que el 422 de
FastAPI llegue en español (`kit 02 §3`). Los rangos se repiten en `description`.

| Campo | Tipo | Unidad | Por defecto | Rango / regla (fuera → 422) | HU |
|---|---|---|---|---|---|
| `scenario` | `Literal["reservoir_pipe_valve"]` | — | `"reservoir_pipe_valve"` | único valor en v1 | épica P1 |
| `geometry` | `Literal["horizontal","profile"]` | — | `"horizontal"` | — | 1.1, 2.1 |
| `length_m` | `float \| None` | m | `None` | obligatorio y > 0 con `horizontal`; prohibido con `profile` | 1.6-7, 2.3-5 |
| `pipe_elevation_m` | `float \| None` | m | `None` | obligatorio y ≤ `reservoir_level_m` con `horizontal`; prohibido con `profile` | 1.6-8 |
| `profile_x_m` | `list[float] \| None` | m | `None` | obligatorio con `profile`, prohibido con `horizontal`; 2–500 puntos; `[0] = 0`; estrictamente creciente | 2.3 |
| `profile_z_m` | `list[float] \| None` | m | `None` | igual longitud que `profile_x_m`; `[0] ≤ reservoir_level_m` | 2.3 |
| `inner_diameter_mm` | `float` | mm | — | > 0 | 1.6-7 |
| `wave_speed_ms` | `float` | m/s | — | 0 < a ≤ 1500 | 1.6-7 |
| `darcy_friction_factor` | `float` | — | — | 0 ≤ f ≤ 0.1 | 1.6-7 |
| `initial_flow_lps` | `float` | L/s | — | > 0 | 1.6-7 |
| `reservoir_level_m` | `float` | m | — | cualquiera (mismo datum que la tubería) | 1.1 |
| `pn_bar` | `float` | bar | — | > 0 | 3.1 |
| `min_allowed_pressure_head_m` | `float` | m.c.a. | `-10.0` | −10.33 ≤ valor ≤ 0 (U-21) | 3.2 |
| `closure_time_s` | `list[float]` | s | — | 2–20 puntos; `[0] = 0`; estrictamente creciente | 1.2, 1.6 |
| `closure_flow_lps` | `list[float]` | L/s | — | igual longitud; `|[0] − Q₀| ≤ 0.1 %·Q₀`; 0 ≤ Q ≤ Q₀; último = 0 | 1.2, 1.6 |
| `n_reaches` | `int` | — | `20` | par; 10 ≤ N ≤ 200 | 1.7 |
| `duration_s` | `float \| None` | s | `None` → Tc + 5·(4L/a) | ≥ Tc + 2L/a; `n_steps` ≤ `MAX_STEPS` = 10 000 (U-09, D-57), también con la duración por defecto | 1.6-10, 1.6-13, 1.7 |
| `include_frames` | `bool` | — | `True` | `False` → campos `frame_*` y `frame_stride` en `null` (U-24) | 4.2 |

Reglas cruzadas adicionales, todas 422 y en el validador del modelo:

- **Número de fricción del tramo** (U-03): φ = f·Δx·V₀ / (2·D·a) ≤ 0.5. El mensaje da φ y el
  `n_reaches` mínimo par que lo cumple. (Confirmado por el dueño en G2.)
- **Tope de pasos** (U-09, D-57, HU-1.6 crit. 13): `n_steps` = ⌈T/Δt − 10⁻⁹⌉ ≤ `MAX_STEPS`
  = 10 000, con T la duración pedida o, si falta, la de por defecto. El mensaje nombra
  `duration_s` y `n_reaches`, da los pasos necesarios, la **duración máxima admisible con esa
  malla** T_max = `MAX_STEPS`·Δt y el N par máximo con la duración pedida, e indica que se puede
  acortar la duración o usar una malla más gruesa. T_max se escribe **truncada** (no redondeada) a
  los decimales de U-26, para que enviar la cifra mostrada calcule sin error (HU-1.6 crit. 13).
  Variantes: si `duration_s` no se envió, el mensaje dice que la duración por defecto
  Tc + 5·(4L/a) = … s supera el tope y propone enviar `duration_s` ≤ T_max; si la duración mínima
  Tc + 2L/a ya supera T_max, no propone acortar sino el N máximo que la admite (y, si ni N = 10 la
  admite, dice que el cierre es demasiado lento para el tope de pasos). Ejemplo del caso del Excel:
  Δt = 1000/(N·1000) → T_max = 500 s con N = 20 y 50 s con N = 200.
- El primer caudal de la ley se sustituye internamente por Q₀ (U-18), tras validar la tolerancia.
- **Campos retirados en la 2.0** (U-40): `density_kgm3` y `gravity_ms2` ya no existen. Si la
  petición trae alguno, 422 con un mensaje propio, en un `model_validator(mode="before")` para
  que llegue en español también a través de FastAPI (U-13), en lugar del genérico de
  `extra="forbid"`: «density_kgm3: la densidad ya no es un dato de entrada; el cálculo usa
  ρ = 1000 kg/m³. Quite el campo de la petición.» y «gravity_ms2: la gravedad ya no es un dato de
  entrada; el cálculo usa g = 9.81 m/s². Quite el campo de la petición.» (ambos si vienen los dos).
  Cualquier otro campo desconocido sigue con el 422 de `extra="forbid"` (U-23).

Mensajes: en español, con unidades, decimales con punto y el punto exacto que falla (`kit 02 §3`;
textos de HU-1.6 y HU-2.3). Formato numérico común en U-26.

### 1.4 `SolveResponse`

`model_config = ConfigDict(allow_inf_nan=False)` (`kit 01 §4`). Todas las series van en columnas
paralelas. Un `null` solo aparece donde la tabla lo dice.

**Precisión de la salida (U-39, D-63 (1)-(2); desde la 2.0).** Se redondean a **3 decimales** todas las
listas en m, m.c.a. y L/s: las seis series temporales salvo `time_s`; las ocho columnas por
progresiva en m (`x_m`, `elevation_m`, `head_initial_m`, `pressure_head_initial_m`, `head_max_m`,
`head_min_m`, `pressure_head_max_m`, `pressure_head_min_m`); y `frame_x_m` y `frame_head_m`. **No
se redondean** `time_s`, `frame_time_s` ni ningún escalar (derivados, extremos con su progresiva y
su instante, PN, eco del límite, referencia teórica, campos de `checks`). Reglas de U-39: cada lista
se redondea **una sola vez, desde el valor de precisión completa**, con una única función privada
(nunca una lista redondeada a partir de otras redondeadas: `pressure_head_valve_m` es
redondeo(H − z), no redondeo(H) − redondeo(z)); el cálculo, los extremos, el primer cruce y los
`checks` usan precisión completa. Consecuencias que el contrato declara:

- Dos listas que llevan el **mismo valor** salen iguales (mismo `float` → mismo redondeo):
  `head_valve_m[0]` = `head_initial_m[-1]` (HU-1.3 crit. 1); `frame_head_m[k]` en x = L y L/2 =
  `head_valve_m` y `head_midpoint_m` en ese instante (HU-4.1 crit. 1); series y envolventes de H en
  los nodos, perfil frente a horizontal (HU-2.1 crit. 1). Ver §6, V-19.
- **Regla de comparación** (D-63 (5); se publica en `portal/INTEGRATION.md`, fase 6): una lista
  **no se compara con igualdad estricta con un escalar**. O se redondea el escalar a 3 decimales con
  la misma regla del paquete (U-39 (4)) y entonces la igualdad es exacta (p. ej. `head_max_m[-1]` =
  redondeo(`head_valve_max_m`), HU-1.5 crit. 2), o se compara con tolerancia 0.0005 m (en la
  práctica 0.0005 m + 10⁻⁹ m, por la coma flotante).
- Una diferencia de listas redondeadas (p. ej. `frame_head_m` − `elevation_m`) se aparta como mucho
  0.001 m (+ 10⁻⁹ m) de la lista redondeada equivalente: las dos son múltiplos de 1 mm y su
  diferencia exacta no pasa de 1.5 mm, así que como mucho es 1 mm.
- Una progresiva escalar (`checks[].x_m`, `first_x_m`, `pressure_head_*_global_x_m`) se localiza en
  `x_m` redondeándola a 3 decimales (U-41). Los instantes escalares están en `time_s` tal cual.
- Una desigualdad entre una lista y un umbral escalar (el tramo rojo de §1.5) no es una igualdad y
  se evalúa tal cual; lo que la gobierna es la regla del rojo de §1.5 (D-63 (3)-(4)).

**Identidad y estado**

| Campo | Tipo | Unidad | Contenido |
|---|---|---|---|
| `schema_version` | `str` | — | igual a `SCHEMA_VERSION` |
| `scenario` | `Literal` | — | eco de la entrada |
| `geometry` | `Literal` | — | eco de la entrada |
| `status` | `Literal["ok","warning","error"]` | — | el más severo de `checks`; `ok` si no hay |
| `checks` | `list[Check]` | — | §1.5 |

**Derivados**

| Campo | Unidad | Fórmula |
|---|---|---|
| `length_m` | m | L (`length_m` o último `profile_x_m`) |
| `area_m2` | m² | A = π·D²/4 |
| `velocity_initial_ms` | m/s | V₀ = Q₀/A |
| `head_loss_m` | m | h_f = f·(L/D)·V₀²/(2g) |
| `dx_m`, `dt_s` | m, s | Δx = L/N, Δt = Δx/a |
| `n_reaches`, `n_steps` | — | N; ⌈T/Δt − 10⁻⁹⌉ |
| `duration_s` | s | duración efectiva = `n_steps`·Δt |
| `reflection_time_s` | s | 2L/a |
| `wave_period_s` | s | 4L/a |
| `closure_duration_s` | s | Tc = primer instante de la tabla con Q = 0 |
| `friction_number` | — | φ = f·Δx·V₀/(2·D·a) (informativo, U-03) |

**Series temporales** (longitud `n_steps + 1`, instante k = k·Δt)

`time_s` (s, sin redondear), `head_valve_m`, `head_midpoint_m` (m), `pressure_head_valve_m`,
`pressure_head_midpoint_m` (m.c.a.), `flow_reservoir_lps`, `flow_valve_lps` (L/s), estas seis a
3 decimales (U-39). «Punto medio» = nodo x = L/2 (N par); su cota es z(L/2) interpolada del perfil.

**Envolventes por progresiva** (todas de la misma longitud, U-07; las de m y m.c.a. a 3 decimales,
U-39)

| Campo | Unidad | Contenido |
|---|---|---|
| `x_m` | m | nodos de cálculo ∪ vértices del perfil, ordenados, sin duplicados en precisión completa; a 3 decimales es no decreciente y dos progresivas a menos de 1 mm pueden mostrar el mismo valor (U-41) |
| `x_is_node` | `list[bool]` | `true` si la progresiva es nodo de cálculo, `false` si es solo vértice |
| `elevation_m` | m | z(x) |
| `head_initial_m` | m | H de régimen |
| `pressure_head_initial_m` | m.c.a. | H de régimen − z |
| `head_max_m`, `head_min_m` | m | sobre **todos** los pasos (U-19) |
| `pressure_head_max_m`, `pressure_head_min_m` | m.c.a. | ídem, con la cota del punto |

**Extremos** (desempate: primer instante, luego menor x; U-25; escalares, sin redondear)

`head_valve_max_m`, `head_valve_max_time_s`, `head_valve_min_m`, `head_valve_min_time_s`,
`pressure_head_max_global_m`, `pressure_head_max_global_x_m`, `pressure_head_max_global_time_s`,
`pressure_head_min_global_m`, `pressure_head_min_global_x_m`, `pressure_head_min_global_time_s`.

**Timbraje y límite de depresión**

`pn_head_m` (m.c.a.) = PN·10⁵/(ρ·g), con ρ = 1000 kg/m³ y g = 9.81 m/s² fijos (U-40);
`pressure_max_pn_ratio_pct` (%) =
100·`pressure_head_max_global_m`/`pn_head_m`; `min_allowed_pressure_head_m` (m.c.a.) = eco del
límite usado (el enviado o −10.0 por defecto), siempre presente (U-35). Con `pn_head_m` es lo que
la pantalla necesita para dibujar las dos líneas de umbral y marcar sus cruces con el predicado de
§1.5 (D-60) sin leer el formulario, que puede haber cambiado tras el cálculo (D-58 (3)).

**Referencia teórica** (informativa: nunca genera aviso ni cambia `status`, HU-3.4)

| Campo | Unidad | Contenido |
|---|---|---|
| `maneuver_type` | `Literal["rapid","slow"]` | `rapid` si Tc ≤ 2L/a |
| `joukowsky_head_rise_m` | m | a·V₀/g (siempre) |
| `michaud_head_rise_m` | m \| `null` | 2·L·V₀/(g·Tc); `null` si la maniobra es rápida |
| `full_pulse_length_m` | m \| `null` | L − a·Tc/2; `null` si la maniobra es lenta |
| `theoretical_head_rise_m` | m | Joukowsky si rápida, Michaud si lenta |
| `moc_head_rise_valve_m` | m | `head_valve_max_m` − H de régimen en la válvula |
| `theory_deviation_pct` | % | 100·(MOC − teórico)/teórico (U-17; igual que `4_Validacion!C27`, que la da como fracción). Caso Excel: 3.712 % |

**Serie para el reproductor** (F4; todos `null` si `include_frames = false`; tope en U-10, D-57)

| Campo | Tipo | Unidad | Contenido |
|---|---|---|---|
| `frame_stride` | `int \| null` | — | pasos de cálculo entre fotogramas consecutivos (1 = sin submuestreo); el último intervalo puede ser más corto, porque el último paso siempre es fotograma |
| `frame_time_s` | `list[float] \| null` | s | instantes, **sin redondear**; el primero 0 y el último `duration_s`; cada uno es exactamente un valor de `time_s` |
| `frame_x_m` | `list[float] \| null` | m | idéntico a `x_m` (mismo redondeo a 3 decimales); invariante de contrato (D-64 (3), abajo). Se mantiene aunque repita `x_m` (decisión del dueño, U-42) |
| `frame_head_m` | `list[list[float]] \| null` | m | `[k][j]`: fotograma k, progresiva j (U-11); a 3 decimales (U-39) |

**No hay `frame_pressure_head_m`** desde la 2.0 (D-64 (1), HU-4.1 crit. 3): la presión de cada
fotograma y progresiva es `frame_head_m[k][j]` − `elevation_m[j]`, la misma resta que hacía el
paquete (H − z, M13), y la hace la pantalla en una función pura (D-64 (2)). Las series de presión
en la válvula y en L/2, las envolventes de presión y los `checks` **siguen** en la respuesta.
**No hay `frame_flow_lps`** ni opción para pedirlo (U-33, D-57 (3)): el caudal en el tiempo está
en `flow_valve_lps` y `flow_reservoir_lps` (HU-1.4).

**Invariantes de la serie: contrato de Capa 1** (D-64 (3), U-42; se publican en
`portal/INTEGRATION.md` y los prueba V-17). Con `include_frames` verdadero:

1. **`frame_x_m` == `x_m`**, lista idéntica elemento a elemento (mismos `float`).
2. **p/γ(x_j, t_k) = `frame_head_m[k][j]` − `elevation_m[j]`**, donde `elevation_m[j]` es la
   **misma cota z(x_j)** con la que el paquete calcula todos los campos `pressure_head_*`
   (`pressure_head_valve_m`, `pressure_head_midpoint_m`, `pressure_head_initial_m`,
   `pressure_head_max_m`, `pressure_head_min_m` y los escalares `pressure_head_*_global_*`): la
   presión es H − z (M13), sin otro término. Con las dos listas a 3 decimales, la presión derivada
   se aparta de la redondeada desde la precisión completa, r(H − z), como mucho **0.001 m + 10⁻⁹ m**
   (con magnitudes de proyecto; con magnitudes extremas el redondeo no actúa y manda la aritmética
   de coma flotante). Definir la presión de otro modo sería cambio de contrato con pedido (D-64 (3)).
3. **Fotograma k ↔ paso i_k de las series**: i_k es el índice con `time_s[i_k]` == `frame_time_s[k]`
   (igualdad exacta). Vale i_k = k·`frame_stride` para todos los fotogramas salvo el último, que es
   siempre i = `n_steps`; sin submuestreo (`frame_stride` = 1) también el último cumple
   i_k = k·`frame_stride`. En x = L y x = L/2, la presión derivada del fotograma k y
   `pressure_head_valve_m[i_k]` / `pressure_head_midpoint_m[i_k]` difieren como mucho
   0.001 m + 10⁻⁹ m, más estricto que los 0.0015 m con que lo prueba el portal (D-64 (2)).

Tope de fotogramas (U-10, **D-65 (1)-(2)**): la fórmula de la 1.0, n_fotogramas ≤ min(1001,
⌊50 000 / n_progresivas⌋), con n_progresivas = longitud de `x_m`, es decir **≤ 50 000 celdas en la
única matriz** `frame_head_m`. Lo que liberó D-64 va a peso, no a resolución temporal. Motivo
(U-10): así el techo de 3,5 MB de D-57 (1) vale para **toda** entrada admitida, incluidas las de
magnitud extrema (cota de ≈ 3,2 MB `[calculado]`, §2); D-65 (3)-(4) exige además medirlo (V-18).
Caso del Excel: 401 fotogramas × 21 progresivas, sin submuestreo (HU-4.1 crit. 1). Peor caso
(N = 200, 500 vértices fuera de nodo → 699 progresivas, 10 000 pasos): tope 71, `frame_stride` =
⌈10 000/69⌉ = 145, **70** fotogramas (k = 0, 145, …, 9 860 y 10 000; el último, i = 10 000, no es
69·145 = 10 005). La constante no se mueve sin pedido: si la película resulta gruesa en las mallas
grandes, el camino es acotar las entradas con su propio pedido, no subirla (D-65 (5)); si una
medición superase el techo, tampoco se baja por cuenta propia (U-34 (6)).

### 1.5 `checks` (`kit 01 §5`)

Modelo `Check`, misma forma para todos los códigos (U-25):

| Campo | Tipo | Unidad | Contenido |
|---|---|---|---|
| `code` | `Literal[…]` | — | tabla de abajo |
| `severity` | `Literal["warning","error"]` | — | |
| `message` | `str` | — | español, con unidades y decimales con punto |
| `value_m` | `float` | m.c.a. | valor que dispara el aviso |
| `limit_m` | `float` | m.c.a. | umbral cruzado |
| `x_m` | `float` | m | progresiva del valor, sin redondear; redondeada a 3 decimales está en `x_m` (U-41) |
| `time_s` | `float` | s | instante del valor (está en `time_s`) |
| `first_x_m` | `float \| null` | m | solo `COLUMN_SEPARATION_RISK`: primera progresiva bajo el límite (como `x_m`, U-41); `null` en los demás |
| `first_time_s` | `float \| null` | s | ídem, primer instante |
| `first_pressure_head_m` | `float \| null` | m.c.a. | ídem, presión en ese punto e instante |

| `code` | Severidad | Condición | `value_m` / `limit_m` / `x_m`, `time_s` |
|---|---|---|---|
| `PN_EXCEEDED` | `error` | p_max global > `pn_head_m` | p_max / `pn_head_m` / lugar del máximo |
| `PN_NEAR_LIMIT` | `warning` | 80 % < p_max/PN ≤ 100 % (U-16) | ídem |
| `COLUMN_SEPARATION_RISK` | `error` | p_min global < `min_allowed_pressure_head_m` | p_min / límite / lugar del mínimo; `first_*` = primer cruce (U-25) |
| `SUBATMOSPHERIC_PRESSURE` | `warning` | límite ≤ p_min global < 0 | p_min / 0 / lugar del mínimo |
| `STEADY_NEGATIVE_PRESSURE` | `warning` o `error` | p de régimen < 0 en algún x; `error` si además < límite | p mínima de régimen / 0 (warning) o límite (error) / su x, t = 0 |

Orden de `checks`: primero los `error`, luego los `warning`; dentro de cada severidad, en el orden de
la tabla. Los avisos son independientes: un régimen negativo puede dar a la vez
`STEADY_NEGATIVE_PRESSURE` y `SUBATMOSPHERIC_PRESSURE` o `COLUMN_SEPARATION_RISK`.

**Correspondencia con la paleta de estado del portal (D-13, `kit 01 §5`)** (U-20): `status` `ok` →
`success`; `warning` → `warning`; `error` → `danger`. `severity` `warning` → `warning`; `error` →
`danger`. `caution` no se usa. Sin niveles fuera de la paleta.

Mensajes modelo: los de HU-3.1 crit. 4 y HU-3.2 crit. 4 (literales, salvo el signo menos, que
es ASCII, U-26). El de
`COLUMN_SEPARATION_RISK` dice siempre, en este orden: valor y límite, dónde, cuándo, y que desde ahí
los resultados del MOC simple dejan de ser físicos.

**Uso en el panel «Transitorio» (D-58, D-60, D-63; U-36).** Sin campos nuevos en `Check`:

- **Botón «Ir a t = … s»** (D-58 (1)): todo aviso lleva instante (`time_s`, y en
  `COLUMN_SEPARATION_RISK` además `first_time_s`; `STEADY_NEGATIVE_PRESSURE` lleva t = 0). Son
  valores de `time_s`, múltiplos de Δt; con `frame_stride` > 1 pueden no coincidir con un
  fotograma, y elegir el fotograma (el más cercano, según `portal/ui-spec.json`) es de la pantalla.
  Con `include_frames: false` no hay fotogramas y el botón no aplica.
- **Rojo en el gráfico de presiones** (D-60 (1), enmendada por **D-63 (3)-(4)**; U-36). Cada
  umbral tiene **un único aviso que lo gobierna**: la línea del PN, `PN_EXCEEDED`; la de la presión
  mínima admisible, `COLUMN_SEPARATION_RISK` (los dos `error` → `danger`). Ningún otro código da
  rojo en el gráfico: `PN_NEAR_LIMIT` y `SUBATMOSPHERIC_PRESSURE` son `warning`, y
  `STEADY_NEGATIVE_PRESSURE` con `error` no tiene marcador propio, porque siempre va acompañado de
  `COLUMN_SEPARATION_RISK` (la envolvente incluye t = 0, así que p_min global ≤ p de régimen <
  límite) y el marcador es el de éste. Dos elementos, con fuentes distintas:
  1. **Marcador del cruce y extremo global en `--color-chart-critical` (obligatorio): se leen del
     aviso**, nunca de comparar una lista con el umbral. Si existe el aviso, el marcador va en el
     punto (`x_m`, `value_m`) del aviso, en el instante `time_s`, y **sustituye** al marcador del
     extremo global de ese lado (el máximo para el PN, el mínimo para el límite), que sin aviso se
     dibuja en `--color-chart-operating`. Los tres campos salen a **precisión completa** (no los
     toca U-39) y son por construcción los mismos `float` que el extremo global: en `PN_EXCEEDED`,
     `value_m` = `pressure_head_max_global_m`, `x_m` = `pressure_head_max_global_x_m` y `time_s` =
     `pressure_head_max_global_time_s`, y `limit_m` = `pn_head_m`; en `COLUMN_SEPARATION_RISK`, los
     tres del mínimo global y `limit_m` = `min_allowed_pressure_head_m`. El marcador no usa
     `first_*` (son el primer cruce, para el mensaje y para «Ir a t»). Para situar `x_m` en la lista
     `x_m`, U-41. Gráfico y estado coinciden **por construcción, sin banda**.
  2. **Tramo coloreado (opcional)**: puede calcularse sobre las envolventes redondeadas — la
     progresiva j cumple si `pressure_head_max_m[j]` > `pn_head_m` (PN) o si
     `pressure_head_min_m[j]` < `min_allowed_pressure_head_m` (límite), desigualdades estrictas con
     el umbral sin redondear —, pero **solo se dibuja si existe el aviso de ese umbral**. Sin aviso
     no se dibuja ningún tramo aunque alguna j cumpla. **Nunca hay rojo sin aviso.**
  3. **Único desacuerdo admitido**: aviso y marcador **sin tramo** (ninguna j redondeada cumple).
     Solo ocurre si el extremo global queda a menos de 0.0005 m del umbral (D-63 (4); en rigor
     ≤ 0.0005 m: la igualdad exige un empate decimal exacto, con el umbral sobre la malla de 1 mm).
     La situación inversa —alguna j redondeada cumple y no hay aviso— solo ocurre en la misma banda,
     y la pantalla no la dibuja por (2). Con aviso, el tramo puede incluir alguna j que a precisión
     completa queda dentro de la banda sin cruzar: diferencia submilimétrica que D-63 (4) admite al
     permitir el tramo sobre la envolvente redondeada.

  Lo que el paquete prueba (V-13): que el aviso existe si y solo si el extremo de precisión
  completa cruza el umbral; que sus campos son los de precisión completa e iguales a los del
  extremo global; y que toda discrepancia entre el predicado sobre las listas redondeadas y el
  aviso cae dentro de la banda. Que la pantalla dibuje el tramo solo con aviso es del portal. La
  pantalla no recalcula hidráulica: lee un aviso y, para el tramo, compara una lista con un número.

### 1.6 Excepciones (`kit 02 §1`)

Prefijo **`MainpipeTransient`** (U-12): único entre los paquetes del portal (`Mainpipe` queda para
`mainpipe-design`).

```python
class MainpipeTransientError(Exception):                        # http_status = 500
class MainpipeTransientValidationError(MainpipeTransientError, ValueError):   # 422
class MainpipeTransientComputationError(MainpipeTransientError):              # 500
```

No hay `MainpipeTransientServiceError`: el paquete no llama a ningún servicio externo (`kit 01 §6`,
`kit 02 §1`). Sin subclases más finas en v1: toda la validación ocurre en el modelo, así que el
nombre concreto que verá `examples/` es `MainpipeTransientValidationError`.

Un `NaN`/`inf` al construir la respuesta (no debería ocurrir: lo previene U-03) sale como
`MainpipeTransientComputationError`.

## 2. Pureza y presupuesto de tiempo (`kit 01 §6`)

- Sin disco, red, variables de entorno ni estado global. Sin `print`; `logging` con el logger
  `mainpipe_transient`.
- **Coste**: (N + 1 + vértices) × `n_steps` actualizaciones, con un bucle Python sobre el tiempo y
  operaciones `numpy` vectorizadas sobre los nodos. Envolventes, primer cruce y fotogramas se
  acumulan dentro del bucle (U-19): no se guarda la historia completa (con 699 progresivas y
  10 000 pasos, H y p/γ serían ≈ 112 MB en `float64`).
- **Presupuesto**: caso del Excel ≈ 400 pasos × 21 nodos → milisegundos. Peor caso admitido:
  N = 200, 500 vértices, `MAX_STEPS` = 10 000 pasos (D-57). Estimación ≈ 0.25–0.35 s (la de
  20 000 pasos era 0.5–0.7 s; el coste es lineal en `n_steps`); **se mide en la fase 2** y de nuevo
  con fotogramas en la fase 5 (medido: 0.088 s en la fase 2 y 0.147 s con fotogramas, U-38; tras la
  enmienda se repite con el redondeo de U-39, que añade una operación vectorizada sobre
  ≈ 115 000 números, del orden de milisegundos). Si la mediana de 5 ejecuciones del peor caso supera 0.8 s en el
  equipo del upstream, primero se optimiza el bucle; `MAX_STEPS` ya no se baja por cuenta propia,
  porque lo fijó el portal (D-57 (5)): sería un pedido nuevo.
- **Tamaño** (D-57; detalle y protocolo de medición en U-34). *Contrato 1.0, medido en la fase 5*:
  174 927 números, **3 167 900 B** en el peor caso del barrido (≈ 18 B por número, `float64` con
  todas sus cifras); con entradas de magnitud absurda, hasta 4 129 794 B (F5-01, aceptado).
  *Contrato 2.0* (D-63, D-64, D-65), números del peor caso realista: `time_s` 10 001
  sin redondear (≈ 18 B cada uno); seis series × 10 001 = 60 006, ocho columnas × 699 = 5 592,
  `frame_x_m` 699 y `frame_head_m` 70 × 699 = 48 930, todos a 3 decimales (≈ 6,7 B cada uno con su
  separador); 70 instantes; 699 booleanos. **≈ 0,96 MB**: el dueño lo midió con un prototipo del
  redondeo sobre la receta de U-34 (963 538 B; caso del Excel con fotogramas, 88 604 B). Se vuelve
  a medir en la fase 5 (V-18).
- **Cota absoluta** (nueva en la 2.0, U-34 (3b)): con magnitudes absurdas (cotas, caudales o
  progresivas de 10¹⁵⁰) el redondeo a 3 decimales no acorta nada y cada número puede ocupar hasta
  **25 B** (24 caracteres de `repr`, como `-1.2345678901234567e+150`, más el separador). Con el
  tope de D-65 (1) la respuesta tiene como mucho ≈ 127 300 números (70 007 de series, 9 × 699 por
  progresiva, ≤ 1 001 instantes de fotograma y ≤ 50 000 celdas) → ≤ 3,19 MB más ≈ 15 kB de claves,
  escalares, booleanos y `checks`: **≤ 3,2 MB < 3,5 MB para toda entrada admitida** `[calculado]`
  (margen ≈ 9 %; ≈ 29 % sobre los 4,5 MB de producción). Recalculada en la fase 5 con la
  estructura medida (U-34): 126 328 números × 25 B + 127 674 B = **3 285 874 B**, que es **el techo
  para toda entrada admitida**. **Ni esta cuenta ni las mediciones del upstream dan por cumplido
  D-57 (1)** (D-65 (4)): se da por cumplido para toda entrada admitida **solo con la guarda de
  D-57 (2) del portal en verde** (`backend/tests/`), que mide las dos recetas deterministas de U-34
  —la realista (3) y la adversaria de magnitud (3b)—, ambas ≤ 3 500 000 B (fase 5, V-18). Las dos
  mediciones son de dos recetas concretas, **no el máximo**: la adversaria desplazada a un datum
  negativo pesa 2 844 325 B, más que la publicada (2 819 475 B, F5R-01); ninguna receta concreta
  acota todas las entradas. Con las mediciones y la cota, el upstream da por cerrado su hallazgo
  F5-01; `portal/INTEGRATION.md` publica la cota, las cifras medidas y esta lectura (fase 6).
- **Petición** (D-57 (10), D-48): el peor caso (perfil de 500 filas, ley de 20) son ≈ 1 060
  números, ≈ 21–26 KB aun con 17 cifras significativas por número, frente a 64 KiB = 65 536 B
  `[calculado]`; medida en la fase 5: 19 919 B (U-34). En la 2.0 lleva dos campos menos (ρ, g). Se
  vuelve a medir (V-18).
- Con esos topes **el dominio cabe en < 1 s** y no hace falta pedido de backend.

## 3. Dependencias (`kit 01 §7`, `kit 07`)

| Dependencia | Uso | Cota | ¿Pedido? |
|---|---|---|---|
| `pydantic` | modelos | `>=2.6` (admite 2.13.4) | no, está en el portal |
| `numpy` | bucle MOC vectorizado | `>=1.24` (debe funcionar con 2.x) | no, disponible (`kit 07 §1`) |
| `pytest` | tests | solo dev | no (`kit 07 §2`) |
| `pywin32` | recalcular el Excel por COM una sola vez para generar la referencia (fase 0, U-28) | solo dev y solo Windows; no se importa desde `src/` ni desde `tests/` | no (`kit 07 §2`) |
| `openpyxl` | leer las fórmulas del Excel para documentar el esquema (fase 0) | solo dev; no se importa desde `src/` ni desde `tests/` | no (`kit 07 §2`) |

Sin `scipy`. **No hay dependencias nuevas para el portal.** Frontend: ninguna; D-61 resolvió DR-5
con fórmulas en HTML semántico y Unicode, sin renderizador.

## 4. Método y fórmulas

Referencias: [WS] Wylie, E. B. & Streeter, V. L. (1993), *Fluid Transients in Systems*, Prentice
Hall, caps. 1–3. [Ch] Chaudhry, M. H. (2014), *Applied Hydraulic Transients*, 3.ª ed., Springer,
caps. 2–3. [Jk] Joukowsky, N. (1898/1904). [Mi] Michaud, J. (1878). [Al] Allievi, L. (1902/1913),
ecuaciones encadenadas, en [WS] cap. 1 y [Ch] cap. 2.

| # | Elemento | Fórmula | Ref. |
|---|---|---|---|
| M1 | Geometría | D = `inner_diameter_mm`/1000; A = πD²/4; Q₀ = `initial_flow_lps`/1000; V₀ = Q₀/A | — |
| M2 | Pérdida de régimen | h_f = f·(L/D)·V₀²/(2g) (Darcy-Weisbach) | [WS] §3, [Ch] §2 |
| M3 | Régimen inicial | Q(x) = Q₀; H(x) = H_dep − h_f·x/L. Sin pérdida de entrada ni altura de velocidad (U-04) | igual que el Excel |
| M4 | Malla | Δx = L/N, Δt = Δx/a (Courant = 1, sin interpolación); x_i = L·i/N | [WS] §3.2, [Ch] §3.4 |
| M5 | Constantes | B = a/(g·A); R = f·Δx/(2·g·D·A²); g = 9.81 m/s² fija desde la 2.0 (U-40) | [WS] §3.2 |
| M6 | Característica C⁺ | C_P = H_{i−1} + B·Q_{i−1} − R·Q_{i−1}·\|Q_{i−1}\|; H_P = C_P − B·Q_P | [WS] ec. 3.3.x, [Ch] §3.4 |
| M7 | Característica C⁻ | C_M = H_{i+1} − B·Q_{i+1} + R·Q_{i+1}·\|Q_{i+1}\|; H_P = C_M + B·Q_P | ídem |
| M8 | Nodo interior | H_P = (C_P + C_M)/2; Q_P = (C_P − C_M)/(2B) | ídem |
| M9 | Depósito (x = 0) | H_P = H_dep; Q_P = (H_dep − C_M)/B | [WS] §3.4 |
| M10 | Válvula (x = L) | Q_P = Q_ley(t_{k+1}) (ley evaluada en el instante que se calcula); H_P = C_P − B·Q_P | [WS] §3.4 (caudal impuesto); igual que `2_Malla_MOC` |
| M11 | Ley de cierre | interpolación lineal en la tabla; Q = 0 para t ≥ último punto; Tc = primer t_i con Q_i = 0 | HU-1.2 |
| M12 | Fricción | primer orden explícita con el caudal del punto de partida (M6–M7), **confirmada contra `2_Malla_MOC`** (U-02; en el Excel B = Cₐ, R = C_f); estabilidad φ = R·Q₀/B = f·Δx·V₀/(2Da) ≤ 0.5 (U-03) | [WS] §3.5, [Ch] §3.6 |
| M13 | Presión | p/γ = H − z(x); el término V·sen α se desprecia (efecto ≤ V₀·Δz/a) (U-05) | antecedente `CLAUDE.md` |
| M14 | Puntos que no son nodo | H interpolada linealmente entre los dos nodos vecinos en cada paso; z del vértice (U-07). Q en los vértices no se calcula: desde D-57 ninguna salida lo usa | — |
| M15 | Joukowsky | ΔH_J = a·V₀/g | [Jk], [WS] §1.2 |
| M16 | Michaud | ΔH_M = 2·L·V₀/(g·Tc), maniobra lenta (Tc > 2L/a) | [Mi], [Ch] §1 |
| M17 | Pulso completo | L_pulso = L − a·Tc/2, maniobra rápida | HU-3.4 |
| M18 | PN en m.c.a. | H_PN = PN·10⁵/(ρ·g), ρ = 1000 kg/m³ y g = 9.81 m/s² fijas (U-40) | HU-3.1 |
| M19 | Allievi (solo verificación, f = 0) | H_v(t) + H_v(t − 2L/a) − 2·H_dep = B·[Q(t − 2L/a) − Q(t)], con H_v = H_dep y Q = Q₀ para t ≤ 0 | [Al], [WS] cap. 1 |

Notas:

- Con fricción explícita (M6–M7) el régimen M3 es punto fijo exacto del esquema
  (N·R·Q₀² = h_f), así que antes de la maniobra H y Q no se mueven (prueba V-15).
- Con f = 0 y Courant = 1 el MOC es exacto en los nodos; M19 da la solución exacta en la válvula
  para cualquier ley Q(t) y sirve de referencia independiente del Excel (V-03).

### Estructura interna (U-01; privada, `kit 01 §2`)

```
src/mainpipe_transient/
  __init__.py       API pública (§1.1)
  schemas.py        SolveRequest, SolveResponse, Check + validadores
  exceptions.py     §1.6
  py.typed
  _solve.py         orquestación y envoltorio de errores
  _closure.py       ley de cierre (M11)
  _geometry.py      malla, perfil, unión de progresivas, pesos de interpolación (M4, M14)
  _moc.py           régimen y bucle MOC con acumuladores (M3–M10, M12)
  _theory.py        Joukowsky, Michaud, pulso (M15–M17)
  _checks.py        checks, status, mensajes (§1.5)
  _format.py        formato numérico de los mensajes (U-26)
  _frames.py        selección de fotogramas (U-10; existe desde la fase 5)
  _constants.py     ρ = 1000 kg/m³ y g = 9.81 m/s² (U-40; nuevo en la 2.0, privado)
tools/extract_excel_reference.py   (fase 0; recalcula una COPIA del Excel por COM con pywin32 y
                                    vuelca los valores; fuera del paquete, se ejecuta una vez)
tools/make_examples.py             (fase 6, llama al paquete instalado)
tests/reference/excel_case.json    (fase 0, generado una vez y versionado con su procedencia;
                                    los tests solo leen este JSON, U-28)
```

## 5. Fases

Orden: primero lo que más riesgo tiene (fidelidad al Excel, unidades, estabilidad), luego el
contrato, y al final lo que dimensionó el portal (F4, D-57), con su medición de tamaño.

**Estado tras la enmienda del 2026-11-15.** Las fases 0–4 están entregadas y verificadas sobre la
1.0 y **no se rehacen**: la enmienda no toca el cálculo (M1–M19), ni la validación salvo ρ y g, ni
los `checks`. Sus criterios de «hecho» siguen valiendo sobre los arrays internos de precisión
completa (`MocResult`); las pruebas que los leen **a través de `solve()`** cambian de tolerancia
(§6, nota de tolerancias) y se ajustan dentro de la fase 5, igual que las de HU-1.6 crit. 7 sobre
ρ y g. La **fase 5 se rehace** con el contenido de la 2.0 y la **fase 6** cambia de contenido
(abajo). La fase 2 queda como registro: su parte de ρ y g y `SCHEMA_VERSION` = `"1.0"` la sustituye
la fase 5.

| Fase | Contenido | Hecho cuando (comprobable) | HU / V |
|---|---|---|---|
| **0. Andamiaje y referencia** | `pyproject.toml` (layout `src/`, `requires-python >=3.12`, `numpy>=1.24`, `pydantic>=2.6`), `py.typed`, `CHANGELOG.md`, excepciones, `solve` vacío. **Referencia del Excel (U-28)**: el `.xlsx` no guarda valores calculados (con `openpyxl` y `data_only=True` toda celda con fórmula sale `None`), así que `tools/extract_excel_reference.py` abre por COM (pywin32, solo dev, solo Windows) una **copia temporal** del libro, la recalcula en Excel y vuelca a `tests/reference/excel_case.json` las entradas, H y Q de todos los nodos en los 401 instantes (hoja `2_Malla_MOC`) y los valores de `4_Validacion`. El JSON se versiona con su bloque de procedencia (fecha, versión de Excel, SHA-256 del `.xlsx`, commit del script); el original no se modifica. Los tests solo leen el JSON | `pip install .` en un venv limpio de Python 3.12 funciona; `import mainpipe_transient` sin efectos; el JSON tiene 401 instantes × 21 nodos de H y Q sin ningún `null`, su SHA-256 de origen coincide con el `.xlsx` archivado, y reproduce los valores de control de V-05 (p. ej. H_v máx = 242.76384 m en t = 2.00 s); la suite corre sin Excel ni pywin32 instalados | — |
| **1. Núcleo MOC horizontal** | `_closure`, `_geometry` (solo nodos), `_moc`, series, envolventes y extremos, llamados con argumentos internos (sin Pydantic todavía) | V-01 … V-09, V-14, V-15 en verde. En particular: Excel paso a paso ± 10⁻⁶ m / ± 10⁻⁶ L/s (U-29); Joukowsky ± 0.01 m; Allievi ± 10⁻⁶ m | HU-1.1 (1–4), 1.2, 1.3, 1.4, 1.5, 1.7 (1–4) |
| **2. Contrato y topes** | `schemas.py` completo, validadores en español, `solve` con envoltorio, φ (U-03), `MAX_STEPS` = 10 000 (U-09, D-57) con sus variantes de mensaje; benchmark del peor caso | Cada criterio de HU-1.6 tiene su test con el mensaje esperado; para el crit. 13, en el caso del Excel con N = 200: `duration_s` = 50 calcula con `n_steps` = 10 000, `duration_s` = 50.001 da 422 con «50 s», y la cifra que muestra el mensaje en un caso con Δt no redondo, reenviada, calcula sin error; la duración por defecto que no cabe da la variante «por defecto»; `solve` nunca deja salir una excepción ajena (test con fallo inyectado); mediana de 5 ejecuciones del peor caso < 0.8 s, anotada en `DECISIONS.md` (V-16) | HU-1.6 (1–13), 1.7 (5) |
| **3. Perfil** | unión de progresivas, interpolación de z y de H en los vértices (Q no: M14, U-07), presiones con la cota | V-10 en verde | HU-2.1, 2.2, 2.3 |
| **4. Verificaciones** | `_theory`, `_checks`, `status`, mensajes | V-11 … V-13 en verde; textos de HU-3.1-4 y HU-3.2-4 literales | HU-3.1 … 3.5 |
| **5. Contrato 2.0 y serie para el reproductor** (rehecha tras la enmienda del 2026-11-15; se construye tras la nueva G4 del 2026-11-15, con D-63 … D-66) | En este orden, de más a menos riesgo: **(5.1) precisión** (U-39, D-63 (1)-(2)): una única función privada de redondeo a 3 decimales aplicada al construir `SolveResponse` a las listas de §1.4, desde los arrays de precisión completa; `time_s`, `frame_time_s`, escalares y **todos los campos de `checks`** intactos; ajuste a §6 (nota de tolerancias) de las pruebas de las fases 1–4 que leen listas a través de `solve()`. **(5.2) entrada 2.0** (U-40): `_constants.py`; fuera `density_kgm3` y `gravity_ms2` de `SolveRequest` con el 422 propio de §1.3; `SCHEMA_VERSION` = `"2.0"`; `CHANGELOG.md` con la entrada de la 2.0. **(5.3) serie** (U-10, U-11, U-24, U-42): solo `frame_head_m` y `frame_x_m`, sin `frame_pressure_head_m` (D-64) ni `frame_flow_lps` (U-33), con el tope de U-10 (D-65 (1)); los invariantes de D-64 (3) (§1.4) con sus pruebas, que sustituyen a las de la 1.0 que leían `frame_pressure_head_m` (`tests/test_frames.py`, HU-4.1 crit. 1–3). **(5.4) mediciones** con `tools/measure_payload.py` (protocolo de U-34, con las **dos recetas deterministas** de D-65 (3): la realista (3) y la adversaria de magnitud (3b)) | V-13 (regla del rojo de D-63, §1.5), V-17 (con los invariantes de D-64 (3)) y V-19 en verde; **los valores que congelarán los casos dorados son los redondeados** (D-63 (6)): V-19 se comprueba sobre la salida de `solve()`, que es la que vuelca `tools/make_examples.py`; **mediciones obligatorias, no estimaciones** (V-18, U-34, D-65 (3)-(4)): (i) respuesta de la receta realista **y** de la entrada adversaria con `include_frames: true` **≤ 3 500 000 B** cada una, la mayor de las dos serializaciones, y la adversaria con **≥ 20 B por número** de media (que sea de verdad del tipo de ≈ 25 B que pide D-65 (3)); (ii) petición del peor caso **≤ 65 536 B** (D-48); (iii) caso del Excel con y sin fotogramas. Las cifras en bytes, con las dos recetas, quedan en `doc/DECISIONS.md` (U-34) y sustituyen a las de la 1.0. **Si (i) no cumple, la fase se detiene y se abre un `DR`** (U-34 (6)): el tope lo fijó el portal (D-65). Tiempo del peor caso con fotogramas < 0.8 s (V-16, U-38) | HU-1.1 (4), 1.3 (1), 1.4 (2), 1.5 (2–3), 2.1 (1–2), 2.2 (1–3), 3.1 (1), 3.2 (2), 4.1, 4.2 (1–4); HU-1.6 (7) sin ρ ni g |
| **6. Entrega** | `tools/make_examples.py`, `portal/examples/`, `portal/INTEGRATION.md`, etiqueta | Checklist `kit 04 §3` completo, con suite, ejemplos **y las mediciones de V-18** ejecutados **desde el paquete instalado en un venv limpio** (kit 2.0.0). `portal/INTEGRATION.md` lleva: **(a) tamaño** (D-57 (1)-(2), (10); D-65 (3)-(4)): las dos cifras medidas de la respuesta en bytes (receta realista y entrada adversaria, ambas ≤ 3,5 MB) y la de la petición (≤ 64 KiB), las **dos recetas deterministas** (para que la guarda de D-57 (2) en `backend/tests/` mida exactamente lo mismo), la **cota absoluta** de U-34 (3b) como techo para toda entrada admitida, con la frase de D-65 (4) —D-57 (1) se da por cumplido para toda entrada admitida solo con esa guarda en verde, no con la cuenta ni con las mediciones del upstream—, la salvedad de que las cifras medidas son de dos recetas concretas y no el máximo (F5R-01), el cierre de F5-01 del lado del upstream con las mediciones y la cota, y el aviso de que producción corta cuerpos > 4,5 MB sin que el CI ni `TestClient` lo detecten; **(b) precisión y comparación** (D-63 (5)): qué listas van a 3 decimales y qué no (`time_s`, `frame_time_s`, escalares, campos de `checks`), que una lista no se compara con igualdad estricta con un escalar (se redondea el escalar a 3 decimales o se usa tolerancia 0.0005 m), las diferencias de listas (0.001 m) y la localización de progresivas escalares (U-41); **(c) regla del rojo** (D-63 (3)-(4), §1.5): marcador y extremo en `critical` leídos del aviso, qué aviso gobierna cada umbral, tramo solo con aviso y el único desacuerdo admitido; **(d) invariantes de la serie** (D-64 (3), §1.4): `frame_x_m` == `x_m`, p/γ = `frame_head_m[k][j]` − `elevation_m[j]` con la misma cota que `pressure_head_*`, la correspondencia fotograma k ↔ paso i_k (con la salvedad del último fotograma con submuestreo) y la tolerancia garantizada; **(e) cambios 1.0 → 2.0** (campos retirados, 422 de ρ y g, `frame_pressure_head_m` retirado) y constantes ρ y g. `portal/examples/` regenerados con la 2.0; cada lista en m, m.c.a. y L/s de cada ejemplo de éxito es igual a su propio redondeo a 3 decimales (V-19 sobre los ejemplos, D-63 (6)) | HU-x.y «entregable» |

Ejemplos previstos para `portal/examples/` (`kit 04 §2`; los genera `hie-api` ejecutando el
paquete): `solve-excel-horizontal` (camino feliz, `status: error` con `COLUMN_SEPARATION_RISK` y
`PN_NEAR_LIMIT`, con fotogramas), `solve-perfil-loma` (perfil), `solve-sin-friccion-ok`
(`status: ok`), `solve-subatmosferica-warning`, `solve-regimen-negativo`, y errores
`MainpipeTransientValidationError`: ley no creciente, ley que no termina en 0, perfil no creciente,
duración insuficiente, más pasos que `MAX_STEPS` (HU-1.6 crit. 13) y, nuevo en la 2.0, petición
con `density_kgm3` (campo retirado, U-40), para que el portal vea el 422 de migración. **Solo el
primero lleva la serie** (`include_frames: true`, ≈ 89 kB en la 2.0; ≈ 0,36 MB en la 1.0); todos
los demás van con `include_frames: false` (D-57 (8)). El peor caso de tamaño **no** es un ejemplo
(≈ 0,96 MB como caso dorado); su entrada se publica como receta en `portal/INTEGRATION.md`
(fase 6, U-34). Todos los ejemplos se regeneran con la 2.0 y congelan los valores redondeados
(D-63 (6)). Nota para el portal, de bajo riesgo: el portal compara los casos dorados con
`REL_TOL = 1e-9` (`kit 04 §2`); con listas al milímetro, un valor que cayera a menos de ≈ 10⁻¹³ m
de un empate de redondeo podría salir 1 mm distinto en otra versión de `numpy` y romper esa
tolerancia. La probabilidad es del orden de 10⁻⁶ por caso dorado; si ocurre, el diagnóstico es
inmediato (un valor que difiere exactamente 0.001) y se trata como hallazgo de integración
(`kit 04 §4`). Las versiones de `numpy` con que se generan los ejemplos se anotan en ellos.

## 6. Estrategia de verificación hidráulica (`kit 01 §9`)

`hie-verifier` la usa tal cual. «Caso Excel» = entradas de la tabla de F1 con N = 20, T = 20 s.
«Caso sin fricción» = HU-1.1 crit. 3.

**Nota de tolerancias desde la 2.0 (U-39, U-29).** Las tolerancias de la tabla son de **verificación
del método** y se aplican a los valores de precisión completa: los arrays internos de `MocResult`
(fases 1, 3 y 4) y los escalares de la respuesta. Cuando una prueba lee una **lista de la
respuesta** de `solve()`, que llega a 3 decimales, la tolerancia efectiva es la de la tabla
**+ 0.0005 m** (o L/s) si compara la lista con una referencia sin redondear, y **0.001 m + 10⁻⁹ m**
si compara una diferencia de listas redondeadas con otra lista redondeada (regla (c) de F1,
«Precisión de las listas de salida»). Las igualdades de «mismo valor» (V-19) son **exactas**. Las
tolerancias de 10⁻⁶ m sobre listas que exigía la 1.0 a través de `solve()` (p. ej. la prueba de
F1-02) pasan a los arrays internos o a la tolerancia efectiva.

| ID | Método | Caso de referencia | Fuente | Tolerancia |
|---|---|---|---|---|
| V-01 | Darcy-Weisbach, régimen (M2–M3) | Caso Excel: V₀, h_f, H(x) | analítica [WS] §3; hoja del Excel | V₀ ± 0.001 m/s; h_f ± 0.01 m; H(500) = 96.60 ± 0.01 m; además rel. 10⁻¹² contra la fórmula |
| V-02 | MOC + contornos, sin fricción | Caso sin fricción, cierre en un paso | Joukowsky [Jk], [WS] §1.2 | H_v = 244.21 ± 0.01 m (0.05 < t < 2.0 s); −44.21 ± 0.01 m (2.05 < t < 4.0 s); Q_dep = −100 ± 0.1 L/s (1.05 < t < 3.0 s) |
| V-03 | MOC, sin fricción, ley arbitraria | Ley del Excel y ley lineal 3 s con f = 0 | Allievi M19 [Al], [WS] cap. 1 | H_v en todos los pasos ± 10⁻⁶ m |
| V-04 | Independencia de malla sin fricción | Caso sin fricción con N = 20 y N = 40 | idem V-02 | `head_valve_max_m` ± 0.01 m en ambos |
| V-05 | MOC con fricción (fidelidad) | Caso Excel | `tests/reference/excel_case.json` (hojas `2_Malla_MOC` y `4_Validacion` recalculadas en Excel, U-28) | **H ± 10⁻⁶ m y Q ± 10⁻⁶ L/s** en los 21 nodos y los 401 pasos (U-29); extremos ± 10⁻⁶ m e instante exacto: H_v máx = 242.76384 m en t = 2.00 s, H_v mín = −37.89904 m en t = 4.00 s, H_v(0) = 93.19944 m; máximo y mínimo de toda la tubería = los de la válvula. Las tolerancias de HU-1.1 crit. 1–2 (± 0.1 m, ± 0.05 m) siguen siendo el criterio de aceptación de la historia; esta es la de verificación, más estricta. **2.0**: ± 10⁻⁶ sobre `MocResult`; a través de `solve()`, listas ± (0.0005 + 10⁻⁶) m o L/s y extremos escalares ± 10⁻⁶ m |
| V-06 | Celeridad / posición del frente | Caso sin fricción, t = 0.55 s | cinemática: frente a a·(t − Δt) de la válvula | H = 100 ± 0.01 m para x < 500 m; 244.21 ± 0.01 m para x > 500 m |
| V-07 | Causalidad | Caso Excel, t < L/a | — | Q_dep sin cambio ± 10⁻⁶ L/s |
| V-08 | Ley de cierre (M11) | HU-1.2 crit. 1–4 | interpolación lineal | ± 0.01 L/s; Tc exacto |
| V-09 | Invariancia de datum | Caso Excel con z = 50, H_dep = 150 | M13 | H = original + 50; presiones iguales, ± 10⁻⁶ m en escalares y `MocResult`; listas de `solve()` ± 0.001 m (HU-1.1 crit. 4, 2.0) |
| V-10 | Perfil (M13–M14) | HU-2.1 y HU-2.2 (perfil plano de 2 puntos, loma 40 m, vértice en 520 m, L = 1250 m) | identidades | ± 10⁻⁶ m sobre `MocResult`; loma: p_min(500) = p_min horizontal − 40 ± 10⁻⁶ m. **2.0**, a través de `solve()`: HU-2.1 crit. 2 y HU-2.2 crit. 3 con 0.001 m + 10⁻⁹ m; HU-2.2 crit. 1–2 con el escalar redondeado; HU-2.1 crit. 1 y 3, igualdad exacta (V-19) |
| V-11 | Joukowsky / Michaud / pulso | HU-3.4 crit. 1–2 | [Jk], [Mi]; `4_Validacion` (C11, C22, C27) | Caso Excel contra el JSON de referencia: ΔH_J = 144.2111 m, ΔH_MOC = 149.56440 m, `theory_deviation_pct` = 100·C27 = 3.712 %, todos a rel. 10⁻⁹ (U-29); `maneuver_type` = `rapid`, L_pulso = 250 m ± 10⁻⁹. Caso lento (sin hoja de referencia): ΔH_M contra la fórmula M16 a rel. 10⁻¹², y 28.84 ± 0.01 (HU-3.4 crit. 2) |
| V-12 | PN | HU-3.1 crit. 1–3 | M18 | `pn_head_m` ± 0.01; ratio ± 0.1 %. **2.0**: `pn_head_m` = PN·10⁵/(1000·9.81) a rel. 10⁻¹²; sin casos con otra ρ u otra g (U-40) |
| V-13 | Umbrales de checks y regla del rojo | HU-3.2 crit. 3–7, HU-3.3, HU-3.5; además la regla del rojo de §1.5 (D-60 (1) enmendada por D-63 (3)-(4)) en el caso Excel, la loma de V-10, un caso sin avisos, la receta de U-34 y **cuatro casos construidos en la banda** (PN y límite × los dos lados), con el umbral (`pn_bar` o `min_allowed_pressure_head_m`, este último en [−10.33, 0]) elegido entre el extremo global de precisión completa y su redondeo a 3 decimales | tabla §1.5 | presencia / ausencia exacta del código; `first_time_s` ± Δt; `min_allowed_pressure_head_m` de la respuesta = el enviado o −10.0. **Regla del rojo (U-36)**: (a) **aviso ⇔ cruce a precisión completa**, exacto: `PN_EXCEEDED` presente ⇔ `pressure_head_max_global_m` > `pn_head_m` ⇔ ∃j con la envolvente máxima de `MocResult` > `pn_head_m`; ídem `COLUMN_SEPARATION_RISK` con el mínimo y `min_allowed_pressure_head_m`. (b) **Campos del aviso a precisión completa**, iguales con `==`: `value_m`, `x_m` y `time_s` del aviso = `pressure_head_max_global_m`, `_x_m`, `_time_s` (o los del mínimo) = el extremo de `MocResult`; `limit_m` = el umbral; en al menos un caso `value_m` ≠ round(`value_m`, 3), para probar que no se redondea; round(`x_m`, 3) está en la lista `x_m` y `time_s` está en `time_s`. (c) `STEADY_NEGATIVE_PRESSURE` con `error` ⇒ `COLUMN_SEPARATION_RISK` presente. (d) **Toda discrepancia cae en la banda**, sobre las listas de `solve()`: si ∃j `pressure_head_max_m[j]` > `pn_head_m` y no hay `PN_EXCEEDED`, entonces 0 ≤ `pn_head_m` − `pressure_head_max_global_m` < 0.0005 m + 10⁻⁹ m; si hay `PN_EXCEEDED` y ninguna j cumple, 0 < `pressure_head_max_global_m` − `pn_head_m` ≤ 0.0005 m + 10⁻⁹ m; ídem con el mínimo y el límite (signos invertidos). Fuera de la banda, «∃j redondeada cumple ⇔ aviso» exacto. Los casos construidos muestran los dos lados (aviso sin tramo; j redondeada sin aviso) y que el aviso es el de precisión completa. Que la pantalla no dibuje el tramo sin aviso no lo puede probar el paquete: es del portal |
| V-14 | Amortiguamiento con fricción | Caso Excel | propiedad física [WS] §3 | máx. \|H_v − H_dep\| de cada periodo 4L/a ≤ el del periodo anterior (después de Tc) |
| V-15 | Régimen como punto fijo | Ley (0; Q₀), (5 s; Q₀), (6 s; 0) | M3 | H y Q sin cambio para t < 5 s, ± 10⁻⁹ |
| V-16 | Presupuesto de tiempo | Caso Excel y peor caso admitido (N = 200, 500 vértices, `MAX_STEPS` = 10 000), con y sin fotogramas | `kit 01 §6` | < 1 s (objetivo interno < 0.8 s, mediana de 5) |
| V-17 | Fotogramas | HU-4.1 crit. 1–4, HU-4.2 crit. 2 (enmendadas por D-57 y por la enmienda del 2026-11-15) | coherencia interna | Caso Excel, 401 fotogramas sin submuestreo: `frame_head_m` en x = L y L/2 frente a `head_valve_m` y `head_midpoint_m`, y en x = 0 frente a `reservoir_level_m` redondeado a 3 decimales, ± 10⁻⁹ m (en la práctica, iguales: V-19); presión derivada `frame_head_m` − `elevation_m` en x = L y L/2 frente a `pressure_head_valve_m` y `pressure_head_midpoint_m`, 0.001 m + 10⁻⁹ m (crit. 1). Sin submuestreo, máx./mín. en el tiempo de `frame_head_m` − `elevation_m` = `pressure_head_max_m` / `pressure_head_min_m`, 0.001 m + 10⁻⁹ m (crit. 2). Las claves `frame_pressure_head_m` y `frame_flow_lps` **no existen** en la respuesta, con `include_frames` verdadero o falso, y `frame_x_m` = `x_m` elemento a elemento (crit. 3). Frente de onda a t = 0.55 s como V-06, sobre `frame_head_m` (crit. 4). Con submuestreo: n_fotogramas ≤ min(1001, ⌊50 000 / n_progresivas⌋) − 1 (U-10, D-65 (1); receta de U-34: 70), primer y último fotograma exactos, cada `frame_time_s` está en `time_s`, envolventes sobre todos los pasos. **Invariantes de D-64 (3)** (§1.4, U-42), en el caso Excel, un perfil genérico y la receta de U-34 (submuestreada): `frame_x_m` == `x_m` (listas idénticas); para todo k y j, \|(`frame_head_m[k][j]` − `elevation_m[j]`) − r(H − z)(x_j, t_{i_k})\| ≤ 0.001 m + 10⁻⁹ m con H y z de precisión completa (`MocResult`); `time_s[i_k]` == `frame_time_s[k]`, con i_k = k·`frame_stride` salvo el último fotograma (i = `n_steps`); en x = L y L/2, presión derivada frente a `pressure_head_valve_m[i_k]` y `pressure_head_midpoint_m[i_k]` ≤ 0.001 m + 10⁻⁹ m para **todo** k, incluido el último del caso submuestreado; misma cota en todos los campos de presión: \|`head_initial_m` − `elevation_m` − `pressure_head_initial_m`\|, \|`head_max_m` − `elevation_m` − `pressure_head_max_m`\| y \|`head_min_m` − `elevation_m` − `pressure_head_min_m`\| ≤ 0.001 m + 10⁻⁹ m en toda j |
| V-18 | Tamaño de petición y respuesta | Peor caso de U-34 (receta determinista y barrido), entrada adversaria de magnitud (U-34 (3b), receta determinista) y caso Excel | D-57 (1), (10); D-65 (3)-(4); D-48 | Medido en bytes, sin tolerancia: respuesta de la receta **y** de la entrada adversaria con `include_frames: true` ≤ 3 500 000 B cada una, en la mayor de las dos serializaciones de U-34; la adversaria con ≥ 20 B por número de media; petición del peor caso ≤ 65 536 B. Además, la cota analítica de U-34 (3b) (números × 25 B + estructura) ≤ 3 500 000 B con el tope vigente: es el techo para toda entrada admitida y se publica, pero D-57 (1) solo se da por cumplido con la guarda de D-57 (2) del portal en verde, no con la cota ni con estas mediciones (D-65 (4)); las dos recetas son mediciones concretas, no el máximo (F5R-01). Desde el paquete instalado en la fase 6 |
| V-19 | Precisión de la serialización (U-39) | HU-4.2 crit. 3–4; HU-1.3 crit. 1; HU-2.1 crit. 1 y 3; HU-4.1 crit. 1 en x = L y L/2; caso del Excel, receta de U-34 y caso de HU-4.2 crit. 4 (L = 100 m, a = 1500 m/s, N = 200, Δt = 1/3000 s, duración por defecto → 8 500 pasos) | U-39 | Exacto, sin tolerancia: cada valor de las listas de §1.4 en m, m.c.a. y L/s es igual a su propio redondeo a 3 decimales; `time_s`, `frame_time_s` y los escalares son los de precisión completa (iguales a los de `MocResult` o a la fórmula); `head_valve_m[0]` = `head_initial_m[-1]`; perfil frente a horizontal con L = 1000 m, series de H y Q y envolventes de H en los nodos idénticas; perfil de dos puntos idéntico a horizontal; `frame_head_m` en x = L y L/2 idéntica a las series. En el caso de Δt = 1/3000 s, paso de `time_s` = Δt ± 10⁻⁹ s, `time_s` y `frame_time_s` estrictamente crecientes y cada `frame_time_s` en `time_s`. Ninguna lista lleva `-0.0` |

## 7. Decisiones que se solicitan al portal

Detalle en `portal/DECISION-REQUESTS.md`. DR-1 … DR-6 resueltos el 2026-11-14 (commit `2466321`
del portal). DR-7 … DR-10 (enmienda del 2026-11-15) resueltos el 2026-11-15 (D-63 … D-66,
alternativa (a) en los cuatro). DR-7, DR-8 y DR-9 eran bloqueantes para la nueva G4; **ningún
pedido queda abierto**. Las condiciones que añadieron D-63 … D-65 están incorporadas en §1.4,
§1.5, §2, §5 y §6; lo que queda para la pantalla y la construcción está en la sección «Pendiente
tras D-63 … D-66» de `portal/DECISION-REQUESTS.md`.

| DR | Pregunta | Bloquea | Estado | Efecto en este plan |
|---|---|---|---|---|
| DR-1 | ¿Se construye en el portal el panel «Transitorio» del prototipo de G3: barra de reproducción común a cuatro gráficos ECharts en pestañas, con salto al instante desde los gráficos y los avisos? | no — pantalla; el contrato F4 se entrega igual (corte R3) | resuelto — **D-58** (a) | Capa 1 sin cambios: los avisos ya llevan instante (§1.5, U-36). El texto de fase (D-58 (4), U-32) lo retiró D-66 (DR-10). Resto: etapa 3 |
| DR-2 | ¿Qué tamaño máximo admite el portal para la serie de fotogramas en la respuesta de `solve`? | **sí** — fija topes y forma de F4 en la Capa 1 | resuelto — **D-57** (a) con techo 3,5 MB, 100 000 celdas, `MAX_STEPS` = 10 000, sin `frame_flow_lps` | Sí: §1.3, §1.4, §2, fases 2, 5 y 6, V-16 … V-18; U-09, U-10, U-33, U-34 |
| DR-3 | ¿Cabe la pantalla con el reproductor en `solver-2col`, o se quiere un lienzo dominante fuera de catálogo? | no — integración de la pantalla | resuelto — **D-59** (a), sticky solo en ≥ lg | Ninguno (etapa 3) |
| DR-4 | ¿Se admite la asignación de colores del panel «Transitorio» con tokens existentes, sin escala de color por presión, incluidos cuatro usos que se apartan del rol documentado del token? | no — integración de la pantalla | resuelto — **D-60** (a) + corrección (b) en los cuatro usos | Rojo solo en el cruce, con el predicado de los avisos `danger`: §1.5, V-13; eco de `min_allowed_pressure_head_m` (U-35). Colores: etapa 3 |
| DR-5 | ¿Cómo se muestran las fórmulas de Joukowsky / Michaud, sin renderizador LaTeX en el portal? | no — integración de la pantalla | resuelto — **D-61** (a), HTML semántico y Unicode | §3: ninguna dependencia de frontend. Resto: etapa 3 |
| DR-6 | ¿Tiene la app análisis de IA? | no | resuelto — **D-62** (a), sin IA en v1 | Ninguno en la Capa 1; sección `ai` de `ui-spec.json` ausente o vacía (etapa 3) |
| DR-7 | ¿Admite el portal que el paquete entregue a 3 decimales las listas de salida en m y L/s, frente a «sin redondeo» de D-57 (9)? | **sí** — precisión de la Capa 1 2.0 | resuelto — **D-63** (a), con el rojo leído de `checks` (enmienda D-57 (9) y D-60 (1)) | U-39 y U-41 vigentes (§1.2, §1.4); regla de comparación en §1.4 (D-63 (5)); regla del rojo reescrita: marcador y extremo en `critical` desde el aviso, tramo solo con aviso, único desacuerdo «aviso sin tramo» en la banda (§1.5, U-36, V-13); casos dorados con valores redondeados (fase 5, fase 6, D-63 (6)) |
| DR-8 | ¿Admite el portal retirar `frame_pressure_head_m` y derivar en la pantalla p/γ(x, t) = `frame_head_m` − `elevation_m`, frente a las dos matrices de D-57 (4)? | **sí** — forma de la Capa 1 2.0 | resuelto — **D-64** (a), con la resta como invariante de contrato (enmienda D-57 (4)) | §1.4 sin `frame_pressure_head_m`; invariantes de D-64 (3) declarados en §1.4 y probados en V-17 (U-42); `frame_x_m` se mantiene (decisión del dueño, U-42); fase 6 los publica en `portal/INTEGRATION.md` |
| DR-9 | Con una sola matriz `frame_*`, ¿qué tope de fotogramas rige: el de hoy, min(1001, ⌊50 000 / n⌋), o el presupuesto de 100 000 celdas de D-57 (4) aplicado a la única matriz? | **sí** — tope de la Capa 1 y guarda de D-57 (2) | resuelto — **D-65** (a), con dos recetas medidas (enmienda D-57 (4), precisa D-57 (1)-(2)) | U-10 vigente sin cambio de fórmula (§1.4); §2: la cota absoluta es el techo y se publica, pero D-57 (1) se da por cumplido solo con la guarda de D-57 (2) del portal en verde, que mide las dos recetas; U-34 (3), (3b) y (6) enmendadas (fase 5, V-18); F5-01 se cierra por esta vía |
| DR-10 | ¿Acepta el portal que el panel «Transitorio» salga sin el texto de fase que aprobó D-58 (1) y (4)? | no — pantalla; la Capa 1 no cambia | resuelto — **D-66** (a); D-58 (4) sin efecto | Ninguno en la Capa 1 (los tres tiempos se quedan como indicadores); U-32 retirada. Una guía de fase futura entraría como dato de la Capa 1, con su pedido (D-66 (2)) |

### Correspondencia con las «Preguntas para el plan» de la épica

| # | Pregunta | Resolución |
|---|---|---|
| 1 | Reproductor | DR-1 → D-58 (y DR-3 → D-59, DR-4 → D-60) |
| 2 | Tamaño de F4 | DR-2 → D-57; U-10, U-33, U-34 |
| 3 | Rangos de N, duración, presupuesto | U-09 (`MAX_STEPS` = 10 000, D-57), §2; N par 10–200 confirmado |
| 4 | Layout | DR-3 → D-59: `solver-2col` |
| 5 | Fórmulas LaTeX | DR-5 → D-61: HTML y Unicode |
| 6 | Dependencias | §3: ninguna nueva (`numpy` disponible, `kit 07 §1`) |
| 7 | IA | DR-6 → D-62: sin IA en v1 |
| 8 | Extensibilidad / `scenario` | U-15, §1.1 |
| 9 | Unidades de entrada | U-06: L/s y mm |
| 10a | Redondeo a 3 decimales (D-57 (9)) | **DR-7 → D-63**; U-39; regla del rojo desde `checks`: U-36 |
| 10b | Retirar `frame_pressure_head_m` (D-57 (4)) | **DR-8 → D-64**; `SCHEMA_VERSION` `"2.0"` (U-15, U-37); invariantes U-42 |
| 10c | Retirar el texto de fase (D-58 (1) y (4), U-32) | **DR-10 → D-66**; U-32 retirada |
| 10d | Presupuesto de celdas con una sola matriz | **DR-9 → D-65**: la fórmula de hoy (U-10), con dos recetas medidas (U-34) |
| 10e | ρ y g fijos | Sin pedido (regla central del kit). U-40: 422 con mensaje propio si la petición los trae; sin eco en la respuesta; cambio de forma ya cubierto por la 2.0 |
| 10f | Medición de tamaños | U-34 enmendada: se repite en la fase 5 con la 2.0, más la entrada adversaria (3b), las dos como recetas deterministas que también mide la guarda del portal (D-65 (3)); las cifras de la 1.0 quedan como registro |

## 8. Hallazgos para el kit

(Se siguen las reglas tal cual; se anotan para `software-architect` del portal.)

- **`kit 01 §4`** no dice cómo van las series bidimensionales (fotogramas × progresivas). El plan
  usa listas de filas por fotograma alineadas con un eje `x_m` (U-11). Convendría una regla.
- **`kit 08 §2`** no tiene categoría para «tamaño / transporte de la respuesta»; DR-2 usa
  `funcionalidad`.
- **`kit 02 §1`** dice «el mismo prefijo en las cuatro clases» y a la vez que `ServiceError` es
  «solo si» hay servicio externo; el plan define tres clases. Una aclaración evitaría dudas.
- **Tamaño de respuesta**: el kit no lo regula y producción corta cuerpos > 4,5 MB (D-47) sin que
  el CI lo vea; D-57 lo resolvió para esta app. Una regla general en `kit 01 §6` (techo, cómo se
  mide, con qué serializador) evitaría repetir el pedido. D-57 expresa el techo en «MB» sin decir
  si son 10⁶ o 2²⁰ B; el plan toma 10⁶ B, lo más estricto (U-34).
- **`06-ui-spec.schema.json` no tiene dónde declarar fórmulas ni cómo se presentan** (etapa 3).
  D-61 fijó ΔH = a·V₀/g y ΔH = 2·L·V₀/(g·T_c) en HTML con `<var>` / `<sub>` y desglose de variables
  con unidades, pero el esquema no tiene un campo para la fórmula ni para su desglose: quedaron solo
  como `symbol` Unicode en los `kpis` de `portal/ui-spec.json` y, completas, en
  `portal/prototype.html`, que es desechable (`kit 04 §1`). El frontend tendrá que leerlas del
  prototipo o de D-61. Convendría un campo `formula` (expresión y variables con unidad) en los kpis
  o un bloque propio.
- **`06-ui-spec.schema.json` no tiene dónde declarar acciones dentro de un aviso de `checks`**
  (etapa 3). El botón «Ir a t = … s en el transitorio» que D-58 mandó añadir (qué instante usa cada
  código, a qué fotograma salta, qué pestaña abre, cuándo no se muestra) quedó descrito en texto
  libre en `charts[].interactions` del gráfico `perfil-envolventes`, lejos de la sección de
  `checks` donde vive el botón. Convendría un campo `actions` por código en la sección de `checks`
  del esquema.
- **`kit 01 §4` no dice nada de la precisión numérica de la salida** (enmienda del 2026-11-15).
  Un `float64` con todas sus cifras ocupa ≈ 18 B en JSON frente a ≈ 7 B a 3 decimales; en una
  respuesta con series largas es la mayor palanca de tamaño, y D-57 (9) la cerró para esta app sin
  regla general. Convendría que el kit diga quién decide la precisión, que el redondeo es del
  paquete y nunca del router (`kit 03 §1`), y qué listas no se redondean (tiempos con Δt no
  múltiplo de la resolución).
- **Los techos de tamaño y las entradas sin rango.** D-57 (1) habla del «peor caso que admiten los
  topes del paquete», pero campos como `reservoir_level_m` no tienen rango (pueden valer 10¹⁵⁰) y
  el peor caso en bytes es entonces el de magnitudes absurdas (F5-01). El plan lo resuelve con una
  cota analítica (25 B por número, U-34 (3b)); el kit podría pedir esa cota en lugar de una receta.
- **`06-ui-spec.schema.json` no tiene cómo declarar una serie derivada** (p/γ por fotograma =
  `frame_head_m` − `elevation_m`, DR-8): `contract_path` apunta a un campo, no a una expresión, y
  `convert` es solo de unidades. La etapa 3 tendrá que describirlo en `interactions`.
- **`06-ui-spec.schema.json` no tiene cómo declarar un elemento de gráfico condicionado a un aviso
  de `checks`** (D-63 (3)-(4)): el marcador del cruce sale de un aviso (`checks[]` con un `code`
  dado, sus `x_m` y `value_m`) y el tramo se dibuja solo si ese aviso existe. `contract_path` apunta
  a un campo, no a «el elemento de `checks` con `code` = X», ni admite una condición de
  visibilidad. La etapa 3 tendrá que describirlo en `interactions`.

Para el portal (no es del kit; va a `portal/INTEGRATION.md` en la fase 6):

- **D-64 (2) indexa la serie de la válvula con k·`frame_stride`.** Es exacto en el fixture que
  nombra (caso del Excel, sin submuestreo), pero con submuestreo el último fotograma es el paso
  `n_steps`, no k·`frame_stride` (receta de U-34: 69·145 = 10 005 ≠ 10 000, índice fuera de
  rango). La regla general es el índice i_k con `time_s[i_k]` == `frame_time_s[k]` (§1.4,
  invariante 3). No cambia la decisión ni el contrato; conviene que la función o su test lo tengan
  en cuenta si algún día usan un caso submuestreado.

---

## Changelog

| Fecha | Cambio |
|---|---|
| 2026-11-14 | Borrador inicial para G2 (`hie-architect`, kit 3.0.0). |
| 2026-11-14 | Lectura del Excel (fórmulas con openpyxl; copia recalculada en Excel por COM, original intacto). U-02 y U-17 pasan a vigentes (M10, M12, `theory_deviation_pct`). Fase 0 reescrita: el `.xlsx` no tiene valores en caché, la referencia se genera una vez por COM y se versiona con su procedencia (U-28, `pywin32` solo dev). V-05 y V-11 endurecidas a 10⁻⁶ m / rel. 10⁻⁹ (U-29). Retirado de las confirmaciones de G2 el punto 6 de entonces, que dependía de la lectura del Excel; la lista se renumeró y el punto 6 actual (tamaño de la respuesta) es otro, vigente (aclaración del 2026-11-14, ver la última entrada). Sin cambio de contrato. |
| 2026-11-14 | Coherencia tras G3 (prototipo aprobado). Cabecera: decisiones internas hasta U-32 (U-30 reformulación de DR-1 y DR-4; U-31 `frame_flow_lps` provisional; U-32 texto de fase calculado en el frontend). §7: preguntas de DR-1 y DR-4 alineadas con su redacción nueva en `portal/DECISION-REQUESTS.md`; DR-3 y DR-4 ya no dependen de DR-1 ni de la etapa 3 (aprobada) y pasan a «integración de la pantalla»; DR-2 cita sus dos palancas (`MAX_STEPS`, `frame_flow_lps`); fila 4 de la correspondencia con la épica anota el layout de G3. Estado del plan y Capa 1 sin cambios; DR-1 … DR-6 siguen `abierto`. |
| 2026-11-14 | Más coherencia tras G3. Estado: de «borrador (para la puerta G2)» a **aprobado** (G2 del 2026-11-14), pendiente de congelarse en G4; misma corrección en la cabecera de `portal/DECISION-REQUESTS.md`. §7: DR-5 pasa de «etapa 3» a «integración de la pantalla», como DR-3 y DR-4 (también en `DECISION-REQUESTS.md`). Parte 1, punto 6 de las confirmaciones de G2: se mantiene, porque es el punto que el dueño aprobó en G2 (el retirado era el 6 de antes de renumerar, que dependía de la lectura del Excel), y ahora cita también la palanca `frame_flow_lps` (U-31); se aclara la redacción de la entrada del changelog que lo retiraba. Capa 1 sin cambios. |
| 2026-11-14 | **G2 reabierta: incorporación de D-57 (DR-2).** Estado a **borrador**, pendiente de reaprobación. Capa 1: `frame_flow_lps` retirado de `SolveResponse` sin opción para pedirlo (U-33, sustituye a U-31); tope de fotogramas min(1001, ⌊50 000 / n_progresivas⌋) con dos matrices (U-10 vigente); `MAX_STEPS` = 10 000 (U-09 vigente) con 422 de HU-1.6 crit. 13, T_max truncada y variantes de mensaje (duración por defecto, duración mínima mayor que T_max). §2 recalculado: tiempo del peor caso ≈ 0.25–0.35 s (antes 0.5–0.7 s); respuesta del peor caso ≈ 3,3 MB `[calculado]` (antes ≈ 5 MB) frente al techo de 3,5 MB; petición ≈ 21–26 KB frente a 64 KiB; caso del Excel ≈ 0,35 MB (antes ≈ 0,5 MB). Fase 5 con las mediciones obligatorias de D-57 (1) y (10) y protocolo U-34; fase 6 vuelca las cifras y la receta del peor caso a `portal/INTEGRATION.md`; V-17 enmendada (HU-4.1 crit. 1 sin caudal; sin clave `frame_flow_lps`), V-18 nueva. Ejemplos: solo el del Excel con serie (D-57 (8)), nuevo ejemplo de error por `MAX_STEPS`. M14 y U-07: Q ya no se interpola en los vértices. |
| 2026-11-14 | **Incorporación de D-58 … D-62.** Capa 1: eco `min_allowed_pressure_head_m` en `SolveResponse` (U-35) y predicado por progresiva del cruce en rojo, igual al de los avisos `danger` (D-60, U-36, V-13); los avisos ya llevan instante para «Ir a t = … s» (D-58), sin campos nuevos. §3: D-61 sin dependencia. §7: DR-1 … DR-6 resueltos, con su efecto en el plan. §8: hallazgo sobre el tamaño de respuesta. Parte 1 reescrita en «Lo que el portal decidió» y «Puntos que el dueño debe confirmar al reaprobar G2» (3 y 6 cambiados por D-57; 7 y 8 nuevos). `SCHEMA_VERSION` sigue en `"1.0"`: el contrato no está congelado. Lo de pantalla (D-58 … D-62 en `ui-spec.json` / `prototype.html`) queda para la etapa 3. |
| 2026-11-14 | **Congelado (G4), `hie-architect`, kit 3.0.0.** Comprobado antes de congelar: DR-1 … DR-6 `resuelto` con su D-NN (D-57 … D-62) y ningún `DR` bloqueante `abierto` (`kit 08 §1`); G1, G2 y G3 reaprobadas el 2026-11-14 con D-57 … D-62; los 73 `contract_path` de `portal/ui-spec.json` están en §1, y el límite se lee de `response.min_allowed_pressure_head_m` (U-35). Estado a **congelado**; **`SCHEMA_VERSION = "1.0"` confirmado como versión congelada** (§1.1), con la regla de enmienda posterior (U-37, `kit 01 §8`). Puestos al día los textos que G2 ya había resuelto, sin cambiar el contrato: Parte 1, riesgos 2 y 3 y la sección de confirmaciones, que pasa a «Puntos que el dueño confirmó en G2» (U-03, U-09 sin recorte de la duración por defecto, U-14, U-21, U-22, regla de ajuste de U-34, U-33, U-35); §1.3, la nota de φ ya no dice «punto abierto». §8: dos hallazgos de la etapa 3 sobre `06-ui-spec.schema.json` (fórmulas de D-61; acciones dentro de un aviso, «Ir a t» de D-58). Capa 1 sin cambios respecto a la reaprobación de G2. |
| 2026-11-15 | **Enmienda tras G4 (`hie-architect`, kit 3.0.0). Estado: de congelado a borrador**, pendiente de G2 y de una nueva G4. **Motivo**: decisiones del dueño del 2026-11-15 a partir del desglose del tamaño de la respuesta medida en la fase 5 (3 156 607 B en la receta: fotogramas 57 %, series 40 %, perfiles 3 %; ≈ 18 B por número), recogidas en las historias reaprobadas en G1 el 2026-11-15. **Capa 1 → `SCHEMA_VERSION` `"2.0"`** (mayor, U-15, U-37; §1.1). Cambios: (1) precisión — listas en m, m.c.a. y L/s a 3 decimales al construir la respuesta, `time_s`, `frame_time_s` y escalares completos, cálculo y `checks` con precisión completa (§1.2, §1.4, U-39; DR-7 por D-57 (9)); (2) `frame_pressure_head_m` retirado, p/γ por fotograma = `frame_head_m` − `elevation_m` en la pantalla (§1.4; DR-8 por D-57 (4)); (3) tope de fotogramas: se propone mantener min(1001, ⌊50 000 / n⌋) con una sola matriz, porque así el techo de 3,5 MB se cumple para toda entrada admitida (cota absoluta ≤ 3,2 MB, §2; U-10; DR-9); (4) texto de fase fuera de v1 (U-32; DR-10 por D-58, no bloqueante; la Capa 1 no cambia); (5) `density_kgm3` y `gravity_ms2` fuera de `SolveRequest`, ρ = 1000 kg/m³ y g = 9.81 m/s² constantes privadas, 422 con mensaje propio si llegan, sin eco (§1.2, §1.3, M5, M18; U-40; sin pedido, regla central del kit). Efectos: predicado del cruce en rojo con banda de ±0.0005 m (§1.5, U-36, V-13); progresivas escalares localizadas en `x_m` redondeándolas (U-41); §2 con las cifras medidas de la 1.0, el estimado de la 2.0 (≈ 0,96 MB) y la cota absoluta; §5: fases 0–4 sin rehacer (pruebas a través de `solve()` con tolerancias ajustadas), **fase 5 rehecha** (precisión, entrada 2.0, serie, mediciones con la entrada adversaria), **fase 6** con contenido nuevo en `portal/INTEGRATION.md` (cambios 1.0 → 2.0, constantes, precisión, F5-01); §6: nota de tolerancias, V-05, V-09, V-10, V-12, V-13, V-17 y V-18 enmendadas, **V-19 nueva**; ejemplos: uno nuevo de campo retirado y todos regenerados; §7: DR-7 … DR-10 y la pregunta 10 de la épica; §8: tres hallazgos. Pendientes corregidos: la fila de la fase 3 decía «H y Q en vértices» (M14 y U-07: Q no se interpola desde D-57) y la cabecera citaba «U-01 … U-37» aunque existía U-38 (ahora U-01 … U-41); `_frames.py` y `_constants.py` en la estructura (U-01). |
| 2026-11-15 | **G2 reaprobada** con la enmienda (`portal/HANDOFF.md`): el dueño aceptó la banda de ±0.0005 m de DR-7 (a) y el tope de DR-9 (a). Sin cambios en el plan. |
| 2026-11-15 | **Incorporación de D-63 … D-66 y congelado (nueva G4), `hie-architect`, kit 3.0.0.** Comprobado antes de congelar: DR-1 … DR-10 `resuelto` con su D-NN (D-57 … D-66), ningún `DR` bloqueante `abierto` (`kit 08 §1`); G1, G2 y G3 reaprobadas el 2026-11-15 con la enmienda. Las cuatro decisiones eligen la alternativa (a) que el plan proponía: **la forma de la Capa 1 2.0 no cambia** respecto al borrador. Cambios por decisión: **D-63** (DR-7) — U-39 y U-41 vigentes; §1.4 con la regla de comparación de D-63 (5) (lista frente a escalar: redondear el escalar o tolerancia 0.0005 m); **§1.5 reescrito**: el marcador del cruce y la sustitución del extremo global por `--color-chart-critical` se leen del aviso `danger` (`PN_EXCEEDED` para el PN, `COLUMN_SEPARATION_RISK` para el límite; `STEADY_NEGATIVE_PRESSURE` sin marcador propio), con sus `x_m`, `time_s` y `value_m` a precisión completa e idénticos al extremo global; el tramo, opcional, sobre la envolvente redondeada pero solo con aviso; nunca rojo sin aviso; único desacuerdo, aviso y marcador sin tramo en la banda de 0.0005 m (U-36); **V-13 reescrita** con lo que el paquete puede probar (aviso ⇔ cruce a precisión completa; campos del aviso = extremo global, sin redondear; régimen en `error` ⇒ `COLUMN_SEPARATION_RISK`; toda discrepancia con las listas redondeadas cae en la banda, con cuatro casos construidos); fases 5 y 6: casos dorados con valores redondeados (D-63 (6)) y nota de riesgo con `REL_TOL`. **D-64** (DR-8) — invariantes de contrato en §1.4 (`frame_x_m` == `x_m`; p/γ = `frame_head_m[k][j]` − `elevation_m[j]` con la misma cota que `pressure_head_*`; fotograma k ↔ paso i_k) y en V-17, con la tolerancia garantizada 0.001 m + 10⁻⁹ m (U-42); `frame_x_m` se mantiene por decisión del dueño (U-42); fase 5.3 sustituye las pruebas de la 1.0 que leían `frame_pressure_head_m`. **D-65** (DR-9) — U-10 vigente sin cambio; §2: la cota absoluta no cierra nada por sí sola, el techo y F5-01 se cierran solo con las dos mediciones en verde; U-34 (3b) con receta determinista y ≥ 20 B por número; **U-34 (6) cambiada**: si una medición supera 3,5 MB, la fase se detiene y se abre un `DR` (antes se bajaba el presupuesto sin pedir), porque el tope ya es decisión del portal; fase 6: `INTEGRATION.md` con las dos recetas, las dos cifras y la cota. **D-66** (DR-10) — U-32 retirada; §7 DR-1 sin texto de fase. Resto: cabecera, Parte 1 (decisiones del portal, puntos que el dueño acepta en esta G4), §1.1 (versión congelada `"2.0"`), §7 (DR-7 … DR-10 resueltos, correspondencia con la épica), §8 (un hallazgo para el kit y una nota para el portal sobre el índice k·`frame_stride` de D-64 (2)). Estado a **congelado**; **`SCHEMA_VERSION = "2.0"`**. |
| 2026-11-15 | **Adopción del kit 3.0.1 (F6-04, `doc/verification/09-fase-6.md`), `hie-architect`, tras la entrega (pin `a04431e`, `v0.1.0`).** Corrección de registro: sin cambio de la Capa 1 ni de su forma (`SCHEMA_VERSION` sigue en `"2.0"`, `kit 01 §8`), del código, de los ejemplos ni del pin; sin DR. Revisado el changelog del kit entre 3.0.0 y 3.0.1: *patch* (DT-33) que solo reescribe `kit 03 §3` (IA: D-53/D-55, `AppEntry.aiDomain`, catálogo `domain` = `"channel"`) y `kit 03 §1` (código en los errores de `/api/ai/analyze`; D-26 ya ejecutada en la ruta), sin cambiar ninguna regla para el upstream. Efecto en el plan: ninguno. Las dos citas a `kit 03 §1` (§1.1, `/health` e import sin efectos; §8, redondeo en el paquete y no en el router) siguen diciendo lo mismo, y la app no tiene IA (D-62, §7 DR-6). Cabecera: `kit` 3.0.0 → 3.0.1; `portal/HANDOFF.md`, fila «Kit con el que se diseñó», ídem, con nota fechada. |
| 2026-11-15 | **U-34 frente a D-65 (4) (F6R-01, `doc/verification/09-fase-6.md`), `hie-architect`.** Corrección de registro, sin cambio de forma ni de números del contrato (`SCHEMA_VERSION` `"2.0"`), sin DR. `doc/DECISIONS.md` U-34 hacía depender el techo de D-57 (1) para toda entrada admitida y el cierre de F5-01 de «las dos mediciones en verde»; D-65 (4) lo hace depender de la **guarda de D-57 (2) del portal** en verde, y la variante con datum negativo (2 844 325 B) muestra que las dos recetas no acotan toda entrada. Se alinea con la «Lectura» del tamaño de `portal/INTEGRATION.md`, que ya era correcta. El plan arrastraba la misma formulación y se corrige en: Parte 1, fila de la fase 5 («la respuesta más grande posible pesada en báscula») y riesgo 3 («el techo solo se da por cumplido si los dos pasan la báscula»); §2, «Cota absoluta» (ahora con la cota medida de 3 285 874 B como techo, las mediciones como recetas concretas y la frase de D-65 (4)); §5, fase 6 (a) (cierre de F5-01 del lado del upstream con las mediciones y la cota, salvedad de F5R-01); §6, V-18; §7, fila DR-9. Los criterios de «hecho» de las fases 5 y 6 no cambian en lo que miden (las mismas mediciones y los mismos topes), solo en cómo se leen. |
| 2026-11-15 | **Erratas señaladas por el dueño, comprobadas: ya estaban corregidas**, sin cambio. La fila de la fase 3 en §5 dice «interpolación de z y de H en los vértices (Q no: M14, U-07)», coherente con M14 y U-07; la corrección se hizo en la enmienda del 2026-11-15 (entrada de ese día, «Pendientes corregidos»). La cabecera cita «U-01 … U-42» y la última fila de `doc/DECISIONS.md` es U-42 (la adopción del kit 3.0.1 y F6R-01 no añaden filas). |
