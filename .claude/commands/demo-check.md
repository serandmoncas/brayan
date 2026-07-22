# /demo-check — Verificar que el agente está listo para la demo

Uso: `/demo-check`

Corre una batería rápida para asegurar que mañana la demo no falla en vivo:

## Checklist automático
1. `ollama list` muestra `hermes3:8b` (o `LLM_PROVIDER` apuntando a API válida).
2. `make test` pasa (tools mockeados + smoke del webhook).
3. `python3 -c "import src.orchestrator"` importa sin error.
4. `config/tools.json` tiene al menos `buscar_web` y `enviar_correo` registradas.
5. El bridge (`src/bridge/wa_bridge.js`) existe y `npm install` no falla.

## Reporte
Al final, imprime ✅/❌ por cada punto y, si hay ❌, la causa exacta y el comando para arreglarlo.
No muestres la demo si hay ❌ en 1–4.
