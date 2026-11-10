"""Nivel 2 — Lógica del controlador, escenario a escenario (H1 v0.2 sección 3.2).
Sin robot ni micrófono: FakeSerial + FakeRecognizer + FakeReloj."""
import pytest

from config import Config
from conftest import Entorno
from estado import Estado
from reloj import segundos


def mover(env, texto="siéntate", **kw):
    return env.decir(texto, **kw)


# ---------------------------------------------------------------- ESC-01
@pytest.mark.caso("TEST-11")
@pytest.mark.req("RO-02", "RI-03", "RI-05", "RU-03", "RS-01")
@pytest.mark.esc("ESC-01")
@pytest.mark.nivel(2)
def test_esc01_sin_enlace_las_ordenes_de_movimiento_estan_inhabilitadas():
    e = Entorno(); e.serie.no_disponible = True
    assert e.ctrl.iniciar_sesion() is False
    assert e.ctrl.gestor.estado is Estado.DESCONECTADO
    assert e.ctrl.activar_escucha()
    s = e.decir("siéntate")
    assert s.resultado == "rechazada" and s.motivo == "sin_enlace"
    assert e.serie.escrituras == []
    assert e.avisos.emitidos[-1].codigo == "sin_enlace"


@pytest.mark.caso("TEST-12")
@pytest.mark.req("RO-02", "RI-03", "RI-04", "RI-05", "RU-03", "RU-01")
@pytest.mark.esc("ESC-01")
@pytest.mark.nivel(2)
def test_esc01_con_enlace_se_habilitan_movimientos_y_la_vista_lo_muestra():
    from interfaz import construir_vista
    e = Entorno()
    v0 = construir_vista(e.ctrl)
    assert not v0["enlace_activo"] and not v0["escucha_activa"]
    e.arrancar()
    v = construir_vista(e.ctrl)
    assert v["enlace_activo"] and v["escucha_activa"] and v["idioma_activo"] == "es"
    frases = {o["frase"] for o in v["ordenes_admitidas"]}
    assert frases == {"siéntate", "ponte de pie", "historial", "estado"}
    assert e.ctrl.gestor.puede_mover() == (True, None)


@pytest.mark.caso("TEST-13")
@pytest.mark.req("RU-03", "RS-01")
@pytest.mark.esc("ESC-01", "ESC-05")
@pytest.mark.nivel(2)
def test_con_la_escucha_desactivada_no_se_procesa_ni_se_envia_nada(env_listo):
    env_listo.ctrl.desactivar_escucha()
    env_listo.reco.encolar("siéntate")
    assert env_listo.ctrl.escuchar() is None
    assert env_listo.serie.escrituras == []


# ---------------------------------------------------------------- ESC-02
@pytest.mark.caso("TEST-14")
@pytest.mark.req("RF-01", "RF-02", "RF-06", "RI-02", "RM-01")
@pytest.mark.esc("ESC-02")
@pytest.mark.nivel(2)
@pytest.mark.parametrize("idioma,frase,token", [
    ("es", "siéntate", b"ksit"), ("es", "ponte de pie", b"kup"),
    ("en", "sit", b"ksit"), ("en", "stand up", b"kup"),
])
def test_esc02_orden_de_movimiento_valida_envia_exactamente_su_token(idioma, frase, token):
    e = Entorno(idioma=idioma).arrancar()
    s = e.decir(frase)
    assert s.resultado == "enviada"
    assert e.serie.escrituras == [token]
    assert e.ctrl.gestor.estado is Estado.EJECUTANDO
    assert e.ctrl.estado_movimiento == "en_curso"
    ev = e.registro.eventos[-1]
    assert ev["resultado"] == "enviada" and ev["texto"] == frase and ev["fecha"] and ev["hora"]


