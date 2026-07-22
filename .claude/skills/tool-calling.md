# Skill: Patrón de Tool-Calling del Orchestrator

El loop central de `src/orchestrator.py` usa function calling en formato OpenAI:

## 1. Definir la tool (JSON schema)
```python
tool_spec = {
    "type": "function",
    "function": {
        "name": "buscar_web",
        "description": "Busca en internet y devuelve resultados.",
        "parameters": {
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"],
        },
    },
}
```

## 2. Llamar al LLM con tools
```python
resp = client.chat.completions.create(
    model=MODEL, messages=messages, tools=[tool_spec], tool_choice="auto"
)
msg = resp.choices[0].message
```

## 3. Si hay tool_call, ejecutar y volver a llamar
```python
if msg.tool_calls:
    for call in msg.tool_calls:
        result = dispatch(call.function.name, **json.loads(call.function.arguments))
        messages.append({"role": "tool", "tool_call_id": call.id, "content": result})
    # vuelve a llamar al LLM con los resultados
```

## 4. Repetir hasta respuesta final (máx MAX_TOOL_ROUNDS)
El `dispatch` mapea `name -> Tool.run()`. Los args vienen como JSON del LLM;
valida tipos antes de ejecutar. Sanitiza el `result` (trunca) antes de devolverlo al LLM.
