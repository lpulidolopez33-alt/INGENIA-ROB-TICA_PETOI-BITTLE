# Especificación actual — VOICE-BITTLE

Versión documental 0.5 · 2026-11-12 · Descripción de la implementación actual,
con criterios verificables y límites explícitos.
Desarrolla [H1 v0.4](../../docs/h1/H1_v0.4.md), alcance final solicitado por el usuario.

## Alcance y actores

El usuario controla un Bittle desde un PC Windows con voz española, texto o botones.
El panel web local es la interfaz principal; una consola ofrece el mismo parser y
cola. El supervisor observa los movimientos e interviene físicamente si hace falta.
El sistema incluye aplicación, PC, micrófono, enlace y robot; la interfaz no mide
posturas ni certifica finalización. La simulación muestra tokens, no dinámica física.

La línea base vigente es H1 v0.4. Los 34 requisitos anteriores se conservan solo
como [historial de cambios](../../docs/h1/EVOLUCION_REQUISITOS.md).
La entrega contiene exclusivamente el código de la aplicación final.

## Requisitos vigentes de H1 v0.4

Los ACT siguientes reproducen la tabla canónica de H1 v0.4. El verificador comprueba que coincidan.

| ID | Comportamiento y criterio observable |
|---|---|
| ACT-01 | Al iniciar el panel, conexión desconectada, micrófono apagado y cola vacía; no abre hardware |
| ACT-02 | Permite sesión simulada o abrir COM seleccionado; una apertura fallida vuelve a desconectado con error. Puerto abierto no significa robot respondiendo |
| ACT-03 | Interpreta tokens de palabras normalizadas, alias más largos primero y secuencias de izquierda a derecha; conserva repeticiones |
| ACT-04 | Una palabra ajena al vocabulario/conectores rechaza la frase entera, salvo palabra de parada, que tiene prioridad |
| ACT-05 | Una cola FIFO con un ejecutor conserva acciones de una o varias frases; máximo 20 pendientes, excluida la acción en curso; exceso rechaza la frase entera |
| ACT-06 | Esperas por acción: 3 s por defecto, ajustable positivo/finito; mínimos 4 s saludo/estiramiento y 6 s flexiones. Son esperas después del envío, no ACK de fin |
| ACT-07 | Caminar/trotar/retroceder/girar solicitan kbalance tras su espera; coreografías conservan sus pasos antes de continuar la cola |
| ACT-08 | Para/quieto/alto/stop cancela pendientes y resto de coreografía, y prioriza equilibrio; un envío ya iniciado no se interrumpe |
| ACT-09 | Panel: carga local Vosk; solo pasa a escuchando al abrir captura. Apagar impide aceptar resultados tardíos, pero no elimina acciones ya aceptadas |
| ACT-10 | Panel: error de captura/modelo apaga escucha y presenta error; cola de audio limitada a 8 bloques. Su desbordamiento solicita terminar la escucha |
| ACT-11 | Panel muestra última frase, nivel sonoro, tarea del ejecutor, pendientes y hasta 40 eventos; no presenta mediciones físicas |
| ACT-12 | Desconexión/cierre cancela pendientes, espera al ejecutor, intenta krest y cierra enlace. Cerrar pestaña no equivale a desconectar |
| ACT-13 | Si el transporte devuelve una excepción, descarta la secuencia pendiente y expone el error; se conserva una parada solicitada mientras fallaba el envío. No bloquea permanentemente nuevas órdenes |
| ACT-14 | HTTP escucha solo en 127.0.0.1; valida Host, token de acciones y Origin cuando se proporciona; no ofrece acceso remoto ni autenticación multiusuario |
| ACT-15 | Consola ofrece texto, voz continua, listado de dispositivos y BLE; panel ofrece COM/simulación. Sus ciclos de captura no son idénticos |
| ACT-16 | La entrega deberá distinguir pruebas automáticas, inspección y confirmación de uso, con referencias de código y resultados; no atribuirá mediciones ni ensayos no realizados |

Pruebas por requisito y pendientes se mantienen en
[trazabilidad_actual.json](trazabilidad_actual.json); resultados en
[RESULTADOS.md](../../evidencias/actual/RESULTADOS.md).

## Escenarios actuales de uso (ACT-ESC)

