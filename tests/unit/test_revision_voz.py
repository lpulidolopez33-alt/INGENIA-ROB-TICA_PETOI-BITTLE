import json
import sys
from dataclasses import replace
from types import SimpleNamespace
import pytest
from conftest import Entorno
from reloj import Reloj
from voz import Resultado
from voz.vosk_reconocedor import VoskReconocedor

pytestmark = [pytest.mark.caso("TEST-37"), pytest.mark.req("RS-01", "RF-04", "RF-10"),
              pytest.mark.esc("ESC-09", "ESC-10", "ESC-11"), pytest.mark.nivel(2)]


def construir(monkeypatch, tmp_path, audio, texto="estado", parcial=False, palabras=None):
    creaciones = []
    class Flujo:
        def __init__(self, **kw): pass
        def __enter__(self): return self
        def __exit__(self, *args): pass
        def read(self, n): return audio, False
    class Rec:
        def __init__(self, *args):
            assert len(args) == 2  # sin gramática restringida
            creaciones.append(self)
        def SetWords(self, b): pass
        def AcceptWaveform(self, d): return not parcial
        def Result(self):
            return json.dumps({"text": texto, "result": palabras if palabras is not None else
                              [{"word": w, "conf": .99, "end": 0} for w in texto.split()]})
    monkeypatch.setitem(sys.modules, "sounddevice", SimpleNamespace(
        query_devices=lambda *a, **kw: {"max_input_channels": 1}, RawInputStream=Flujo))
    monkeypatch.setitem(sys.modules, "vosk", SimpleNamespace(Model=lambda p: object(), KaldiRecognizer=Rec))
    r = VoskReconocedor({"es": str(tmp_path)}, {"es": ["estado", "siéntate"]})
    r.cargar_modelo("es")
    return r, creaciones


@pytest.mark.parametrize("texto", ["estado", "siéntate", "ponte de pie"])
def test_silencio_digital_rechaza_incluso_alucinacion_del_motor(monkeypatch, tmp_path, texto):
    r, _ = construir(monkeypatch, tmp_path, bytes(8000), texto)
    assert r.escuchar(.02) is None


def test_parciales_no_se_usan_y_capturas_independientes(monkeypatch, tmp_path):
    r, instancias = construir(monkeypatch, tmp_path, b"\x01\x00" * 4000, "siéntate", parcial=True)
    assert r.escuchar(.002) is None
    assert r.escuchar(.002) is None
    assert len(instancias) == 2 and instancias[0] is not instancias[1]


@pytest.mark.parametrize("texto", ["ruido", "[unk]", "", "hola estado", "siéntate ponte de pie"])
def test_ruido_o_texto_ajeno_no_es_orden(monkeypatch, tmp_path, texto):
    r, _ = construir(monkeypatch, tmp_path, b"\x17\xff" * 4000, texto)
    e = Entorno().arrancar()
    assert e.ctrl.procesar(r.escuchar(.002)).resultado == "rechazada"
    assert not e.serie.escrituras


def test_minimo_por_palabra_no_oculta_palabra_insegura(monkeypatch, tmp_path):
    palabras = [{"word": w, "conf": c, "end": 0} for w, c in
                [("ponte", .99), ("de", .4), ("pie", .99)]]
    r, _ = construir(monkeypatch, tmp_path, b"\x01\x00", "ponte de pie", palabras=palabras)
    resultado = r.escuchar(.02)
    assert resultado.confianza == .4
    e = Entorno().arrancar()
    assert e.ctrl.procesar(resultado).motivo == "baja_confianza"
    assert not e.serie.escrituras


@pytest.mark.parametrize("defecto", ["repetida", "caducada", "futura", "sin_id"])
def test_frescura_captura(defecto):
    e = Entorno().arrancar()
    e.reloj.avanzar(10)
    r = Resultado("estado", .99, e.reloj.ahora(), e.reloj.ahora(), 10,
                  "estimado_vosk", "una_captura", 10)
    if defecto == "repetida": assert e.ctrl.procesar(r).resultado == "aceptada"
    elif defecto == "caducada": e.reloj.avanzar(6)
    elif defecto == "futura": r = replace(r, emitido_monotonic=20)
    else: r = replace(r, captura_id=None)
    assert e.ctrl.procesar(r).motivo == "captura_invalidada"
    assert not e.serie.escrituras


def test_desactivar_durante_captura_descarta_resultado(monkeypatch):
    e = Entorno().arrancar()
    def capturar(timeout):
        e.ctrl.desactivar_escucha()
        e.ctrl.activar_escucha()
        return Resultado("siéntate", .99, e.reloj.ahora(), e.reloj.ahora())
    monkeypatch.setattr(e.reco, "escuchar", capturar)
    assert e.ctrl.escuchar().motivo == "captura_invalidada"
    assert not e.serie.escrituras
