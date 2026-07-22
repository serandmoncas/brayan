import sys
from pathlib import Path

import pytest

# Asegura que 'src' esté en el path para importar módulos del proyecto
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))


@pytest.fixture(autouse=True)
def _env(monkeypatch):
    """Evita tocar credenciales reales en los tests."""
    monkeypatch.setenv("GMAIL_USER", "")
    monkeypatch.setenv("GMAIL_APP_PASSWORD", "")
    monkeypatch.setenv("GOOGLE_SHEET_ID", "")
    monkeypatch.setenv("GOOGLE_CREDENTIALS_PATH", "")
    monkeypatch.setenv("MEMORY_DIR", str(ROOT / "tests" / "tmp_memory"))
