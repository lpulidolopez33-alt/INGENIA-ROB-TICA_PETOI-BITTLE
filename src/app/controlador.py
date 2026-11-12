"""Controlador de sesión: orquesta captura, validación, estado, enlace, avisos y registro.
Implementa ESC-01 a ESC-12 de H1 v0.2 (ESC-13 es un procedimiento humano, no software)."""
from dataclasses import dataclass
from typing import Callable
from seguridad import numero_valido
from datetime import datetime

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
        if not enlace.simulado:
            perfil = getattr(enlace.puerto, "perfil", None)
            if perfil is None or perfil.parametros != config:
                raise ValueError("Los parámetros del controlador no coinciden con el perfil revisado")
        self.gestor = Gestor()
        self.idioma = idioma
        self.estado_movimiento = "desconocido"   # reposo|en_curso|finalizado|estimado|desconocido
        self.ultima_consulta = None
        self.modelo_listo = False
        self._generacion_escucha = 0
        self._capturas_consumidas = set()
        self.requiere_reposo = not enlace.simulado

    # ---- ESC-01: inicio de sesión -------------------------------------------------------------
    def iniciar_sesion(self) -> bool:
        try:
            self.reconocedor.cargar_modelo(self.idioma)
        except ModeloNoDisponible:
            self.avisos.emitir("idioma_no_cargado")
            self._error("modelo_voz")
            self.modelo_listo = False
            self.desactivar_escucha()
            return False
        self.modelo_listo = True
        return self._conectar()

    def _conectar(self) -> bool:
        try:
            self.enlace.conectar()
        except LinkError:
            self.avisos.emitir("sin_enlace")
            self._error("sin_enlace")
            return False
        self.gestor.enlace_establecido()
        self.estado_movimiento = "desconocido" if self.requiere_reposo else "reposo"
        if self.requiere_reposo:
            self.gestor.estado = Estado.DESCONOCIDO
        return True

    def activar_escucha(self) -> bool:
        if not self.modelo_listo:
            self.avisos.emitir("escucha_inactiva")
            return False
        if not self.reconocedor.disponible():
            self._microfono_perdido()
            return False
        self.gestor.escucha = True
        return True

    def desactivar_escucha(self) -> None:
        self._generacion_escucha += 1
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
        self.modelo_listo = True
        return True

    # ---- captura y procesamiento (ESC-02, 03, 07, 09, 10, 11, 12) -----------------------------
    def escuchar(self) -> Salida | None:
        if not self.gestor.escucha:
            return None
        try:
            generacion = self._generacion_escucha
            resultado = self.reconocedor.escuchar(self.config.t_escucha)
        except ModeloNoDisponible:
            self.modelo_listo = False
            self.desactivar_escucha()
            self.avisos.emitir("idioma_no_cargado")
            self._error("modelo_voz")
            return None
        except MicrofonoNoDisponible:
            self._microfono_perdido()
            return None
        if generacion != self._generacion_escucha or not self.gestor.escucha:
            return self._salida("rechazada", "", None, "captura_invalidada", None)
        return self.procesar(resultado)

    def procesar(self, resultado: Resultado | None) -> Salida:
        interp = self.traductor.interpretar(resultado, self.idioma)
        texto = resultado.texto if isinstance(resultado, Resultado) and isinstance(resultado.texto, str) else ""
        conf = resultado.confianza if isinstance(resultado, Resultado) and numero_valido(resultado.confianza) else None
        if not interp.valida:
            self.avisos.emitir(interp.motivo)
            return self._salida("rechazada", texto, conf, interp.motivo, resultado,
                                intencion=interp.intencion.id if interp.intencion else None)
        if resultado.origen_tiempo == "estimado_vosk":
            identificador = resultado.captura_id
            emitido = resultado.emitido_monotonic
            ahora = self.reloj.monotonic()
            if (not isinstance(identificador, str) or not identificador
                    or not numero_valido(emitido, 0, float("inf"))
                    or not numero_valido(resultado.fin_monotonic, 0, ahora)
                    or not 0 <= ahora - emitido <= self.config.t_escucha
                    or not 0 <= emitido - resultado.fin_monotonic <= self.config.t_escucha
                    or identificador in self._capturas_consumidas):
                self.avisos.emitir("captura_invalidada")
                return self._salida("rechazada", texto, conf, "captura_invalidada", resultado)
            self._capturas_consumidas.add(identificador)
        it = interp.intencion
        if not it.es_movimiento:                       # consulta: nunca escribe en el enlace
            self.ultima_consulta = self._responder(it.id)
            return self._salida("aceptada", texto, conf, None, resultado, it.id,
                                detalle=self.ultima_consulta)
        if not self.gestor.escucha or not self.modelo_listo:
            self.avisos.emitir("escucha_inactiva")
            return self._salida("rechazada", texto, conf, "escucha_inactiva", resultado, it.id)
        ok, motivo = self.gestor.puede_mover()
        if not ok:
            self.avisos.emitir(motivo)
            return self._salida("rechazada", texto, conf, motivo, resultado, it.id)
        try:
            self.enlace.enviar(it.token)
        except (LinkError, ValueError):
            self._enlace_perdido("error_escritura", aviso="error_transmision")
            return self._salida("error", texto, conf, "error_escritura", resultado, it.id)
        latencia_envio = (self.reloj.monotonic() - resultado.fin_monotonic
                          if resultado.fin_monotonic is not None else
                          segundos(resultado.fin, self.reloj.ahora()))
        self.gestor.iniciar_accion()
        self.estado_movimiento = "en_curso"
        return self._salida("enviada", texto, conf, None, resultado, it.id, token=it.token, latencia_envio=latencia_envio,
                            origen_tiempo=resultado.origen_tiempo)

    def _responder(self, intencion: str):
        if intencion == "historial":
            return list(self.registro.historial())
        return {"enlace_activo": self.gestor.estado is not Estado.DESCONECTADO,
                "estado_movimiento": self.estado_movimiento}

    def _salida(self, resultado, texto, conf, motivo, r, intencion=None, detalle=None, **extra):
        tipo_error = motivo if resultado == "error" else None
        self.registro.registrar(texto, resultado, intencion, conf,
                                None if resultado == "error" else motivo, tipo_error, **extra)
        lat = None
        if isinstance(r, Resultado) and isinstance(r.fin, datetime):
            try:
                lat = max(0.0, segundos(r.fin, self.reloj.ahora()))
            except (TypeError, ValueError):
                pass
        return Salida(resultado, motivo, extra.get("latencia_envio", lat), detalle)

    # ---- fin de acción y resultado físico (ESC-02, ESC-06) ------------------------------------
    def finalizar_accion(self, evidencia_fisica: bool = False) -> None:
        """Sin evidencia observada el estado queda «estimado» (OPEN-14): enviar != ejecutar."""
        self.gestor.fin_accion()
        self.estado_movimiento = "finalizado" if evidencia_fisica else "estimado"
        if not self.enlace.simulado and not evidencia_fisica:
            self.gestor.estado = Estado.DESCONOCIDO
            self.estado_movimiento = "desconocido"
            self.requiere_reposo = True

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
        self.requiere_reposo = True
        self.gestor.enlace_perdido()
        self.estado_movimiento = "desconocido"
        self.avisos.emitir(aviso)
        self._error(tipo)

    def confirmar_reposo(self, evidencia: str) -> bool:
        """Acción manual; no deducir reposo de una escritura o reconexión."""
        if not evidencia.strip() or not self.enlace.activo():
            return False
        if self.gestor.estado not in (Estado.DESCONOCIDO, Estado.REPOSO):
            return False
        self.registro.registrar("", "aceptada", tipo_error=None,
                                evento="reposo_confirmado", evidencia=evidencia,
                                simulado=self.enlace.simulado)
        self.requiere_reposo = False
        self.gestor.estado = Estado.REPOSO
        self.estado_movimiento = "estimado" if self.enlace.simulado else "reposo"
        return True

    def _microfono_perdido(self) -> None:
        self.gestor.escucha = False
        self.avisos.emitir("microfono")
        self._error("microfono_no_disponible")

    def _error(self, tipo: str) -> None:
        self.registro.registrar("", "error", tipo_error=tipo)

    # ---- ESC-05: cierre de sesión -------------------------------------------------------------
    def cerrar_sesion(self, esperar_fin: Callable[[], bool] | None = None) -> Cierre:
        self.desactivar_escucha()
        if self.requiere_reposo:
            return Cierre(False, "estado_desconocido", requiere_supervisor=True)
        if self.gestor.estado is Estado.EJECUTANDO:
            if esperar_fin and esperar_fin():
                self.finalizar_accion(evidencia_fisica=False)
                if self.requiere_reposo:
                    return Cierre(False, "estado_desconocido", requiere_supervisor=True)
            else:
                return Cierre(False, "accion_en_curso", requiere_supervisor=True)
        self.enlace.cerrar()
        self.gestor.enlace_perdido()
        self.estado_movimiento = "desconocido"
        return Cierre(True)
