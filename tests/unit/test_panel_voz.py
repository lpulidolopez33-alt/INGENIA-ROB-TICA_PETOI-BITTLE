"""Pruebas sin interfaz gráfica, micrófono, Bluetooth ni red para el panel."""
from datetime import datetime, timezone
from queue import Queue
from threading import Event
from time import monotonic, sleep

from cola_voz import ColaSecuencial
from enlace import EnlaceBittle, FakeSerial
from panel_voz import ControlMicrofono, describir
from vocabulario import Vocabulario
from voz import Resultado


class ReconocedorFalso:
    def __init__(self):
        self.cargado = False
        self.fallo = False
        self.entrada = []
        self.capturando = Event()

    def cargar_modelo(self, idioma):
        assert idioma == "es"
        self.cargado = True

    def disponible(self):
        return not self.fallo

    def escuchar(self, timeout, cancelar=None):
        self.capturando.set()
        if cancelar is not None:
            cancelar.wait(timeout=.025)
        else:
            sleep(.025)
        if self.entrada:
            return self.entrada.pop(0)
        return None


def resultado(texto):
    instante = datetime.now(timezone.utc)
    return Resultado(texto, .99, instante, instante)


def hasta(condicion, limite=2):
    fin = monotonic() + limite
    while monotonic() < fin:
        if condicion():
            return True
        sleep(.01)
    return condicion()


def preparar():
    puerto = FakeSerial()
    enlace = EnlaceBittle(puerto, ["ksit", "kup"])
    enlace.conectar()
    cola = ColaSecuencial(enlace, duracion_minima=.20, avisar=lambda _: None)
    cola.iniciar()
    recon = ReconocedorFalso()
    eventos = Queue()
    control = ControlMicrofono(recon, Vocabulario.cargar(), cola, eventos)
    control.iniciar()
    return control, recon, cola, puerto, eventos


def terminar(control, cola):
    control.cerrar()
    cola.detener()


def test_inicia_apagado_y_no_escucha_hasta_activar():
    control, recon, cola, puerto, _ = preparar()
    try:
        assert not control.activo
        recon.entrada.append(resultado("siéntate"))
        sleep(.05)
        assert not recon.capturando.is_set()
        assert puerto.escrituras == []
        control.cambiar(True)
        assert hasta(lambda: recon.capturando.is_set())
        assert hasta(lambda: puerto.escrituras == [b"ksit"])
    finally:
        terminar(control, cola)


def test_desactivar_descarta_resultado_tardio():
    control, recon, cola, puerto, eventos = preparar()
    try:
        control.cambiar(True)
        assert hasta(lambda: recon.capturando.is_set())
        control.cambiar(False)
        recon.entrada.append(resultado("siéntate"))
        sleep(.08)
        assert not control.activo
        assert puerto.escrituras == []
        assert cola.estado()["pendientes"] == ()
    finally:
        terminar(control, cola)


def test_secuencia_y_estado_visible():
    control, recon, cola, puerto, eventos = preparar()
    try:
        recon.entrada.append(resultado("siéntate y luego ponte de pie"))
        control.cambiar(True)
        assert hasta(lambda: puerto.escrituras == [b"ksit", b"kup"])
        tipos = []
        while not eventos.empty():
            tipos.append(eventos.get_nowait()[0])
        assert "microfono" in tipos
        assert "frase" in tipos
        assert "accion" in tipos
        assert describir(("ksit", "kup")) == "Sentarse → Ponerse de pie"
    finally:
        terminar(control, cola)


def test_fallo_micro_desactiva_y_pausa_cola():
    control, recon, cola, puerto, eventos = preparar()
    try:
        recon.fallo = True
        control.cambiar(True)
        assert hasta(lambda: not control.activo)
        assert cola.estado()["pausada"]
        assert puerto.escrituras == []
        assert any(item == ("microfono", "ERROR / DESACTIVADO")
                   for item in list(eventos.queue))
    finally:
        terminar(control, cola)


def test_los_movimientos_pendientes_no_desaparecen_al_apagar_micro():
    control, recon, cola, puerto, _ = preparar()
    try:
        cola.pausar()
        cola.agregar(("ksit", "kup"))
        control.cambiar(True)
        control.cambiar(False)
        assert cola.estado()["pendientes"] == ("ksit", "kup")
        assert puerto.escrituras == []
    finally:
        terminar(control, cola)
