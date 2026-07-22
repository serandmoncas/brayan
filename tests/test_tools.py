from src.tools.registry import get_tool_specs, dispatch


def test_tool_specs_registered():
    specs = get_tool_specs()
    names = {s["function"]["name"] for s in specs}
    assert {"buscar_web", "enviar_correo", "guardar_sheets", "programar_recordatorio"} <= names


def test_dispatch_unknown_tool():
    out = dispatch("no_existe", {})
    assert "error" in out.lower()


def test_buscar_web_runs(monkeypatch):
    # Mock de requests.post para no tocar la red
    import src.tools.buscar_web as bw

    class _Resp:
        text = "<html>Resultado de prueba sobre python</html>"

    class _Req:
        @staticmethod
        def post(*a, **k):
            return _Resp()

    monkeypatch.setattr(bw.requests, "post", _Req.post)
    out = dispatch("buscar_web", {"query": "python"})
    assert "Resultado" in out


def test_buscar_web_network_failure_is_handled(monkeypatch):
    # Sin red / timeout -> mensaje claro, no excepción sin capturar
    import src.tools.buscar_web as bw

    def _raise(*a, **k):
        raise ConnectionError("sin red")

    monkeypatch.setattr(bw.requests, "post", _raise)
    out = dispatch("buscar_web", {"query": "python"})
    assert out.startswith("[buscar_web error]")


def test_enviar_correo_without_creds():
    out = dispatch("enviar_correo", {"to": "x@y.com", "subject": "s", "body": "b"})
    assert "GMAIL_USER" in out  # falta credencial -> avisa, no crashea


def test_enviar_correo_success(monkeypatch):
    import src.tools.enviar_correo as ec

    monkeypatch.setenv("GMAIL_USER", "yo@gmail.com")
    monkeypatch.setenv("GMAIL_APP_PASSWORD", "clave")
    sent = {}

    class _FakeSMTP:
        def __init__(self, *a, **k):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def login(self, user, pwd):
            sent["login"] = (user, pwd)

        def sendmail(self, from_addr, to_addrs, msg):
            sent["sent"] = (from_addr, to_addrs)

    monkeypatch.setattr(ec.smtplib, "SMTP_SSL", _FakeSMTP)
    out = dispatch("enviar_correo", {"to": "prov@x.com", "subject": "s", "body": "b"})
    assert "enviado" in out.lower()
    assert sent["sent"] == ("yo@gmail.com", ["prov@x.com"])


def test_enviar_correo_smtp_failure_is_handled(monkeypatch):
    import src.tools.enviar_correo as ec

    monkeypatch.setenv("GMAIL_USER", "yo@gmail.com")
    monkeypatch.setenv("GMAIL_APP_PASSWORD", "clave")

    class _FakeSMTPBoom:
        def __init__(self, *a, **k):
            raise OSError("smtp caído")

    monkeypatch.setattr(ec.smtplib, "SMTP_SSL", _FakeSMTPBoom)
    out = dispatch("enviar_correo", {"to": "prov@x.com", "subject": "s", "body": "b"})
    assert out.startswith("[enviar_correo error]")


def test_guardar_sheets_without_creds():
    out = dispatch("guardar_sheets", {"datos": "Pedido: 2 bolsas orellanas -> Juan David"})
    assert "GOOGLE_SHEET_ID" in out  # falta credencial -> avisa, no crashea


def test_programar_recordatorio_runs():
    out = dispatch("programar_recordatorio", {"hora": "09:00", "texto": "valor acción X", "dias": "*"})
    assert "programado" in out.lower()


def test_programar_recordatorio_no_arbitrary_execution():
    # Cierra la falla de seguridad de Jorge: el "self-programming" solo re-dispara
    # tools ya registradas; nunca eval/exec/os.system/subprocess.
    # Nota: estas strings NUNCA se invocan aquí; son patrones prohibidos que el
    # test confirma que están AUSENTES del código fuente de la tool.
    import inspect

    import src.tools.programar_recordatorio as pr

    source = inspect.getsource(pr)
    forbidden_patterns = ("eval" + "(", "exec" + "(", "os.system" + "(", "subprocess")
    for forbidden in forbidden_patterns:
        assert forbidden not in source
