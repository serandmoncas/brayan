# Agente de Bolsillo — Contexto para Claude Code

Asistente personal en WhatsApp con cerebro **Hermes** (open-source, Ollama), tool-calling y memoria.
El usuario habla en lenguaje natural; el agente resuelve el *cómo* con herramientas.

## ⚠️ CONTRATO DE TRABAJO (ciclo de desarrollo dirigido por especificación)
Estas prácticas son **obligatorias** y se aplican a CUALQUIER cambio en este repo.
Fuente: "Ciclo de Desarrollo de Software Moderno" (Jorge Johnson / Claude Opus 4).

1. **Spec primero.** Ningún build sin `specs/US-NNN-<nombre>.md`. El chat NO es el
   contrato; la spec versionada sí. Usa `/spec <nombre>` para crearla.
2. **TDD con agentes.** Escribe PRIMERO el test derivado del criterio de aceptación
   (resultado de NEGOCIO, no mecánica), luego implementa hasta que pase.
3. **Lotes pequeños.** Diffs de ~50 líneas; una preocupación por paso
   (no mezcles refactor + feature + fix). Revisar 2000 líneas es exponencial.
4. **Verificación adversarial (/verify) ANTES de cerrar.** Tu tarea es REFUTAR, no
   aprobar: correctitud, seguridad (inyección, PII, eval/exec), rendimiento, "¿se reproduce?".
5. **Puertas de aprobación en lo irreversible:** push, deploy, borrar, publicar →
   confirmación explícita del humano. La aprobación en un contexto NO se hereda.
6. **Definición de Done:** criterios cubiertos por test + ejecución real + spec actualizada
   + trazabilidad commit→spec→CA. Cero parcial silencioso.
7. **Regenerable ≠ verificado.** El código se regenera desde la spec; la aceptación
   es humana y cara. Si no puedes explicar línea por línea qué hace, NO está listo.
8. **Principios de diseño:** SRP, Open/Closed, SoC, DRY, KISS, YAGNI, IoC, AHA.
   No sobre-genereres ni dupliques (la IA tiende a lo contrario → usa `grep` antes de copiar).
9. **Sin ejecución de código del usuario.** Nunca `eval`/`exec` de texto del usuario.

## Arquitectura (ver `SPECS.md` y `specs/`)
- **Bridge** (`src/bridge/wa_bridge.js`, Node + whatsapp-web.js) escanea QR y hace `POST /webhook`.
- **Orchestrator** (`src/orchestrator.py`, FastAPI) corre el loop LLM↔tools.
- **Brain:** Hermes vía Ollama (`http://localhost:11434/v1`, modelo `hermes3:8b`). Fallback a Anthropic/OpenAI con env vars.
- **Tools:** clases Python en `src/tools/` registradas en `config/tools.json`.
- **Memory:** `src/memory/store.py` (JSONL corto + largo).
- **Scheduler:** `src/scheduler/jobs.py` (APScheduler).

## Comandos clave
- `make dev` — corre orchestrator (FastAPI :8000) + bridge Node.
- `make test` — pytest.  `make lint` — ruff.  `ollama pull hermes3:8b`.

## Cómo construir (subagentes especializados)
- Nueva spec → `/spec <nombre>` (luego implementa con TDD).
- Nueva tool → `@tool-builder` (debe crear spec + test).
- Bridge WhatsApp → `@whatsapp-bridge`.
- Estabilidad/config/memoria → `@harness-architect`.
- Tests → `@test-writer`.
- Antes de mostrar demo o cerrar ciclo → `/verify` y `/demo-check`.

## Notas
- El cerebro puede correr 100% local (Hermes/Ollama) — el punto ético de Jorge.
- Para demo de mañana: Ollama + `hermes3:8b` bajado y al menos `buscar_web` + `enviar_correo` probadas ANTES de la sesión.
