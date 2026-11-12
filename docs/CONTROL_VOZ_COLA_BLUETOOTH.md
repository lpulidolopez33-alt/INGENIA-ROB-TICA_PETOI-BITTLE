# Control por micrófono y cola FIFO del Petoi Bittle

Esta propuesta es una ampliación **experimental** de H1 v0.2: el proyecto anterior rechazaba movimientos mientras había otro activo. La nueva cola es **opcional y separada**, no modifica `src/app/controlador.py` ni cambia la especificación aprobada. El equipo/profesor debe revisar el cambio de alcance antes de ensayar.

## Arquitectura

Micrófono del ordenador → Vosk (español, sin Internet) → validador cerrado → cola FIFO acotada → adaptador pyserial → puerto Bluetooth serie → Bittle.

El reconocimiento y la cola se ejecutan en el **ordenador local**. GitHub se usa para alojar y revisar el código, **no es necesario para dar órdenes en tiempo real**, y el chat de ChatGPT no recibe audio del micrófono de este programa. La conexión de GitHub Issues de la PR #4 es una vía independiente.

## 1. Requisitos

- Petoi Bittle y módulo Bluetooth serie compatible, **emparejados** con el ordenador; identificar el puerto **saliente** (Windows: COMx; macOS: /dev/cu.*). La compatibilidad exacta y la velocidad serie dependen de la placa y firmware.
- Python, `pyserial==3.5`, `vosk`, `sounddevice`, `pytest` y un micrófono que el ordenador reconozca.
- Modelo **español** de Vosk descargado y descomprimido en una carpeta local. Modelos oficiales: https://alphacephei.com/vosk/models. No se descarga al ejecutar el programa.
- Espacio despejado, superficie seca y estable, persona supervisando y forma de apagar/desenergizar el robot. No confiar en una orden verbal como parada de emergencia.

Ejecutar en la raíz del repositorio:

```bash
python -m pip install -r requirements.txt
python -m pytest -q tests/unit/test_cola_voz.py
```

## 2. Probar el software SIN robot

Primero introducir frases con el teclado para comprobar la lógica (sin Bluetooth):

```bash
python tools/voz_bittle_cola.py --dry-run --keyboard --interval 5
```

Luego **con el micrófono, pero sin robot**:

```bash
python tools/voz_bittle_cola.py --dry-run --model modelos/vosk-es --interval 5
```

La ruta `modelos/vosk-es` es un ejemplo: reemplazarla por la carpeta real que contiene los archivos del modelo Vosk.

## 3. Prueba física supervisada

Emparejar Bittle, identificar el puerto correcto y **verificar primero la documentación del firmware**: `ksit` y `kup`, baud rate y terminador de comando pueden depender del modelo. El token `kup` sigue pendiente de confirmar en la documentación actual del proyecto.

Con aprobación del responsable del ensayo y robot situado en una superficie segura:

```powershell
python tools/voz_bittle_cola.py --live --arm --port COM7 --model modelos/vosk-es --interval 8
```

Sustituir `COM7` por el puerto Bluetooth saliente y ajustar `--interval` únicamente tras ensayos físicos. El valor 8 es un intervalo de precaución sugerido, **no** una duración validada ni una señal de fin del robot. Se puede añadir `--baud 115200` o `--terminator lf` solo si el firmware lo requiere.

## 4. Frases aceptadas

- `siéntate` → token `ksit`
- `ponte de pie` → token `kup`
- `siéntate y luego ponte de pie` → añade dos movimientos en ese orden
- `pausa la cola` → no despacha nuevos movimientos tras el que está en curso
- `reanuda la cola` → continúa los movimientos pendientes si el enlace sigue activo
- `vacía la cola` / `cancela la cola` → descarta los movimientos **no enviados**
- Puede acumular nuevas instrucciones individuales mientras espera entre envíos. Límite: **8 pendientes** por defecto (configurable `--capacity`). Una frase admite como máximo 4 órdenes, aunque la gramática Vosk de demostración está optimizada para órdenes simples y parejas.

Se rechazan frases no recogidas, órdenes peligrosas o desconocidas y reconocimiento bajo el umbral de confianza (por defecto 0,80). No se transmite texto libre al firmware. La aplicación muestra si un token **fue enviado**, pero **no puede confirmar la postura física**.

## 5. Comportamiento de la cola

- Cola FIFO: primero en entrar, primero en salir.
- Tras cada envío espera un intervalo configurable antes de transmitir el siguiente; el intervalo **no confirma** que el movimiento haya finalizado.
- El micrófono sigue operativo mientras la cola trabaja, pero la detección no es instantánea: cada ventana Vosk de escucha tiene hasta 5 s.
- `pausa` y `vacía` afectan a **órdenes futuras**. **No detienen** el movimiento ya enviado. `Ctrl+C` cierra el puente y descarta pendientes, pero tampoco detiene necesariamente al robot.
- Error de escritura o enlace Bluetooth perdido: se descartan las órdenes pendientes, no hay reconexión/reintento automático y se exige reiniciar tras revisar el robot.
- Cola en memoria: desaparece al detener el programa. No hay persistencia ni repetición de movimientos al volver a arrancar.

## 6. Límites conocidos y siguientes pasos

**No se ha probado con el hardware real.** Antes de uso físico es obligatorio validar emparejamiento, protocolo, terminador, velocidad, capacidad de completar cada acción en los intervalos configurados, respuesta a desconexiones y ruidos ambientales. Para secuencias fiables, el siguiente paso sería incorporar acuse de ejecución/estado de firmware o validación física del final del movimiento, no suponerlo por tiempo.

La opción `--keyboard` está destinada a ensayos o control manual, no al reconocimiento por micrófono. Conservar `--dry-run` hasta terminar las validaciones.