@pytest.mark.caso("TEST-15")
@pytest.mark.req("RF-06", "RF-03", "RM-01")
@pytest.mark.esc("ESC-02", "ESC-06")
@pytest.mark.nivel(2)
def test_esc02_enviar_no_equivale_a_ejecutar_sin_evidencia_el_estado_es_estimado(env_listo):
    mover(env_listo)
    env_listo.ctrl.finalizar_accion(evidencia_fisica=False)
    assert env_listo.ctrl.estado_movimiento == "estimado"
    assert env_listo.ctrl.gestor.estado is Estado.REPOSO
    mover(env_listo, "ponte de pie")
    env_listo.ctrl.finalizar_accion(evidencia_fisica=True)
    assert env_listo.ctrl.estado_movimiento == "finalizado"


@pytest.mark.caso("TEST-16")
@pytest.mark.req("RR-02")
@pytest.mark.esc("ESC-02")
@pytest.mark.nivel(2)
def test_rr02_95_por_ciento_de_ordenes_transmitidas_en_3s_con_enlace_simulado():
    e = Entorno().arrancar()
    # 20 órdenes con latencias de proceso simuladas; 1 supera los 3 s (95 % exacto)
    latencias = [0.2, 0.4, 0.3, 0.5, 0.6, 0.3, 0.2, 0.9, 1.1, 0.7,
                 0.4, 0.3, 0.8, 1.5, 0.6, 0.5, 2.9, 0.3, 0.2, 3.6]
    dentro = 0
    for i, lat in enumerate(latencias):
        s = e.decir("siéntate" if i % 2 == 0 else "ponte de pie", latencia=lat)
        assert s.resultado == "enviada"
        dentro += s.latencia <= Config().t_transmision
        e.ctrl.finalizar_accion()
    assert dentro / len(latencias) >= 0.95
    # Software-only: la latencia real por Bluetooth se mide en el ensayo físico (TEST-F06).


# ---------------------------------------------------------------- ESC-03
@pytest.mark.caso("TEST-17")
@pytest.mark.req("RF-10", "RI-06", "RI-07", "RM-01")
@pytest.mark.esc("ESC-03")
@pytest.mark.nivel(2)
@pytest.mark.parametrize("idioma,h,s", [("es", "historial", "estado"), ("en", "history", "status")])
def test_esc03_consultas_no_escriben_en_el_enlace(idioma, h, s):
    e = Entorno(idioma=idioma).arrancar()
    mover_ = "siéntate" if idioma == "es" else "sit"
    e.decir(mover_); e.ctrl.finalizar_accion()
    e.decir("corre" if idioma == "es" else "run")            # rechazada
    antes = list(e.serie.escrituras)
    r = e.decir(h)
    assert r.resultado == "aceptada" and e.serie.escrituras == antes
    historial = r.detalle
    assert [x["resultado"] for x in historial] == ["enviada", "rechazada"]
    assert all(x["fecha"] and x["hora"] for x in historial)
    r2 = e.decir(s)
    assert e.serie.escrituras == antes
    assert r2.detalle == {"enlace_activo": True, "estado_movimiento": "estimado"}


@pytest.mark.caso("TEST-18")
@pytest.mark.req("RI-07", "RF-10")
@pytest.mark.esc("ESC-03", "ESC-07")
@pytest.mark.nivel(2)
def test_esc03_la_consulta_se_atiende_durante_un_movimiento_supuesto_open11(env_listo):
    mover(env_listo)
    r = env_listo.decir("estado")
    assert r.resultado == "aceptada" and r.detalle["estado_movimiento"] == "en_curso"
    assert env_listo.serie.escrituras == [b"ksit"]


