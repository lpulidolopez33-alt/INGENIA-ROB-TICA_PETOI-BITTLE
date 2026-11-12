# Panel HTML local de VOICE-BITTLE

> **Estado de esta versión de `main`: incompleta.** Falta `web/index.html`,
> archivo que `bittle_web.py` necesita para servir la página. La petición a la
> página devuelve error 500; las instrucciones siguientes describen el diseño
> y solo son reproducibles después de recuperar el archivo correspondiente.
> No se ha comprobado aquí la recuperación ni el funcionamiento físico.

Desde la carpeta del proyecto, ejecuta `INICIAR_PANEL.bat` con doble clic o:

```powershell
.\.venv\Scripts\python.exe -X utf8 bittle_web.py
```

Se abre http://127.0.0.1:8765. Mantén abierta la terminal. No abras `web/index.html`
directamente: necesita el servidor Python. No hay dependencias nuevas respecto
a `requirements-bittle.txt`. Para instalar desde cero:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-bittle.txt
```

## Uso

1. Cierra antes el programa de consola que utilice el puerto o micrófono.
2. Inicia simulación para probar el panel. Para el robot selecciona Bittle real
   y su COM saliente (COM6 en la última sesión del usuario), y pulsa Conectar.
3. Escoge micrófono y carpeta Vosk. El valor inicial apunta al modelo que ya
   existe en la carpeta vecina `VOICE-BITTLE/modelos/vosk-model-small-es-0.42`.
   En otro ordenador escribe la ruta de tu modelo descargado según README.
4. Pulsa Activar micrófono. «Cargando» todavía no escucha. «Escuchando» aparece
   únicamente cuando se abre la captura. El medidor indica nivel de sonido,
   no reconocimiento correcto: revisa la última frase y la cola.
5. Di las órdenes visibles o pulsa sus botones. También puedes escribir una
   secuencia. La cola y los tiempos son los descritos en `SECUENCIAS.md`.
6. Desactivar micrófono impide aceptar nuevos resultados, incluidos resultados
   que lleguen tarde; las acciones ya aceptadas continúan. PARA vacía la cola
   y solicita equilibrio. No es una parada física garantizada.
7. Antes de salir, desactiva escucha y desconecta. Desconectar cancela la cola
   e intenta enviar descanso, que puede mover el robot. Cierra luego la terminal
   con Ctrl+C. Cerrar solo la pestaña NO cierra el servidor ni la escucha.

La página controla el micrófono del PC donde corre Python, no el del navegador.
Funciona solo en ese ordenador; el servidor escucha en 127.0.0.1. No requiere
Internet durante el uso ni envía audio a servicios externos. Varias pestañas
comparten la misma sesión. Esta interfaz ofrece simulación y puerto serie
Bluetooth/USB; BLE sigue disponible en la consola original.

## Estado y límites

«Puerto del robot abierto» confirma apertura del puerto, no recepción ni
finalización física de cada movimiento. Los errores de transporte aparecen en
el panel y las acciones pendientes se descartan cuando el transporte informa
el fallo. Se conserva el reintento interno del transporte original.

El botón PARA depende del servidor y del enlace, y espera a una escritura o
reconexión que ya esté en curso. Mantén accesible el interruptor físico.
Si la captura se desborda o informa un error, se apaga la escucha en vez de
ejecutar audio acumulado. Los errores se muestran en la parte superior.

Opciones: `--puerto-web 8766` cambia el puerto del panel;
`--sin-navegador` evita abrir automáticamente una pestaña.

Las pruebas del panel usan simulación y sustitutos de micrófono/robot. La
validación física y con voz real de esta interfaz queda pendiente del usuario;
no se deduce de sus pruebas de la consola anterior.

Verificación histórica comunicada el 2026-11-12 en otra copia, anterior a la
comprobación de que falta `web/index.html` en este checkout: 149 pruebas
automatizadas superadas, incluidas
9 del panel (HTTP local, protección de acciones, conexión fallida, cola,
desconexión, errores de micrófono y descarte de resultados tras desactivar).
Revisión en navegador: carga, enumeración de dispositivos, conexión simulada,
envío de cuatro acciones, cancelación y desconexión. Sin activar micrófono
ni abrir el puerto del robot. Se detuvo el servidor de revisión al terminar.
