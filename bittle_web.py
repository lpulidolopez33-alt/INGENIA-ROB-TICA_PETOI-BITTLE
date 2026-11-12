"""Interfaz local de VOICE-BITTLE. Arranca sin conectar robot ni micrófono."""
import argparse
import array
import json
import math
import queue
import secrets
import threading
import time
import webbrowser
from collections import deque
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import bittle_voz as bittle


class Panel:
    def __init__(self):
        self.lock = threading.RLock()
        self.operacion = threading.Lock()
        self.enlace = self.cola = None
        self.conexion = "desconectado"
        self.microfono = "apagado"
        self.nivel = 0
        self.ultima_frase = ""
        self.error = ""
        self.eventos = deque(maxlen=40)
        self.mic_stop = threading.Event()
        self.mic_hilo = None

    def registrar(self, texto):
        with self.lock:
            self.eventos.appendleft({"hora": time.strftime("%H:%M:%S"), "texto": texto})

    def estado(self):
        with self.lock:
            return {"conexion": self.conexion, "microfono": self.microfono,
                    "nivel": self.nivel, "ultima_frase": self.ultima_frase,
                    "error": self.error, "eventos": list(self.eventos),
                    "cola": self.cola.estado() if self.cola else {"actual": None, "pendientes": [], "error": None}}

    def conectar(self, modo="simulado", puerto="", segundos=3):
        segundos = float(segundos)
        if not math.isfinite(segundos) or segundos <= 0:
            raise ValueError("El tiempo por acción debe ser positivo")
        if modo not in ("simulado", "serie"):
            raise ValueError("Modo desconocido")
        if modo == "serie" and not puerto.strip():
            raise ValueError("Selecciona el puerto COM saliente del Bittle")
        with self.operacion:
            with self.lock:
                if self.conexion != "desconectado":
                    raise ValueError("Desconecta la sesión anterior primero")
                self.conexion = "conectando"
                self.error = ""
            try:
                enlace = bittle.EnlaceSimulado() if modo == "simulado" else bittle.EnlaceSerie(puerto, 115200)
                with self.lock:
                    self.enlace = enlace
                    self.cola = bittle.ColaAcciones(enlace, segundos)
                    self.conexion = "simulado" if modo == "simulado" else "conectado"
                self.registrar("Simulación iniciada" if modo == "simulado" else f"Puerto {puerto} abierto; comprueba la respuesta física")
            except Exception as exc:
                with self.lock:
                    self.conexion = "desconectado"
                    self.error = str(exc)
                raise

    def ordenar(self, texto):
        with self.lock:
            if self.conexion not in ("conectado", "simulado"):
                raise ValueError("Conecta o inicia la simulación primero")
            self.ultima_frase = texto
            comandos = bittle.buscar_comandos(texto)
            if not comandos:
                self.registrar(f"No reconocida: {texto}")
                return False
            aceptada = self.cola.agregar(comandos)
            self.registrar(("En cola: " if aceptada else "Cola llena: ") + texto)
            return aceptada

    def apagar_microfono(self):
        with self.lock:
            self.mic_stop.set()
            self.microfono = "apagado"
            self.nivel = 0
        self.registrar("Escucha desactivada; las acciones ya aceptadas siguen en cola")

    def activar_microfono(self, modelo, dispositivo=None):
        dispositivo = None if dispositivo in (None, "") else int(dispositivo)
        if not Path(modelo).is_dir():
            raise ValueError("No existe la carpeta del modelo Vosk indicada")
        with self.lock:
            if self.conexion not in ("conectado", "simulado"):
                raise ValueError("Conecta o inicia la simulación primero")
            if self.mic_hilo and self.mic_hilo.is_alive():
                raise ValueError("El micrófono está activo o terminando de cerrarse; espera un momento")
            self.mic_stop = threading.Event()
            self.microfono = "cargando"
            self.error = ""
            self.mic_hilo = threading.Thread(target=self._escuchar, args=(modelo, dispositivo, self.mic_stop), daemon=True)
            self.mic_hilo.start()

    def _escuchar(self, modelo, dispositivo, parar):
        try:
            import sounddevice as sd
            from vosk import Model, KaldiRecognizer, SetLogLevel
            SetLogLevel(-1)
            rec = KaldiRecognizer(Model(str(modelo)), 16000, json.dumps(bittle.GRAMATICA, ensure_ascii=False))
            audio = queue.Queue(maxsize=8)
            def callback(datos, frames, tiempo, estado):
                if parar.is_set():
                    return
                try:
                    audio.put_nowait((bytes(datos), str(estado) if estado else ""))
                except queue.Full:
                    parar.set()
                    with self.lock:
                        self.error = "Audio acumulado: escucha detenida. Vuelve a activar el micrófono."
            with self.lock:
                if parar.is_set():
                    return
            with sd.RawInputStream(samplerate=16000, blocksize=4000, device=dispositivo,
                                   dtype="int16", channels=1, callback=callback):
                with self.lock:
                    if parar.is_set():
                        return
                    self.microfono = "escuchando"
                self.registrar("Micrófono abierto: escuchando órdenes")
                while not parar.is_set():
                    try:
                        datos, fallo = audio.get(timeout=.2)
                    except queue.Empty:
                        continue
                    if fallo:
                        raise RuntimeError(f"Problema de captura de audio: {fallo}")
                    muestras = array.array("h", datos)
                    nivel = min(100, round(math.sqrt(sum(x*x for x in muestras) / max(1, len(muestras))) / 32768 * 500))
                    final = rec.AcceptWaveform(datos)
                    texto = json.loads(rec.Result()).get("text", "").strip() if final else ""
                    with self.lock:
                        if parar.is_set():
                            break
                        self.nivel = nivel
                        if texto:
                            self.ordenar(texto)
        except Exception as exc:
            with self.lock:
                if not parar.is_set():
                    self.error = f"Micrófono: {exc}"
                    self.registrar(self.error)
        finally:
            with self.lock:
                self.microfono = "apagado"
                self.nivel = 0

    def desconectar(self):
        with self.operacion:
            self.apagar_microfono()
            with self.lock:
                self.conexion = "desconectando"
                cola, enlace = self.cola, self.enlace
            try:
                if cola:
                    cola.cerrar()
                if enlace:
                    try:
                        enlace.enviar("krest")
                    finally:
                        enlace.cerrar()
            finally:
                with self.lock:
                    self.cola = self.enlace = None
                    self.conexion = "desconectado"
                self.registrar("Sesión cerrada; se intentó enviar descanso")


