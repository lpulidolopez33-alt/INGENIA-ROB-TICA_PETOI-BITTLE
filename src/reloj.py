"""Reloj inyectable: permite medir tiempos de forma determinista en las pruebas."""
from datetime import datetime, timedelta


class Reloj:
    def ahora(self) -> datetime:
        return datetime.now()


class FakeReloj(Reloj):
    def __init__(self, inicio: datetime | None = None):
        self._t = inicio or datetime(2026, 11, 10, 10, 0, 0)

    def ahora(self) -> datetime:
        return self._t

    def avanzar(self, segundos: float) -> None:
        self._t += timedelta(seconds=segundos)


def segundos(a: datetime, b: datetime) -> float:
    """Segundos transcurridos de a a b."""
    return (b - a).total_seconds()
