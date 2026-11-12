# VOICE-BITTLE — ARGOS

## Panel web local

Abre **INICIAR_PANEL.bat** para conectar desde una interfaz HTML, ver las
órdenes, activar/desactivar la escucha y consultar la cola. Inicia desconectado
y con el micrófono apagado. Instrucciones: [PANEL_WEB.md](PANEL_WEB.md).

## 🎤 Control por voz del robot real: `bittle_voz.py`

Programa que hace que el perro robot **Petoi Bittle** obedezca órdenes habladas en
español. Escucha el micrófono continuamente, reconoce la frase con **Vosk** (sin
Internet) y envía el comando a Bittle por **Bluetooth** (puerto COM o Bluetooth LE).
La versión recibida indicaba pruebas con Bittle real (firmware `N_240517`).
La nueva cola está probada en software; sus tiempos físicos y el reconocimiento
de secuencias por voz están pendientes de validación.

**Secuencias:** di «siéntate y después ponte de pie» o añade órdenes mientras
ejecuta otra. Consulta [uso y límites de la cola](SECUENCIAS.md).
Los PDF y la presentación existentes son anteriores a esta actualización.

| Material | Archivo |
|---|---|
| Programa | [bittle_voz.py](bittle_voz.py) |
| Guía paso a paso para principiantes (VS Code) | [GUIA_PASO_A_PASO.md](GUIA_PASO_A_PASO.md) · [PDF](GUIA_PASO_A_PASO.pdf) |
| Presentación de clase | [Presentacion_Bittle_por_voz.pptx](Presentacion_Bittle_por_voz.pptx) · [PDF](Presentacion_Bittle_por_voz.pdf) |

### Inicio rápido (PowerShell, desde esta carpeta)

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-bittle.txt
```

Descargar el modelo de voz español (~39 MB, no se incluye en el repositorio) desde
<https://alphacephei.com/vosk/models/vosk-model-small-es-0.42.zip> y descomprimirlo en
`modelos/vosk-model-small-es-0.42`.

```powershell
.\.venv\Scripts\python.exe bittle_voz.py --simulado        # sin robot: muestra lo que enviaría
.\.venv\Scripts\python.exe bittle_voz.py --listar          # puertos COM, micrófonos y Bluetooth LE
.\.venv\Scripts\python.exe bittle_voz.py --puerto COM7     # Bittle por Bluetooth clásico
.\.venv\Scripts\python.exe bittle_voz.py --ble             # Bittle por Bluetooth LE
```

**Órdenes:** siéntate, de pie/levántate, camina/adelante, corre, atrás, izquierda,
derecha, saluda/hola, flexiones, estira, descansa/duerme, **baila** (coreografía casera),
**cristiano** (celebración «SIUUU» casera) y **para/quieto/alto**, que cancelan
la cola y solicitan equilibrio. La parada física depende del reconocimiento y del enlace.
Ctrl+C cancela la cola e intenta dejar a Bittle en reposo antes de salir.

---

## Proyecto original ARGOS (H3, solo simulación)

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
