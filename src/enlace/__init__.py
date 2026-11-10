"""Enlace serie/Bluetooth con Bittle (D-04, RI-01, RI-02). El módulo BT se trata como puerto serie.
Solo se transmiten tokens de la lista blanca (RS-01): nunca cargas arbitrarias."""
from typing import Protocol


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
        self.tokens_permitidos = frozenset(tokens_permitidos)
        self.terminador = terminador  # a confirmar con la documentación de Petoi (T004)

    def conectar(self) -> None:
        self.puerto.abrir()

    def activo(self) -> bool:
        return self.puerto.abierto

    def enviar(self, token: str) -> None:
        if token not in self.tokens_permitidos:
            raise ValueError(f"token no permitido: {token!r}")
        if not self.activo():
            raise LinkError("enlace inactivo")
        self.puerto.escribir(token.encode("ascii") + self.terminador)

    def cerrar(self) -> None:
        self.puerto.cerrar()
