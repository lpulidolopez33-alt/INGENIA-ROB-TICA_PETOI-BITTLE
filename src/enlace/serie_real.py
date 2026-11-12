"""Transporte pyserial preparado para H4; nunca abre en el constructor.

Las referencias son declaraciones auditables del operador, no aprobaciones
emitidas por el programa. No existe configuración física aprobada en el repo.
"""
from dataclasses import dataclass
from math import isfinite
from enlace import LinkError
from seguridad import TOKENS
from config import Config
from datetime import datetime, timezone


@dataclass(frozen=True)
class PerfilFisico:
    puerto: str
    baudrate: int
    terminador: bytes
    modelo: str
    firmware: str
    referencia_protocolo: str
    aprobacion_parametros: str
    aprobacion_seguridad: str
    parametros: Config
    timeout: float = 1.0

    def validar(self):
        if not isinstance(self.parametros, Config):
            raise LinkError("Faltan parámetros de control revisados")
        for nombre in ("puerto", "modelo", "firmware", "referencia_protocolo",
                       "aprobacion_parametros", "aprobacion_seguridad"):
            if not isinstance(getattr(self, nombre), str) or not getattr(self, nombre).strip():
                raise LinkError(f"Modo físico bloqueado: falta {nombre}")
        if type(self.baudrate) is not int or self.baudrate <= 0:
            raise LinkError("Velocidad serie sin validar")
        if self.terminador not in (b"", b"\n", b"\r", b"\r\n"):
            raise LinkError("Terminador sin validar")
        if type(self.timeout) not in (int, float) or not isfinite(self.timeout) or self.timeout <= 0:
            raise LinkError("Timeout inválido")


class PuertoSerieReal:
    simulado = False

    def __init__(self, perfil: PerfilFisico, fabrica=None):
        self.perfil = perfil
        self._fabrica = fabrica
        self._serial = None
        self._sesion = None
        self.eventos = []

    def _evento(self, datos):
        self.eventos.append({"fecha_utc": datetime.now(timezone.utc).isoformat(), **datos})

    def habilitar(self, autorizacion_sesion: str):
        self.perfil.validar()
        if not isinstance(autorizacion_sesion, str) or not autorizacion_sesion.strip():
            raise LinkError("Falta autorización expresa de la sesión supervisada")
        self._sesion = autorizacion_sesion
        self._evento({"evento": "habilitacion", "referencia": autorizacion_sesion})

    def abrir(self):
        self.perfil.validar()
        if not self._sesion:
            raise LinkError("Modo físico bloqueado: sesión no habilitada")
        if self.abierto:
            return
        try:
            if self._fabrica is None:
                import serial
                fabrica = serial.Serial
            else:
                fabrica = self._fabrica
            self._serial = fabrica(port=self.perfil.puerto, baudrate=self.perfil.baudrate,
                                   timeout=self.perfil.timeout, write_timeout=self.perfil.timeout)
            self._evento({"evento": "conexion", "puerto": self.perfil.puerto})
        except Exception as exc:
            self._sesion = None
            raise LinkError("Error de apertura serie") from exc

    @property
    def abierto(self):
        return bool(self._serial is not None and self._serial.is_open and self._sesion)

    def escribir(self, datos: bytes):
        permitidos = {t.encode("ascii") + self.perfil.terminador for t in TOKENS}
        if type(datos) is not bytes or datos not in permitidos:
            raise LinkError("Carga serie no autorizada")
        if not self.abierto:
            raise LinkError("Puerto físico no preparado")
        try:
            if self._serial.write(datos) != len(datos):
                raise IOError("Escritura parcial; no reintentar")
            self._evento({"evento": "escritura", "datos": datos.hex(),
                                 "resultado_fisico": "desconocido"})
        except Exception as exc:
            self._evento({"evento": "error_escritura"})
            self.cerrar()
            raise LinkError("Error serie; estado físico desconocido; no reintentar") from exc

    def cerrar(self):
        self._sesion = None
        actual, self._serial = self._serial, None
        if actual is not None:
            try:
                actual.close()
            except Exception as exc:
                raise LinkError("Error al cerrar el puerto") from exc
        self._evento({"evento": "cierre"})
