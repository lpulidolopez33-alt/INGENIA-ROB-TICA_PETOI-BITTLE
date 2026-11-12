import json
import sys
from types import SimpleNamespace
import pytest
from enlace import LinkError
from enlace.serie_real import PerfilFisico, PuertoSerieReal
from voz import MicrofonoNoDisponible, ModeloNoDisponible
from voz.vosk_reconocedor import VoskReconocedor
from config import Config

pytestmark = [pytest.mark.caso("TEST-34"), pytest.mark.req("RS-01", "RFI-01", "RFI-02", "RD-02"),
              pytest.mark.esc("ESC-01", "ESC-08", "ESC-12"), pytest.mark.nivel(3)]


def perfil(**kw):
    datos = dict(puerto="DOBLE_NO_COM", baudrate=115200, terminador=b"\n", modelo="doble",
                 firmware="doble", referencia_protocolo="ensayo simulado",
                 aprobacion_parametros="ficticia SOLO TEST", aprobacion_seguridad="ficticia SOLO TEST",
                 parametros=Config())
    return PerfilFisico(**(datos | kw))


class SerialDoble:
    def __init__(self, **kw):
        self.is_open = True
        self.escrituras = []
        self.parcial = False
    def write(self, datos):
        self.escrituras.append(datos)
        return 1 if self.parcial else len(datos)
    def close(self):
        self.is_open = False


def test_fisico_no_abre_por_defecto():
    llamadas = []
    p = PuertoSerieReal(perfil(), fabrica=lambda **kw: llamadas.append(kw))
    with pytest.raises(LinkError):
        p.abrir()
    with pytest.raises(LinkError):
        p.escribir(b"ksit\n")
    assert llamadas == []


@pytest.mark.parametrize("campo", ["puerto", "modelo", "firmware", "referencia_protocolo",
                                   "aprobacion_parametros", "aprobacion_seguridad"])
def test_aprobaciones_incompletas(campo):
    p = PuertoSerieReal(perfil(**{campo: ""}), fabrica=SerialDoble)
    with pytest.raises(LinkError):
        p.habilitar("SOLO TEST")


def test_serie_estricta_y_escritura_parcial():
    p = PuertoSerieReal(perfil(), fabrica=SerialDoble)
    p.habilitar("SOLO TEST"); p.abrir()
    for malo in (b"kbalance\n", b"ksit", b"ksit\nkup\n", b"", "ksit\n"):
        with pytest.raises(LinkError):
            p.escribir(malo)
    assert not p._serial.escrituras
    p.escribir(b"ksit\n")
    doble = p._serial
    doble.parcial = True
    with pytest.raises(LinkError):
        p.escribir(b"kup\n")
    assert not p.abierto
    assert doble.escrituras == [b"ksit\n", b"kup\n"]
    with pytest.raises(LinkError):
        p.abrir()


def test_error_apertura():
    def fallo(**kw):
        raise OSError("puerto ausente")
    p = PuertoSerieReal(perfil(), fabrica=fallo)
    p.habilitar("SOLO TEST")
    with pytest.raises(LinkError):
        p.abrir()
    assert not p.abierto


def test_controlador_fisico_exige_reposo_y_parametros_coincidentes():
    from conftest import Entorno
    from app.controlador import Controlador
    from enlace import EnlaceBittle
    from estado import Estado
    e = Entorno()
    puerto = PuertoSerieReal(perfil(), fabrica=SerialDoble)
    enlace = EnlaceBittle(puerto, {"ksit", "kup"}, terminador=b"\n")
    with pytest.raises(ValueError):
        Controlador(e.vocab, e.reco, enlace, e.registro, e.avisos, e.reloj, Config(umbral_u=.9))
    ctrl = Controlador(e.vocab, e.reco, enlace, e.registro, e.avisos, e.reloj)
    puerto.habilitar("SOLO TEST")
    assert ctrl.iniciar_sesion() and ctrl.activar_escucha()
    assert ctrl.gestor.estado is Estado.DESCONOCIDO
    e.reco.encolar("siéntate")
    assert ctrl.escuchar().motivo == "estado_desconocido"
    assert not puerto._serial.escrituras
    assert ctrl.confirmar_reposo("Observación FICTICIA de prueba")
    e.reco.encolar("siéntate")
    assert ctrl.escuchar().resultado == "enviada"
    ctrl.finalizar_accion(False)
    assert ctrl.gestor.estado is Estado.DESCONOCIDO
    assert not ctrl.cerrar_sesion().ok
    assert ctrl.confirmar_reposo("Fin FICTICIO observado")
    assert ctrl.cerrar_sesion().ok