# ---------------------------------------------------------------- ESC-04
@pytest.mark.caso("TEST-19")
@pytest.mark.req("RF-07", "RU-01", "RI-04", "RF-01")
@pytest.mark.esc("ESC-04")
@pytest.mark.nivel(2)
def test_esc04_cambio_de_idioma_sin_comandos_motrices_y_frases_del_idioma_activo(env_listo):
    from interfaz import construir_vista
    assert env_listo.ctrl.cambiar_idioma("en")
    assert env_listo.serie.escrituras == []
    assert not env_listo.ctrl.gestor.escucha                 # el usuario debe reactivarla
    assert env_listo.reco.idioma_cargado == "en"
    v = construir_vista(env_listo.ctrl)
    assert v["idioma_activo"] == "en"
    assert {o["frase"] for o in v["ordenes_admitidas"]} == {"sit", "stand up", "history", "status"}
    env_listo.ctrl.activar_escucha()
    assert env_listo.decir("siéntate").resultado == "rechazada"   # frase del otro idioma
    assert env_listo.decir("sit").resultado == "enviada"


@pytest.mark.caso("TEST-20")
@pytest.mark.req("RF-07", "RU-01")
@pytest.mark.esc("ESC-04")
@pytest.mark.nivel(2)
def test_esc04_si_el_modelo_no_carga_se_mantiene_el_idioma_y_se_avisa(env_listo):
    env_listo.reco.idiomas_sin_modelo.add("en")
    assert env_listo.ctrl.cambiar_idioma("en") is False
    assert env_listo.ctrl.idioma == "es" and env_listo.reco.idioma_cargado == "es"
    assert env_listo.avisos.emitidos[-1].codigo == "idioma_no_cargado"
    assert env_listo.serie.escrituras == []


# ---------------------------------------------------------------- ESC-05
@pytest.mark.caso("TEST-21")
@pytest.mark.req("RF-08", "RU-03")
@pytest.mark.esc("ESC-05")
@pytest.mark.nivel(2)
def test_esc05_cierre_en_reposo_cierra_enlace_y_desactiva_escucha(env_listo):
    mover(env_listo); env_listo.ctrl.finalizar_accion()
    c = env_listo.ctrl.cerrar_sesion()
    assert c.ok and not env_listo.ctrl.gestor.escucha
    assert not env_listo.enlace.activo()
    assert len(env_listo.registro.eventos) == 1


@pytest.mark.caso("TEST-22")
@pytest.mark.req("RF-08", "RS-03")
@pytest.mark.esc("ESC-05", "ESC-13")
@pytest.mark.nivel(2)
def test_esc05_cierre_con_accion_en_curso_no_confirma_reposo_y_pide_supervisor(env_listo):
    mover(env_listo)
    c = env_listo.ctrl.cerrar_sesion()
    assert not c.ok and c.requiere_supervisor and env_listo.enlace.activo()
    c2 = env_listo.ctrl.cerrar_sesion(esperar_fin=lambda: True)      # procedimiento validado
    assert c2.ok and not env_listo.enlace.activo()


# ---------------------------------------------------------------- ESC-06
@pytest.mark.caso("TEST-23")
@pytest.mark.req("RM-01", "RF-03")
@pytest.mark.esc("ESC-06")
@pytest.mark.nivel(2)
def test_esc06_resultado_fisico_incorrecto_queda_registrado_como_no_conforme(env_listo):
    mover(env_listo); env_listo.ctrl.finalizar_accion(evidencia_fisica=False)
    ev = env_listo.ctrl.registrar_no_conformidad("siéntate", "ksit", "movimiento incompleto")
    assert ev["veredicto"] == "no_conforme" and ev["comando"] == "ksit"
    assert env_listo.ctrl.estado_movimiento != "finalizado"


# ---------------------------------------------------------------- ESC-07
@pytest.mark.caso("TEST-24")
@pytest.mark.req("RF-05", "RF-06", "RF-09", "RI-07")
@pytest.mark.esc("ESC-07")
@pytest.mark.nivel(2)
def test_esc07_orden_durante_otra_accion_se_rechaza_sin_encolar(env_listo):
    mover(env_listo, "ponte de pie")
    s = mover(env_listo, "siéntate")
    assert s.resultado == "rechazada" and s.motivo == "accion_en_curso"
    assert env_listo.serie.escrituras == [b"kup"]
    assert env_listo.avisos.emitidos[-1].codigo == "accion_en_curso"
    assert env_listo.registro.eventos[-1]["motivo"] == "accion_en_curso"
    env_listo.ctrl.finalizar_accion()
    assert env_listo.serie.escrituras == [b"kup"]          # la rechazada NO se ejecuta después
    assert env_listo.ctrl.estado_movimiento == "estimado"


