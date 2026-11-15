"""Contratos de H3: sin Bluetooth, puerto físico, modelo ni micrófono real."""
import json
import sys
import threading
import types
import urllib.error
import urllib.request

import pytest
import bittle_voz as bittle
import bittle_web as web


class Capturador:
    def __init__(self):
        self.tokens = []
        self.cerrado = False

    def enviar(self, token):
        self.tokens.append(token)

    def cerrar(self):
        self.cerrado = True


def test_dos_ordenes_y_desconocida_por_http(monkeypatch):
    enlace = Capturador()
    monkeypatch.setattr(web.bittle, 'EnlaceSimulado', lambda: enlace)
    panel = web.Panel()
    servidor = web.crear_servidor(panel, 0)
    hilo = threading.Thread(target=servidor.serve_forever, daemon=True)
    hilo.start()
    base = f'http://127.0.0.1:{servidor.server_port}'
    try:
        with urllib.request.urlopen(base) as r:
            token = r.read().decode().split("const token='")[1].split("'")[0]

        def post(ruta, datos):
            req = urllib.request.Request(base + ruta, json.dumps(datos).encode(),
                {'Content-Type': 'application/json', 'X-Bittle-Token': token, 'Origin': base})
            with urllib.request.urlopen(req) as r:
                return json.load(r)

        assert post('/api/conectar', {'modo': 'simulado', 'segundos': .01})['microfono'] == 'apagado'
        for texto, esperado in [('siéntate', ['ksit']), ('ponte de pie', ['ksit', 'kup'])]:
            post('/api/orden', {'texto': texto})
            assert panel.cola.esperar_vacia(2)
            assert enlace.tokens == esperado
        with pytest.raises(urllib.error.HTTPError) as exc:
            post('/api/orden', {'texto': 'siéntate y vuela'})
        assert exc.value.code == 400
        assert 'Orden no reconocida' in json.loads(exc.value.read())['error']
        assert enlace.tokens == ['ksit', 'kup']
        assert post('/api/desconectar', {})['conexion'] == 'desconectado'
        assert enlace.tokens == ['ksit', 'kup', 'krest']
        assert enlace.cerrado
    finally:
        servidor.shutdown()
        servidor.server_close()
        hilo.join(2)
        panel.desconectar()


def test_formato_serie_ascii_lf_sin_puerto(monkeypatch):
    escritos = []
    def escribir(datos):
        escritos.append(datos)
        return len(datos)
    serie = types.SimpleNamespace(write=escribir, flush=lambda: None, in_waiting=0, is_open=True)
    enlace = object.__new__(bittle.EnlaceSerie)  # no ejecutar Serial() ni abrir COM
    enlace.s = serie
    monkeypatch.setattr(bittle.time, 'sleep', lambda _: None)
    enlace._escribir('ksit')
    enlace._escribir('kup')
    assert escritos == [b'ksit\n', b'kup\n']


def test_parada_preservada_durante_error():
    enlace = Capturador()
    enviado, liberar = threading.Event(), threading.Event()
    def enviar(token):
        enlace.tokens.append(token)
        if token == 'ksit':
            enviado.set()
            assert liberar.wait(2)
            raise OSError('fallo en envío ya iniciado')
    enlace.enviar = enviar
    cola = bittle.ColaAcciones(enlace, segundos=.01)
    try:
        cola.agregar(bittle.buscar_comandos('siéntate y ponte de pie'))
        assert enviado.wait(2)
        cola.agregar(bittle.buscar_comandos('para'))
        liberar.set()
        assert cola.esperar_vacia(2)
        assert enlace.tokens == ['ksit', 'kbalance']
        assert cola.estado()['error'] == 'fallo en envío ya iniciado'
    finally:
        liberar.set()
        cola.cerrar()


def test_audio_saturado_apaga_sin_aceptar_orden(monkeypatch, tmp_path):
    class Captura:
        def __init__(self, **kw):
            self.callback = kw['callback']
        def __enter__(self):
            for _ in range(9):
                self.callback(b'\0\0' * 4000, 4000, None, None)
        def __exit__(self, *args):
            return False
    def aceptar(_):
        pytest.fail('No debe reconocer audio tras saturación')
    rec = types.SimpleNamespace(AcceptWaveform=aceptar)
    monkeypatch.setitem(sys.modules, 'vosk', types.SimpleNamespace(
        Model=lambda p: object(), KaldiRecognizer=lambda *a: rec, SetLogLevel=lambda _: None))
    monkeypatch.setitem(sys.modules, 'sounddevice', types.SimpleNamespace(RawInputStream=Captura))
    panel = web.Panel()
    panel.conectar()
    try:
        panel.activar_microfono(str(tmp_path))
        panel.mic_hilo.join(2)
        estado = panel.estado()
        assert not panel.mic_hilo.is_alive()
        assert estado['microfono'] == 'apagado'
        assert estado['nivel'] == 0
        assert 'Audio acumulado' in estado['error']
        assert estado['ultima_frase'] == ''
        assert estado['cola']['pendientes'] == []
    finally:
        panel.desconectar()


def test_eventos_limitados_conservan_mas_recientes():
    panel = web.Panel()
    for i in range(45):
        panel.registrar(f'evento {i}')
    eventos = panel.estado()['eventos']
    assert len(eventos) == 40
    assert eventos[0]['texto'] == 'evento 44'
    assert eventos[-1]['texto'] == 'evento 5'


def test_esperas_minimas_y_parametro_invalido():
    for valor in [0, -1, float('nan'), float('inf')]:
        with pytest.raises(ValueError):
            bittle.ColaAcciones(Capturador(), segundos=valor)
    cola = bittle.ColaAcciones(Capturador(), segundos=.01)
    try:
        assert cola._pasos('khi') == [('khi', 4.0)]
        assert cola._pasos('kstr') == [('kstr', 4.0)]
        assert cola._pasos('kpu') == [('kpu', 6.0)]
        assert cola._pasos('kwkF') == [('kwkF', .01), ('kbalance', 0)]
    finally:
        cola.cerrar()
