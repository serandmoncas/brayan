## US-002 — Solo el dueño puede usar el agente por WhatsApp
**Como** dueño del agente de bolsillo (Sergio)
**quiero** que solo mi número autorizado pueda hacer que el agente actúe
**para** que nadie más pueda pedirle enviar correos, guardar datos o programar tareas en mi nombre.

**Valor:** el bridge corre sobre un WhatsApp real; sin este control, cualquiera que le escriba a ese
número dispara tools (correo, sheets, recordatorios) con las credenciales del dueño. Es la falla de
seguridad que `SPECS.md` §6 da por resuelta y hoy no lo está.
**Prioridad:** alta   **Estimación:** S (1 ciclo)

### Criterios de aceptación (reglas de NEGOCIO)
- [x] CA1: un mensaje cuyo remitente (`from`) coincide con `AUTHORIZED_WHATSAPP_ID` se procesa normalmente (el agente responde).
- [x] CA2: un mensaje de cualquier otro remitente NO dispara el LLM ni ninguna tool, y el agente
      no responde nada (silencio, para no revelar que el bot existe a un desconocido).
- [x] CA3: si `AUTHORIZED_WHATSAPP_ID` no está configurado (vacío), el agente falla CERRADO:
      no procesa ningún mensaje de nadie, en vez de abrir por defecto a cualquiera.
- [x] CA4: cada intento (autorizado o no) queda en un log estructurado con el remitente, para que
      el dueño pueda ver su propio `from` la primera vez que se prueba y completar `.env`.

### Escenario Gherkin
  Dado  `AUTHORIZED_WHATSAPP_ID=5215500000000@c.us` configurado
  Cuando llega un webhook con `from="5215500000000@c.us"`
  Entonces el agente procesa el mensaje y responde normalmente.

  Dado  `AUTHORIZED_WHATSAPP_ID=5215500000000@c.us` configurado
  Cuando llega un webhook con `from="otronumero@c.us"`
  Entonces el agente no llama al LLM ni a ninguna tool y responde sin texto (`reply` vacío/null).

  Dado  `AUTHORIZED_WHATSAPP_ID` vacío
  Cuando llega cualquier webhook
  Entonces el agente no procesa el mensaje (falla cerrado).

### Restricciones
- La validación se hace releyendo la env var en cada request (no como constante de import), para
  poder configurarla sin reiniciar el proceso en caliente durante la preparación de la demo.
- No se valida body vacío después de esta capa: la regla de "body vacío -> 400" (ya existente) se
  mantiene igual y corre antes.
- No se agrega lista de múltiples IDs autorizados ni roles: un solo dueño (YAGNI).

### No-objetivos
- No se cubre autenticación de múltiples usuarios ni grupos.
- No se cubre notificación al dueño de intentos no autorizados (solo log local).

### Trazabilidad
- commit: (pendiente, ver git diff)  ·  test: tests/test_orchestrator.py::test_webhook_unauthorized_sender_is_ignored,
  tests/test_orchestrator.py::test_webhook_authorized_sender_is_processed,
  tests/test_orchestrator.py::test_webhook_fails_closed_when_unset  ·  intención: sesión 2026-07-22
