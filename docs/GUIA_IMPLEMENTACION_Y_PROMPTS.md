# Bittle por voz: implementación, pasos y acciones

Guía del estado del repositorio `main` en el commit `4ff90b729ca9668332a8e46645c6e2243d603781`, revisado el 12 de noviembre de 2026. Describe el código disponible y los pasos para reproducirlo. Las pruebas de software no acreditan que una acción se haya completado en el robot físico.

## 1. Qué se ha construido

El ordenador recibe texto o audio en español, lo convierte en acciones reconocidas y las pone en una cola. Un ejecutor envía las órdenes, una detrás de otra, a un enlace simulado, un puerto serie Bluetooth o BLE. Vosk realiza el reconocimiento local de voz; el modelo debe instalarse por separado. La ruta principal de esta guía es `bittle_voz.py`.

**Hay dos aplicaciones distintas.** `voice_bittle.py` y `src/` contienen el proyecto ARGOS H3, con un vocabulario y unos adaptadores propios; su modo físico está bloqueado. `bittle_voz.py` es la ruta ampliada con baile, flexiones y cola. No se deben atribuir automáticamente a una las garantías o funciones de la otra. El prototipo `tools/panel_bittle.py` también usa la ruta H3 y no es el panel `bittle_web.py`.

El servidor `bittle_web.py` usa la ruta ampliada, pero **falta `web/index.html` en el commit revisado**. Por eso arrancar el servidor desde este repositorio no permite cargar su página: solicita ese archivo y devuelve un error. Hay que recuperarlo antes de usar el panel; la consola descrita abajo es una alternativa. El servidor admite simulación o serie, mientras que BLE está disponible en la consola.

### Evolución registrada

El historial de Git permite identificar estas etapas, aunque no permite reconstruir todos los pasos ni los mensajes originales:

1. **26 de octubre:** requisitos y planificación iniciales H1/H2.
2. **10 de noviembre:** desarrollo y evidencias de H3 con simulación.
3. **12 de noviembre:** prototipos de puente GitHub/Bluetooth, cola de voz local, secuencias mediante Issues y panel anterior; después se incorporó una entrega con `bittle_voz.py`, `bittle_web.py` y guías actualizadas.

La fecha de un commit refleja el registro Git, no demuestra por sí sola que se haya ensayado una función sobre el robot. El último commit revisado agrupa archivos y no detalla el orden de todas las decisiones.

## 2. Material y preparación

