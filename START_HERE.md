# START_HERE.md — Brief de arranque para Claude Code

> Pegá esto a Claude Code para iniciar la construcción del proyecto.
> Todo el flujo es **spec-driven** (ver `CLAUDE.md`, `specs/README.md`, `.claude/skills/spec-driven-dev.md`).
> Regla de oro: **spec primero, TDD, lote pequeño, `/verify` antes de cerrar.**

---

## 1. Qué es este proyecto
Un **agente de bolsillo**: asistente personal que vive en el WhatsApp del usuario y al que se
le habla en lenguaje natural. El usuario escribe el *qué*; el agente resuelve el *cómo* usando
herramientas (tools/skills). El cerebro es **Hermes** (open-source, Ollama), con fallback a API de pago.

Ya existe un **skeleton runnable** (orchestrator FastAPI + 4 tools + memoria + scheduler + bridge
WhatsApp). Los tests pasan (9/9). Tu trabajo NO es reescribir eso: es **dejarlo demo-ready**
para una sesión mañana y **completar/endurecer** las tools con disciplina spec-driven.

## 2. Dónde vive todo (lee estos archivos primero)
- `CLAUDE.md` — contexto + contrato de trabajo (OBLIGATORIO).
- `SPECS.md` — especificaciones técnicas de arquitectura.
- `specs/README.md` + `specs/US-001-buscar-web.md` — formato de spec y primer ejemplo.
- `config/` — `system_prompt.txt` (fijo) y `tools.json` (registro de skills).
- `src/` — `orchestrator.py`, `tools/`, `memory/`, `scheduler/`, `bridge/`.
- `.claude/agents/` — `@whatsapp-bridge`, `@tool-builder`, `@harness-architect`, `@test-writer`.
- `.claude/commands/` — `/spec`, `/verify`, `/build`, `/demo-check`.
- `.claude/skills/` — `spec-driven-dev`, `ollama-hermes`, `tool-calling`.

## 3. Reglas que debés respetar en CADA paso
1. **Spec primero.** Sin `specs/US-NNN-*.md` no hay build. Usá `/spec <nombre>` para crearla.
2. **TDD.** Escribí PRIMERO el test derivado del criterio de aceptación (resultado de NEGOCIO),
   luego implementá hasta que pase.
3. **Lotes pequeños.** Diffs ~50 líneas; una preocupación por paso. Revisar 2000 líneas es exponencial.
4. **`/verify` ANTES de cerrar.** Tu tarea es REFUTAR, no aprobar: correctitud, seguridad
   (inyección, PII, eval/exec), rendimiento, "¿se reproduce?".
5. **Puertas de aprobación.** push / deploy / borrar → confirmación explícita del humano.
6. **Definition of Done:** CAs por test + ejecución real + spec actualizada + trazabilidad.
7. **Sin ejecución de código del usuario.** Nunca `eval`/`exec` de texto del usuario.
8. **Principios de diseño:** SRP, Open/Closed, SoC, DRY, KISS, YAGNI, IoC, AHA. No sobre-genereres.

## 4. Backlog inicial (orden sugerido)
Ejecutá los ítems de a uno, con spec + TDD + `/verify` en cada uno.

### T0 — Preparar entorno local (setup, sin spec: es infra)
- `ollama pull hermes3:8b` (el cerebro local; tu Ollama hoy solo tiene llama3.2 y granité3.3).
- Copiar `.env.example` → `.env` y dejar claras las vars (no llenar secretos reales todavía).
- Instalar deps del bridge: `cd src/bridge && npm install`.
- Levantar `ollama serve` y correr `make dev` en segundo plano; verificar `curl localhost:8000/health`
  reporta `provider: ollama` y las 4 tools.
- Reportá ✅/❌ por cada paso. No avancés si `/health` falla.

### T1 — Endurecer `buscar_web` (spec US-001 ya existe)
- Ampliar `specs/US-001-buscar-web.md` con CAs de borde: (a) red caída → mensaje claro,
  no crash; (b) respuesta vacía → "no encontré resultados"; (c) query con caracteres raros
  no rompe el scrape ni inyecta nada.
