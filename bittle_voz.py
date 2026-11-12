"""Control de Bittle por voz (español), escucha continua.

Hablas -> Vosk reconoce la frase (sin Internet) -> se envía el comando Petoi
por Bluetooth (puerto COM serie o Bluetooth LE).

Uso (desde esta carpeta):
  .\\.venv\\Scripts\\python.exe bittle_voz.py --simulado          # sin robot: solo muestra lo que enviaría
  .\\.venv\\Scripts\\python.exe bittle_voz.py --puerto COM7       # Bittle emparejado como puerto serie
  .\\.venv\\Scripts\\python.exe bittle_voz.py --ble               # Bittle por Bluetooth LE (busca "Bittle"/"Petoi")
  .\\.venv\\Scripts\\python.exe bittle_voz.py --simulado --texto  # escribir las órdenes en vez de hablar
  .\\.venv\\Scripts\\python.exe bittle_voz.py --listar            # lista puertos COM, micrófonos y dispositivos BLE

Di "para" o "quieto" en cualquier momento para detenerlo. Ctrl+C para salir.
"""
import argparse
import asyncio
import json
import queue
import re
import math
from collections import deque
import sys
import threading
import time
import unicodedata
from pathlib import Path

AQUI = Path(__file__).resolve().parent
MODELO_POR_DEFECTO = AQUI / "modelos" / "vosk-model-small-es-0.42"

# frase (sin tildes, minúsculas) -> (comando Petoi/OpenCat, descripción)
COMANDOS = {
    "sientate": ("ksit", "sentarse"),
    "sentado": ("ksit", "sentarse"),
    "sienta": ("ksit", "sentarse"),
    "ponte de pie": ("kup", "ponerse de pie"),
    "de pie": ("kup", "ponerse de pie"),
    "pie": ("kup", "ponerse de pie"),
    "levantate": ("kup", "ponerse de pie"),
    "arriba": ("kup", "ponerse de pie"),
    "camina": ("kwkF", "caminar adelante"),
    "adelante": ("kwkF", "caminar adelante"),
    "anda": ("kwkF", "caminar adelante"),
    "corre": ("ktrF", "trotar adelante"),
    "atras": ("kbk", "caminar hacia atrás"),
    "marcha atras": ("kbk", "caminar hacia atrás"),
    "izquierda": ("kwkL", "girar a la izquierda"),
    "derecha": ("kwkR", "girar a la derecha"),
    "saluda": ("khi", "saludar"),
    "hola": ("khi", "saludar"),
    "flexiones": ("kpu", "flexiones"),
    "estirate": ("kstr", "estirarse"),
    "estira": ("kstr", "estirarse"),
    "descansa": ("krest", "descansar (servos relajados)"),
    "duerme": ("krest", "descansar (servos relajados)"),
    "baila": ("BAILE", "bailar (coreografía casera)"),
    "baile": ("BAILE", "bailar (coreografía casera)"),
    "bailar": ("BAILE", "bailar (coreografía casera)"),
    "cristiano": ("CRISTIANO", "celebración SIUUU de Cristiano"),
    "ronaldo": ("CRISTIANO", "celebración SIUUU de Cristiano"),
    "siu": ("CRISTIANO", "celebración SIUUU de Cristiano"),
    "para": ("kbalance", "parar / equilibrio"),
    "quieto": ("kbalance", "parar / equilibrio"),
    "alto": ("kbalance", "parar / equilibrio"),
    "stop": ("kbalance", "parar / equilibrio"),
}

# Palabras con tildes tal como las escribe el modelo español (para la gramática).
GRAMATICA = ["siéntate", "sentado", "sienta", "ponte de pie", "de pie", "levántate",
             "arriba", "camina", "adelante", "anda", "corre", "atrás", "marcha atrás",
             "izquierda", "derecha", "saluda", "hola", "flexiones", "estira",
             "descansa", "duerme", "baila", "baile", "bailar", "cristiano", "ronaldo", "siu",
             "para", "quieto", "alto", "[unk]"]
GRAMATICA += ["y", "luego", "después", "primero", "entonces", "stop", "estírate"]

