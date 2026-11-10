# VOICE-BITTLE — control por voz del Petoi Bittle (INGENIA Robótica · ARGOS)

Software del reto Bittle: la voz se reconoce, se valida y, solo si es una orden permitida y el robot puede moverse, se envía `ksit`/`kup` por Bluetooth. Todo se prueba **sin robot ni micrófono**.

👉 **¿Primera vez? Lee [`GUIA.md`](GUIA.md)** (cómo funciona, cómo actualizarlo y cómo usar Git).

## Dónde está cada cosa (una sola copia de cada cosa)
| Qué | Dónde |
|---|---|
| H1 vigente (requisitos y escenarios) | `docs/h1/H1_v0.2.pdf` |
| Spec, plan, tareas, investigación, contratos (Spec Kit) | `specs/001-voice-bittle-spec/` |
| Casos de prueba (paso 5) | `docs/H3/casos_de_prueba.md` |
| Código | `src/` |
| Pruebas | `tests/` |
| Resultados y trazabilidad (generados) | `evidencias/` |
| Configuración de Spec Kit | `.specify/`, `.github/skills/` |

> Estado: `specs/` se escribió a partir del H1 v0.1; **falta actualizarlo al H1 v0.2** (consultas «historial»/«estado», español e inglés, escenarios ESC-01 a ESC-13). El código y los casos de prueba ya siguen el H1 v0.2.

## Comandos
```bash
python3 -m pip install pytest
python3 -m pytest -q                  # 56 pruebas
python3 tools/generar_evidencias.py   # regenera evidencias/ y avisa de huecos
```
