"""Regresiones de cierre: puertos y audio falsos; nunca abrir hardware."""
import json
import sys
import threading
import types
import urllib.request

import pytest
import bittle_voz as b
import bittle_web as w


class Puerto:
    def __init__(self, fallo=None):
        self.fallo = fallo
        self.is_open = True
        self.intentos = []
        self.in_waiting = 1 if fallo == 'lectura' else 0

    def write(self, datos):
        self.intentos.append(datos)
        if self.fallo == 'escritura':
            raise OSError('timeout; posible transmisión parcial')
        return len(datos) - 1 if self.fallo == 'parcial' else len(datos)

    def flush(self):
        if self.fallo == 'vaciado':
            raise OSError('fallo en flush')

    def read(self, cantidad):
        if self.fallo == 'lectura':
            raise OSError('fallo de respuesta')
        return b'Ready!'

    def reset_input_buffer(self):
        pass

    def close(self):
        self.is_open = False


def enlace(monkeypatch, puerto):
    monkeypatch.setattr(b.EnlaceSerie, '_abrir', lambda self: setattr(self, 's', puerto))
    monkeypatch.setattr(b.time, 'sleep', lambda _: None)
    return b.EnlaceSerie('FALSO', 115200)


@pytest.mark.parametrize('fallo,fase', [('escritura','escritura'), ('parcial','escritura'),
                                      ('vaciado','vaciado'), ('lectura','lectura_respuesta')])
def test_envio_incierto_no_repite_y_conserva_resultado(monkeypatch, fallo, fase):
    puerto = Puerto(fallo)
    e = enlace(monkeypatch, puerto)
    with pytest.raises(RuntimeError, match='desconocido'):
        e.enviar('ksit')
    esperado = e.estado()
    assert esperado == dict(token='ksit', fase=fase, resultado='desconocido', requiere_reconexion=True)
    for token in ['ksit', 'kup', 'kbalance', 'krest']:
        with pytest.raises(RuntimeError, match='bloqueado'):
            e.enviar(token)
    assert puerto.intentos == [b'ksit\n']
    assert e.estado() == esperado
    e.cerrar()
    assert not puerto.is_open
    assert e.estado() == esperado


def test_fallo_previo_no_escribe_y_recuperacion_es_explicita(monkeypatch):
    puerto = Puerto()
    puerto.is_open = False
    e = enlace(monkeypatch, puerto)
    with pytest.raises(RuntimeError, match='no_enviado'):
        e.enviar('ksit')
    assert e.estado()['fase'] == 'antes_escritura'
    assert puerto.intentos == []
    # Aunque reaparezca el dispositivo, no repetir ni desbloquear en enviar().
    puerto.is_open = True
    with pytest.raises(RuntimeError, match='bloqueado'):
        e.enviar('kup')
    e.cerrar()
    nuevo = Puerto()
    recuperado = enlace(monkeypatch, nuevo)
    assert nuevo.intentos == []
    recuperado.enviar('kup')  # nueva solicitud explícita, ninguna orden recuperada
    assert nuevo.intentos == [b'kup\n']
    assert recuperado.estado()['resultado'] == 'enviado_sin_confirmacion_fisica'


def test_fallo_serie_descarta_cola_y_no_transmite_al_cerrar(monkeypatch):
    puerto = Puerto('escritura')
    e = enlace(monkeypatch, puerto)
    panel = w.Panel()
    panel.conectar('serie', 'FALSO', .001)
    # conectar crea un enlace nuevo sobre el mismo puerto falso.
    assert panel.ordenar('siéntate y ponte de pie')
    assert panel.cola.esperar_vacia(2)
    assert panel.estado()['transporte']['resultado'] == 'desconocido'
    assert panel.estado()['cola']['pendientes'] == []
    with pytest.raises(RuntimeError, match='bloqueado'):
        panel.desconectar()
    assert puerto.intentos == [b'ksit\n']
    assert panel.estado()['conexion'] == 'desconectado'
    assert not puerto.is_open


def test_fallo_con_parada_no_conserva_movimientos_añadidos():
    inicio, continuar = threading.Event(), threading.Event()
    tokens = []
    def enviar(token):
        tokens.append(token)
        if token == 'ksit':
            inicio.set()
            assert continuar.wait(2)
            raise OSError('fallo')
    cola = b.ColaAcciones(types.SimpleNamespace(enviar=enviar), .001)
    try:
        cola.agregar(b.buscar_comandos('siéntate y ponte de pie'))
        assert inicio.wait(2)
        cola.agregar(b.buscar_comandos('para'))
        cola.agregar(b.buscar_comandos('camina'))
        continuar.set()
        assert cola.esperar_vacia(2)
        assert tokens == ['ksit', 'kbalance']
    finally:
        continuar.set()
        cola.cerrar()


