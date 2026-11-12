"""Parámetros del sistema. Todos son PROPUESTAS pendientes de validar (H1 OPEN-04, OPEN-12)."""
from dataclasses import dataclass
from seguridad import numero_valido


@dataclass(frozen=True)
class Config:
    umbral_u: float = 0.80          # U: confianza mínima para aceptar una orden (OPEN-04)
    t_aviso: float = 2.0            # s máx. para avisar de una entrada no reconocida (OPEN-12)
    t_enlace: float = 2.0           # s máx. para detectar la pérdida del enlace (OPEN-12)
    t_escucha: float = 5.0          # s máx. de escucha sin texto reconocido (OPEN-12)
    t_transmision: float = 3.0      # s máx. fin de locución -> comando transmitido (RR-02)
    periodo_vigilancia: float = 0.5  # s entre comprobaciones del enlace (debe ser <= t_enlace)

    def __post_init__(self):
        if not numero_valido(self.umbral_u) or self.umbral_u == 0:
            raise ValueError("umbral_u debe estar en (0, 1]")
        for nombre in ("t_aviso", "t_enlace", "t_escucha", "t_transmision", "periodo_vigilancia"):
            valor = getattr(self, nombre)
            if not numero_valido(valor, 0, float("inf")) or valor == 0:
                raise ValueError(f"{nombre} debe ser positivo y finito")
        if self.periodo_vigilancia > self.t_enlace:
            raise ValueError("periodo_vigilancia no puede superar t_enlace")
