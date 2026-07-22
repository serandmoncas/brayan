"""Tool: enviar correo vía Gmail SMTP (app password)."""
from __future__ import annotations

import os
import smtplib
from email.mime.text import MIMEText

from src.tools.base import Tool


class EnviarCorreoTool(Tool):
    name = "enviar_correo"
    description = (
        "Redacta y envía un correo electrónico desde tu cuenta configurada. "
        "Usala para contactar proveedores o enviar mensajes por ti."
    )
    parameters = {
        "type": "object",
        "properties": {
            "to": {"type": "string", "description": "Correo del destinatario"},
            "subject": {"type": "string", "description": "Asunto del correo"},
            "body": {"type": "string", "description": "Cuerpo del mensaje"},
        },
        "required": ["to", "subject", "body"],
    }

    def run(self, to: str, subject: str, body: str) -> str:
        user = os.getenv("GMAIL_USER")
        pwd = os.getenv("GMAIL_APP_PASSWORD")
        if not user or not pwd:
            return "[enviar_correo] faltan GMAIL_USER / GMAIL_APP_PASSWORD en .env"
        try:
            msg = MIMEText(body, "plain", "utf-8")
            msg["Subject"] = subject
            msg["From"] = user
            msg["To"] = to
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=10) as s:
                s.login(user, pwd)
                s.sendmail(user, [to], msg.as_string())
            return f"Correo enviado a {to}."
        except Exception as exc:  # noqa: BLE001
            return f"[enviar_correo error] {exc}"
