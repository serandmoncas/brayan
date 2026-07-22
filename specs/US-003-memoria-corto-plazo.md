## US-003 — El agente recuerda el hilo de la conversación
**Como** usuario del agente de bolsillo
**quiero** que recuerde lo que hablamos hace un momento en el mismo WhatsApp
**para** no tener que repetir contexto en cada mensaje (ej. "¿y a qué hora la programaste?").

**Valor:** es la promesa del Bloque D de la charla ("la gente cree que el agente no tiene memoria;
la tiene si tú se la das"). Hoy `src/memory/store.py` existe pero `orchestrator.py` nunca lo usa:
cada webhook manda `history=[]`, así que el agente "olvida" apenas responde.
**Prioridad:** alta   **Estimación:** S (1 ciclo)

### Criterios de aceptación (reglas de NEGOCIO)
- [x] CA1: si el usuario manda un segundo mensaje que depende del primero (ej. "¿y agrégale 2kg más?"),
      el agente recibe el turno anterior (usuario + respuesta) como contexto.
- [x] CA2: la ventana de contexto no crece sin límite: se trunca a `MAX_SHORT_TERM` turnos, para no
      saturar el contexto del LLM (reutiliza `short_term_window` ya existente).
- [x] CA3: la memoria es de un solo dueño (consistente con US-002): no se separa por remitente.

### Escenario Gherkin
  Dado  el usuario preguntó "cuánto vale la acción de Globant" y el agente respondió
  Cuando el usuario pregunta "¿y ayer cuánto valía?"
  Entonces el agente recibe en su historial el turno anterior (pregunta + respuesta).

### Restricciones
- No persiste a disco entre reinicios del proceso (alcance: "corto plazo" = hilo de la sesión activa).
  Persistencia entre reinicios queda fuera de este ciclo (no-objetivo).
- Reutiliza `short_term_window` de `src/memory/store.py`, no reimplementa la truncación.

### No-objetivos
- No se cubre memoria de largo plazo (`remember`/`recall`) conectada al webhook todavía — ya existen
  como funciones pero conectarlas a una lógica "el agente decide qué recordar" es otro ciclo.
- No se cubre historial multi-usuario.

### Trazabilidad
- commit: (pendiente)  ·  test: tests/test_orchestrator.py::test_webhook_passes_previous_turn_as_history
  ·  intención: sesión 2026-07-22
