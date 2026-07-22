## US-001 — Buscar en internet desde el WhatsApp
**Como** usuario del agente de bolsillo
**quiero** preguntarle el valor de una acción o datos actuales
**para** recibir la respuesta sin abrir un navegador.

**Valor:** es la skill base que demuestra el "agente que resuelve el cómo"; la usan los casos de acción de Globant y resumen de noticias.
**Prioridad:** alta   **Estimación:** S (1 ciclo)

### Criterios de aceptación (reglas de NEGOCIO)
- [x] CA1: una consulta válida retorna texto con resultados relevantes (no vacío ni error).
- [x] CA2: si la búsqueda falla (sin red / timeout), el agente avisa con mensaje claro y NO se rompe.
- [x] CA3: la salida está truncada a `WEB_TRUNCATE_CHARS` para no saturar el contexto del LLM.

### Escenario Gherkin
  Dado  el agente conectado y sin caché
  Cuando el usuario pregunta "¿cuánto vale la acción de Globant hoy?"
  Entonces el agente responde un resumen con resultados de búsqueda legibles.

  Dado  el equipo sin conexión a internet
  Cuando el usuario hace cualquier búsqueda
  Entonces el agente responde "[buscar_web error] ..." sin caerse.

### Restricciones
- Idioma de mensajes: español.
- Límite de salida: `WEB_TRUNCATE_CHARS` (4000 por defecto).
- Sin ejecución de código del usuario; solo scrape de DuckDuckGo lite.

### No-objetivos
- No se cubre búsqueda por imagen ni paginación de resultados.

### Trazabilidad
- commit: inicial   ·  test: tests/test_tools.py::test_buscar_web_runs   ·  intención: sesión 2026-07-22
