"""Reloj inyectable: permite medir tiempos de forma determinista en las pruebas."""
from datetime import datetime, timedelta
import time


class Reloj:
    def monotonic(self) -> float:
        return time.monotonic()

    def ahora(self) -> datetime:
        return datetime.now()


class FakeReloj(Reloj):
    def __init__(self, inicio: datetime | None = None):
        self._t = inicio or datetime(2026, 11, 10, 10, 0, 0)
        self._mono = 0.0

    def monotonic(self):
        return self._mono

    def ahora(self) -> datetime:
        return self._t

    def avanzar(self, segundos: float) -> None:
        self._t += timedelta(seconds=segundos)
        self._mono += segundos


def segundos(a: datetime, b: datetime) -> float:
    """Segundos transcurridos de a a b."""
    return (b - a).total_seconds()
