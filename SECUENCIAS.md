# Secuencias de acciones — 2026-11-12

Actualización de `bittle_voz.py`, por texto y voz. No cambia la aplicación
histórica `voice_bittle.py` ni aprueba decisiones H1/H2/H3 pendientes.
Reinicia el programa para cargarla; no necesita dependencias nuevas.
Para el recorrido de implementación, ejemplos de prompts y acciones, consulta
[la guía de implementación](docs/GUIA_IMPLEMENTACION_Y_PROMPTS.md).

## Uso

```powershell
.\.venv\Scripts\python.exe bittle_voz.py --simulado --texto
```

Prueba `siéntate y después ponte de pie` o
`siéntate y ponte de pie y saluda y descansa`.
También puedes dar órdenes por separado mientras ejecuta otra: se añaden al
final. Límite: 20 acciones pendientes; una frase que lo exceda se rechaza entera.
Las repeticiones explícitas se conservan. Se eliminó la supresión de órdenes
iguales durante 1,5 segundos: un eco también podría repetirlas.

Usa los nombres existentes y los conectores `y`, `después`, `luego`, `primero`,
`entonces`. No interpreta duraciones habladas ni lenguaje libre.
Palabras desconocidas o negaciones rechazan la frase entera, salvo si contiene
`para`, `quieto`, `alto` o `stop`: la parada tiene prioridad absoluta.
El reconocimiento puede transcribir mal la voz; validar el texto no garantiza
detectar negaciones o ruido del audio original.

## Tiempos y cancelación

- Un único hilo ejecuta en orden mientras continúa la escucha.
- Espera predeterminada: 3 segundos después del envío. Se cambia con
  `--segundos-accion 5`. Saludar y estirar tienen mínimo 4 s; flexiones, 6 s.
- Caminar, trotar, retroceder y girar solicitan `kbalance` al terminar ese
  tiempo, incluso al final de la cola. Ya no continúan indefinidamente.
- Las coreografías conservan sus tiempos; la siguiente acción espera al final
  de la secuencia programada.
- Son tiempos estimados: no hay confirmación de finalización física.
- `para` vacía la cola, cancela el resto de la coreografía y solicita equilibrio.
  Si aparece en una frase con otras acciones, solo se solicita la parada.
- Una escritura/reconexión en curso no es interrumpible por esta cola: la
  parada espera a que retorne. No sustituye al interruptor físico.
- Un error devuelto por el transporte cancela la secuencia pendiente. El
  transporte serie conserva su reintento interno, que puede retrasar el error
  o repetir una escritura. No se garantiza parada física al perder el enlace.
- Ctrl+C o fin de entrada cancela las pendientes, espera al envío en curso e
  intenta `krest` antes de cerrar. Esa postura puede mover el robot.

## Verificación

En una verificación histórica se comunicaron 140 pruebas aprobadas, incluidas
16 nuevas en `tests/unit/test_cola_bittle_voz.py`:
interpretación de dos/cuatro acciones, alias, repeticiones, frases inválidas,
prioridad de parada, FIFO entre frases, coreografía completa/cancelada,
movimiento temporizado, error, límite y cierre. Fue una prueba sin hardware ni
micrófono y no acredita por sí sola el estado del checkout actual.

Pendiente: reconocimiento real de frases encadenadas y validación física de
tiempos, habilidades y parada. La confirmación del usuario de voz/texto de la
versión anterior no valida esta nueva cola. Los PDF existentes son anteriores.
