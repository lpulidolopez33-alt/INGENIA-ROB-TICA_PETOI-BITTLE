"""Adaptador Vosk (RD-02, RR-03). NO cubierto por las pruebas automáticas (necesita micrófono
y modelos): se valida en T005/T010 y en el ensayo de integración (OPEN-03).

Los modelos se cargan desde rutas LOCALES; nunca se descargan en ejecución (RR-03).
Confianza de la orden = media de la confianza por palabra que devuelve Vosk con SetWords(True).
"""
import json
import time
from datetime import datetime

from voz import MicrofonoNoDisponible, ModeloNoDisponible, Resultado


class VoskReconocedor:
    def __init__(self, rutas_modelos: dict, frases_por_idioma: dict, sample_rate: int = 16000):
        self.rutas = rutas_modelos              # {"es": "modelos/vosk-es", "en": "modelos/vosk-en"}
        self.frases = frases_por_idioma         # {"es": ["siéntate", ...], ...} para la gramática
        self.sample_rate = sample_rate
        self._modelo = None
        self._idioma = None

    def cargar_modelo(self, idioma: str) -> None:
        try:
            from vosk import Model
            self._modelo = Model(self.rutas[idioma])
        except Exception as e:  # modelo ausente o corrupto
            raise ModeloNoDisponible(idioma) from e
        self._idioma = idioma

    def disponible(self) -> bool:
        try:
            import sounddevice as sd
            return sd.query_devices(kind="input") is not None
        except Exception:
            return False

    def escuchar(self, timeout: float) -> Resultado | None:
        import sounddevice as sd
        from vosk import KaldiRecognizer
        if not self.disponible():
            raise MicrofonoNoDisponible()
        gramatica = json.dumps(self.frases[self._idioma] + ["[unk]"], ensure_ascii=False)
        rec = KaldiRecognizer(self._modelo, self.sample_rate, gramatica)
        rec.SetWords(True)
        inicio = datetime.now()
        limite = time.monotonic() + timeout
        with sd.RawInputStream(samplerate=self.sample_rate, blocksize=4000,
                               dtype="int16", channels=1) as flujo:
            while time.monotonic() < limite:
                datos, _ = flujo.read(4000)
                if rec.AcceptWaveform(bytes(datos)):
                    res = json.loads(rec.Result())
                    palabras = res.get("result", [])
                    if res.get("text") and palabras:
                        conf = sum(p["conf"] for p in palabras) / len(palabras)
                        return Resultado(res["text"], conf, inicio, datetime.now())
        return None
