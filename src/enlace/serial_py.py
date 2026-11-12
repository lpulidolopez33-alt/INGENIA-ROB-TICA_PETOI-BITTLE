"""Adaptador pyserial para un puerto serie Bluetooth emparejado con Petoi.

No abre el puerto hasta llamar a abrir(). No busca dispositivos ni permite comandos crudos.
"""
from enlace import LinkError


class PySerialPort:
    def __init__(self, nombre: str, baudios: int = 115200):
        if not nombre:
            raise ValueError("Debe indicarse el puerto Bluetooth serie saliente")
        self.nombre = nombre
        self.baudios = baudios
        self._serial = None

    def abrir(self) -> None:
        if self.abierto:
            return
        try:
            import serial
            self._serial = serial.Serial(
                port=self.nombre, baudrate=self.baudios,
                timeout=1, write_timeout=2,
            )
        except Exception as exc:
            self._serial = None
            raise LinkError(f"no se pudo abrir el puerto {self.nombre}: {exc}") from exc

    @property
    def abierto(self) -> bool:
        return self._serial is not None and self._serial.is_open

    def escribir(self, datos: bytes) -> None:
        if not self.abierto:
            raise LinkError("puerto Bluetooth cerrado")
        try:
            escritos = self._serial.write(datos)
            self._serial.flush()
            if escritos != len(datos):
                raise LinkError("escritura parcial en el puerto Bluetooth")
        except LinkError:
            raise
        except Exception as exc:
            raise LinkError(f"error enviando datos por Bluetooth: {exc}") from exc

    def cerrar(self) -> None:
        if self._serial is not None:
            try:
                self._serial.close()
            finally:
                self._serial = None
