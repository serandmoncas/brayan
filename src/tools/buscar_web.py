"""Tool: búsqueda web (DuckDuckGo lite HTML scraper)."""
from __future__ import annotations

import os
import re

import requests

from src.tools.base import Tool

WEB_TRUNCATE = int(os.getenv("WEB_TRUNCATE_CHARS", "4000"))


class BuscarWebTool(Tool):
    name = "buscar_web"
    description = (
        "Busca en internet el término dado y devuelve un resumen de los "
        "primeros resultados. Usala cuando necesites datos actuales o externos."
    )
    parameters = {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Término o pregunta de búsqueda"}
        },
        "required": ["query"],
    }

    def run(self, query: str) -> str:
        try:
            resp = requests.post(
                "https://lite.duckduckgo.com/lite/",
                data={"q": query},
                headers={"User-Agent": "Mozilla/5.0"},
                timeout=10,
            )
            text = re.sub(r"<[^>]+>", " ", resp.text)
            text = re.sub(r"\s+", " ", text).strip()
            return text[:WEB_TRUNCATE]
        except Exception as exc:  # noqa: BLE001
            return f"[buscar_web error] {exc}"
