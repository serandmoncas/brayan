# Skill: Correr Hermes localmente con Ollama

Cuando el orchestrator necesite el cerebro del agente y se quiera 100% local/gratis:

## Instalar Ollama
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

## Bajar Hermes 3
```bash
ollama pull hermes3:8b      # ~5 GB, cabe en 8 GB RAM
# opcional, más capaz (requiere 24+ GB RAM):
# ollama pull hermes3:70b
```

## Arrancar el servidor (ya corre por defecto al usar ollama)
El endpoint OpenAI-compatible queda en `http://localhost:11434/v1`.

## Usarlo desde Python (cliente OpenAI-compatible)
```python
from openai import OpenAI
client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
r = client.chat.completions.create(
    model="hermes3:8b",
    messages=[{"role": "user", "content": "hola"}],
    tools=[...],          # function calling
    tool_choice="auto",
)
```

## Notas de tool-calling
- Hermes 3 soporta function calling en Ollama. Para tareas largas un 8B puede equivocarse;
  si la demo lo exige, apunta el cliente a Anthropic/OpenAI con `LLM_PROVIDER` (misma interfaz).
- RAM: 8B ≈ 6–8 GB; 70B ≈ 40+ GB. En Raspberry Pi usa 8B y acepta latencia.

## Fallback (sin tocar el código del orchestrator)
En `.env`: `LLM_PROVIDER=anthropic` y `ANTHROPIC_API_KEY=...` (o `openai`).
El orchestrator elige el cliente según la env var.