1. Inicio: abrir panel → iniciar simulación → mantener micrófono apagado hasta dictar.
2. Orden simple: activar y esperar Escuchando → decir «siéntate» → aceptación y envío → desactivar escucha manualmente.
3. Secuencia: «siéntate y ponte de pie y saluda y descansa» → cuatro acciones en orden.
4. Durante ejecución: mantener escucha apagada; otra orden requiere activar para dictar y desactivar de nuevo. El botón PARA sustituye pendientes por equilibrio.
5. Desactivar escucha: no acepta voz nueva, sigue ejecutando lo ya aceptado.
6. Fallo: muestra el error disponible; consultar límites de conexión/captura antes de reintentar.
7. Cierre: desactivar → desconectar → observar robot → terminar servidor.

## Límites que no deben presentarse como prestaciones

No hay umbral de confianza, selección EN, consultas por voz de estado/historial,
registro persistente completo, detector de hablante, palabra de activación, medida
de latencia ni detector de fin físico en la aplicación actual. La gramática restringida
puede producir falsos positivos; rechazar texto desconocido no prueba rechazo de ruido.

El transporte serie no reenvía ni reconecta automáticamente. Un fallo antes de
write se registra como no_enviado; durante write, flush o lectura posterior, como
desconocido. El envío completo queda enviado_sin_confirmacion_fisica. Después de
un fallo se requiere desconectar/conectar para crear una sesión vacía; no se reanudan
pendientes. No hay monitor continuo ni confirmación física. Precisión, latencias,
todas las habilidades y fallos físicos no están caracterizados; no bloquean la
preparación documental ni se solicitan nuevos ensayos en este cierre.

## Historias de usuario priorizadas

### US1 Solicitar dos órdenes y rechazar entradas ajenas P1

Como operador quiero usar siéntate y ponte de pie y recibir rechazo de una entrada
desconocida. Es el primer incremento verificable de Moodle. Prueba independiente:
sesión simulada, solicitar cada orden y capturar ksit/kup; solicitar siéntate y vuela
y comprobar que no añade comandos. ACT-01/02/03/04/11/14/15.
Si no hay sesión, la orden falla; si la frase contiene PARA, prevalece ACT-08.

### US2 Encadenar y cancelar P1

Como operador quiero añadir secuencias y cancelarlas. Dada una acción en curso,
otra frase válida se añade al final si cabe; si excede 20 pendientes se rechaza entera.
Dada una secuencia, PARA invalida sus pasos futuros y solicita equilibrio después
del I/O comprometido. Prueba independiente con enlace capturador y sincronización.
ACT-05/06/07/08/12/13. Depende del parser US1.

### US3 Habilitar voz y observar el estado P2

Como operador quiero activar/desactivar escucha y ver fallos. Dada una sesión,
activar un modelo válido inicia carga; solo una captura abierta se muestra escuchando.
Apagar impide resultados tardíos. Error o saturación terminan captura. Prueba independiente
con dobles de Vosk y audio; no demuestra precisión acústica. ACT-09/10/11. Depende de US1.

### US4 Reproducir y defender la entrega P1

Como equipo/profesor quiero relacionar requisitos con tareas, código y resultados.
Desde una extracción limpia puedo instalar dependencias, ejecutar pruebas y simulación,
y consultar huellas y commit de referencia. ACT-16. Depende de US1, US2 y US3 para cierre H3.

## Criterios de éxito del incremento software

- SC-01: dos órdenes de demostración producen exactamente ksit/kup en la prueba del adaptador;
  la entrada inválida no añade comandos. No equivale a postura física.
- SC-02: FIFO conserva orden y repeticiones; PARA cancela pendientes en los casos de prueba.
- SC-03: sin conexión inicial ni captura al arrancar; errores de captura y resultados tardíos
  cumplen los casos vinculados. El ensayo de conversación con escucha activa dio falsos positivos según el usuario; no se presenta como PASS. El uso nominal adopta escucha manual.
- SC-04: cada ACT tiene fuente, necesidad, escenario, tarea, componente y método verificable;
  el paquete extraído pasa suite y demostración, con versión identificable.

Entidades y estados: [data-model.md](data-model.md). Contratos: [interfaces](contracts/interfaces.md).
Supuestos y decisiones pendientes: [OPEN](../../docs/h1/ASUNTOS_ABIERTOS.md).

## Estrategia operativa de voz

La estrategia de uso elegida por el equipo mantiene el micrófono apagado salvo al
dictar instrucciones desde el panel. Tras aceptar una orden o secuencia, se desactiva
manualmente la escucha; la cola continúa. PARA se pulsa en pantalla cuando no se escucha.
No hay silenciamiento automático ni confirmación previa: las acciones pueden comenzar
al aceptarse. Persiste la posibilidad de transcripción errónea con escucha activa.
OPEN-03 documenta una limitación conocida con mitigación operativa, no una corrección
software pendiente. El ensayo fallido de conversación se conserva como tal.

