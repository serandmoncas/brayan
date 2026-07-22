## US-004 — Enviar correo a un proveedor por WhatsApp
**Como** dueño del agente de bolsillo
**quiero** pedirle por WhatsApp que redacte y mande un correo
**para** no tener que abrir el cliente de correo para pedidos rutinarios (ej. sustrato para el negocio de setas).

**Valor:** es el caso de uso "pedidos y proveedores" de la charla — demuestra una tool con efecto
real fuera del chat.
**Prioridad:** alta   **Estimación:** S (1 ciclo)

### Criterios de aceptación (reglas de NEGOCIO)
- [x] CA1: si faltan `GMAIL_USER`/`GMAIL_APP_PASSWORD` en `.env`, el agente avisa claro y NO crashea.
- [x] CA2: con credenciales válidas, el envío se confirma con un mensaje de éxito.
- [x] CA3: si el SMTP falla (credenciales inválidas, servidor caído), el agente responde un error
      legible en español, nunca un stack trace crudo al usuario.

### Escenario Gherkin
  Dado  `GMAIL_USER`/`GMAIL_APP_PASSWORD` configurados
  Cuando el usuario pide "mándale correo a mi proveedor pidiendo 10 kg de sustrato"
  Entonces el agente redacta y envía el correo, y confirma "Correo enviado a ...".

  Dado  el envío SMTP falla (red o credenciales)
  Cuando se intenta enviar el correo
  Entonces el agente responde `[enviar_correo error] ...` sin caerse.

### Restricciones
- Secretos solo desde `.env` (nunca hardcodeados, nunca logueados).
- No se reintenta automáticamente el envío (fuera de alcance: rate limiting/retries es "problema
  del 80%" para otro ciclo).

### No-objetivos
- No se cubren adjuntos ni HTML rico en el correo (solo texto plano).
- No se cubre selección de múltiples proveedores en un solo mensaje.

### Trazabilidad
- commit: (pendiente, ver git diff)  ·  test: tests/test_tools.py::test_enviar_correo_without_creds,
  tests/test_tools.py::test_enviar_correo_success, tests/test_tools.py::test_enviar_correo_smtp_failure_is_handled
  ·  intención: sesión 2026-07-22