Para simulación por texto basta Python y los archivos del proyecto. Para voz se necesita micrófono, dependencias y modelo Vosk; para uso físico, además, un Bittle compatible, batería y un enlace verificado. Los ejemplos siguientes son para Windows PowerShell y se ejecutan desde la carpeta del repositorio.

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-bittle.txt
```

Descarga el modelo español [vosk-model-small-es-0.42](https://alphacephei.com/vosk/models/vosk-model-small-es-0.42.zip), descomprímelo y comprueba que la carpeta quede en `modelos/vosk-model-small-es-0.42`. El modelo no está incluido en Git. Se puede elegir otra carpeta con `--modelo RUTA`.

Enumera los dispositivos antes de elegir el puerto o el micrófono:

```powershell
.\.venv\Scripts\python.exe bittle_voz.py --listar
```

Para Bluetooth serie, usa el COM **saliente** que corresponda al robot; `COM7` es solo un ejemplo. No abras el mismo puerto con la aplicación Petoi y el programa al mismo tiempo. Con BLE hay que verificar la compatibilidad de la placa y sus características de escritura.

## 3. Primera prueba sin robot

```powershell
.\.venv\Scripts\python.exe bittle_voz.py --simulado --texto
```

Escribe una frase por línea y observa las órdenes que **se enviarían**:

```text
siéntate
flexiones
baila
siéntate y después ponte de pie y saluda
para
```

Espera a que termine una acción antes de valorar la siguiente. `para` tiene prioridad: cancela las pendientes y solicita equilibrio. Para terminar usa Ctrl+C; al cerrar, el programa intenta enviar `krest`, incluso en simulación. La salida simulada no demuestra movimiento real ni reconocimiento del micrófono.

Para probar reconocimiento con micrófono sin robot, ejecuta:

```powershell
.\.venv\Scripts\python.exe bittle_voz.py --simulado
```

Habla con las palabras admitidas. Comprueba la transcripción mostrada: un reconocimiento erróneo puede convertir la frase en otra orden. Esta ruta usa una gramática Vosk, pero no aplica el umbral de confianza de la aplicación H3.

## 4. Conexión con el robot

Tras comprobar las órdenes y la compatibilidad del firmware, realizar una primera prueba presencial, sobre superficie estable, con espacio libre y el interruptor físico accesible. Sustituye `COM7` por el puerto correcto:

```powershell
.\.venv\Scripts\python.exe bittle_voz.py --puerto COM7
```

Para escribir en lugar de hablar, añade `--texto`. Para BLE, la alternativa de consola es:

```powershell
.\.venv\Scripts\python.exe bittle_voz.py --ble
```

La búsqueda BLE puede elegir automáticamente un dispositivo por nombre y, si no encuentra los UUID previstos, recurrir a una característica escribible genérica. Usa `--nombre-ble` o `--direccion-ble` para precisar la selección y comprueba que corresponda a tu robot y firmware.

Empieza con una orden sencilla y verifica la respuesta real antes de probar desplazamientos o coreografías. Los tiempos son estimados, no hay señal de fin físico. Una escritura o reconexión en curso puede retrasar la parada; el enlace serie reintenta una vez algunas escrituras tras un fallo. Si se pierde el enlace no se garantiza la detención. `para` y Ctrl+C no sustituyen el interruptor físico; el intento de `krest` al salir también puede mover el robot.

## 5. Órdenes actuales

| Frase de ejemplo | Token o acción | Función prevista |
|---|---|---|
| siéntate | `ksit` | Sentarse |
| ponte de pie / levántate | `kup` | Ponerse de pie |
| camina / adelante | `kwkF` | Caminar hacia delante |
| corre | `ktrF` | Trotar hacia delante |
| atrás | `kbk` | Retroceder |
| izquierda / derecha | `kwkL` / `kwkR` | Girar |
| saluda / hola | `khi` | Saludar |
| flexiones | `kpu` | Solicitar la habilidad de flexiones del firmware |
| estira / estírate | `kstr` | Estirarse |
| descansa / duerme | `krest` | Solicitar descanso |
| baila / baile / bailar | `BAILE` | Ejecutar una coreografía definida en Python |
| cristiano / ronaldo / siu | `CRISTIANO` | Ejecutar una celebración definida en Python |
| para / quieto / alto / stop | `kbalance` | Cancelar pendientes y solicitar equilibrio |

Estos nombres describen la intención del código; la disponibilidad y el resultado físico de cada habilidad dependen de la placa, el firmware y la calibración. En particular, la cola y las coreografías necesitan validación física y de reconocimiento con micrófono; no se infiere de las pruebas simuladas.

## 6. Cómo funciona el código

### 6.1. Frase y traducción

`COMANDOS`, al comienzo de [`bittle_voz.py`](../bittle_voz.py), relaciona las frases normalizadas con una orden y una descripción. Fragmento literal:

```python
"flexiones": ("kpu", "flexiones"),
"baila": ("BAILE", "bailar (coreografía casera)"),
"baile": ("BAILE", "bailar (coreografía casera)"),
"bailar": ("BAILE", "bailar (coreografía casera)"),
```

`normalizar()` pasa a minúsculas y elimina tildes. `buscar_comandos()` identifica primero una palabra de parada; si aparece, devuelve únicamente la parada. Después busca las frases más largas primero y acepta conectores como `y`, `después`, `luego`, `primero` y `entonces`. Una palabra desconocida o una negación que llega al intérprete hace que se rechace la frase completa. Esto no garantiza detectar una negación que Vosk haya omitido al transcribir.

### 6.2. Cola y tiempos

`ColaAcciones` tiene un único hilo ejecutor y admite hasta 20 acciones pendientes. Una frase que exceda el límite se rechaza entera. Se conservan las repeticiones, por lo que un eco también podría repetir una orden. La espera predeterminada es de 3 segundos, configurable con `--segundos-accion`; `khi` y `kstr` tienen al menos 4 s y `kpu` al menos 6 s. Los movimientos continuos solicitan `kbalance` al terminar su intervalo. Las coreografías usan sus propios tiempos.

El siguiente fragmento literal muestra cómo se preparan las acciones en `_pasos()`:

```python
if token in COREOGRAFIAS:
    return COREOGRAFIAS[token]
if token == "kbalance":
    return [(token, 0)]
espera = max(self.segundos, {"khi": 4.0, "kpu": 6.0, "kstr": 4.0}.get(token, 0))
pasos = [(token, espera)]
if token in self.CONTINUOS:
    pasos.append(("kbalance", 0))
