"""Enlace serie/Bluetooth con Bittle (D-04, RI-01, RI-02). El módulo BT se trata como puerto serie.
Solo se transmiten tokens de la lista blanca (RS-01): nunca cargas arbitrarias."""
from typing import Protocol
from seguridad import TOKENS


class LinkError(Exception):
    pass


class SerialPort(Protocol):
    def abrir(self) -> None: ...
    def escribir(self, datos: bytes) -> None: ...
    def cerrar(self) -> None: ...
    @property
    def abierto(self) -> bool: ...


class FakeSerial:
    """Sustituto del robot: registra escrituras e inyecta fallos. NO emula posturas del firmware."""

    simulado = True

    def __init__(self):
        self.escrituras: list[bytes] = []
        self._abierto = False
        self.no_disponible = False       # abrir() falla
        self.fallo_escritura = False     # escribir() falla

    def abrir(self) -> None:
        if self.no_disponible:
            raise LinkError("puerto no disponible")
        self._abierto = True

    def escribir(self, datos: bytes) -> None:
        if not self._abierto or self.fallo_escritura:
            raise LinkError("error de escritura")
        self.escrituras.append(datos)

    def cerrar(self) -> None:
        self._abierto = False

    @property
    def abierto(self) -> bool:
        return self._abierto

    def desconectar(self) -> None:
        """Simula apagar el módulo Bluetooth / salir de alcance."""
        self._abierto = False
        self.no_disponible = True

    def restablecer(self) -> None:
        self.no_disponible = False
        self.fallo_escritura = False


class EnlaceBittle:
    def __init__(self, puerto: SerialPort, tokens_permitidos, terminador: bytes = b""):
        self.puerto = puerto
        self.tokens_permitidos = frozenset(tokens_permitidos) & TOKENS
        if terminador not in (b"", b"\n", b"\r", b"\r\n"):
            raise ValueError("terminador no permitido")
        self.terminador = terminador  # confirmar según hardware (OPEN-02/10/15)

    def conectar(self) -> None:
        if not self.simulado:
            from enlace.serie_real import PuertoSerieReal
            if not isinstance(self.puerto, PuertoSerieReal):
                raise LinkError("Transporte no autorizado: usar FakeSerial o PuertoSerieReal")
            if self.terminador != self.puerto.perfil.terminador:
                raise LinkError("Terminador distinto del perfil físico revisado")
        self.puerto.abrir()

    @property
    def simulado(self) -> bool:
        return isinstance(self.puerto, FakeSerial)

    def activo(self) -> bool:
        return self.puerto.abierto

    def enviar(self, token: str) -> None:
        if not self.simulado:
            from enlace.serie_real import PuertoSerieReal
            if not isinstance(self.puerto, PuertoSerieReal):
                raise LinkError("Transporte físico no autorizado")
        if token not in self.tokens_permitidos:
            raise ValueError(f"token no permitido: {token!r}")
        if not self.activo():
            raise LinkError("enlace inactivo")
        self.puerto.escribir(token.encode("ascii") + self.terminador)

    def cerrar(self) -> None:
        self.puerto.cerrar()