- TDD: añadir tests en `tests/test_tools.py` mockeando `requests.post` para cada borde.
- Implementar en `src/tools/buscar_web.py`. Respetar `WEB_TRUNCATE_CHARS`.
- `/verify` y cerrar.

### T2 — Completar `enviar_correo` (spec + TDD)
- `/spec enviar-correo-proveedor`. CAs de negocio: (a) credenciales faltantes → avisa,
  no crashea; (b) envío OK → confirma; (c) fallo SMTP → error legible, no stack trace al usuario.
- TDD: test mock de `smtplib.SMTP_SSL` (no enviar correo real).
- Implementar en `src/tools/enviar_correo.py`. Leer secretos de `.env` (nunca hardcode).
- `/verify` y cerrar.

### T3 — Completar `guardar_sheets` (spec + TDD) — solo si hay credenciales de prueba
- `/spec guardar-pedido-sheets`. CAs: (a) faltan `GOOGLE_SHEET_ID`/`creds` → avisa;
  (b) guardado OK → confirma fila escrita.
- TDD: test mock de `gspread` (no tocar Sheets real).
- Implementar en `src/tools/guardar_sheets.py`.
- `/verify` y cerrar. Si no hay credenciales, dejalo con el aviso claro y marcalo en la spec.

### T4 — Auditar `programar_recordatorio` (seguridad, lo más crítico)
- `/spec programar-recordatorio` (si no existe). CA clave: (a) SOLO crea jobs que
  re-disparan tools YA registradas; (b) NUNCA ejecuta comandos del sistema ni evalúa texto
  arbitrario del usuario; (c) hora inválida → error claro.
- TDD: test que confirma que pasarle un "comando malicioso" NO se ejecuta (p.ej. no hay
  `subprocess`/`os.system` en el camino).
- Revisar `src/tools/programar_recordatorio.py`. Si hay cualquier `eval`/`exec`/`os.system`,
  REMOVELo y usá solo el scheduler. `/verify` (lente de seguridad) y cerrar.

### T5 — Conectar el bridge WhatsApp (smoke)
- Usar `@whatsapp-bridge`. Verificar `src/bridge/wa_bridge.js` hace `POST /webhook` y
  reenvía `reply`. Ignora grupos y mensajes propios.
- Smoke: con el orchestrator arriba, simular un `POST /webhook` (curl) y confirmar que el
  loop LLM↔tool retorna `{"reply": "..."}`.
- NO escanees el QR real todavía (eso lo hace Sergio en vivo). Dejá documentado el paso.
- `/verify` y cerrar.

### T6 — Checklist pre-demo
- Ejecutar `/demo-check` (o correr manual: `ollama list` tiene hermes3:8b, `make test`
  pasa, `config/tools.json` tiene buscar_web + enviar_correo, bridge instala).
- Reportá ✅/❌. Si hay ❌ en T0–T5, no declarar "listo".

## 5. Definition of Done por ítem
- [ ] Spec creada/actualizada con CAs de NEGOCIO.
- [ ] Test escrito ANTES que el código y pasa.
- [ ] Lote pequeño; diff legible.
- [ ] `make lint` y `make test` en verde.
- [ ] Ejecutado de verdad al menos una vez (o verificado manualmente, rotulado así).
- [ ] `/verify` sin ❌ en seguridad.
- [ ] Trazabilidad: commit → spec US-NNN → CA → intención.
- [ ] Changelog actualizado.

## 6. Qué NUNCA hacer
- No escribas código sin spec.
- No aceptes "se ve bien" como verificación.
- No ejecutes código del usuario (eval/exec).
- No hardcodees secretos ni los leas en pantalla.
- No hagas big-bang: un ítem a la vez, un commit por concern.

## 7. Señal de alarma
Si pensás *"se ve bien, la IA sabe lo que hace"* → detenete. Esa frase es un sesgo activándose.
La confianza fluida es el síntoma, no la prueba. Verificá, no confíes.

---
Cuando termines T0–T6, reportá un resumen corto: qué quedó ✅, qué ❌, y el comando exacto
para que Sergio corra la demo mañana.
