"""Validación de órdenes (RF-01, RF-04, RS-01). El reconocedor no decide qué es una acción válida."""
from dataclasses import dataclass

from config import Config
from vocabulario import Vocabulario, Intencion
from voz import Resultado
from seguridad import ACCIONES, CONSULTAS, numero_valido
from datetime import datetime


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
        if resultado is None:
            return Interpretacion(None, "silencio")
        if (not isinstance(resultado, Resultado) or not isinstance(resultado.texto, str)
                or not isinstance(resultado.inicio, datetime) or not isinstance(resultado.fin, datetime)):
            return Interpretacion(None, "resultado_invalido")
        if not resultado.texto.strip():
            return Interpretacion(None, "silencio")
        if not numero_valido(resultado.confianza):
            return Interpretacion(None, "confianza_invalida")
        try:
            if resultado.inicio.tzinfo is not None or resultado.fin.tzinfo is not None:
                return Interpretacion(None, "resultado_invalido")
            if (resultado.fin - resultado.inicio).total_seconds() < 0:
                return Interpretacion(None, "resultado_invalido")
            if resultado.fin_monotonic is not None and not numero_valido(resultado.fin_monotonic, 0, float("inf")):
                return Interpretacion(None, "resultado_invalido")
        except (TypeError, ValueError):
            return Interpretacion(None, "resultado_invalido")
        intencion = self.vocabulario.buscar(resultado.texto, idioma)
        if intencion is None:
            return Interpretacion(None, "no_reconocida")
        if ((intencion.es_movimiento and ACCIONES.get(intencion.id) != intencion.token)
                or (not intencion.es_movimiento and
                    (intencion.tipo != "consulta" or intencion.id not in CONSULTAS or intencion.token is not None))):
            return Interpretacion(None, "accion_no_autorizada")
        if resultado.confianza < self.config.umbral_u:
            return Interpretacion(intencion, "baja_confianza")
        return Interpretacion(intencion, None)
