"""Cola de voz local para Bittle (experimental, aislada del controlador H1).

El micrófono añade órdenes a una cola FIFO mientras un hilo independiente transmite
como máximo una acción por intervalo. Los intervalos son estimaciones, NO telemetría
ni confirmación de que el robot haya terminado el movimiento.
"""
from collections import deque
from dataclasses import dataclass
import re
from threading import Condition, Event, Thread
from typing import Callable

from enlace import EnlaceBittle, LinkError
from vocabulario import Vocabulario, normalizar
from voz import Resultado


# Mantener las dos acciones autorizadas en H1. No enviar texto arbitrario al firmware.
ACCIONES = {"sentarse": "ksit", "ponerse_de_pie": "kup"}
CONTROLES = {
    "cancela la cola": "vaciar",
    "borra la cola": "vaciar",
    "vacia la cola": "vaciar",
    "pausa la cola": "pausar",
    "reanuda la cola": "reanudar",
}
MAX_ACCIONES_FRASE = 4


@dataclass(frozen=True)
class OrdenVoz:
    tipo: str  # movimiento | vaciar | pausar | reanudar
    tokens: tuple[str, ...] = ()


def interpretar_voz(resultado: Resultado | None, vocabulario: Vocabulario,
                   idioma: str = "es", umbral: float = 0.80) -> OrdenVoz | None:
    """Solo órdenes exactas reconocidas con confianza suficiente. Todo lo demás se descarta."""
    if resultado is None or not resultado.texto.strip():
        return None
    if not 0 < umbral <= 1 or not 0 <= resultado.confianza <= 1:
        return None
    if resultado.confianza < umbral or idioma != "es":
        return None
    normal = normalizar(resultado.texto.replace(",", " y "))
    if normal in CONTROLES:
        return OrdenVoz(CONTROLES[normal])
    partes = re.split(r"\s+(?:y\s+despues|y\s+luego|y|luego|despues)\s+", normal)
    if not 1 <= len(partes) <= MAX_ACCIONES_FRASE or any(not p for p in partes):
        return None
    autorizadas = {}
    for frase, intencion in vocabulario.admitidas(idioma):
        if intencion.id in ACCIONES and intencion.es_movimiento and intencion.token == ACCIONES[intencion.id]:
            autorizadas[normalizar(frase)] = intencion.token
    if any(p not in autorizadas for p in partes):
        return None
    return OrdenVoz("movimiento", tuple(autorizadas[p] for p in partes))


def frases_vosk(vocabulario: Vocabulario) -> list[str]:
    """Gramática limitada: órdenes individuales, controles y parejas habituales."""
    simples = [frase for frase, intencion in vocabulario.admitidas("es")
               if intencion.id in ACCIONES and intencion.token == ACCIONES[intencion.id]]
    parejas = [f"{a} y {b}" for a in simples for b in simples]
    parejas += [f"{a} y luego {b}" for a in simples for b in simples]
    return list(dict.fromkeys(simples + parejas + list(CONTROLES)))


class ColaSecuencial:
    """FIFO acotada con cancelación de pendientes, pausa y fallo cerrado.

    - La recepción por micrófono sucede en otro hilo (normalmente el principal).
    - El trabajador nunca envía dos tokens simultáneamente.
    - 'Vaciar' NO detiene físicamente una acción que ya se haya enviado.
    - Una pérdida de enlace borra pendientes e impide toda continuación automática.
    """

    def __init__(self, enlace: EnlaceBittle, duracion_minima: float = 5.0,
                 capacidad: int = 8, avisar: Callable[[str], None] = print):
        if not 0 < duracion_minima <= 120:
            raise ValueError("duracion_minima debe estar entre 0 y 120 segundos")
        if not 1 <= capacidad <= 32:
            raise ValueError("capacidad debe estar entre 1 y 32")
        self.enlace = enlace
        self.duracion_minima = duracion_minima
        self.capacidad = capacidad
        self.avisar = avisar
        self._cola: deque[str] = deque()
        self._condicion = Condition()
        self._parada = Event()
        self._hilo: Thread | None = None
        self._pausada = False
        self._actual: str | None = None
        self._fallo: str | None = None

    def iniciar(self) -> None:
        if self._hilo is not None:
            raise RuntimeError("la cola ya se ha iniciado")
        if not self.enlace.activo():
            raise LinkError("no hay enlace activo con Bittle")
        self._hilo = Thread(target=self._trabajar, name="bittle-cola-voz", daemon=True)
        self._hilo.start()

    def agregar(self, tokens: tuple[str, ...]) -> tuple[bool, str]:
        if not tokens or any(t not in ACCIONES.values() for t in tokens):
            return False, "tokens_no_autorizados"
        with self._condicion:
            if self._parada.is_set() or self._fallo:
                return False, "cola_detenida"
            if not self.enlace.activo():
                self._fallo = "sin_enlace"
                self._cola.clear()
                self._parada.set()
                self._condicion.notify_all()
                return False, "sin_enlace"
            if len(self._cola) + len(tokens) > self.capacidad:
                return False, "cola_llena"
            self._cola.extend(tokens)
            pendientes = len(self._cola)
            self._condicion.notify_all()
        return True, f"{len(tokens)} orden(es) aceptada(s); {pendientes} pendiente(s)"

    def vaciar(self) -> int:
        with self._condicion:
            n = len(self._cola)
            self._cola.clear()
            self._condicion.notify_all()
            return n

    def pausar(self) -> None:
        with self._condicion:
            self._pausada = True

    def reanudar(self) -> bool:
        with self._condicion:
            if self._parada.is_set() or self._fallo or not self.enlace.activo():
                return False
            self._pausada = False
            self._condicion.notify_all()
            return True

    def estado(self) -> dict:
        with self._condicion:
            return {"pendientes": tuple(self._cola), "enviando_o_esperando": self._actual,
                    "pausada": self._pausada, "fallo": self._fallo}

    def detener(self) -> None:
        # Detiene FUTUROS envíos, no interrumpe mágicamente el movimiento físico.
        self._parada.set()
        with self._condicion:
            self._cola.clear()
            self._condicion.notify_all()
        if self._hilo is not None:
            self._hilo.join()

    def _trabajar(self) -> None:
        while not self._parada.is_set():
            with self._condicion:
                while not self._parada.is_set() and (self._pausada or not self._cola):
                    self._condicion.wait(timeout=0.2)
                if self._parada.is_set():
                    return
                token = self._cola.popleft()
                self._actual = token
            try:
                if not self.enlace.activo():
                    raise LinkError("enlace Bluetooth desconectado")
                self.enlace.enviar(token)
                self.avisar(f"ENVIADO: {token} (resultado físico NO confirmado)")
                # Permite que el micrófono siga encolando mientras transcurre el tiempo mínimo.
                if self._parada.wait(self.duracion_minima):
                    return
                if not self.enlace.activo():
                    raise LinkError("enlace Bluetooth perdido durante la espera")
                self.avisar(f"Intervalo de {token} transcurrido: fin solo ESTIMADO")
            except (LinkError, OSError, ValueError) as exc:
                with self._condicion:
                    self._fallo = str(exc)
                    self._cola.clear()
                    self._pausada = True
                    self._parada.set()
                    self._condicion.notify_all()
                self.avisar(f"ERROR: {exc}; pendientes descartadas. Revisar y reiniciar manualmente.")
                return
            finally:
                with self._condicion:
                    self._actual = None
                    self._condicion.notify_all()
