# SPECS — Agente de Bolsillo (WhatsApp + Hermes)

> Documento de especificaciones técnicas para construir el proyecto con **Claude Code**.
> Versión 1.0 · 2026-07-22

## 1. Visión
Un asistente personal que vive en el **WhatsApp del usuario** y al que se le habla en lenguaje natural.
No se programa nada: el usuario escribe *qué* quiere y el agente resuelve el *cómo* usando herramientas (tools/skills).
El cerebro es **Hermes** (modelo open-source de Nous Research) corriendo localmente vía Ollama, con fallback a API de pago.

## 2. Arquitectura

```
┌─────────────┐   QR / escaneo   ┌────────────────────┐
│  WhatsApp   │ ◄───────────────►│  Bridge Node        │  (whatsapp-web.js)
│  (celular)  │   POST /webhook  │  src/bridge/        │
└─────────────┘                  └─────────┬────────────┘
                                           │ JSON {from, body, id}
                                           ▼
                                  ┌────────────────────┐
                                  │  Orchestrator       │  FastAPI (Python)
                                  │  src/orchestrator.py│
                                  ├─ Brain: Hermes      │  Ollama / fallback API
                                  ├─ Memory manager     │  corto + largo plazo
                                  ├─ Tool registry      │  skills declaradas
                                  └─ Scheduler          │  "self-programming"
                                           │
                      ┌────────────────────┼────────────────────┐
                      ▼                    ▼                    ▼
                 buscar_web           enviar_correo        guardar_sheets
                                                        programar_recordatorio
```

## 3. Stack
| Capa | Tecnología | Notas |
|------|-----------|------|
| Canal | `whatsapp-web.js` (Node) | Bridge por QR; alt: Twilio Sandbox |
| Orquestador | Python 3.9 + FastAPI | Recibe webhook, corre el loop |
| Cerebro | Hermes 3 (`hermes3:8b`) vía Ollama | OpenAI-compatible API en `:11434/v1` |
| Fallback | Anthropic / OpenAI | Misma interfaz, cambia 1 env var |
| Memoria | JSONL (corto) + Chroma (largo, opcional) | Rotación por ventana |
| Tools | Python (clases `Tool`) | Web, Gmail, Sheets, Scheduler |
| Scheduler | APScheduler | Cron para skills programadas |
| Tests | pytest | Tool unit + smoke integration |

## 4. Componentes y responsabilidades

### 4.1 WhatsApp Bridge (`src/bridge/wa_bridge.js`)
- Cliente `whatsapp-web.js` que escanea QR con el celular.
- Por cada mensaje entrante: `POST http://localhost:8000/webhook` con `{from, name, body, message_id}`.
- Por cada respuesta del orquestador: `client.sendMessage(from, text)`.
- Debe reconectar ante caídas y loguear errores.

### 4.2 Orchestrator (`src/orchestrator.py`)
- Endpoint `POST /webhook` valida el payload y encola el mensaje.
- Construye el `messages` con system prompt + memoria + historial.
- Llama al LLM con `tools` (function calling). Bucle:
  1. LLM devuelve texto → responde por WhatsApp.
  2. LLM devuelve `tool_call` → ejecuta la tool, vuelve a llamar al LLM con el resultado.
  3. Repite hasta respuesta final (máx `MAX_TOOL_ROUNDS=5`).
- Actualiza memoria al final.

### 4.3 Tools (skills)
Cada tool = clase con: `name`, `description`, `parameters` (JSON schema), `run(**kwargs)`.
Se registran en `config/tools.json` y se traducen al formato function-calling.

| Tool | Entrada | Acción |
|------|--------|--------|
| `buscar_web` | query | HTML scrape de DuckDuckGo lite (o API config) |
| `enviar_correo` | to, subject, body | SMTP/Gmail vía `.env` |
| `guardar_sheets` | fila/datos | gspread a Google Sheet |
| `programar_recordatorio` | hora, texto | APScheduler job que re-dispara al agente |

### 4.4 Memoria (`src/memory/store.py`)
- **Corto plazo:** últimos N mensajes del usuario (ventana deslizante).
- **Largo plazo:** hechos persistentes en JSONL; búsqueda opcional con Chroma.
- No se inyecta memoria no solicitada en el prompt (límites de contexto).

### 4.5 Scheduler (`src/scheduler/jobs.py`)
- Da vida a *"el agente que crea sus propias skills"*: si el usuario pide
  *"cada día a las 9 dame X"*, el orchestrator crea un job cron que a esa hora
  vuelve a invocar al agente con el contexto guardado.
- **Seguridad:** solo puede programar jobs que re-disparan herramientas YA existentes.
  **Nunca** ejecución de código arbitrario.

## 5. Harness Engineering (estabilidad)
Lo que Jorge llama "el arnés que mantiene esto estable sin que se enloquezca":

1. **System prompt acotado y fijo** en `config/system_prompt.txt`. Las skills se añaden
   como *tool definitions*, NO se concatenan libremente al prompt.
2. **Límites duros:** `MAX_TOOL_ROUNDS`, largo máximo de respuesta, timeout por tool.
3. **Sanitización:** salida de web se trunca; inputs del usuario no ejecutan código.
4. **Sin ejecución arbitraria:** el "self-programming" solo crea jobs de scheduler sobre
   tools del whitelist. Esto cierra la falla de seguridad que preocupaba Jorge.
5. **Observabilidad:** logs estructurados de cada tool call (qué, cuándo, resultado).
6. **Context compaction:** rotación de memoria para no saturar la ventana.

## 6. Seguridad y aislamiento (para la sesión 2)
- Bridge en número dedicado o Twilio Sandbox (no lee chats personales).
- Para productivo 24/7: correr en **Raspberry Pi / Docker aislado** con solo lo necesario.
- `.env` con secrets, nunca commiteado (ver `.gitignore`).

## 7. Casos de uso objetivo (demo)
1. "¿Cuánto vale la acción de Globant hoy?" → `buscar_web`.
2. "Mañana a las 9 quiero el valor de la acción X." → `programar_recordatorio`.
3. "Mándale correo a mi proveedor pidiendo 10 kg de sustrato." → `enviar_correo`.
4. "Guarda: entregar 2 bolsas de orellanas a Juan David mañana." → `guardar_sheets`.
5. "Resumen ejecutivo de noticias de IA de hoy en 3 párrafos." → `buscar_web` + síntesis.

## 8. Convenciones de código (para Claude Code)
- Python 3.9, type hints en funciones públicas, docstrings estilo Google.
- `ruff` en save (hook). `pytest` para tests. `make dev` / `make test`.
- Commits pequeños y descriptivos; ramas por feature.

## 9. Roadmap
- [x] Spec + harness (esta sesión)
- [ ] Skeleton runnable (orchestrator + bridge)
- [ ] Tools web/gmail/sheets/scheduler
- [ ] Demo mañana (Juan D intro + Sergio demo)
- [ ] Sesión 2: productivo 24/7 + aislamiento Raspberry/Docker
- [ ] Modelos locales open (Ollama + Hermes/Qwen) sin pagos
