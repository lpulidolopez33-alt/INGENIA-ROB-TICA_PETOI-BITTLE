"""Carga Vosk y decodifica PCM sintético; nunca abre micrófono ni puertos."""
import argparse
import hashlib
import json
import math
import random
from array import array
from pathlib import Path
from importlib.metadata import version


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--modelo", required=True)
    parser.add_argument("--salida", default="evidencias/audio_sintetico.json")
    args = parser.parse_args()
    from vosk import Model, KaldiRecognizer
    ruta = Path(args.modelo)
    model = Model(str(ruta))
    rng = random.Random(42)
    rate, n = 16000, 80000
    senales = {"silencio_digital": [0] * n,
               "ruido_uniforme_semilla42": [rng.randint(-300, 300) for _ in range(n)],
               "tono_440Hz": [int(4000 * math.sin(2 * math.pi * 440 * i / rate)) for i in range(n)]}
    resultados = []
    for nombre, muestras in senales.items():
        pcm = array("h", muestras).tobytes()
        rec = KaldiRecognizer(model, rate)
        rec.SetWords(True)
        segmentos = []
        for i in range(0, len(pcm), 8000):
            if rec.AcceptWaveform(pcm[i:i+8000]): segmentos.append(json.loads(rec.Result()))
        segmentos.append(json.loads(rec.FinalResult()))
        resultados.append({"senal": nombre, "segundos": 5, "pcm_sha256": hashlib.sha256(pcm).hexdigest(),
                           "segmentos": segmentos})
    informe = {"modelo": ruta.name, "vosk": version("vosk"), "carga": "correcta",
               "metodo": "Vosk real con PCM sintético, sin micrófono, sin voz humana, sin robot",
               "modelo_sha256": {p.relative_to(ruta).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                                 for p in sorted(ruta.rglob("*")) if p.is_file()},
               "resultados": resultados,
               "limite": "No reproduce el audio del incidente ni valida rechazo de todo ruido ni precisión con voz"}
    Path(args.salida).write_text(json.dumps(informe, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"carga": "correcta", "resultados": resultados}, ensure_ascii=False))


if __name__ == "__main__": main()
