# /spec — Crear una especificación (contrato verificable)

Uso: `/spec <nombre-corto>`  ·  ej. `/spec enviar-correo-proveedor`

Crea `specs/US-NNN-<nombre>.md` desde la plantilla y te ayuda a llenarla.

## Qué hace Claude
1. Busca el siguiente número US libre en `specs/`.
2. Crea el archivo con la estructura de `specs/README.md`:
   - Historia (Como/quiero/para), Valor, Prioridad, Estimación.
   - **Criterios de aceptación como reglas de NEGOCIO** (no detalle técnico).
   - Escenario Gherkin si aplica.
   - Restricciones y No-objetivos.
   - Trazabilidad (commit/test/intención).
3. Pide la intención (el PROBLEMA, no la solución) y los criterios en lenguaje que el negocio entienda.
4. Recuerda: cada CA se mapea 1-a-1 a un test; el test afirma resultado de negocio.

$ARGUMENTS

> No construyas código hasta que esta spec exista y tenga al menos 2 criterios de aceptación.
