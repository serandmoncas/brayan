"""Orchestrator del Agente de Bolsillo.

Recibe mensajes por POST /webhook (desde el bridge de WhatsApp), corre el
bucle LLM <-> tools con function calling, y devuelve {"reply": "..."}.

El cerebro es Hermes vía Ollama por defecto, con fallback a Anthropic/OpenAI
según LLM_PROVIDER. Las tools se registran en config/tools.json.
"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException
from openai import OpenAI

from src.memory.store import short_term_window
from src.tools.registry import get_tool_specs, dispatch

load_dotenv()

HERE = Path(__file__).parent
CONFIG = HERE.parent / "config"

MAX_TOOL_ROUNDS = int(os.getenv("MAX_TOOL_ROUNDS", "5"))
TOOL_TIMEOUT_S = int(os.getenv("TOOL_TIMEOUT_S", "10"))
MAX_REPLY_CHARS = int(os.getenv("MAX_REPLY_CHARS", "1500"))
PORT = int(os.getenv("PORT", "8000"))

PROVIDER = os.getenv("LLM_PROVIDER", "ollama")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "hermes3:8b")

SYSTEM_PROMPT = (CONFIG / "system_prompt.txt").read_text(encoding="utf-8")
TOOL_SPECS = get_tool_specs()


def _client() -> OpenAI:
    """Construye el cliente OpenAI-compatible según el proveedor configurado."""
    if PROVIDER == "ollama":
        return OpenAI(base_url=OLLAMA_BASE_URL, api_key="ollama")
    if PROVIDER == "anthropic":
        return OpenAI(
            base_url="https://api.anthropic.com/v1/",
            api_key=os.getenv("ANTHROPIC_API_KEY", ""),
            default_headers={"anthropic-version": "2023-06-01"},
        )
    # openai por defecto
    return OpenAI(api_key=os.getenv("OPENAI_API_KEY", ""))


_CLIENT = _client()
_MODEL = OLLAMA_MODEL if PROVIDER == "ollama" else os.getenv("OPENAI_API_KEY") and "gpt-4o-mini"


def _truncate(text: str, limit: int = MAX_REPLY_CHARS) -> str:
    return text if len(text) <= limit else text[:limit] + "… [truncado]"


# Memoria de corto plazo del hilo activo (un solo dueño, ver US-002/US-003).
_HISTORY: list[dict] = []


def is_authorized(sender_id: str) -> bool:
    """Solo el dueño configurado en AUTHORIZED_WHATSAPP_ID puede usar el agente.

    Falla cerrado: si la env var no está configurada, nadie está autorizado.
    Se relee en cada llamada (no es constante de import) para poder fijarla
    en caliente mientras se prepara la demo.
    """
    authorized = os.getenv("AUTHORIZED_WHATSAPP_ID", "").strip()
    return bool(authorized) and sender_id == authorized


def run_agent(user_message: str, history: list[dict]) -> str:
    """Bucle LLM <-> tools. Retorna el texto final para WhatsApp."""
    messages: list[dict[str, Any]] = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(history)
    messages.append({"role": "user", "content": user_message})

    for _ in range(MAX_TOOL_ROUNDS):
        try:
            resp = _CLIENT.chat.completions.create(
                model=_MODEL,
                messages=messages,
                tools=TOOL_SPECS or None,
                tool_choice="auto",
            )
        except Exception as exc:  # noqa: BLE001
            return f"[error] no pude consultar al modelo: {exc}"

        msg = resp.choices[0].message

        # Sin tool calls -> respuesta final
        if not msg.tool_calls:
            return _truncate(msg.content or "")

        # Ejecuta cada tool call y vuelve a llamar al LLM con los resultados
        messages.append(
            {
                "role": "assistant",
                "content": msg.content or "",
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {"name": tc.function.name, "arguments": tc.function.arguments},
                    }
                    for tc in msg.tool_calls
                ],
            }
        )
        for tc in msg.tool_calls:
            name = tc.function.name
            try:
                args = json.loads(tc.function.arguments or "{}")
            except json.JSONDecodeError:
                args = {}
            start = time.time()
            try:
                result = dispatch(name, args)
                ok = True
            except Exception as exc:  # noqa: BLE001
                result = f"[tool error] {exc}"
                ok = False
            print(f"{{tool={name}, ok={ok}, ms={int((time.time()-start)*1000)}}}", flush=True)
            messages.append(
                {"role": "tool", "tool_call_id": tc.id, "content": str(result)}
            )

    return _truncate("Lo siento, llegué al límite de pasos. ¿Podés reformularlo?")


app = FastAPI(title="Agente de Bolsillo")


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "provider": PROVIDER, "tools": [t["function"]["name"] for t in TOOL_SPECS]}


@app.post("/webhook")
async def webhook(req: Request) -> dict:
    payload = await req.json()
    body = (payload.get("body") or "").strip()
    if not body:
        raise HTTPException(status_code=400, detail="empty body")

    sender = payload.get("from", "")
    authorized = is_authorized(sender)
    print(f"{{event=webhook, from={sender!r}, authorized={authorized}}}", flush=True)
    if not authorized:
        # Silencio: no se le confirma a un remitente no autorizado que el bot existe.
        return {"reply": None}

    history = short_term_window(_HISTORY)
    reply = run_agent(body, history)
    _HISTORY.append({"role": "user", "content": body})
    _HISTORY.append({"role": "assistant", "content": reply})
    return {"reply": reply}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("orchestrator:app", host="0.0.0.0", port=PORT)
