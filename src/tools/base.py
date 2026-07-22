"""Clase base para las herramientas (skills) del agente."""
from __future__ import annotations

from abc import ABC, abstractmethod


class Tool(ABC):
    """Una skill del agente. Se registra en config/tools.json y se expone al LLM
    vía function calling (spec)."""

    name: str = ""
    description: str = ""
    parameters: dict = {"type": "object", "properties": {}, "required": []}

    @abstractmethod
    def run(self, **kwargs) -> str:
        """Ejecuta la herramienta y retorna texto plano (sanitizado)."""

    def spec(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }
