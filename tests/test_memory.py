from pathlib import Path

from src.memory.store import remember, recall, short_term_window


def test_remember_recall():
    remember("cliente_favorito", "Juan David")
    assert recall("cliente_favorito") == "Juan David"


def test_remember_does_not_touch_real_project_memory():
    # Regresión: MEMORY_DIR se leía como constante de import, así que el
    # monkeypatch del fixture autouse (tests/conftest.py) nunca surtía efecto
    # y cada corrida de pytest contaminaba memory/long_term.jsonl real.
    real_memory = Path(__file__).parent.parent / "memory" / "long_term.jsonl"
    before = real_memory.read_text(encoding="utf-8") if real_memory.exists() else None
    remember("clave_test_aislamiento", "valor")
    after = real_memory.read_text(encoding="utf-8") if real_memory.exists() else None
    assert before == after


def test_short_term_window_truncates():
    hist = [{"role": "user", "content": str(i)} for i in range(50)]
    window = short_term_window(hist)
    assert len(window) <= 20
    assert window[-1]["content"] == "49"