# Comandos caseros: secuencias de (orden para Bittle, segundos de espera).
# "kXXX" = habilidad de Bittle; "m0 40" = girar la cabeza (articulación 0) a 40°.
# Para crear uno nuevo: añade aquí la secuencia y en COMANDOS la palabra que lo lanza.
COREOGRAFIAS = {
    "BAILE": [
        ("kbalance", 1.0),
        ("kvtF", 2.5),                    # pasitos en el sitio
        ("kbalance", 0.6),
        ("m0 45", 0.35), ("m0 -45", 0.35), ("m0 45", 0.35), ("m0 -45", 0.35),  # menear la cabeza
        ("m0 0", 0.4),
        ("khi", 3.0),                     # saludo
        ("kbuttUp", 1.5),                 # culo arriba
        ("kbalance", 0.8),
        ("kmw", 4.0),                     # moonwalk
        ("kbalance", 0.6),
        ("kvtL", 2.0),                    # pasitos girando a la izquierda
        ("kvtR", 2.0),                    # y a la derecha
        ("kbalance", 0.6),
        ("kchr", 3.0),                    # celebración final
        ("kbalance", 0.5),
    ],
    # Celebración de Cristiano: giro, se pone de pie sobre las patas traseras y abre
    # las delanteras en X (una arriba, otra abajo) mientras el PC grita "SIUUU".
    # Las posturas salen de los fotogramas de la habilidad "hu" (manos arriba) de Petoi.
    # "i" mueve varias articulaciones a la vez: i<articulación> <ángulo> ...
    # Articulaciones: 0 cabeza giro, 1 cabeza arriba/abajo, 8-11 hombros, 12-15 rodillas.
    # Se rellena más abajo con cristiano(), que calcula los movimientos suaves.
}


def postura(angulos):
    """Convierte {articulación: ángulo} en la orden 'i' de Bittle."""
    return "i" + " ".join(f"{j} {round(a)}" for j, a in sorted(angulos.items()))


def suave(desde, hasta, segundos, paso=0.1):
    """Pasa de una postura a otra poco a poco (sin tirones que lo desequilibren).
    Solo envía las articulaciones que cambian, para no saturar la placa."""
    n = max(1, round(segundos / paso))
    pasos, anterior = [], {j: round(a) for j, a in desde.items()}
    for k in range(1, n + 1):
        actual = {j: round(desde[j] + (hasta[j] - desde[j]) * k / n) for j in hasta}
        cambios = {j: a for j, a in actual.items() if a != anterior.get(j)}
        if cambios:
            pasos.append((postura(cambios), paso))
        anterior = actual
    return pasos


# Posturas de Cristiano. 8/9 = hombros delanteros, 10/11 = hombros traseros,
# 12/13 = rodillas delanteras, 14/15 = rodillas traseras, 0/1/2 = cabeza.
# P1-P4 son los fotogramas con los que la habilidad "hu" de Petoi se pone de pie.
P1 = {0: 39, 1: -22, 2: 22, 8: 30, 9: 30, 10: 74, 11: 74, 12: 74, 13: 74, 14: -14, 15: -14}
P2 = {0: 26, 1: -22, 2: 22, 8: 30, 9: 30, 10: 31, 11: 3, 12: 91, 13: 74, 14: -14, 15: 32}
P3 = {0: 9, 1: -22, 2: 22, 8: 35, 9: 35, 10: 3, 11: 3, 12: 85, 13: 85, 14: 43, 15: 43}
ERGUIDO = {0: 9, 1: -22, 2: 22, 8: 35, 9: 35, 10: 40, 11: 40, 12: 85, 13: 85, 14: 21, 15: 21}
# Patas traseras más flexionadas (cadera más baja = más estable). Ajusta aquí si hace falta:
# más hombro trasero (10/11) y menos rodilla trasera (14/15) = más agachado.
AGACHADO = {**ERGUIDO, 0: 0, 10: 60, 11: 60, 14: 0, 15: 0}
X = {**AGACHADO, 0: 17, 1: -22, 2: -22, 8: -100, 9: 60, 12: 53, 13: -47}   # ¡la X!
BAJAR1 = {0: 17, 1: 0, 2: 0, 8: 23, 9: 23, 10: -12, 11: -12, 12: 3, 13: 3, 14: 30, 15: 30}
BAJAR2 = {0: 0, 1: 0, 2: 0, 8: 23, 9: 23, 10: 50, 11: 50, 12: 59, 13: 59, 14: -32, 15: -32}


