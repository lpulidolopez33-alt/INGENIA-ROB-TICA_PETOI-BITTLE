"""Panel local: ninguna prueba abre hardware real."""
import importlib.util
import json
import sys
import threading
import types
import urllib.request
import urllib.error
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
try:
    import bittle_web as web
finally:
    sys.path.pop(0)


def test_arranque_sin_conexion_ni_escucha():
    panel = web.Panel()
    assert panel.estado()["conexion"] == "desconectado"
    assert panel.estado()["microfono"] == "apagado"
    assert panel.enlace is None
    with pytest.raises(ValueError):
        panel.ordenar("siéntate")


def test_simulacion_cola_y_desconexion():
    panel = web.Panel()
    panel.conectar(segundos=.01)
    try:
        assert panel.ordenar("siéntate y ponte de pie")
        assert panel.cola.esperar_vacia(2)
        assert panel.estado()["ultima_frase"] == "siéntate y ponte de pie"
        assert not panel.ordenar("no camina")
    finally:
        panel.desconectar()
    assert panel.estado()["conexion"] == "desconectado"


def test_parada_visible_descarta_pendientes():
    panel = web.Panel()
    panel.conectar(segundos=30)
    try:
        panel.ordenar("siéntate y ponte de pie y descansa")
        panel.ordenar("para")
        assert panel.cola.esperar_vacia(2)
        assert panel.estado()["cola"]["pendientes"] == []
    finally:
        panel.desconectar()


def test_error_conexion_restaura_estado(monkeypatch):
    def fallar(*args):
        raise OSError("COM ocupado")
    monkeypatch.setattr(web.bittle, "EnlaceSerie", fallar)
    panel = web.Panel()
    with pytest.raises(OSError):
        panel.conectar("serie", "COM6")
    assert panel.estado()["conexion"] == "desconectado"
    assert "COM ocupado" in panel.estado()["error"]


def test_modelo_ausente_no_activa_microfono(tmp_path):
    panel = web.Panel()
    with pytest.raises(ValueError):
        panel.activar_microfono(str(tmp_path / "inexistente"))
    assert panel.estado()["microfono"] == "apagado"


def test_apagar_durante_carga_no_abre_captura(monkeypatch, tmp_path):
    cargando, seguir = threading.Event(), threading.Event()
    def modelo(ruta):
        cargando.set()
        assert seguir.wait(2)
        return object()
    def captura(**kwargs):
        pytest.fail("No debe abrir captura tras desactivar")
    monkeypatch.setitem(sys.modules, "vosk", types.SimpleNamespace(Model=modelo, KaldiRecognizer=lambda *a: object(), SetLogLevel=lambda n: None))
    monkeypatch.setitem(sys.modules, "sounddevice", types.SimpleNamespace(RawInputStream=captura))
    panel = web.Panel()
    panel.conectar()
    try:
        panel.activar_microfono(str(tmp_path))
        assert cargando.wait(2)
        assert panel.estado()["microfono"] == "cargando"
        panel.apagar_microfono()
        seguir.set()
        panel.mic_hilo.join(2)
        assert not panel.mic_hilo.is_alive()
        assert panel.estado()["microfono"] == "apagado"
    finally:
        seguir.set()
        panel.desconectar()


def test_microfono_informa_error_de_apertura(monkeypatch, tmp_path):
    def captura(**kwargs):
        raise OSError("Dispositivo no disponible")
    monkeypatch.setitem(sys.modules, "vosk", types.SimpleNamespace(Model=lambda p: object(), KaldiRecognizer=lambda *a: object(), SetLogLevel=lambda n: None))
    monkeypatch.setitem(sys.modules, "sounddevice", types.SimpleNamespace(RawInputStream=captura))
    panel = web.Panel()
    panel.conectar()
    try:
        panel.activar_microfono(str(tmp_path))
        panel.mic_hilo.join(2)
        assert panel.estado()["microfono"] == "apagado"
        assert "Dispositivo no disponible" in panel.estado()["error"]
    finally:
        panel.desconectar()


def test_resultado_tardio_no_se_encola_al_apagar(monkeypatch, tmp_path):
    procesando, seguir = threading.Event(), threading.Event()
    class Reconocedor:
        def AcceptWaveform(self, datos):
            procesando.set()
            assert seguir.wait(2)
            return True
        def Result(self):
            return '{"text":"camina"}'
    class Captura:
        def __init__(self, **kw):
            self.callback = kw["callback"]
        def __enter__(self):
            self.callback(b'\0\0' * 4000, 4000, None, None)
        def __exit__(self, *args):
            pass
    monkeypatch.setitem(sys.modules, "vosk", types.SimpleNamespace(Model=lambda p: object(), KaldiRecognizer=lambda *a: Reconocedor(), SetLogLevel=lambda n: None))
    monkeypatch.setitem(sys.modules, "sounddevice", types.SimpleNamespace(RawInputStream=Captura))
    panel = web.Panel()
    panel.conectar()
    try:
        panel.activar_microfono(str(tmp_path))
        assert procesando.wait(2)
        assert panel.estado()["microfono"] == "escuchando"
        panel.apagar_microfono()
        seguir.set()
        panel.mic_hilo.join(2)
        assert panel.estado()["ultima_frase"] == ""
        assert panel.estado()["cola"]["pendientes"] == []
    finally:
        seguir.set()
        panel.desconectar()


def test_http_pagina_estado_y_proteccion_de_acciones():
    panel = web.Panel()
    server = web.crear_servidor(panel, 0)
    hilo = threading.Thread(target=server.serve_forever, daemon=True)
    hilo.start()
    base = f"http://127.0.0.1:{server.server_port}"
    try:
        with urllib.request.urlopen(base) as r:
            html = r.read().decode()
        assert "__TOKEN__" not in html
        assert "Activar micrófono" in html
        token = html.split("const token='")[1].split("'")[0]
        def post(token_value, origin=base):
            return urllib.request.Request(base + "/api/conectar", data=b'{"modo":"simulado"}', headers={"X-Bittle-Token": token_value, "Origin": origin}, method="POST")
        for request in (post("incorrecto"), post(token, "http://otro-sitio.test")):
            with pytest.raises(urllib.error.HTTPError) as error:
                urllib.request.urlopen(request)
            assert error.value.code == 403
        with urllib.request.urlopen(post(token)) as r:
            assert json.load(r)["conexion"] == "simulado"
        with urllib.request.urlopen(base + "/api/estado") as r:
            assert json.load(r)["microfono"] == "apagado"
    finally:
        server.shutdown()
        server.server_close()
        hilo.join(2)
        panel.desconectar()