def test_cancelacion_antes_de_seleccionar_envio_no_ejecuta_orden():
    preparado, seguir = threading.Event(), threading.Event()
    tokens = []
    cola = b.ColaAcciones(types.SimpleNamespace(enviar=tokens.append), .001)
    pasos = cola._pasos
    def pausado(token):
        if token == 'ksit':
            preparado.set()
            assert seguir.wait(2)
        return pasos(token)
    cola._pasos = pausado
    try:
        cola.agregar(b.buscar_comandos('siéntate'))
        assert preparado.wait(2)
        cola.agregar(b.buscar_comandos('para'))
        seguir.set()
        assert cola.esperar_vacia(2)
        assert tokens == ['kbalance']
    finally:
        seguir.set()
        cola.cerrar()


@pytest.mark.parametrize('resultado', ['{}', '[]', 'null', '{', '{"partial":"camina"}',
                                     '{"text":null}', '{"text":7}', '{"text":"  "}'])
def test_resultado_vosk_vacio_invalido_no_es_orden(resultado):
    assert b.texto_reconocido(resultado) == ''
    assert b.buscar_comandos(b.texto_reconocido(resultado)) == []


def test_audio_invalido_no_envia_y_nueva_activacion_no_reutiliza(monkeypatch, tmp_path):
    visto = threading.Event()
    resultados = iter(['{"text":null}', '{"text":"siéntate"}'])
    class Rec:
        def AcceptWaveform(self, datos):
            return True
        def Result(self):
            resultado = next(resultados)
            visto.set()
            return resultado
    class Captura:
        def __init__(self, **kw): self.callback = kw['callback']
        def __enter__(self): self.callback(b'\0\0'*4000,4000,None,None)
        def __exit__(self, *args): pass
    monkeypatch.setitem(sys.modules, 'vosk', types.SimpleNamespace(Model=lambda _:None, KaldiRecognizer=lambda *a:Rec(), SetLogLevel=lambda _:None))
    monkeypatch.setitem(sys.modules, 'sounddevice', types.SimpleNamespace(RawInputStream=Captura))
    tokens=[]
    monkeypatch.setattr(b,'EnlaceSimulado',lambda:types.SimpleNamespace(enviar=tokens.append,cerrar=lambda:None))
    panel=w.Panel()
    panel.conectar(segundos=.001)
    try:
        panel.activar_microfono(str(tmp_path))
        assert visto.wait(2)
        panel.apagar_microfono()
        panel.mic_hilo.join(2)
        assert tokens == []
        # Nueva sesión de captura: solo acepta el resultado nuevo; no conserva audio previo.
        visto.clear()
        panel.activar_microfono(str(tmp_path))
        assert visto.wait(2)
        # ordenar se sincroniza con el lock del panel; esperar a que se acepte.
        for _ in range(200):
            with panel.lock:
                if panel.ultima_frase == 'siéntate': break
            threading.Event().wait(.005)
        assert panel.ultima_frase == 'siéntate'
        panel.apagar_microfono()
        panel.mic_hilo.join(2)
        assert panel.cola.esperar_vacia(2)
        assert tokens == ['ksit']
    finally:
        panel.desconectar()


def test_arranque_http_no_abre_hardware_ni_transmite(monkeypatch):
    def prohibido(*args, **kwargs): pytest.fail('No debe abrir hardware ni transmitir al arrancar')
    monkeypatch.setattr(b.EnlaceSerie, '_abrir', prohibido)
    monkeypatch.setattr(b.EnlaceSimulado, 'enviar', prohibido)
    monkeypatch.setattr(w.Panel, 'activar_microfono', prohibido)
    panel = w.Panel()
    servidor = w.crear_servidor(panel, 0)
    hilo = threading.Thread(target=servidor.serve_forever, daemon=True)
    hilo.start()
    try:
        base=f'http://127.0.0.1:{servidor.server_port}'
        with urllib.request.urlopen(base) as r: assert 'Activar micrófono' in r.read().decode()
        with urllib.request.urlopen(base+'/api/estado') as r: estado=json.load(r)
        assert estado['conexion']=='desconectado'
        assert estado['microfono']=='apagado'
        assert estado['cola']['pendientes']==[]
        assert panel.enlace is panel.cola is None
    finally:
        servidor.shutdown()
        servidor.server_close()
        hilo.join(2)
