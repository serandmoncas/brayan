## US-006 — Guardar un pedido/tarea en Google Sheets
**Como** dueño del agente de bolsillo
**quiero** pedirle por WhatsApp que anote algo en mi hoja de cálculo
**para** llevar registro de pedidos/entregas sin abrir Sheets (caso "fábrica de arepas / setas").

**Valor:** caso de uso objetivo #4 de la demo ("Guarda: entregar 2 bolsas de orellanas a Juan
David mañana").
**Prioridad:** media   **Estimación:** S (1 ciclo)

### Criterios de aceptación (reglas de NEGOCIO)
- [x] CA1: si faltan `GOOGLE_SHEET_ID`/`GOOGLE_CREDENTIALS_PATH`, el agente avisa claro y NO crashea.
- [ ] CA2: con credenciales reales de una hoja de prueba, guardar una fila se confirma y la fila
      aparece en la hoja. **BLOQUEADO:** no hay credenciales de Google Service Account disponibles
      en este ciclo. Queda como no-verificado con datos reales — solo hay mock de la ausencia de
      credenciales (CA1). Antes de confiar en esta tool en la demo en vivo, correrla una vez con
      credenciales reales de prueba.

### Escenario Gherkin
  Dado  `GOOGLE_SHEET_ID`/`GOOGLE_CREDENTIALS_PATH` sin configurar
  Cuando el usuario pide guardar un dato
  Entonces el agente responde `[guardar_sheets] faltan GOOGLE_SHEET_ID / GOOGLE_CREDENTIALS_PATH`.

### Restricciones
- Requiere una Service Account de Google con acceso de editor a la hoja destino (fuera del
  alcance de este repo generar esas credenciales).

### No-objetivos
- No se cubre lectura de la hoja ni actualización de filas existentes, solo `append_row`.

### Trazabilidad
- commit: (pendiente, ver git diff)  ·  test: tests/test_tools.py::test_guardar_sheets_without_creds
  ·  intención: sesión 2026-07-22 · **pendiente:** verificación con credenciales reales antes de la demo.
