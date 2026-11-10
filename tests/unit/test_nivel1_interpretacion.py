"""Nivel 1 — Interpretación de entradas (H1 6.3; presentación paso 6)."""
import pytest

from config import Config
from traductor import Traductor
from vocabulario import Vocabulario, normalizar
from voz import Resultado
from reloj import FakeReloj

R = FakeReloj()
T = Traductor(Vocabulario.cargar(), Config())


def res(texto, conf=0.95):
    return Resultado(texto, conf, R.ahora(), R.ahora())


@pytest.mark.caso("TEST-01")
@pytest.mark.req("RF-01", "RD-02")
@pytest.mark.esc("ESC-02", "ESC-03", "ESC-04")
@pytest.mark.nivel(1)
@pytest.mark.parametrize("idioma,frase,intencion", [
    ("es", "siéntate", "sentarse"), ("es", "ponte de pie", "ponerse_de_pie"),
    ("es", "historial", "historial"), ("es", "estado", "estado"),
    ("en", "sit", "sentarse"), ("en", "stand up", "ponerse_de_pie"),
    ("en", "history", "historial"), ("en", "status", "estado"),
])
def test_frases_canonicas_se_reconocen_en_su_idioma(idioma, frase, intencion):
    i = T.interpretar(res(frase), idioma)
    assert i.valida and i.intencion.id == intencion


@pytest.mark.caso("TEST-02")
@pytest.mark.req("RF-04", "RS-01")
@pytest.mark.esc("ESC-09")
@pytest.mark.nivel(1)
@pytest.mark.parametrize("idioma,frase", [
    ("es", "corre"), ("es", "salta"), ("es", "sit"), ("en", "siéntate"), ("es", "kbalance"),
    ("es", "siéntate y ponte de pie"),
])
def test_entrada_fuera_de_vocabulario_o_de_idioma_no_es_valida(idioma, frase):
    i = T.interpretar(res(frase), idioma)
    assert not i.valida and i.motivo == "no_reconocida"


@pytest.mark.caso("TEST-03")
@pytest.mark.req("RF-04", "RS-01", "RF-01")
@pytest.mark.esc("ESC-10")
@pytest.mark.nivel(1)
def test_umbral_u_frontera():
    u = Config().umbral_u
    assert T.interpretar(res("siéntate", u), "es").valida                   # = U se acepta
    bajo = T.interpretar(res("siéntate", u - 0.01), "es")                   # < U no
    assert not bajo.valida and bajo.motivo == "baja_confianza"


@pytest.mark.caso("TEST-04")
@pytest.mark.req("RF-01")
@pytest.mark.esc("ESC-02")
@pytest.mark.nivel(1)
@pytest.mark.parametrize("texto", ["¡Siéntate!", "SIENTATE", "  siéntate  ", "Siéntate."])
def test_normalizacion_de_mayusculas_tildes_y_signos(texto):
    assert T.interpretar(res(texto), "es").valida
    assert normalizar(texto) == "sientate"


@pytest.mark.caso("TEST-05")
@pytest.mark.req("RS-01", "RS-03", "RI-02")
@pytest.mark.esc("ESC-13")
@pytest.mark.nivel(1)
def test_vocabulario_solo_tokens_ksit_kup_y_sin_orden_de_parada_por_voz():
    v = Vocabulario.cargar()
    assert v.tokens_permitidos() == {"ksit", "kup"}
    ids = {i.id for i in v.intenciones}
    assert ids == {"sentarse", "ponerse_de_pie", "historial", "estado"}   # sin «para»/«stop»
    for it in v.intenciones:
        if not it.es_movimiento:
            assert it.token is None


@pytest.mark.caso("TEST-06")
@pytest.mark.req("RF-04")
@pytest.mark.esc("ESC-11")
@pytest.mark.nivel(1)
@pytest.mark.parametrize("r", [None, "", "   "])
def test_silencio_o_texto_vacio_es_silencio(r):
    obj = None if r is None else res(r)
    assert T.interpretar(obj, "es").motivo == "silencio"
