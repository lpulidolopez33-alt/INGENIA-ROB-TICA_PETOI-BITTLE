# VOICE-BITTLE — ARGOS

Aplicación Python para cuatro intenciones ES/EN: sentarse (`ksit`), ponerse de
pie (`kup`), historial y estado. Solo las dos primeras generan escrituras.

**Estado H3:** consola funcional con simuladores y adaptadores Vosk/serie
probados con dobles. **Modo físico bloqueado**; ningún ensayo con Bittle realizado.
H1 vigente: `docs/h1/H1_v0.2.pdf` (borrador, 13 escenarios, 7 necesidades,
34 requisitos y OPEN-01…15). No se modifica el H1 ni se aprueban sus parámetros.

## Inicio rápido (PowerShell, desde esta carpeta)

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe voice_bittle.py --demo
.\.venv\Scripts\python.exe voice_bittle.py
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe tools/generar_evidencias.py
```

No hace falta activar el entorno ni cambiar la política de ejecución de PowerShell.
En consola: `/activar`, escribir «siéntate», `/fin`, «historial», «estado», `/salir`.
Escribir texto en modo fake **no es reconocimiento de audio**.

- [Guía práctica Windows](GUIA.md): instalación, modelos, voz real sobre enlace simulado y comandos.
- [Informe de desarrollo](docs/H3/informe_desarrollo.md): cambios, resultados y límites.
- [Preprueba física](docs/H3/preprueba_fisica.md): condiciones pendientes antes de habilitar hardware.
- [Casos](docs/H3/casos_de_prueba.md) y [resultados generados](evidencias/resultados_H3.md).
- [Especificación](specs/001-voice-bittle-spec/spec.md), plan y tareas actualizados;
  T001–T050 históricos preservados sin copiar la renumeración de otra rama.

`--modo fisico` informa bloqueos y sale con código 2 sin abrir puertos.
Para audio real, instalar `requirements-voz.txt` y modelos locales siguiendo GUIA.md.
No añadir movimientos editando el JSON: la autorización de acciones es independiente.

Entrega integral: empezar por [PROYECTO.md](PROYECTO.md). Resultados de la revisión final y checklist en [ENTREGA_COMPANEROS.md](docs/H3/ENTREGA_COMPANEROS.md).
