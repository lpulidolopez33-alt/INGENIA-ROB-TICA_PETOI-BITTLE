"""Avisos al usuario: visual (lista/ventana) y de voz por el altavoz del ordenador (D-07)."""
from dataclasses import dataclass
from datetime import datetime
from typing import Callable

from reloj import Reloj

MENSAJES = {
    "captura_invalidada": "Captura caducada, repetida o invalidada. Inicia una nueva captura.",
    "confianza_invalida": "Confianza inválida. Orden rechazada; repítela.",
    "resultado_invalido": "Resultado de voz inválido. Orden rechazada; repítela.",
    "accion_no_autorizada": "Acción no autorizada. No se envía ningún comando.",
    "escucha_inactiva": "Escucha desactivada o modelo no disponible.",
    "estado_desconocido": "Estado desconocido: confirma reposo antes de continuar.",
    "no_reconocida": "No he entendido la orden. Repítela, por favor.",
    "baja_confianza": "No he entendido la orden con claridad. Repítela, por favor.",
    "silencio": "No se ha recibido ninguna orden. Puedes intentarlo de nuevo.",
    "accion_en_curso": "Bittle está ejecutando una acción. Orden rechazada.",
    "sin_enlace": "Sin enlace con Bittle. Las órdenes de movimiento están inhabilitadas.",
    "enlace_perdido": "Se ha perdido el enlace con Bittle. Reconecta para continuar.",
    "error_transmision": "Error al transmitir al robot. Órdenes de movimiento bloqueadas.",
    "microfono": "Micrófono no disponible. Escucha deshabilitada.",
    "idioma_no_cargado": "No se pudo cargar el modelo del idioma. Se mantiene el idioma anterior.",
    "enviada": "Orden enviada a Bittle.",
}


@dataclass(frozen=True)
class Aviso:
    codigo: str
    texto: str
    momento: datetime


class Avisos:
    def __init__(self, reloj: Reloj, voz: Callable[[str], None] | None = None):
        self.reloj = reloj
        self.voz = voz                  # función TTS (T012); None en pruebas
        self.emitidos: list[Aviso] = []

    def emitir(self, codigo: str) -> Aviso:
        a = Aviso(codigo, MENSAJES[codigo], self.reloj.ahora())
        self.emitidos.append(a)
        if self.voz:
            self.voz(a.texto)
        return a
