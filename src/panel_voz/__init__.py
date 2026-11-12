"""Estado/control del micro para una interfaz Tkinter (sin dependencia de Tk).

El micro esta apagado al iniciar. La escucha ocurre en un hilo separado;
TODAS las notificaciones salen a una cola para ser leidas por el hilo GUI.
Desactivar cancela la captura en curso y descarta cualquier resultado tardio.
"""
from __future__ import annotations

from queue import Queue
from threading import Condition, Event, Thread

from cola_voz import ColaSecuencial, interpretar_voz
from vocabulario import Vocabulario
from voz import Resultado


TEXTO_TOKEN = {"ksit": "Sentarse", "kup": "Ponerse de pie"}


def describir(tokens: tuple[str, ...]) -> str:
    return " → ".join(TEXTO_TOKEN.get(t, "Desconocida") for t in tokens)


class ControlMicrofono:
    """Conecta un reconocedor Vosk y la cola del robot con una GUI.

    El reconocedor debe proporcionar cargar_modelo(), disponible() y
    escuchar(timeout, cancelar=Event). No llama nunca directamente a Tkinter.
    """

    def __init__(self, reconocedor, vocabulario: Vocabulario,
                 cola: ColaSecuencial, eventos: Queue,
                 *, confianza: float = .80, ventana: float = 5.0):
        if not 0 < confianza <= 1:
            raise ValueError("Confianza fuera de rango")
        if not .25 <= ventana <= 10:
            raise ValueError("Ventana de escucha fuera de rango")
        self.reconocedor = reconocedor
        self.vocabulario = vocabulario
        self.cola = cola
        self.eventos = eventos
        self.confianza = confianza
        self.ventana = ventana
        self._cond = Condition()
        self._cerrado = False
        self._activo = False
        self._generacion = 0
        self._cancelar = Event()
        self._cancelar.set()
        self._hilo = None
        self._cargado = False

    @property
    def activo(self) -> bool:
        with self._cond:
            return self._activo

    def iniciar(self):
        with self._cond:
            if self._hilo is not None:
                raise RuntimeError("El controlador ya se ha iniciado")
            self._hilo = Thread(target=self._bucle, daemon=True, name="bittle-microfono")
            self._hilo.start()

    def cambiar(self, encender: bool):
        """Cambio instantaneo del estado logico; captura puede tardar <1 bloque en cesar."""
        with self._cond:
            if self._cerrado:
                return
            if self._activo == encender:
                return
            if encender and self.cola.estado()["fallo"]:
                self.eventos.put(("mensaje", "No se puede escuchar: error de la cola"))
                return
            self._generacion += 1
            self._activo = encender
            if encender:
                self._cancelar = Event()
            else:
                self._cancelar.set()
            self._cond.notify_all()
        self.eventos.put(("microfono", "ACTIVADO" if encender else "DESACTIVADO"))

    def cerrar(self):
        with self._cond:
            self._cerrado = True
            self._activo = False
            self._generacion += 1
            self._cancelar.set()
            self._cond.notify_all()
        # El hilo es daemon; el cierre de captura se comprueba en cada bloque.
        if self._hilo is not None:
            self._hilo.join(timeout=2)

    def _fallo(self, generacion: int, exc: Exception):
        with self._cond:
            if self._cerrado or generacion != self._generacion:
                return
            self._generacion += 1
            self._activo = False
            self._cancelar.set()
        # Ante fallo de micro, evitar movimientos futuros no supervisados.
        descartadas = self.cola.vaciar()
        self.cola.pausar()
        self.eventos.put(("microfono", "ERROR / DESACTIVADO"))
        self.eventos.put(("mensaje", f"Micrófono no disponible: {exc}. "
                                     f"{descartadas} pendientes descartadas; cola pausada."))

    def _bucle(self):
        while True:
            with self._cond:
                while not self._activo and not self._cerrado:
                    self._cond.wait()
                if self._cerrado:
                    return
                generacion = self._generacion
                cancelar = self._cancelar
            try:
                if not self._cargado:
                    self.reconocedor.cargar_modelo("es")
                    self._cargado = True
                if not self.reconocedor.disponible():
                    raise RuntimeError("Windows no detecta un micrófono de entrada")
                if cancelar.is_set():
                    continue
                r = self.reconocedor.escuchar(self.ventana, cancelar=cancelar)
            except Exception as exc:
                self._fallo(generacion, exc)
                continue
            # La interpretacion y encolado se serializan con el toggle.
            with self._cond:
                if self._cerrado or not self._activo or cancelar.is_set():
                    continue
                if generacion != self._generacion:
                    continue
                if r is None or not r.texto.strip():
                    continue
                self._procesar(r)

    def _procesar(self, resultado: Resultado):
        self.eventos.put(("frase", resultado.texto))
        orden = interpretar_voz(resultado, self.vocabulario,
                               umbral=self.confianza)
        if orden is None:
            self.eventos.put(("accion", "No reconocida o confianza insuficiente"))
            self.eventos.put(("mensaje", "Orden descartada; no se envía ningún movimiento"))
            return
        if orden.tipo == "movimiento":
            nombres = describir(orden.tokens)
            self.eventos.put(("accion", nombres))
            ok, motivo = self.cola.agregar(orden.tokens)
            self.eventos.put(("mensaje", motivo if ok else f"RECHAZADA: {motivo}"))
        elif orden.tipo == "vaciar":
            self.eventos.put(("accion", "Vaciar cola"))
            n = self.cola.vaciar()
            self.eventos.put(("mensaje", f"{n} pendientes canceladas; el envío actual NO se interrumpe"))
        elif orden.tipo == "pausar":
            self.eventos.put(("accion", "Pausar cola"))
            self.cola.pausar()
            self.eventos.put(("mensaje", "Envíos futuros pausados"))
        elif orden.tipo == "reanudar":
            self.eventos.put(("accion", "Reanudar cola"))
            ok = self.cola.reanudar()
            self.eventos.put(("mensaje", "Cola reanudada" if ok else
                             "No se puede reanudar: comprueba la conexión Bluetooth"))
