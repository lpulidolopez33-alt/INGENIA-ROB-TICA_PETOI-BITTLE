"""Controlador de sesión: orquesta captura, validación, estado, enlace, avisos y registro.
Implementa ESC-01 a ESC-12 de H1 v0.2 (ESC-13 es un procedimiento humano, no software)."""
from dataclasses import dataclass
from typing import Callable

from avisos import Avisos
from config import Config
from enlace import EnlaceBittle, LinkError
from estado import Estado, Gestor
from registro import Registro
from reloj import Reloj, segundos
from traductor import Traductor
from vocabulario import Vocabulario, IDIOMAS
from voz import MicrofonoNoDisponible, ModeloNoDisponible, Recognizer, Resultado


@dataclass
class Salida:
    resultado: str            # aceptada | rechazada | enviada | error
    motivo: str | None = None
    latencia: float | None = None   # s desde el fin de la locución
    detalle: object = None          # contenido de una consulta


@dataclass
class Cierre:
    ok: bool
    motivo: str | None = None
    requiere_supervisor: bool = False


class Controlador:
    def __init__(self, vocabulario: Vocabulario, reconocedor: Recognizer, enlace: EnlaceBittle,
                 registro: Registro, avisos: Avisos, reloj: Reloj,
                 config: Config = Config(), idioma: str = "es"):
        assert idioma in IDIOMAS
        self.vocabulario, self.reconocedor, self.enlace = vocabulario, reconocedor, enlace
        self.registro, self.avisos, self.reloj, self.config = registro, avisos, reloj, config
        self.traductor = Traductor(vocabulario, config)
        self.gestor = Gestor()
        self.idioma = idioma
        self.estado_movimiento = "desconocido"   # reposo|en_curso|finalizado|estimado|desconocido
        self.ultima_consulta = None

    # ---- ESC-01: inicio de sesión -------------------------------------------------------------
    def iniciar_sesion(self) -> bool:
        try:
            self.reconocedor.cargar_modelo(self.idioma)
        except ModeloNoDisponible:
            self.avisos.emitir("idioma_no_cargado")
            self._error("modelo_voz")
        return self._conectar()

    def _conectar(self) -> bool:
        try:
            self.enlace.conectar()
        except LinkError:
            self.avisos.emitir("sin_enlace")
            self._error("sin_enlace")
            return False
        self.gestor.enlace_establecido()
        self.estado_movimiento = "reposo"
        return True

    def activar_escucha(self) -> bool:
        if not self.reconocedor.disponible():
            self._microfono_perdido()
            return False
        self.gestor.escucha = True
        return True

    def desactivar_escucha(self) -> None:
        self.gestor.escucha = False

    # ---- ESC-04: cambio de idioma -------------------------------------------------------------
    def cambiar_idioma(self, idioma: str) -> bool:
        assert idioma in IDIOMAS
        self.desactivar_escucha()
        try:
            self.reconocedor.cargar_modelo(idioma)
        except ModeloNoDisponible:
            self.avisos.emitir("idioma_no_cargado")
            self._error("modelo_voz")
            return False
        self.idioma = idioma
        return True

    # ---- captura y procesamiento (ESC-02, 03, 07, 09, 10, 11, 12) -----------------------------
    def escuchar(self) -> Salida | None:
        if not self.gestor.escucha:
            return None
        try:
            resultado = self.reconocedor.escuchar(self.config.t_escucha)
        except MicrofonoNoDisponible:
            self._microfono_perdido()
            return None
        return self.procesar(resultado)

    def procesar(self, resultado: Resultado | None) -> Salida:
        interp = self.traductor.interpretar(resultado, self.idioma)
        texto = resultado.texto if resultado else ""
        conf = resultado.confianza if resultado else None
        if not interp.valida:
            self.avisos.emitir(interp.motivo)
            return self._salida("rechazada", texto, conf, interp.motivo, resultado,
                                intencion=interp.intencion.id if interp.intencion else None)
        it = interp.intencion
        if not it.es_movimiento:                       # consulta: nunca escribe en el enlace
            self.ultima_consulta = self._responder(it.id)
            return self._salida("aceptada", texto, conf, None, resultado, it.id,
                                detalle=self.ultima_consulta)
        ok, motivo = self.gestor.puede_mover()
        if not ok:
            self.avisos.emitir(motivo)
            return self._salida("rechazada", texto, conf, motivo, resultado, it.id)
        try:
            self.enlace.enviar(it.token)
        except LinkError:
            self._enlace_perdido("error_escritura", aviso="error_transmision")
            return self._salida("error", texto, conf, "error_escritura", resultado, it.id)
        self.gestor.iniciar_accion()
        self.estado_movimiento = "en_curso"
        return self._salida("enviada", texto, conf, None, resultado, it.id, token=it.token)

    def _responder(self, intencion: str):
        if intencion == "historial":
            return list(self.registro.historial())
        return {"enlace_activo": self.gestor.estado is not Estado.DESCONECTADO,
                "estado_movimiento": self.estado_movimiento}

    def _salida(self, resultado, texto, conf, motivo, r, intencion=None, detalle=None, **extra):
        tipo_error = motivo if resultado == "error" else None
        self.registro.registrar(texto, resultado, intencion, conf,
                                None if resultado == "error" else motivo, tipo_error, **extra)
        lat = segundos(r.fin, self.reloj.ahora()) if r else None
        return Salida(resultado, motivo, lat, detalle)

    # ---- fin de acción y resultado físico (ESC-02, ESC-06) ------------------------------------
    def finalizar_accion(self, evidencia_fisica: bool = False) -> None:
        """Sin evidencia observada el estado queda «estimado» (OPEN-14): enviar != ejecutar."""
        self.gestor.fin_accion()
        self.estado_movimiento = "finalizado" if evidencia_fisica else "estimado"

    def registrar_no_conformidad(self, orden: str, comando: str, observado: str) -> dict:
        return self.registro.registrar(orden, "error", tipo_error="resultado_fisico_incorrecto",
                                       comando=comando, observado=observado,
                                       veredicto="no_conforme")

    # ---- ESC-08: enlace ----------------------------------------------------------------------
    def vigilar_enlace(self) -> bool:
        """Llamar cada config.periodo_vigilancia s. Devuelve True si detecta pérdida."""
        if self.gestor.estado is not Estado.DESCONECTADO and not self.enlace.activo():
            self._enlace_perdido("perdida_enlace", aviso="enlace_perdido")
            return True
        return False

    def reconectar(self) -> bool:
        """Solo por acción explícita del usuario; no existe cola de órdenes que reenviar."""
        if self.gestor.estado is not Estado.DESCONECTADO:
            return True
        return self._conectar()

    def _enlace_perdido(self, tipo: str, aviso: str) -> None:
        self.gestor.enlace_perdido()
        self.estado_movimiento = "desconocido"
        self.avisos.emitir(aviso)
        self._error(tipo)

    def _microfono_perdido(self) -> None:
        self.gestor.escucha = False
        self.avisos.emitir("microfono")
        self._error("microfono_no_disponible")

    def _error(self, tipo: str) -> None:
        self.registro.registrar("", "error", tipo_error=tipo)

    # ---- ESC-05: cierre de sesión -------------------------------------------------------------
    def cerrar_sesion(self, esperar_fin: Callable[[], bool] | None = None) -> Cierre:
        self.desactivar_escucha()
        if self.gestor.estado is Estado.EJECUTANDO:
            if esperar_fin and esperar_fin():
                self.finalizar_accion(evidencia_fisica=False)
            else:
                return Cierre(False, "accion_en_curso", requiere_supervisor=True)
        self.enlace.cerrar()
        self.gestor.enlace_perdido()
        self.estado_movimiento = "desconocido"
        return Cierre(True)
