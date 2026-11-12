"""Adaptador Vosk cancelable para el panel: reconoce en bloques de 250 ms.

Solo abre la entrada de audio mientras el micro está activado.
"""
from __future__ import annotations
from datetime import datetime
import json
from time import monotonic

from voz import MicrofonoNoDisponible, Resultado
from voz.vosk_reconocedor import VoskReconocedor


class VoskCancelable(VoskReconocedor):
    def escuchar(self, timeout: float, cancelar=None) -> Resultado | None:
        if cancelar is not None and cancelar.is_set():
            return None
        if not self.disponible():
            raise MicrofonoNoDisponible("No se detectó micrófono")
        try:
            import sounddevice as sd
            from vosk import KaldiRecognizer
            gramatica = json.dumps(self.frases[self._idioma] + ["[unk]"], ensure_ascii=False)
            rec = KaldiRecognizer(self._modelo, self.sample_rate, gramatica)
            rec.SetWords(True)
            inicio = datetime.now()
            limite = monotonic() + timeout
            # 4000 muestras = 250 ms a 16000 Hz.
            with sd.RawInputStream(samplerate=self.sample_rate, blocksize=4000,
                                   dtype="int16", channels=1) as flujo:
                while monotonic() < limite:
                    if cancelar is not None and cancelar.is_set():
                        return None
                    datos, _overflow = flujo.read(4000)
                    if cancelar is not None and cancelar.is_set():
                        return None
                    if rec.AcceptWaveform(bytes(datos)):
                        res = json.loads(rec.Result())
                        palabras = res.get("result", [])
                        if res.get("text") and palabras:
                            conf = sum(p.get("conf", 0.0) for p in palabras) / len(palabras)
                            return Resultado(res["text"], conf, inicio, datetime.now())
            # Al acabar la ventana, recuperar la frase final de Vosk (si existe).
            if cancelar is not None and cancelar.is_set():
                return None
            res = json.loads(rec.FinalResult())
            palabras = res.get("result", [])
            if res.get("text") and palabras:
                conf = sum(p.get("conf", 0.0) for p in palabras) / len(palabras)
                return Resultado(res["text"], conf, inicio, datetime.now())
            return None
        except (OSError, ValueError, RuntimeError) as exc:
            raise MicrofonoNoDisponible(str(exc)) from exc
