"""Gestor de estados (D-08). Desviación respecto a D-08: la escucha es un indicador independiente
porque ESC-07 exige poder recibir (y rechazar) órdenes mientras Bittle ejecuta una acción."""
from enum import Enum


class Estado(Enum):
    DESCONECTADO = "desconectado"   # sin enlace: movimientos inhabilitados (RO-02, RS-02)
    REPOSO = "reposo"               # enlace activo, sin acción en curso
    EJECUTANDO = "ejecutando"       # acción enviada; nuevas órdenes de movimiento se rechazan


class TransicionInvalida(Exception):
    pass


class Gestor:
    def __init__(self):
        self.estado = Estado.DESCONECTADO
        self.escucha = False

    def enlace_establecido(self) -> None:
        if self.estado is not Estado.DESCONECTADO:
            raise TransicionInvalida(f"enlace_establecido desde {self.estado}")
        self.estado = Estado.REPOSO

    def enlace_perdido(self) -> None:
        self.estado = Estado.DESCONECTADO

    def puede_mover(self) -> tuple[bool, str | None]:
        if self.estado is Estado.DESCONECTADO:
            return False, "sin_enlace"
        if self.estado is Estado.EJECUTANDO:
            return False, "accion_en_curso"
        return True, None

    def iniciar_accion(self) -> None:
        if self.estado is not Estado.REPOSO:
            raise TransicionInvalida(f"iniciar_accion desde {self.estado}")
        self.estado = Estado.EJECUTANDO

    def fin_accion(self) -> None:
        if self.estado is not Estado.EJECUTANDO:
            raise TransicionInvalida(f"fin_accion desde {self.estado}")
        self.estado = Estado.REPOSO
