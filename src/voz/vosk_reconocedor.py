"""Vosk local; confianza mínima por palabra experimental (OPEN-03/04).
El fin acústico se estima con el último segmento de palabra sobre el reloj de
captura. No es una medición calibrada ni evidencia de cumplimiento de RR-02.
"""
import json
import time
from uuid import uuid4
from datetime import datetime, timedelta
from pathlib import Path
from voz import MicrofonoNoDisponible, ModeloNoDisponible, Resultado
from seguridad import numero_valido


class VoskReconocedor:
    def __init__(self, rutas_modelos, frases_por_idioma, sample_rate=16000, dispositivo=None):
        self.rutas = rutas_modelos
        self.frases = frases_por_idioma
        self.sample_rate = sample_rate
        self.dispositivo = dispositivo
        self._modelo = None
        self._idioma = None

    def cargar_modelo(self, idioma):
        try:
            from vosk import Model
            if not Path(self.rutas[idioma]).is_dir():
                raise FileNotFoundError(self.rutas[idioma])
            modelo = Model(self.rutas[idioma])
        except Exception as exc:
            raise ModeloNoDisponible(idioma) from exc
        self._modelo, self._idioma = modelo, idioma

    def disponible(self):
        try:
            import sounddevice as sd
            return sd.query_devices(self.dispositivo, kind="input")["max_input_channels"] > 0
        except Exception:
            return False

    def escuchar(self, timeout):
        if self._modelo is None:
            raise ModeloNoDisponible("Cargar un modelo antes de escuchar")
        if not self.disponible():
            raise MicrofonoNoDisponible()
        try:
            import sounddevice as sd
            from vosk import KaldiRecognizer
            # Decodificación abierta: no forzar ruido hacia un vocabulario de cuatro órdenes.
            # La autorización sigue siendo estricta en Traductor.
            rec = KaldiRecognizer(self._modelo, self.sample_rate)
            captura_id = uuid4().hex
            hay_senal = False
            rec.SetWords(True)
            with sd.RawInputStream(samplerate=self.sample_rate, blocksize=4000,
                                   device=self.dispositivo, dtype="int16", channels=1) as flujo:
                inicio = datetime.now()
                inicio_mono = time.monotonic()
                limite = inicio_mono + timeout
                while time.monotonic() < limite:
                    datos, overflow = flujo.read(4000)
                    if overflow:
                        raise MicrofonoNoDisponible("Desbordamiento de audio; captura descartada")
                    datos = bytes(datos)
                    hay_senal = hay_senal or any(datos)
                    if rec.AcceptWaveform(datos):
                        res = json.loads(rec.Result())
                        if not hay_senal:
                            return None
                        texto, palabras = res.get("text", ""), res.get("result", [])
                        if not isinstance(texto, str):
                            raise ValueError("Texto Vosk inválido")
                        if not texto:
                            continue
                        if not palabras or any(not numero_valido(p.get("conf")) for p in palabras):
                            return Resultado(texto, None, inicio, datetime.now())
                        if " ".join(p.get("word", "") for p in palabras).strip() != texto.strip():
                            return Resultado(texto, None, inicio, datetime.now())
                        conf = min(p["conf"] for p in palabras)
                        fin = palabras[-1].get("end")
                        transcurrido = time.monotonic() - inicio_mono
                        if not numero_valido(fin, 0, transcurrido):
                            return Resultado(texto, None, inicio, datetime.now())
                        return Resultado(texto, conf, inicio, inicio + timedelta(seconds=fin),
                                         inicio_mono + fin, "estimado_vosk", captura_id, time.monotonic())
            return None
        except MicrofonoNoDisponible:
            raise
        except Exception as exc:
            raise MicrofonoNoDisponible("Fallo de captura o reconocimiento; no se conserva audio") from exc
