import pytest
from conftest import Entorno
from voz import Resultado
from vocabulario import Vocabulario, Intencion
from enlace import EnlaceBittle, FakeSerial
from estado import Estado

pytestmark = [pytest.mark.caso("TEST-33"), pytest.mark.req("RS-01", "RS-02", "RFI-01"),
              pytest.mark.esc("ESC-08", "ESC-10", "ESC-12"), pytest.mark.nivel(2)]


@pytest.mark.parametrize("conf", [None, float("nan"), float("inf"), -float("inf"),
                                  -.1, 1.1, "0.95", True, [], {}])
def test_confianza_invalida_no_escribe(conf):
    e = Entorno().arrancar()
    assert e.decir("siéntate", confianza=conf).resultado == "rechazada"
    assert not e.serie.escrituras


@pytest.mark.parametrize("r", [{}, object(), "siéntate", Resultado(None, .9, None, None)])
def test_resultado_mal_formado(r):
    e = Entorno().arrancar()
    assert e.ctrl.procesar(r).resultado == "rechazada"
    assert not e.serie.escrituras


def test_modelo_ausente_bloquea_inicio_y_escucha():
    e = Entorno()
    e.reco.idiomas_sin_modelo.add("es")
    assert not e.ctrl.iniciar_sesion()
    assert not e.ctrl.activar_escucha()
    assert not e.serie.abierto


def test_procesamiento_directo_con_escucha_desactivada():
    e = Entorno().arrancar()
    e.ctrl.desactivar_escucha()
    r = Resultado("siéntate", .95, e.reloj.ahora(), e.reloj.ahora())
    assert e.ctrl.procesar(r).motivo == "escucha_inactiva"
    assert not e.serie.escrituras


def test_json_no_autoriza_movimiento_nuevo():
    e = Entorno().arrancar()
    v = Vocabulario([Intencion("sentarse", "movimiento", "kbalance", "", {"es": ["siéntate"]})])
    e.ctrl.traductor.vocabulario = v
    assert e.decir("siéntate").motivo == "accion_no_autorizada"
    s = FakeSerial()
    enlace = EnlaceBittle(s, {"kbalance"})
    enlace.conectar()
    with pytest.raises(ValueError):
        enlace.enviar("kbalance")
    assert not s.escrituras


def test_reconexion_no_acredita_reposo():
    e = Entorno().arrancar()
    e.decir("siéntate")
    e.serie.desconectar()
    e.ctrl.vigilar_enlace()
    e.serie.restablecer()
    assert e.ctrl.reconectar()
    assert e.ctrl.gestor.estado is Estado.DESCONOCIDO
    assert e.decir("ponte de pie").motivo == "estado_desconocido"
    assert not e.ctrl.cerrar_sesion().ok
    assert e.serie.escrituras == [b"ksit"]
    assert e.ctrl.confirmar_reposo("Reposo simulado por el operador")
    assert e.ctrl.activar_escucha()
    assert e.decir("ponte de pie").resultado == "enviada"