# ---------------------------------------------------------------- ESC-08
@pytest.mark.caso("TEST-25")
@pytest.mark.req("RS-02", "RFI-02", "RM-02", "RI-03", "RO-02")
@pytest.mark.esc("ESC-08")
@pytest.mark.nivel(2)
def test_esc08_perdida_de_enlace_se_detecta_en_t_enlace_y_bloquea_movimientos(env_listo):
    cfg = Config(); e = env_listo
    mover(e)
    e.serie.desconectar()
    t0 = e.reloj.ahora(); detectado = None
    while detectado is None:
        e.reloj.avanzar(cfg.periodo_vigilancia)
        if e.ctrl.vigilar_enlace():
            detectado = segundos(t0, e.reloj.ahora())
        assert segundos(t0, e.reloj.ahora()) <= cfg.t_enlace + 1e-9, "no detectado a tiempo"
    assert detectado <= cfg.t_enlace
    assert e.ctrl.gestor.estado is Estado.DESCONECTADO
    assert e.ctrl.estado_movimiento == "desconocido"
    assert e.avisos.emitidos[-1].codigo == "enlace_perdido"
    err = e.registro.errores()[-1]
    assert err["tipo_error"] == "perdida_enlace" and err["fecha"] and err["hora"]
    s = mover(e, "ponte de pie")
    assert s.resultado == "rechazada" and s.motivo == "sin_enlace"
    assert e.serie.escrituras == [b"ksit"]                  # sin reintentos ni nuevos envíos


@pytest.mark.caso("TEST-26")
@pytest.mark.req("RS-02", "RFI-02", "RM-02")
@pytest.mark.esc("ESC-08")
@pytest.mark.nivel(2)
def test_esc08_error_de_escritura_bloquea_y_no_reintenta(env_listo):
    env_listo.serie.fallo_escritura = True
    s = mover(env_listo)
    assert s.resultado == "error"
    assert env_listo.ctrl.gestor.estado is Estado.DESCONECTADO
    assert env_listo.serie.escrituras == []
    assert env_listo.registro.errores()[-1]["tipo_error"] == "error_escritura"
    assert env_listo.avisos.emitidos[-1].codigo == "error_transmision"


@pytest.mark.caso("TEST-27")
@pytest.mark.req("RS-02", "RF-05")
@pytest.mark.esc("ESC-08")
@pytest.mark.nivel(2)
def test_sc006_tras_reconexion_no_se_ejecuta_ninguna_orden_anterior(env_listo):
    e = env_listo
    mover(e); e.serie.desconectar(); e.ctrl.vigilar_enlace()
    mover(e, "ponte de pie")                                # rechazada por falta de enlace
    escrito = list(e.serie.escrituras)
    e.serie.restablecer()
    assert e.ctrl.reconectar()
    assert e.ctrl.gestor.estado is Estado.REPOSO
    assert e.serie.escrituras == escrito                    # nada reenviado automáticamente
    assert mover(e, "ponte de pie").resultado == "enviada"  # solo con orden nueva


# ---------------------------------------------------------------- ESC-09 / 10 / 11 / 12
@pytest.mark.caso("TEST-28")
@pytest.mark.req("RF-04", "RF-06", "RS-01", "RU-02", "RM-01")
@pytest.mark.esc("ESC-09")
@pytest.mark.nivel(2)
@pytest.mark.parametrize("frase", ["corre", "baila", "hola bittle", "kbalance"])
def test_esc09_entrada_no_reconocida_no_envia_avisa_a_tiempo_y_pide_repetir(env_listo, frase):
    s = env_listo.decir(frase, latencia=1.2)
    assert s.resultado == "rechazada" and s.motivo == "no_reconocida"
    assert env_listo.serie.escrituras == []
    assert s.latencia <= Config().t_aviso
    assert env_listo.avisos.emitidos[-1].codigo == "no_reconocida"
    assert "Repítela" in env_listo.avisos.emitidos[-1].texto
    ev = env_listo.registro.eventos[-1]
    assert ev["resultado"] == "rechazada" and ev["motivo"] == "no_reconocida"
    assert env_listo.ctrl.gestor.estado is Estado.REPOSO


