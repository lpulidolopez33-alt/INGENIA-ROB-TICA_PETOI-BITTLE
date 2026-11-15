# Secuencias de acciones — 2026-11-12

Cola compartida por `bittle_voz.py` y el panel `bittle_web.py`, por texto, botones y voz. Su comportamiento forma parte de H1 v0.4.
Reinicia el programa para cargarla; no necesita dependencias nuevas.

## Uso

```powershell
.\.venv\Scripts\python.exe bittle_voz.py --simulado --texto
```

Prueba `siéntate y después ponte de pie` o
`siéntate y ponte de pie y saluda y descansa`.
También puedes dar órdenes por separado mientras ejecuta otra: se añaden al
final. Límite: 20 acciones pendientes, sin contar la que está ejecutándose; una frase que lo exceda se rechaza entera.
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
  tiempo, incluso al final de la cola. Si falla el envío de equilibrio, el software no garantiza que la marcha física termine.
- Las coreografías conservan sus tiempos; la siguiente acción espera al final
  de la secuencia programada.
- Son tiempos estimados: no hay confirmación de finalización física.
- `para` vacía la cola, cancela el resto de la coreografía y solicita equilibrio.
  Si aparece en una frase con otras acciones, solo se solicita la parada.
- Una escritura en curso no es interrumpible por esta cola: la
  parada espera a que retorne. Además, un paso ya seleccionado por el hilo puede
  llegar a enviarse antes del equilibrio: la comprobación de cancelación y la
  escritura no forman una operación atómica. No sustituye al interruptor físico.
- Un error devuelto por el transporte cancela la secuencia pendiente. El
  transporte serie no repite el envío: si se inició la escritura, conserva resultado
  desconocido y bloquea nuevas transmisiones hasta desconectar/conectar manualmente.
  No se recuperan pendientes, tampoco las añadidas detrás de PARA durante el fallo.
  Una parada explícita conserva prioridad en la cola, pero no atraviesa un enlace
  serie bloqueado. No se garantiza parada física al perder el enlace.
- Ctrl+C o fin de entrada cancela las pendientes, espera al envío en curso e
  intenta `krest` antes de cerrar. Esa postura puede mover el robot.

## Verificación

Los 16 casos parametrizados de cola prueban parser, orden entre frases, prioridad
de parada, coreografías reducidas, movimiento temporizado, error, límite y cierre.
Los resultados de toda la suite están en [RESULTADOS.md](evidencias/actual/RESULTADOS.md).

El usuario confirmó que las secuencias funcionan; consta en
[validacion_usuario.md](docs/H3/validacion_usuario.md). Quedan por medir tiempos
físicos, todas las habilidades y escenarios de fallo. No equiparar esa confirmación
con una prueba formal de precisión, seguridad o fin de movimiento.

El estado «sin acciones» solo significa que el ejecutor no tiene trabajo: no
confirma reposo físico. La cola está en RAM y no sobrevive al cierre del proceso.
Una espera larga es compatible con el alcance final: H1 v0.4 retira la garantía
de transmisión en 3 s de v0.2. Ver [el historial](docs/h1/EVOLUCION_REQUISITOS.md).

## Uso de voz acordado

Usar el panel con el micrófono apagado salvo al dictar: activar, esperar Escuchando,
decir la orden o secuencia, comprobar su aceptación y desactivar inmediatamente.
La cola sigue ejecutándose con la escucha apagada; para cancelar se pulsa PARA en
el panel. Es una operación manual, no un modo automático ni una confirmación previa.
Procedimiento y límites: [estrategia de escucha](PANEL_WEB.md#estrategia-de-escucha-manual-acordada).

