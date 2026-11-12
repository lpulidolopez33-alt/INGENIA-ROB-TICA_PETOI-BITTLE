"""Pruebas de la cola de micrófono: no requieren robot, sonido ni red."""
from datetime import datetime, timezone
import time

from cola_voz import ColaSecuencial, interpretar_voz, frases_vosk
from enlace import EnlaceBittle, FakeSerial
from vocabulario import Vocabulario
from voz import Resultado


def reconocer(texto, confianza=0.99):
    ahora = datetime.now(timezone.utc)
    return Resultado(texto, confianza, ahora, ahora)


def esperar(condicion, timeout=1.0):
    plazo = time.monotonic() + timeout
    while time.monotonic() < plazo:
        if condicion():
            return True
        time.sleep(.005)
    return condicion()


def preparar(intervalo=0.08, capacidad=8):
    puerto = FakeSerial()
    enlace = EnlaceBittle(puerto, ["ksit", "kup"])
    enlace.conectar()
    cola = ColaSecuencial(enlace, duracion_minima=intervalo, capacidad=capacidad,
                          avisar=lambda _: None)
    return cola, puerto


def test_cadenas_y_sinonimos_normalizados():
    vocab = Vocabulario.cargar()
    orden = interpretar_voz(reconocer("Siéntate y luego ponte de pie"), vocab)
    assert orden.tipo == "movimiento" and orden.tokens == ("ksit", "kup")
    assert interpretar_voz(reconocer("siéntate, ponte de pie"), vocab).tokens == ("ksit", "kup")
    assert interpretar_voz(reconocer("Pausa la cola"), vocab).tipo == "pausar"
    assert interpretar_voz(reconocer("Vacía la cola"), vocab).tipo == "vaciar"
    assert interpretar_voz(reconocer("Reanuda la cola"), vocab).tipo == "reanudar"
    assert "siéntate y luego ponte de pie" in frases_vosk(vocab)


def test_ordenes_inseguras_y_baja_confianza_rechazadas():
    vocab = Vocabulario.cargar()
    for texto in ("da una voltereta", "siéntate y salta", "ksit",
                  "siéntate y siéntate y siéntate y siéntate y siéntate"):
        assert interpretar_voz(reconocer(texto), vocab) is None
    assert interpretar_voz(reconocer("siéntate", .5), vocab) is None
    assert interpretar_voz(None, vocab) is None


def test_envio_fifo_una_por_una():
    cola, serial = preparar()
    try:
        assert cola.agregar(("ksit", "kup"))[0]
        cola.iniciar()
        assert esperar(lambda: len(serial.escrituras) == 2)
        assert serial.escrituras == [b"ksit", b"kup"]
    finally:
        cola.detener()


def test_pausa_sin_descartar_y_reanudacion():
    cola, serial = preparar()
    cola.pausar()
    try:
        cola.iniciar()
        assert cola.agregar(("ksit", "kup"))[0]
        time.sleep(.05)
        assert serial.escrituras == []
        assert cola.estado()["pendientes"] == ("ksit", "kup")
        assert cola.reanudar()
        assert esperar(lambda: len(serial.escrituras) == 2)
    finally:
        cola.detener()


def test_vaciar_no_revierte_accion_enviada():
    cola, serial = preparar(intervalo=.3)
    try:
        cola.iniciar()
        assert cola.agregar(("ksit", "kup"))[0]
        assert esperar(lambda: len(serial.escrituras) == 1)
        assert cola.vaciar() == 1
        time.sleep(.05)
        assert serial.escrituras == [b"ksit"]
    finally:
        cola.detener()


def test_limite_de_cola_y_allowlist():
    cola, serial = preparar(capacidad=2)
    try:
        assert cola.agregar(("ksit", "kup"))[0]
        assert cola.agregar(("ksit",))[0] is False
        assert cola.agregar(("kflip",))[0] is False
        assert cola.estado()["pendientes"] == ("ksit", "kup")
        cola.iniciar()
        assert esperar(lambda: len(serial.escrituras) == 2)
    finally:
        cola.detener()


def test_desconexion_borra_pendientes_y_no_reintenta():
    cola, serial = preparar(intervalo=.3)
    try:
        cola.iniciar()
        cola.agregar(("ksit", "kup"))
        assert esperar(lambda: len(serial.escrituras) == 1)
        serial.desconectar()
        assert esperar(lambda: cola.estado()["fallo"] is not None, timeout=1)
        assert serial.escrituras == [b"ksit"]
        assert cola.estado()["pendientes"] == ()
        assert cola.agregar(("ksit",))[0] is False
        assert cola.reanudar() is False
    finally:
        cola.detener()


def test_detener_descarta_pendientes():
    cola, serial = preparar(intervalo=.3)
    cola.pausar()
    cola.iniciar()
    cola.agregar(("ksit", "kup"))
    cola.detener()
    assert cola.estado()["pendientes"] == ()
    assert serial.escrituras == []