@pytest.mark.caso("TEST-29")
@pytest.mark.req("RF-04", "RS-01", "RR-01")
@pytest.mark.esc("ESC-10")
@pytest.mark.nivel(2)
def test_esc10_orden_valida_con_confianza_baja_no_se_ejecuta(env_listo):
    s = env_listo.decir("siéntate", confianza=0.55, latencia=1.0)
    assert s.resultado == "rechazada" and s.motivo == "baja_confianza"
    assert env_listo.serie.escrituras == [] and s.latencia <= Config().t_aviso
    assert env_listo.registro.eventos[-1]["intencion"] == "sentarse"


@pytest.mark.caso("TEST-30")
@pytest.mark.req("RF-04", "RS-01", "RI-05", "RU-02")
@pytest.mark.esc("ESC-11")
@pytest.mark.nivel(2)
def test_esc11_silencio_cierra_la_captura_en_t_escucha_sin_movimiento(env_listo):
    t0 = env_listo.reloj.ahora()
    env_listo.reco.encolar_silencio()
    s = env_listo.ctrl.escuchar()
    assert s.resultado == "rechazada" and s.motivo == "silencio"
    assert segundos(t0, env_listo.reloj.ahora()) == Config().t_escucha
    assert env_listo.serie.escrituras == []
    assert env_listo.avisos.emitidos[-1].codigo == "silencio"
    assert env_listo.decir("siéntate").resultado == "enviada"       # nuevo intento posible


@pytest.mark.caso("TEST-31")
@pytest.mark.req("RFI-01", "RM-02", "RU-03")
@pytest.mark.esc("ESC-12")
@pytest.mark.nivel(2)
def test_esc12_microfono_no_disponible_deshabilita_escucha_y_se_recupera(env_listo):
    e = env_listo
    e.reco.microfono = False
    e.reco.encolar("siéntate")
    assert e.ctrl.escuchar() is None
    assert not e.ctrl.gestor.escucha and e.serie.escrituras == []
    assert e.avisos.emitidos[-1].codigo == "microfono"
    assert e.registro.errores()[-1]["tipo_error"] == "microfono_no_disponible"
    assert e.ctrl.activar_escucha() is False                  # sigue sin micro
    e.reco.microfono = True
    assert e.ctrl.activar_escucha()                           # control manual (RU-03)
    assert e.ctrl.escuchar().resultado == "enviada"


@pytest.mark.caso("TEST-32")
@pytest.mark.req("RM-01", "RM-02")
@pytest.mark.esc("ESC-02", "ESC-08", "ESC-09", "ESC-10", "ESC-11", "ESC-12")
@pytest.mark.nivel(2)
def test_sc007_el_100_por_ciento_de_las_entradas_aparece_en_el_registro_con_sus_campos(env_listo):
    e = env_listo
    entradas = ["siéntate", "corre", "estado", "historial"]
    for x in entradas:
        e.decir(x)
        if e.ctrl.gestor.estado is Estado.EJECUTANDO:
            e.ctrl.finalizar_accion()
    e.decir("siéntate", confianza=0.1)
    e.reco.encolar_silencio(); e.ctrl.escuchar()
    n = len(entradas) + 2
    assert len(e.registro.eventos) == n
    for ev in e.registro.eventos:
        assert ev["fecha"] and ev["hora"] and ev["resultado"] in ("aceptada", "rechazada", "enviada", "error")
        assert "texto" in ev
