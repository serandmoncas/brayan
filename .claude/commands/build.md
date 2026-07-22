# /build — Construir un componente del agente

Uso: `/build <componente>` donde componente ∈ {bridge, tool <nombre>, memory, scheduler, orchestrator}

Este comando delega al subagente adecuado y deja el repo en estado runnable.

## Pasos que ejecuta Claude
1. Lee `SPECS.md` y `CLAUDE.md` para el contexto completo.
2. Según el componente, invoca:
   - `bridge` → `@whatsapp-bridge`
   - `tool <nombre>` → `@tool-builder` (pásale el nombre y la descripción de $ARGUMENTS)
   - `memory` / `scheduler` / `orchestrator` → `@harness-architect`
3. Corre `make lint` y `make test` al terminar.
4. Reporta qué archivos creó/modificó y cómo probarlo.

$ARGUMENTS
