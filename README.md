# 🤖 Brayan — el Agente de Bolsillo

El "Jarvis" Colombiano... Antioqueño... paisa.

Un asistente personal que vive en tu WhatsApp y al que le hablás en lenguaje natural. Vos escribís
el **qué** ("mándale correo a mi proveedor pidiendo 10kg de sustrato"); el agente resuelve el
**cómo**, eligiendo y ejecutando la herramienta correcta. El cerebro es **Hermes 3**
(Nous Research), un modelo open-source que corre 100% local vía **Ollama** — sin depender de una
API de pago — con fallback opcional a Anthropic/OpenAI.

Construido con un ciclo de desarrollo **spec-driven**: cada capacidad nace como una spec versionada
con criterios de aceptación de negocio, se implementa con TDD, y se cierra con una verificación
adversarial antes de darla por lista. Nada se acepta con un "se ve bien".

## ✨ Qué sabe hacer

| Le decís... | El agente... |
|---|---|
| "¿Cuánto vale la acción de Globant hoy?" | busca en internet y responde con datos reales |
| "Mándale correo a mi proveedor pidiendo 10kg de sustrato" | redacta y envía el correo por Gmail |
| "Guarda: entregar 2 bolsas de orellanas a Juan David mañana" | anota la fila en Google Sheets |
| "Cada día a las 9 dame el valor de la acción X" | se programa solo — un scheduler lo vuelve a invocar a esa hora |

## 🏗️ Arquitectura

```
┌─────────────┐   QR / escaneo   ┌──────────────────────┐
│  WhatsApp   │◄────────────────►│  Bridge (Node)        │  whatsapp-web.js
│  (celular)  │   POST /webhook  │  src/bridge/          │
└─────────────┘                  └──────────┬────────────┘
                                             │ {from, name, body, message_id}
                                             ▼
                                  ┌──────────────────────┐
                                  │  Orchestrator          │  FastAPI (Python)
                                  │  src/orchestrator.py   │
                                  ├─ Auth gate            │  solo el dueño puede usarlo
                                  ├─ Brain: Hermes         │  Ollama (local) / fallback API
                                  ├─ Memoria corto plazo   │  hilo de la conversación
                                  ├─ Tool registry         │  function-calling
                                  └─ Scheduler             │  "self-programming" seguro
                                             │
                     ┌───────────────────────┼───────────────────────┐
                     ▼                       ▼                       ▼
               buscar_web             enviar_correo            guardar_sheets
                                                         programar_recordatorio
```

**El loop del orchestrator:** recibe el mensaje → arma `system prompt + memoria + mensaje` → se
lo pasa al LLM con las tools disponibles → si el LLM pide una tool, la ejecuta y le devuelve el
resultado → repite hasta una respuesta final (máx. `MAX_TOOL_ROUNDS`) → responde por WhatsApp.

## 🔐 Seguridad ("harness engineering")

Un agente con tool-calling sobre tu WhatsApp real y tu correo real necesita un arnés, no solo un
prompt bien escrito:

- **Gate de autorización, falla cerrado.** Solo `AUTHORIZED_WHATSAPP_ID` puede activar tools. Si
  esa variable no está configurada, el agente **ignora a todos** (no se abre por defecto a
  cualquiera). Cualquier otro remitente no recibe ni respuesta — no se le confirma que el bot existe.
- **Cero ejecución arbitraria.** El "self-programming" (`programar_recordatorio`) solo puede crear
  jobs que vuelven a invocar al agente con texto fijo. Nunca hay `eval`, `exec`, `os.system` ni
  `subprocess` en el camino — verificado con un test estático sobre el propio código fuente, no
  solo con pruebas de caja negra.
- **Límites duros:** `MAX_TOOL_ROUNDS`, `TOOL_TIMEOUT_S`, `MAX_REPLY_CHARS`, `WEB_TRUNCATE_CHARS` —
  nada de loops infinitos ni respuestas que saturen el contexto.
- **Fallo seguro en cada tool.** Sin red, sin credenciales o con el proveedor caído, cada tool
  responde un mensaje claro en vez de tirar una excepción sin capturar al usuario.
- **Secretos solo en `.env`**, nunca hardcodeados ni logueados.

## 🧠 Memoria

- **Corto plazo:** el hilo de la conversación activa se inyecta en cada llamada al LLM (ventana
  truncada por `MAX_SHORT_TERM`, sin persistir entre reinicios del proceso).
- **Largo plazo:** `remember`/`recall` sobre un JSONL persistente, para hechos que deberían
  sobrevivir más allá de una sesión (base construida; conectarla a "el agente decide qué recordar"
  queda para un próximo ciclo).

## 🛠️ Stack

| Capa | Tecnología |
|---|---|
| Canal | `whatsapp-web.js` (Node), bridge por QR |
| Orquestador | Python 3.11 + FastAPI |
| Cerebro | Hermes 3 8B vía Ollama (API compatible con OpenAI) — fallback Anthropic/OpenAI |
| Tools | Clases Python (`Tool`), registradas en `config/tools.json` |
| Scheduler | APScheduler (cron) |
| Memoria | JSONL |
| Tests | pytest (18 tests) · `ruff` para lint |

## 🚀 Cómo correrlo

```bash
# 1. Instalar dependencias
make install                          # pip + npm install

# 2. Bajar el cerebro local (una sola vez, ~5GB)
ollama pull hermes3:8b
ollama serve                          # si no corre ya como servicio

# 3. Configurar
cp .env.example .env
# completar AUTHORIZED_WHATSAPP_ID (obligatorio) y las credenciales de las tools que uses

# 4. Levantar todo
make dev                              # orchestrator (:8000) + bridge Node
# escaneá el QR que aparece en consola con tu WhatsApp

# Verificar
curl localhost:8000/health
make test                             # 18 tests
make lint                             # ruff
```

## 📋 Desarrollo spec-driven

Todo cambio en este repo sigue un contrato explícito (ver `CLAUDE.md`):

1. **Spec primero** — cada capacidad nace en `specs/US-NNN-*.md` con criterios de aceptación de
   negocio, no como una idea suelta en el chat.
2. **TDD** — el test del criterio de aceptación se escribe antes que el código.
3. **Lotes pequeños** — diffs de ~50 líneas, una preocupación por commit.
4. **Verificación adversarial** antes de cerrar: correctitud, seguridad, rendimiento, "¿se
   reproduce?" con una ejecución real, no solo con el test.

Specs actuales: `buscar_web`, autorización por WhatsApp, memoria de corto plazo, `enviar_correo`,
`programar_recordatorio` (con auditoría de seguridad), `guardar_sheets`.

## 🧭 Roadmap

- [x] Skeleton runnable (orchestrator + bridge + 4 tools + memoria + scheduler)
- [x] Gate de autorización por WhatsApp (falla cerrado)
- [x] Memoria de corto plazo conectada al webhook
- [ ] Productivo 24/7 (Raspberry Pi / Docker)
- [ ] Aislamiento: entorno sin acceso a archivos privados del dueño
- [ ] Memoria de largo plazo conectada a decisiones del agente

## ⚠️ Nota honesta

`hermes3:8b` corre 100% local y gratis, y ya se probó en vivo con tool-calling real (búsqueda web
grounded, no alucinada) y memoria entre turnos. Un modelo de 8B puede confundirse en tareas largas
o encadenadas; para un entorno de producción con mayor exigencia de fiabilidad, el mismo código
apunta a Anthropic/OpenAI cambiando una sola variable de entorno (`LLM_PROVIDER`).