def dispositivos():
    import serial.tools.list_ports
    import sounddevice as sd
    return {"puertos": [{"id": p.device, "nombre": f"{p.device} · {p.description}"} for p in serial.tools.list_ports.comports()],
            "microfonos": [{"id": i, "nombre": d["name"]} for i, d in enumerate(sd.query_devices()) if d["max_input_channels"] > 0]}


def crear_servidor(panel, puerto):
    token = secrets.token_urlsafe(32)
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def responder(self, valor, codigo=200, tipo="application/json"):
            datos = valor.encode("utf-8") if isinstance(valor, str) else json.dumps(valor, ensure_ascii=False).encode("utf-8")
            self.send_response(codigo)
            self.send_header("Content-Type", tipo + "; charset=utf-8")
            self.send_header("Content-Length", str(len(datos)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("X-Frame-Options", "DENY")
            self.end_headers()
            self.wfile.write(datos)

        def local(self):
            return self.headers.get("Host") == f"127.0.0.1:{self.server.server_port}"

        def do_GET(self):
            if not self.local():
                return self.responder({"error": "Usa la dirección local indicada"}, 403)
            try:
                if self.path == "/":
                    html = (Path(__file__).parent / "web" / "index.html").read_text(encoding="utf-8")
                    return self.responder(html.replace("__TOKEN__", token), tipo="text/html")
                if self.path == "/api/estado":
                    return self.responder(panel.estado())
                if self.path == "/api/dispositivos":
                    return self.responder(dispositivos())
                self.responder({"error": "No encontrado"}, 404)
            except Exception as exc:
                self.responder({"error": str(exc)}, 500)

        def do_POST(self):
            origen = f"http://127.0.0.1:{self.server.server_port}"
            if not self.local() or self.headers.get("X-Bittle-Token") != token or self.headers.get("Origin", origen) != origen:
                return self.responder({"error": "Solicitud no autorizada"}, 403)
            try:
                longitud = int(self.headers.get("Content-Length", 0))
                if not 0 < longitud <= 8192:
                    raise ValueError("Solicitud inválida")
                datos = json.loads(self.rfile.read(longitud))
                if self.path == "/api/conectar":
                    panel.conectar(datos.get("modo", "simulado"), datos.get("puerto", ""), datos.get("segundos", 3))
                elif self.path == "/api/desconectar":
                    panel.desconectar()
                elif self.path == "/api/orden":
                    if not panel.ordenar(str(datos.get("texto", ""))):
                        raise ValueError("Orden no reconocida o cola llena")
                elif self.path == "/api/microfono":
                    if datos.get("activo") is True:
                        panel.activar_microfono(datos.get("modelo", ""), datos.get("dispositivo"))
                    else:
                        panel.apagar_microfono()
                else:
                    return self.responder({"error": "No encontrado"}, 404)
                self.responder(panel.estado())
            except Exception as exc:
                self.responder({"error": str(exc)}, 400)
    return ThreadingHTTPServer(("127.0.0.1", puerto), Handler)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--puerto-web", type=int, default=8765)
    parser.add_argument("--sin-navegador", action="store_true")
    args = parser.parse_args()
    panel = Panel()
    servidor = crear_servidor(panel, args.puerto_web)
    url = f"http://127.0.0.1:{servidor.server_port}"
    print(f"VOICE-BITTLE: {url}\nCtrl+C para cerrar. Sin conexión ni micrófono al arrancar.")
    if not args.sin_navegador:
        webbrowser.open(url)
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        servidor.server_close()
        panel.desconectar()


if __name__ == "__main__":
    main()
