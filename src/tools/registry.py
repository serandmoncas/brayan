"""Registry: carga las tools declaradas en config/tools.json y las expone
al LLM como specs de function calling, y dispatch por nombre."""
from __future__ import annotations

import importlib
import json
import re
from pathlib import Path
from typing import Any

from src.tools.base import Tool

CONFIG = Path(__file__).parent.parent.parent / "config" / "tools.json"

_INSTANCES: dict[str, Tool] = {}


def _snake(name: str) -> str:
    """'BuscarWebTool' -> 'buscar_web'."""
    s = re.sub(r"(?<!^)(?=[A-Z])", "_", name.replace("Tool", ""))
    return s.lower()


def _load() -> None:
    if _INSTANCES:
        return
    data = json.loads(CONFIG.read_text(encoding="utf-8"))
    for class_name in data.get("tools", []):
        module = importlib.import_module(f"src.tools.{_snake(class_name)}")
        cls = getattr(module, class_name)
        _INSTANCES[cls.name] = cls()


def get_tool_specs() -> list[dict[str, Any]]:
    _load()
    return [t.spec() for t in _INSTANCES.values()]


def dispatch(name: str, args: dict) -> str:
    _load()
    tool = _INSTANCES.get(name)
    if tool is None:
        return f"[error] tool desconocida: {name}"
    return tool.run(**args)
