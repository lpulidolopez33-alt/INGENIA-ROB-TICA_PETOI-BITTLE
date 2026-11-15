# Panel HTML local de VOICE-BITTLE

Desde la carpeta del proyecto, ejecuta `INICIAR_PANEL.bat` con doble clic o:

```powershell
.\.venv\Scripts\python.exe -X utf8 bittle_web.py
```

Se abre http://127.0.0.1:8765. Mantén abierta la terminal. No abras `web/index.html`
directamente: necesita el servidor Python. La instalación y el modelo se explican
una sola vez en [GUIA.md](GUIA.md); el panel no añade dependencias web.

## Uso

1. Cierra antes el programa de consola que utilice el puerto o micrófono.
2. Inicia simulación para probar el panel. Para el robot selecciona Bittle real
   y su COM saliente (COM6 en la última sesión del usuario), y pulsa Conectar.
3. Escoge micrófono y carpeta Vosk. El valor inicial es
   `modelos/vosk-model-small-es-0.42`. Descarga el modelo según GUIA.md
   o selecciona otra copia válida antes de activar.
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
Bluetooth/USB; BLE sigue disponible solo en la consola `bittle_voz.py`, no en el panel.

## Estado y límites

«Puerto del robot abierto» confirma apertura del puerto, no recepción ni
finalización física de cada movimiento. Los errores de transporte aparecen en
el panel y las acciones pendientes se descartan cuando el transporte informa
el fallo. No se reenvía una orden automáticamente. Tras un fallo serie se requiere
desconectar y volver a conectar, con cola nueva vacía. El indicador
puede seguir mostrando puerto abierto tras un fallo: no hay vigilancia continua
ni confirmación de movimiento. El estado de transporte distingue no_enviado,
desconocido y enviado_sin_confirmacion_fisica. El error exige recuperación manual.

El botón PARA depende del servidor y del enlace, y espera a una escritura o
operación que ya esté en curso; no hay reconexión automática. Mantén accesible el interruptor físico.
Si la captura se desborda o informa un error, se apaga la escucha en vez de
ejecutar audio acumulado. Los errores se muestran en la parte superior.

Opciones: `--puerto-web 8766` cambia el puerto del panel;
`--sin-navegador` evita abrir automáticamente una pestaña.

## Evidencia y alcance

El usuario confirmó posteriormente que el panel «ha funcionado perfectamente».
Se registra como uso nominal en [validacion_usuario.md](docs/H3/validacion_usuario.md),
sin inventar precisión, latencia, fallos ensayados ni aprobación docente.

Las pruebas automáticas usan sustitutos de micrófono/robot. Resultados vigentes:
[RESULTADOS.md](evidencias/actual/RESULTADOS.md). La revisión de navegador del agente
comprobó carga, enumeración, simulación, secuencia, parada y desconexión, sin abrir
COM ni capturar voz. No constan mediciones sistemáticas de rendimiento, condiciones acústicas, fallos
físicos ni todas las habilidades. Son límites de evidencia; no se requieren nuevos ensayos para entregar.

La actividad reciente conserva como máximo 40 eventos con hora en memoria. No es
un historial persistente y no se exporta. Es el alcance de ACT-11 en H1 v0.4; el registro completo de v0.2 se retiró de esta entrega.

## Estrategia de escucha manual acordada

El micrófono permanece apagado salvo al dictar una orden o secuencia. El operador:

1. Mantiene la escucha apagada mientras no va a dar instrucciones.
2. Pulsa Activar micrófono, espera el estado Escuchando y dice únicamente la orden o secuencia del catálogo.
3. Comprueba la frase y la aceptación en el panel; después pulsa Desactivar micrófono y verifica el estado Apagado.
4. Deja que termine la cola con la escucha apagada. Para una nueva instrucción, repite el ciclo.
5. Si necesita cancelar con el micrófono apagado, pulsa el botón PARA del panel; PARA por voz no se recibe en ese estado.

Se utilizan los controles existentes del panel, sin cambiar código ni añadir un modo
automático. La ejecución puede empezar en cuanto se acepta una orden: revisar la frase
no es una confirmación previa que bloquee movimientos. Desactivar escucha no cancela
lo ya aceptado; el botón PARA cancela pendientes con los límites descritos en SECUENCIAS.md.

El equipo elige este procedimiento para reducir entradas accidentales y mantener el
comportamiento actual. Vosk aún puede interpretar mal mientras escucha; no se garantiza
rechazo de conversación ni se transforma el ensayo fallido en satisfactorio. No se deja
pendiente una modificación de reconocimiento: se conserva la limitación y la mitigación
operativa. No se recomienda dejar la escucha abierta fuera del intervalo de dictado.
La consola de voz mantiene captura continua y no tiene estos botones; para aplicar
esta estrategia se usa el panel HTML. Texto y botones siguen disponibles sin micrófono.
