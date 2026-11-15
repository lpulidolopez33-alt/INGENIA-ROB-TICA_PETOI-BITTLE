# Entorno y configuración constatados

Revisión 2026-11-12. Windows, Python 3.12.10 de 64 bits en las ejecuciones previas.
La herramienta de evidencias actual registra la versión de Python y las dependencias de cada nueva
prueba, omitiendo rutas personales; no se confunde con el `.venv` del operador.

- Uso: requirements-bittle.txt (vosk 0.3.45, sounddevice 0.5.6, pyserial 3.5, bleak 3.1.0).
- Pruebas: requirements.txt (dependencias de uso anteriores y pytest 9.2.0).

- Panel: biblioteca estándar HTTP, sin framework ni compilación de recursos.
- Modelo: vosk-model-small-es-0.42, instalado localmente en `modelos/`. Se comprobó
  su carga con Vosk y la creación del reconocedor a 16 kHz, sin abrir micrófono.
  No se incluye en el ZIP: el destinatario debe descargarlo según GUIA.md.
  Inglés no está soportado por el vocabulario actual.
- Hardware declarado: Bittle normal; captura identifica Petoi-30AD, COM6 saliente.
- Firmware N_240517: afirmación del ZIP recibido, no lectura verificada del equipo.
- Configuración serie implementada: 115200 y LF; no universalizar a otros módulos.

Las versiones transitivas del entorno de pruebas se registran al generar evidencias;
no son un lockfile portable ni justifican la antigua afirmación de Python 3.14 probado.
