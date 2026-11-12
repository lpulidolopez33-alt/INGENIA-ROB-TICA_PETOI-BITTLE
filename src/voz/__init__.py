"""Frontera de reconocimiento (D-02, D-11): Recognizer + FakeRecognizer sin micrófono."""
from collections import deque
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from reloj import Reloj, FakeReloj


class MicrofonoNoDisponible(Exception):
    pass


class ModeloNoDisponible(Exception):
    pass


@dataclass(frozen=True)
class Resultado:
    texto: str
    confianza: float
    inicio: datetime
    fin: datetime
    fin_monotonic: float | None = None
    origen_tiempo: str = "simulado"
    captura_id: str | None = None
    emitido_monotonic: float | None = None


class Recognizer(Protocol):
    def cargar_modelo(self, idioma: str) -> None: ...
    def disponible(self) -> bool: ...
    def escuchar(self, timeout: float) -> Resultado | None: ...


class FakeRecognizer:
    """Reconocedor guionizado. None en el guion = silencio (se agota timeout)."""

    def __init__(self, reloj: FakeReloj, latencia: float = 0.0):
        self.reloj = reloj
        self.latencia = latencia          # s de proceso tras el fin de la locución
        self.microfono = True
        self.idiomas_sin_modelo: set = set()
        self.idioma_cargado: str | None = None
        self._guion: deque = deque()

    def encolar(self, texto: str, confianza: float = 0.95, duracion: float = 1.0,
                latencia: float | None = None) -> None:
        self._guion.append((texto, confianza, duracion,
                            self.latencia if latencia is None else latencia))

    def encolar_silencio(self) -> None:
        self._guion.append(None)

    def cargar_modelo(self, idioma: str) -> None:
        if idioma in self.idiomas_sin_modelo:
            raise ModeloNoDisponible(idioma)
        self.idioma_cargado = idioma

    def disponible(self) -> bool:
        return self.microfono

    def escuchar(self, timeout: float) -> Resultado | None:
        if not self.microfono:
            raise MicrofonoNoDisponible()
        item = self._guion.popleft() if self._guion else None
        if item is None:
            self.reloj.avanzar(timeout)
            return None
        texto, conf, duracion, latencia = item
        inicio = self.reloj.ahora()
        self.reloj.avanzar(duracion)
        fin = self.reloj.ahora()
        self.reloj.avanzar(latencia)
        return Resultado(texto, conf, inicio, fin)
