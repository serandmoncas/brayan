## US-005 — El agente programa sus propios recordatorios (self-programming seguro)
**Como** dueño del agente de bolsillo
**quiero** pedirle "cada día a las 9 dame el valor de la acción X"
**para** que se dispare solo, sin que yo tenga que volver a preguntar.

**Valor:** es el momento "wow" de la demo (Paso 3: "el agente que se programa solo") y a la vez
el punto más sensible en seguridad — es exactamente lo que Jorge señala como riesgo si se hace mal.
**Prioridad:** alta   **Estimación:** S (1 ciclo)

### Criterios de aceptación (reglas de NEGOCIO)
- [x] CA1: el agente SOLO puede crear jobs que, a la hora indicada, vuelven a invocar al propio
      agente (`run_agent`) con un texto fijo — nunca ejecuta comandos del sistema ni evalúa texto
      arbitrario del usuario como código.
- [x] CA2: una hora inválida (formato incorrecto) responde un error claro, no crashea el proceso.
- [x] CA3: el código de la tool no contiene `eval`, `exec`, `os.system` ni `subprocess` en ningún
      camino (verificado por análisis estático del propio archivo, no solo por caja negra).

### Escenario Gherkin
  Dado  el orchestrator corriendo
  Cuando el usuario pide "mañana a las 9 quiero el valor de la acción X"
  Entonces se crea un job de scheduler que a esa hora vuelve a llamar al agente con ese texto,
  y el agente confirma "Recordatorio programado a las 09:00 ...".

  Dado  el usuario manda una hora con formato inválido
  Cuando se intenta programar
  Entonces el agente responde `[programar_recordatorio error] ...` sin caerse.

### Restricciones
- Whitelist implícita: el único punto de entrada del job es `run_agent(texto, history=[])`, que a
  su vez solo puede disparar tools ya registradas en `config/tools.json`. No hay ruta a ejecución
  de código arbitrario del usuario.
- El scheduler vive en memoria del proceso (`BackgroundScheduler`); no persiste entre reinicios
  (no-objetivo de este ciclo).

### No-objetivos
- No se cubre persistencia de jobs entre reinicios del proceso.
- No se cubre cancelar/listar recordatorios ya programados (solo creación).

### Trazabilidad
- commit: (pendiente, ver git diff)  ·  test: tests/test_tools.py::test_programar_recordatorio_runs,
  tests/test_tools.py::test_programar_recordatorio_no_arbitrary_execution  ·  intención: sesión 2026-07-22
