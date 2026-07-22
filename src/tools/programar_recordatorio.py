"""Tool: programar un recordatorio recurrente (self-programming del agente).

SOLO crea jobs que re-disparan el agente con un texto ya definido.
NO ejecuta código ni comandos del sistema (cierra la falla de seguridad de Jorge).
"""
from __future__ import annotations

import os

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from src.tools.base import Tool

_sched = BackgroundScheduler()
_sched.start()


# El disparador llama al orchestrator de forma local (import) para no abrir red.
def _fire(texto: str) -> None:
    from src.orchestrator import run_agent

    run_agent(texto, history=[])


class ProgramarRecordatorioTool(Tool):
    name = "programar_recordatorio"
    description = (
        "Programa un recordatorio o tarea recurrente. A la hora indicada el "
        "agente te avisará o ejecutará la acción que pediste. Indica hora (HH:MM, 24h) "
        "y, opcionalmente, los días (ej. 'lun,mar,mie') y el texto a ejecutar."
    )
    parameters = {
        "type": "object",
        "properties": {
            "hora": {"type": "string", "description": "Hora en formato HH:MM (24h)"},
            "texto": {
                "type": "string",
                "description": "Qué debe hacer o avisar el agente a esa hora",
            },
            "dias": {
                "type": "string",
                "description": "Días separados por coma: lun,mar,mie,... O '*' para diario",
            },
        },
        "required": ["hora", "texto"],
    }

    def run(self, hora: str, texto: str, dias: str = "*") -> str:
        try:
            h, m = hora.strip().split(":")
            day_of_week = "*" if dias.strip() in ("", "*") else dias.strip()
            _sched.add_job(
                _fire,
                trigger=CronTrigger(hour=int(h), minute=int(m), day_of_week=day_of_week),
                args=[texto],
                id=f"rem_{os.urandom(4).hex()}",
                replace_existing=False,
            )
            return f"Recordatorio programado a las {hora} ({dias}): {texto}"
        except Exception as exc:  # noqa: BLE001
            return f"[programar_recordatorio error] {exc}"
