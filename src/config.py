"""Parámetros del sistema. Todos son PROPUESTAS pendientes de validar (H1 OPEN-04, OPEN-12)."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    umbral_u: float = 0.80          # U: confianza mínima para aceptar una orden (OPEN-04)
    t_aviso: float = 2.0            # s máx. para avisar de una entrada no reconocida (OPEN-12)
    t_enlace: float = 2.0           # s máx. para detectar la pérdida del enlace (OPEN-12)
    t_escucha: float = 5.0          # s máx. de escucha sin texto reconocido (OPEN-12)
    t_transmision: float = 3.0      # s máx. fin de locución -> comando transmitido (RR-02)
    periodo_vigilancia: float = 0.5  # s entre comprobaciones del enlace (debe ser <= t_enlace)

    def __post_init__(self):
        if not 0.0 < self.umbral_u <= 1.0:
            raise ValueError("umbral_u debe estar en (0, 1]")
        if self.periodo_vigilancia > self.t_enlace:
            raise ValueError("periodo_vigilancia no puede superar t_enlace")