return pasos
```

Si el transporte informa un error, se cancela la secuencia pendiente. Consulta [SECUENCIAS.md](../SECUENCIAS.md) para los detalles de cancelación y cierre.

### 6.3. Baile

`COREOGRAFIAS["BAILE"]` define una lista de pares `(orden, espera_en_segundos)`: equilibrio, pasos `kvtF`, movimientos de cabeza `m0`, saludo `khi`, `kbuttUp`, `kmw`, giros `kvtL`/`kvtR`, celebración `kchr` y equilibrio. Un extracto literal:

```python
("kbalance", 1.0),
("kvtF", 2.5),
("kbalance", 0.6),
("m0 45", 0.35), ("m0 -45", 0.35), ("m0 45", 0.35), ("m0 -45", 0.35),
("m0 0", 0.4),
("khi", 3.0),
```

Son órdenes y pausas programadas, no una confirmación de que cada postura se haya completado. Revisa la compatibilidad y estabilidad de cada movimiento antes de probarlo físicamente.

### 6.4. Flexiones y celebración

`flexiones` se traduce directamente a `kpu`; la cola espera al menos 6 s antes de continuar. No es una secuencia de articulaciones personalizada en este programa.

`cristiano()` construye una celebración propia mediante giro, posturas `i` calculadas, interpolaciones de articulaciones con `suave()`, una espera y vuelta a equilibrio. `DI:SIUUUUUUUU` hace que el **PC** intente hablar con la voz de Windows; no es un token enviado al robot. Esta rutina es distinta de la acción `siuu` del puente de GitHub, que envía `T` solo si se ha cargado y verificado una skill personalizada. No hay que confundir ambas rutas ni presentar la postura programada como una prueba física realizada.

## 7. Prompts de ejemplo para continuar el desarrollo

Los siguientes textos son **propuestas reproducibles**, redactadas para esta guía; no son una transcripción de los mensajes históricos del equipo. Revisad el resultado y las pruebas antes de aplicarlo al robot.

1. **Comprender el sistema:** «Lee `bittle_voz.py`, `SECUENCIAS.md` y las pruebas de la cola. Explícame cómo se traduce una frase y cómo se cancela una secuencia. Distingue lo probado en simulación de lo comprobado físicamente».
2. **Añadir una frase existente:** «Añade un alias español para una acción ya admitida en `COMANDOS` y `GRAMATICA`; conserva el rechazo de palabras desconocidas y añade pruebas del intérprete. No cambies el protocolo del robot».
3. **Diseñar una coreografía:** «Propón una coreografía estable para Bittle como lista de órdenes y pausas, inicialmente solo en simulación. Explica cada token, los riesgos de estabilidad y las comprobaciones que faltan en el firmware antes de una prueba supervisada».
4. **Revisar flexiones:** «Localiza dónde se asigna `kpu` a flexiones, cuánto espera la cola y qué pruebas lo cubren. No afirmes que se ha validado con hardware si no hay evidencia».
5. **Comprobar el panel:** «Comprueba que todos los archivos necesarios para abrir `bittle_web.py` estén versionados; prueba la página en simulación y documenta cualquier archivo que falte».
6. **Documentar una actualización:** «Compara el código y las pruebas con README y las guías; actualiza las instrucciones, separa cada aplicación y conserva los resultados históricos con su fecha».

Para controlar el prototipo mediante ChatGPT y GitHub hay ejemplos y formato de Issue en [CHATGPT_GITHUB_BLUETOOTH.md](CHATGPT_GITHUB_BLUETOOTH.md) y [CHATGPT_SECUENCIAS_SIUU.md](CHATGPT_SECUENCIAS_SIUU.md). Es una vía independiente: requiere un puente local abierto y admite un conjunto restringido de acciones; el chat y GitHub no controlan directamente el Bluetooth. Los Issues de este repositorio son públicos.

## 8. Verificación y documentación relacionada

Para ejecutar las pruebas del proyecto, instala las dependencias necesarias y usa:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pytest -q
```

Registra fecha, versión, resultado y entorno de cada ejecución; no reutilices un recuento histórico como si fuera una prueba nueva. Las pruebas automatizadas con simuladores o dobles no sustituyen los ensayos físicos. Para preparar una validación presencial, revisa [preprueba física H3](H3/preprueba_fisica.md) y adapta el plan a la ruta y firmware que se vayan a usar.

- [README](../README.md): mapa de las aplicaciones e inicio rápido.
- [Guía de consola](../GUIA_PASO_A_PASO.md) y [secuencias](../SECUENCIAS.md).
- [Panel web](../PANEL_WEB.md): estado y limitaciones del archivo faltante.
- [Proyecto ARGOS H3](../PROYECTO.md): requisitos y evidencias de la ruta histórica.

No se dispone aquí de una transcripción completa de los prompts originales ni de evidencia nueva de funcionamiento físico. Si el equipo conserva esos materiales, se pueden incorporar citando su origen y fecha.
