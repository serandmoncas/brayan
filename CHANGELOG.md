# Changelog

Formato sugerido (Keep a Changelog). Cada entrada linkea a la spec US-NNN.

## [Unreleased]
- Consolidación: el proyecto se movió de `agente-bolsillo` (sin git) a este repo (`brayan`), que
  ya tenía remoto en GitHub. Un solo repo real de aquí en adelante.
- Fix: `src/memory/store.py` releía `MEMORY_DIR` como constante de import; el autouse fixture de
  tests nunca surtía efecto y cada `make test` contaminaba `memory/long_term.jsonl` real (se
  encontraron y limpiaron 12 líneas de datos de prueba). US-007.
- Fix: pin `openai==1.58.1` (era `1.47.0`, incompatible con `httpx==0.28.1` instalado: rompía la
  colección de tests con `TypeError: Client.__init__() got an unexpected keyword argument 'proxies'`).
- US-002 autorizacion-whatsapp: `/webhook` solo procesa mensajes de `AUTHORIZED_WHATSAPP_ID`; falla
  cerrado si no está configurado; log estructurado de cada intento.
- US-003 memoria-corto-plazo: `/webhook` ahora inyecta el historial reciente (`short_term_window`)
  al LLM en cada turno; antes siempre mandaba `history=[]`.
- US-001 buscar-web: skill de búsqueda internet (DuckDuckGo lite) con truncado y fallo seguro.
- US-004 enviar-correo-proveedor: tests de éxito y fallo SMTP (antes solo se probaba sin credenciales).
- US-005 programar-recordatorio: test estático que confirma ausencia de eval/exec/os.system/subprocess.
- US-006 guardar-pedido-sheets: test de aviso sin credenciales. CA2 (fila real) queda bloqueado sin
  credenciales de Google Service Account — verificar antes de usar en vivo.
- Verificado end-to-end con el proceso real (no solo TestClient): `/health`, auth gate, tool-calling
  real de `buscar_web` vía Hermes/Ollama (grounded, no alucinado), y memoria de corto plazo entre
  dos turnos. `ollama pull hermes3:8b` completado (4.7GB).
- Harness: spec-driven dev, TDD, verificación adversarial, Definition of Done, puertas de aprobación.

## [0.1.0] - 2026-07-22
- Skeleton runnable: orchestrator (FastAPI), 4 tools, memoria, scheduler.
- Bridge WhatsApp (whatsapp-web.js).
- 9 tests (tools, orchestrator, memory).
