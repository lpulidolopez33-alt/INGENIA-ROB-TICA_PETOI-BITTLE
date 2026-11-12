"""Pruebas sin micrófono, Bluetooth ni robot para el ejecutable bittle_voz."""
import importlib.util
import threading
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location("bittle_voz", Path(__file__).resolve().parents[2] / "bittle_voz.py")
bittle = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bittle)


@pytest.mark.parametrize("frase,tokens", [
    ("Siéntate y después ponte de pie", ["ksit", "kup"]),
    ("primero siéntate, luego levántate, saluda y descansa", ["ksit", "kup", "khi", "krest"]),
    ("marcha atrás y ponte de pie", ["kbk", "kup"]),
    ("siéntate y siéntate", ["ksit", "ksit"]),
    ("camina y PARA y saluda", ["kbalance"]),
    ("no camina", []),
    ("siéntate [unk] camina", []),
    ("siéntate y vuela", []),
])
def test_interpretacion(frase, tokens):
    assert [t for t, _ in bittle.buscar_comandos(frase)] == tokens


class Enlace:
    def __init__(self):
        self.tokens = []
        self.primero = threading.Event()

    def enviar(self, token):
        self.tokens.append(token)
        self.primero.set()


def test_fifo_frases_separadas_y_repeticiones():
    enlace = Enlace()
    cola = bittle.ColaAcciones(enlace, segundos=0.01)
    try:
        cola.agregar(bittle.buscar_comandos("siéntate y ponte de pie"))
        cola.agregar(bittle.buscar_comandos("siéntate y siéntate"))
        assert cola.esperar_vacia(2)
        assert enlace.tokens == ["ksit", "kup", "ksit", "ksit"]
    finally:
        cola.cerrar()


def test_parada_cancela_espera_y_pendientes():
    enlace = Enlace()
    cola = bittle.ColaAcciones(enlace, segundos=30)
    try:
        cola.agregar(bittle.buscar_comandos("siéntate y ponte de pie y saluda"))
        assert enlace.primero.wait(2)
        cola.agregar(bittle.buscar_comandos("para"))
        assert cola.esperar_vacia(2)
        assert enlace.tokens == ["ksit", "kbalance"]
    finally:
        cola.cerrar()


def test_coreografia_completa_antes_de_siguiente(monkeypatch):
    monkeypatch.setitem(bittle.COREOGRAFIAS, "BAILE", [("kbalance", .01), ("khi", .01)])
    enlace = Enlace()
    cola = bittle.ColaAcciones(enlace, segundos=.01)
    try:
        cola.agregar(bittle.buscar_comandos("baila y siéntate"))
        assert cola.esperar_vacia(2)
        assert enlace.tokens == ["kbalance", "khi", "ksit"]
    finally:
        cola.cerrar()


def test_parada_corta_coreografia(monkeypatch):
    monkeypatch.setitem(bittle.COREOGRAFIAS, "BAILE", [("khi", 30), ("krest", 30)])
    enlace = Enlace()
    cola = bittle.ColaAcciones(enlace)
    try:
        cola.agregar(bittle.buscar_comandos("baila y siéntate"))
        assert enlace.primero.wait(2)
        cola.agregar(bittle.buscar_comandos("para"))
        assert cola.esperar_vacia(2)
        assert enlace.tokens == ["khi", "kbalance"]
    finally:
        cola.cerrar()


def test_caminar_tiene_fin_temporizado():
    enlace = Enlace()
    cola = bittle.ColaAcciones(enlace, segundos=.01)
    try:
        cola.agregar(bittle.buscar_comandos("camina y siéntate"))
        assert cola.esperar_vacia(2)
        assert enlace.tokens == ["kwkF", "kbalance", "ksit"]
    finally:
        cola.cerrar()


def test_error_descarta_secuencia():
    enlace = Enlace()
    def fallar(token):
        enlace.tokens.append(token)
        raise OSError("enlace perdido")
    enlace.enviar = fallar
    cola = bittle.ColaAcciones(enlace, segundos=.01)
    try:
        cola.agregar(bittle.buscar_comandos("siéntate y ponte de pie"))
        assert cola.esperar_vacia(2)
        assert enlace.tokens == ["ksit"]
    finally:
        cola.cerrar()


def test_limite_rechaza_frase_entera():
    enlace = Enlace()
    cola = bittle.ColaAcciones(enlace, capacidad=2)
    try:
        assert not cola.agregar(bittle.buscar_comandos("siéntate y ponte de pie y saluda"))
        assert enlace.tokens == []
    finally:
        cola.cerrar()


def test_cierre_descarta_pendientes_y_termina_hilo():
    enlace = Enlace()
    cola = bittle.ColaAcciones(enlace, segundos=30)
    cola.agregar(bittle.buscar_comandos("siéntate y ponte de pie"))
    assert enlace.primero.wait(2)
    cola.cerrar()
    assert not cola._hilo.is_alive()
    assert enlace.tokens == ["ksit"]
    assert not cola.agregar(bittle.buscar_comandos("camina"))
