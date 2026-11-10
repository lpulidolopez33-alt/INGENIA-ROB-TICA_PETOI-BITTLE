"""Nivel 3 — Interfaz hacia el robot: comando capturado frente al esperado (H1 6.3)."""
import json

import pytest

from enlace import EnlaceBittle, FakeSerial, LinkError
from registro import Registro
from reloj import FakeReloj
from vocabulario import Vocabulario


@pytest.mark.caso("TEST-07")
@pytest.mark.req("RS-01", "RI-02", "RF-02")
@pytest.mark.esc("ESC-02")
@pytest.mark.nivel(3)
def test_enlace_solo_envia_tokens_de_la_lista_blanca():
    s = FakeSerial(); e = EnlaceBittle(s, Vocabulario.cargar().tokens_permitidos())
    e.conectar()
    for malo in ("kbalance", "m0 30", "ksit\nkup", "", "KSIT"):
        with pytest.raises(ValueError):
            e.enviar(malo)
    assert s.escrituras == []
    e.enviar("ksit"); e.enviar("kup")
    assert s.escrituras == [b"ksit", b"kup"]          # ASCII, sensible a mayúsculas (CTX-01)


@pytest.mark.caso("TEST-08")
@pytest.mark.req("RI-01", "RFI-02", "RS-02")
@pytest.mark.esc("ESC-08")
@pytest.mark.nivel(3)
def test_enlace_inactivo_o_con_error_lanza_linkerror_y_no_escribe():
    s = FakeSerial(); e = EnlaceBittle(s, {"ksit"})
    with pytest.raises(LinkError):
        e.enviar("ksit")                               # sin conectar
    e.conectar(); s.fallo_escritura = True
    with pytest.raises(LinkError):
        e.enviar("ksit")
    assert s.escrituras == []


@pytest.mark.caso("TEST-09")
@pytest.mark.req("RM-01", "RM-02")
@pytest.mark.esc("ESC-03", "ESC-08")
@pytest.mark.nivel(3)
def test_registro_jsonl_en_fichero_con_campos_obligatorios(tmp_path):
    f = tmp_path / "reg.jsonl"
    reg = Registro(FakeReloj(), f)
    reg.registrar("siéntate", "enviada", "sentarse", 0.95)
    reg.registrar("", "error", tipo_error="perdida_enlace")
    lineas = [json.loads(x) for x in f.read_text(encoding="utf-8").splitlines()]
    assert len(lineas) == 2
    for ev in lineas:
        assert {"fecha", "hora", "texto", "resultado"} <= ev.keys()
    assert lineas[1]["tipo_error"] == "perdida_enlace"


@pytest.mark.caso("TEST-10")
@pytest.mark.req("RR-03", "RD-01")
@pytest.mark.esc("ESC-01")
@pytest.mark.nivel(3)
def test_inspeccion_adaptador_vosk_no_usa_red_y_carga_modelos_locales():
    from pathlib import Path
    fuente = Path("src/voz/vosk_reconocedor.py").read_text(encoding="utf-8")
    for prohibido in ("requests", "urllib", "http://", "https://", "socket", "lang="):
        assert prohibido not in fuente, prohibido     # Model(lang=...) descargaría el modelo
    assert "Model(self.rutas[idioma])" in fuente      # modelo por ruta local
    assert not list(Path("src").rglob("*.js")), "RD-01: la lógica es solo Python"
