import pytest

from app.controlador import Controlador
from avisos import Avisos
from config import Config
from enlace import EnlaceBittle, FakeSerial
from registro import Registro
from reloj import FakeReloj
from vocabulario import Vocabulario
from voz import FakeRecognizer


class Entorno:
    """Sistema completo con sustitutos de micrófono y robot (sin hardware)."""

    def __init__(self, config: Config = Config(), idioma: str = "es", latencia: float = 0.3):
        self.reloj = FakeReloj()
        self.vocab = Vocabulario.cargar()
        self.reco = FakeRecognizer(self.reloj, latencia=latencia)
        self.serie = FakeSerial()
        self.enlace = EnlaceBittle(self.serie, self.vocab.tokens_permitidos())
        self.registro = Registro(self.reloj)
        self.avisos = Avisos(self.reloj)
        self.ctrl = Controlador(self.vocab, self.reco, self.enlace, self.registro,
                                self.avisos, self.reloj, config, idioma)

    def arrancar(self):
        """ESC-01 completo: enlace + escucha activa."""
        assert self.ctrl.iniciar_sesion()
        assert self.ctrl.activar_escucha()
        return self

    def decir(self, texto, confianza=0.95, **kw):
        self.reco.encolar(texto, confianza, **kw)
        return self.ctrl.escuchar()


@pytest.fixture
def env():
    return Entorno()


@pytest.fixture
def env_listo():
    return Entorno().arrancar()