def cristiano(segundos_x=2.0):
    return [
        ("kbalance", 0.8),
        ("kvtL", 1.5),                    # media vuelta, como el giro en el aire
        ("kbalance", 0.8),
        (postura(P1), 0.5),               # impulso para ponerse de pie (como "hu")
        (postura(P2), 0.5),
        (postura(P3), 0.7),
        (postura(ERGUIDO), 0.6),          # erguido sobre las traseras
        *suave(ERGUIDO, AGACHADO, 0.7),   # baja la cadera poco a poco para estabilizarse
        ("DI:SIUUUUUUUU", 0.0),
        *suave(AGACHADO, X, 0.5),         # abre los brazos en X sin tirones
        ("ESPERA", segundos_x),           # aguanta la X
        *suave(X, AGACHADO, 0.4),         # recoge los brazos
        (postura(BAJAR1), 0.5),           # vuelve a cuatro patas
        (postura(BAJAR2), 0.6),
        ("kbalance", 0.5),
    ]


COREOGRAFIAS["CRISTIANO"] = cristiano()


def decir(texto):
    """Lo dice en voz alta el PC (voz de Windows), sin bloquear al robot."""
    import subprocess
    orden = ("Add-Type -AssemblyName System.Speech; $v = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
             "$v.Rate = 2; $v.Volume = 100; $v.Speak($env:TEXTO_BITTLE)")
    try:
        subprocess.Popen(["powershell", "-NoProfile", "-Command", orden],
                         env={**__import__("os").environ, "TEXTO_BITTLE": texto},
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass


class ColaAcciones:
    """Un único ejecutor FIFO. Los tiempos no confirman la finalización física."""

    CONTINUOS = {"kwkF", "ktrF", "kbk", "kwkL", "kwkR"}

    def __init__(self, enlace, segundos=3.0, capacidad=20):
        if not math.isfinite(segundos) or segundos <= 0:
            raise ValueError("El tiempo por acción debe ser positivo y finito")
        self.enlace = enlace
        self.segundos = segundos
        self.capacidad = capacidad
        self._cv = threading.Condition()
        self._pendientes = deque()
        self._generacion = 0
        self._cerrada = False
        self._activa = False
        self._actual = None
        self._error = None
        self._hilo = threading.Thread(target=self._ejecutar, daemon=True)
        self._hilo.start()

    def agregar(self, comandos):
        with self._cv:
            if self._cerrada:
                return False
            if any(token == "kbalance" for token, _ in comandos):
                self._generacion += 1
                self._pendientes.clear()
                self._pendientes.append(("kbalance", "parar / equilibrio"))
                print("   ✋ Cola cancelada; parada solicitada")
            elif len(self._pendientes) + len(comandos) > self.capacidad:
                print(f"   Cola llena (máximo {self.capacidad} pendientes); frase rechazada")
                return False
            else:
                self._pendientes.extend(comandos)
                print(f"   En cola: {len(self._pendientes)} acción(es) pendientes")
            self._cv.notify_all()
            return True

    def _cancelada(self, generacion):
        return self._cerrada or generacion != self._generacion

    def _pasos(self, token):
        if token in COREOGRAFIAS:
            return COREOGRAFIAS[token]
        if token == "kbalance":
            return [(token, 0)]
        espera = max(self.segundos, {"khi": 4.0, "kpu": 6.0, "kstr": 4.0}.get(token, 0))
        pasos = [(token, espera)]
        if token in self.CONTINUOS:
            pasos.append(("kbalance", 0))
        return pasos

    def _ejecutar(self):
        while True:
            with self._cv:
                self._cv.wait_for(lambda: self._cerrada or self._pendientes)
                if self._cerrada:
                    return
                token, descripcion = self._pendientes.popleft()
                generacion = self._generacion
                self._activa = True
                self._actual = descripcion
            try:
                print(f"   ▶ Ejecutando: {descripcion} ({token})")
                for orden, espera in self._pasos(token):
                    with self._cv:
                        if self._cancelada(generacion):
                            break
                    # Solo este hilo escribe: una parada espera al envío en curso.
                    if orden.startswith("DI:"):
                        decir(orden[3:])
                    elif orden != "ESPERA":
                        self.enlace.enviar(orden)
                    with self._cv:
                        if self._cv.wait_for(lambda: self._cancelada(generacion), timeout=espera):
                            break
            except Exception as exc:
                with self._cv:
                    self._error = str(exc)
                    # Preservar una parada solicitada durante el envío fallido.
                    if generacion == self._generacion:
                        self._pendientes.clear()
                        self._generacion += 1
                print(f"   ⚠ Error enviando a Bittle; secuencia cancelada: {exc}")
            finally:
                with self._cv:
                    self._activa = False
                    self._actual = None
                    self._cv.notify_all()

    def estado(self):
        with self._cv:
            return {"actual": self._actual,
                    "pendientes": [descripcion for _, descripcion in self._pendientes],
                    "error": self._error}

    def esperar_vacia(self, timeout=None):
        with self._cv:
            return self._cv.wait_for(lambda: not self._pendientes and not self._activa, timeout)

    def cerrar(self):
        with self._cv:
            self._cerrada = True
            self._pendientes.clear()
            self._cv.notify_all()
        self._hilo.join()

# Bluetooth LE: UART de Nordic (BiBoard / Bittle X) y módulo JDY-23 (NyBoard).
BLE_ESCRITURA = ["6e400002-b5a3-f393-e0a9-e50e24dcca9e", "0000ffe1-0000-1000-8000-00805f9b34fb"]
BLE_NOMBRES = ("bittle", "petoi", "biboard", "nybble", "jdy", "opencat")


def normalizar(texto):
    texto = unicodedata.normalize("NFD", texto.replace("﻿", "").lower())
    return " ".join("".join(c for c in texto if unicodedata.category(c) != "Mn").split())


def buscar_comando(texto):
    """Compatibilidad: devuelve la primera acción de una frase válida."""
    comandos = buscar_comandos(texto)
    return comandos[0] if comandos else None


def buscar_comandos(texto):
    """Lee acciones en orden, sin duplicar alias solapados; parada prioritaria."""
    palabras = re.findall(r"\w+", normalizar(texto))
    if set(palabras) & {"para", "quieto", "alto", "stop"}:
        return [COMANDOS["para"]]
    frases = sorted(COMANDOS, key=lambda frase: len(frase.split()), reverse=True)
    conectores = {"y", "luego", "despues", "primero", "entonces"}
    comandos, i = [], 0
    while i < len(palabras):
        for frase in frases:
            partes = frase.split()
            if palabras[i:i + len(partes)] == partes:
                comandos.append(COMANDOS[frase])
                i += len(partes)
                break
        else:
            if palabras[i] not in conectores:
                return []  # No ejecutar fragmentos de frases desconocidas o negadas.
            i += 1
    return comandos


# ---------------------------------------------------------------- transportes
class EnlaceSimulado:
    def enviar(self, token):
        print(f"   [SIMULADO] se enviaría: {token!r}")

    def cerrar(self):
        pass


class EnlaceSerie:
    def __init__(self, puerto, baudios):
        self.puerto, self.baudios, self.s = puerto, baudios, None
        self._abrir()

    def _abrir(self):
        import serial
        print(f"Conectando a {self.puerto} a {self.baudios} baudios...")
        self.s = serial.Serial(self.puerto, self.baudios, timeout=1, write_timeout=2)
        # Al abrir el puerto la placa se reinicia: esperar a que diga "Ready!".
        recibido, limite = "", time.monotonic() + 10
        while time.monotonic() < limite and "Ready" not in recibido:
            recibido += self.s.read(self.s.in_waiting or 1).decode("ascii", "ignore")
        self.s.reset_input_buffer()
        print("Conectado. Bittle listo." if "Ready" in recibido else "Conectado (sin confirmación de arranque).")

    def _reconectar(self):
        print("   🔌 Se perdió la conexión con Bittle. Reconectando... "
              "(si se repite, carga la batería)")
        try:
            self.s.close()
        except Exception:
            pass
        self.s = None
        self._abrir()

    def enviar(self, token):
        try:
            if self.s is None:
                self._reconectar()
            self._escribir(token)
        except Exception:
            if token.startswith("i"):
                self.s = None  # a mitad de coreografía no se reintenta; la próxima orden reconecta
                raise
            self._reconectar()  # una vez; si falla, el error llega al usuario
            self._escribir(token)

    def _escribir(self, token):
        self.s.write((token + "\n").encode("ascii"))
        self.s.flush()
        if token.startswith("i"):  # movimientos rápidos encadenados: no esperar ni imprimir
            self.s.reset_input_buffer()
            return
        time.sleep(0.1)
        if self.s.in_waiting:
            resp = self.s.read(self.s.in_waiting).decode("ascii", "replace").strip()
            if resp:
                print(f"   Bittle: {resp}")

    def cerrar(self):
        if self.s is not None:
            self.s.close()


class EnlaceBLE:
    """Ejecuta bleak en un hilo propio para poder usarlo desde el bucle de voz."""

    def __init__(self, nombre=None, direccion=None):
        from bleak import BleakClient, BleakScanner
        self.loop = asyncio.new_event_loop()
        threading.Thread(target=self.loop.run_forever, daemon=True).start()

        async def conectar():
            if direccion:
                dispositivo = direccion
            else:
                print("Buscando Bittle por Bluetooth LE (10 s)...")
                encontrados = await BleakScanner.discover(timeout=10)
                claves = (nombre.lower(),) if nombre else BLE_NOMBRES
                candidatos = [d for d in encontrados if d.name and any(k in d.name.lower() for k in claves)]
                if not candidatos:
                    vistos = ", ".join(sorted({d.name for d in encontrados if d.name})) or "ninguno"
                    raise RuntimeError(f"No encuentro a Bittle. Dispositivos BLE vistos: {vistos}")
                dispositivo = candidatos[0]
                print(f"Encontrado: {dispositivo.name} ({dispositivo.address})")
            cliente = BleakClient(dispositivo)
            await cliente.connect()
            caracteristica = None
            for servicio in cliente.services:
                for c in servicio.characteristics:
                    if c.uuid.lower() in BLE_ESCRITURA:
                        caracteristica = c
            if caracteristica is None:  # cualquier característica escribible
                for servicio in cliente.services:
                    for c in servicio.characteristics:
                        if {"write", "write-without-response"} & set(c.properties):
                            caracteristica = caracteristica or c
            if caracteristica is None:
                raise RuntimeError("Conectado, pero no hay característica escribible")
            return cliente, caracteristica

        self.cliente, self.car = self._ejecutar(conectar(), 40)
        print("Conectado por BLE.")

    def _ejecutar(self, corrutina, timeout=10):
        return asyncio.run_coroutine_threadsafe(corrutina, self.loop).result(timeout)

    def enviar(self, token):
        con_respuesta = "write" in self.car.properties
        datos = (token + "\n").encode("ascii")
        for i in range(0, len(datos), 20):  # BLE solo admite ~20 bytes por envío
            self._ejecutar(self.cliente.write_gatt_char(self.car, datos[i:i + 20],
                                                        response=con_respuesta))

    def cerrar(self):
        try:
            self._ejecutar(self.cliente.disconnect())
        finally:
            self.loop.call_soon_threadsafe(self.loop.stop)


# ---------------------------------------------------------------- entrada
def escuchar_microfono(ruta_modelo, dispositivo):
    """Generador de frases reconocidas por el micrófono (escucha continua)."""
    import sounddevice as sd
    from vosk import KaldiRecognizer, Model, SetLogLevel

    if not Path(ruta_modelo).is_dir():
        sys.exit(f"No encuentro el modelo Vosk en {ruta_modelo}\n"
                 "Descárgalo de https://alphacephei.com/vosk/models/vosk-model-small-es-0.42.zip "
                 "y descomprímelo en la carpeta 'modelos'.")
    SetLogLevel(-1)
    modelo = Model(str(ruta_modelo))
    rec = KaldiRecognizer(modelo, 16000, json.dumps(GRAMATICA, ensure_ascii=False))
    audio = queue.Queue()

    def callback(datos, frames, tiempo, estado):
        audio.put(bytes(datos))

    with sd.RawInputStream(samplerate=16000, blocksize=8000, device=dispositivo,
                           dtype="int16", channels=1, callback=callback):
        print("\n🎤 Escuchando... habla cuando quieras (Ctrl+C para salir)\n")
        while True:
            if rec.AcceptWaveform(audio.get()):
                texto = json.loads(rec.Result()).get("text", "").strip()
                if texto:
                    yield texto


def escuchar_teclado():
    print("\n⌨  Modo texto: escribe la orden y pulsa Enter (Ctrl+C para salir)\n")
    while True:
        yield input("> ")


def listar():
    import serial.tools.list_ports
    print("Puertos COM:")
    for p in serial.tools.list_ports.comports():
        print(f"  {p.device}: {p.description}")
    from bleak import BleakScanner  # antes de sounddevice: este cambia el modo COM del hilo
    print("\nDispositivos Bluetooth LE cercanos (5 s):")
    for d in asyncio.run(BleakScanner.discover(timeout=5)):
        print(f"  {d.address}  {d.name or '(sin nombre)'}")
    import sounddevice as sd
    print("\nMicrófonos:")
    for i, d in enumerate(sd.query_devices()):
        if d["max_input_channels"] > 0:
            print(f"  [{i}] {d['name']}")


def main():
    ap = argparse.ArgumentParser(description="Controla Bittle con la voz")
    destino = ap.add_mutually_exclusive_group()
    destino.add_argument("--puerto", help="puerto COM de Bittle, p. ej. COM7")
    destino.add_argument("--ble", action="store_true", help="conectar por Bluetooth LE")
    destino.add_argument("--simulado", action="store_true", help="no envía nada, solo lo muestra")
    destino.add_argument("--listar", action="store_true", help="lista puertos, micrófonos y BLE")
    ap.add_argument("--baudios", type=int, default=115200)
    ap.add_argument("--nombre-ble", help="parte del nombre BLE de tu Bittle")
    ap.add_argument("--direccion-ble", help="dirección MAC BLE de tu Bittle")
    ap.add_argument("--modelo", default=str(MODELO_POR_DEFECTO), help="carpeta del modelo Vosk")
    ap.add_argument("--microfono", type=int, default=None, help="índice del micrófono (ver --listar)")
    ap.add_argument("--texto", action="store_true", help="escribir órdenes en vez de hablar")
    ap.add_argument("--segundos-accion", type=float, default=3.0,
                    help="espera por acción (defecto: 3 s; algunas habilidades tienen un mínimo mayor)")
    args = ap.parse_args()
    if not math.isfinite(args.segundos_accion) or args.segundos_accion <= 0:
        ap.error("--segundos-accion debe ser positivo y finito")

    if args.listar:
        return listar()
    if args.puerto:
        try:
            enlace = EnlaceSerie(args.puerto, args.baudios)
        except Exception as exc:
            sys.exit(f"No puedo abrir {args.puerto}: {exc}\n"
                     "Comprueba que Bittle está encendido, con batería y cerca del PC, "
                     "y que ningún otro programa (app Petoi, otra terminal) usa ese puerto.")
    elif args.ble:
        enlace = EnlaceBLE(args.nombre_ble, args.direccion_ble)
    else:
        if not args.simulado:
            print("Sin --puerto ni --ble: arranco en modo SIMULADO.")
        enlace = EnlaceSimulado()

    print("Órdenes: siéntate, de pie/levántate, camina/adelante, corre, atrás, izquierda, "
          "derecha, saluda/hola, flexiones, estira, descansa, BAILA, PARA/quieto")
    print("Puedes encadenar órdenes con 'y después'. PARA cancela toda la cola.")
    cola = ColaAcciones(enlace, args.segundos_accion)
    entrada = escuchar_teclado() if args.texto else escuchar_microfono(args.modelo, args.microfono)
    try:
        for texto in entrada:
            comandos = buscar_comandos(texto)
            if not comandos:
                print(f"🗣  «{texto}» -> no es una orden")
                continue
            print(f"🗣  «{texto}» -> " + " → ".join(d for _, d in comandos))
            cola.agregar(comandos)
    except (KeyboardInterrupt, EOFError):
        print("\nSaliendo...")
    finally:
        try:
            cola.cerrar()
            enlace.enviar("krest")  # dejarlo en reposo al salir
        except Exception:
            pass
        enlace.cerrar()


if __name__ == "__main__":
    main()