@pytest.fixture
def voz_doble(monkeypatch, tmp_path):
    estado = {"fallo": None, "overflow": False, "texto": "siéntate", "conf": .9}
    class Flujo:
        def __init__(self, **kw):
            if estado["fallo"] == "abrir": raise OSError("abrir")
        def __enter__(self): return self
        def __exit__(self, *args): pass
        def read(self, n):
            if estado["fallo"] == "leer": raise OSError("leer")
            return b"audio", estado["overflow"]
    class Rec:
        def __init__(self, *args): pass
        def SetWords(self, value): pass
        def AcceptWaveform(self, data): return True
        def Result(self):
            return json.dumps({"text": estado["texto"], "result": [{"word": w, "conf": estado["conf"], "end": 0.0} for w in estado["texto"].split()]})
    monkeypatch.setitem(sys.modules, "sounddevice", SimpleNamespace(
        query_devices=lambda *args, **kw: {"max_input_channels": 1}, RawInputStream=Flujo))
    monkeypatch.setitem(sys.modules, "vosk", SimpleNamespace(Model=lambda p: object(), KaldiRecognizer=Rec))
    reco = VoskReconocedor({"es": str(tmp_path)}, {"es": ["siéntate", "estado"]})
    reco.cargar_modelo("es")
    return reco, estado


@pytest.mark.parametrize("fallo", ["abrir", "leer", "overflow"])
def test_fallos_audio_controlados(voz_doble, fallo):
    r, estado = voz_doble
    estado["fallo"] = fallo
    estado["overflow"] = fallo == "overflow"
    with pytest.raises(MicrofonoNoDisponible): r.escuchar(.1)


def test_vosk_estimacion_fin_y_confianza(voz_doble):
    r, _ = voz_doble
    resultado = r.escuchar(.1)
    assert resultado.confianza == .9
    assert resultado.fin_monotonic is not None
    assert resultado.origen_tiempo == "estimado_vosk"


def test_modelo_ausente_y_cambio_atomico(voz_doble):
    r, _ = voz_doble
    anterior = r._modelo
    with pytest.raises(ModeloNoDisponible): r.cargar_modelo("en")
    assert r._modelo is anterior and r._idioma == "es"


def test_silencio_y_confianza_invalida(voz_doble):
    r, estado = voz_doble
    estado["conf"] = None
    assert r.escuchar(.1).confianza is None
    estado["texto"] = ""
    assert r.escuchar(.001) is None


@pytest.mark.parametrize("idioma,texto,token", [
    ("es", "siéntate", b"ksit"), ("es", "ponte de pie", b"kup"),
    ("es", "historial", None), ("es", "estado", None),
    ("en", "sit", b"ksit"), ("en", "stand up", b"kup"),
    ("en", "history", None), ("en", "status", None),
])
def test_vosk_con_dobles_integrado_en_controlador(voz_doble, idioma, texto, token):
    from conftest import Entorno
    from reloj import Reloj
    reco, estado = voz_doble
    reco.rutas[idioma] = reco.rutas["es"]
    reco.frases[idioma] = [texto]
    estado["texto"] = texto
    e = Entorno(idioma=idioma)
    e.ctrl.reconocedor = reco
    e.ctrl.reloj = Reloj()
    assert e.ctrl.iniciar_sesion() and e.ctrl.activar_escucha()
    salida = e.ctrl.escuchar()
    assert salida.resultado == ("enviada" if token else "aceptada")
    assert e.serie.escrituras == ([token] if token else [])


@pytest.mark.parametrize("fallo", ["abrir", "leer", "overflow"])
def test_fallo_audio_integrado_no_envia(voz_doble, fallo):
    from conftest import Entorno
    reco, estado = voz_doble
    e = Entorno()
    e.ctrl.reconocedor = reco
    assert e.ctrl.iniciar_sesion() and e.ctrl.activar_escucha()
    estado["fallo"] = fallo
    estado["overflow"] = fallo == "overflow"
    assert e.ctrl.escuchar() is None
    assert not e.ctrl.gestor.escucha and not e.serie.escrituras
    assert e.registro.errores()[-1]["tipo_error"] == "microfono_no_disponible"
