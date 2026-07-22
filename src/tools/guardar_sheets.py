"""Tool: guardar fila en Google Sheet (gspread)."""
from __future__ import annotations

import os

from src.tools.base import Tool


class GuardarSheetsTool(Tool):
    name = "guardar_sheets"
    description = (
        "Guarda una fila de datos en tu hoja de cálculo de Google Sheets. "
        "Usala para registrar pedidos, recordatorios o tareas."
    )
    parameters = {
        "type": "object",
        "properties": {
            "datos": {
                "type": "string",
                "description": "Texto o fila a guardar (ej. 'Pedido: 2 bolsas orellanas -> Juan David')",
            }
        },
        "required": ["datos"],
    }

    def run(self, datos: str) -> str:
        sheet_id = os.getenv("GOOGLE_SHEET_ID")
        creds = os.getenv("GOOGLE_CREDENTIALS_PATH")
        if not sheet_id or not creds:
            return "[guardar_sheets] faltan GOOGLE_SHEET_ID / GOOGLE_CREDENTIALS_PATH"
        try:
            import gspread
            from google.oauth2.service_account import Credentials

            scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
            c = Credentials.from_service_account_file(creds, scopes=scope)
            gc = gspread.authorize(c)
            ws = gc.open_by_key(sheet_id).sheet1
            ws.append_row([datos])
            return "Guardado en la hoja de cálculo."
        except Exception as exc:  # noqa: BLE001
            return f"[guardar_sheets error] {exc}"
