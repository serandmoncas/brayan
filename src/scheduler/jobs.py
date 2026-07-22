"""Scheduler wrapper (expone el BackgroundScheduler compartido)."""
from __future__ import annotations

from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()
