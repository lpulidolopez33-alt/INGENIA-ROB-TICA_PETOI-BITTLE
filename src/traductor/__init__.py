"""Validación de órdenes (RF-01, RF-04, RS-01). El reconocedor no decide qué es una acción válida."""
from dataclasses import dataclass

from config import Config
from vocabulario import Vocabulario, Intencion
from voz import Resultado


@dataclass(frozen=True)
class Interpretacion:
    intencion: Intencion | None
    motivo: str | None   # None = válida; "silencio" | "no_reconocida" | "baja_confianza"

    @property
    def valida(self) -> bool:
        return self.intencion is not None and self.motivo is None


class Traductor:
    def __init__(self, vocabulario: Vocabulario, config: Config):
        self.vocabulario = vocabulario
        self.config = config

    def interpretar(self, resultado: Resultado | None, idioma: str) -> Interpretacion:
        if resultado is None or not resultado.texto.strip():
            return Interpretacion(None, "silencio")
        intencion = self.vocabulario.buscar(resultado.texto, idioma)
        if intencion is None:
            return Interpretacion(None, "no_reconocida")
        if resultado.confianza < self.config.umbral_u:
            return Interpretacion(intencion, "baja_confianza")
        return Interpretacion(intencion, None)
