# Investigación técnica y decisiones

Revisión 13/11/2026. Fuentes y localizadores en [FUENTES.md](../../docs/FUENTES.md).
Esta comparación documental no se presenta como experimento de rendimiento.

| Cuestión | Hallazgo y alternativas | Decisión y efecto en requisitos |
|---|---|---|
| Capacidades Bittle | REF-05 documenta habilidades con prefijo k, como sentarse, equilibrio y caminar. El catálogo efectivo depende de OpenCat/firmware | Reutilizar habilidades; no deducir soporte de todo COMANDOS a partir de dos movimientos. ACT-02, ACT-07; OPEN-02 |
| Voz | REF-07 ofrece modelo español pequeño y configuración de vocabulario. REF-08 ofrece transcripción general multilingüe | Mantener Vosk local por compatibilidad con el ejecutable y gramática existente. Whisper no se ha integrado ni comparado en este PC. ACT-09, ACT-10; OPEN-03 |
| Entrada controlada | Botones/texto evitan errores acústicos; escucha continua conserva manos libres, pero puede confundir conversación | Mantener las tres entradas actuales. El equipo decide usar los botones existentes de activar/desactivar: apagado salvo dictado. No se planifica pulsar para hablar, palabra de activación ni confirmación previa. ACT-03, ACT-04, ACT-15 |
| Comunicación | REF-06 describe Python/serie y módulos Bluetooth con más de un COM. El proyecto usa pyserial directamente; la API Petoi es otra alternativa | Mantener adaptador serie pequeño y comprobable, seleccionar COM saliente explícito. El panel no usa PetoiRobot. ACT-02, ACT-13 |
| BLE | El código CLI usa bleak; disponibilidad de servicio y característica depende del módulo | Mantener soporte separado del panel, sin prometer compatibilidad física verificada. ACT-15; OPEN-02 |
| Ejecución | Habilidades continuas no aportan aquí confirmación física de finalización | Un ejecutor y esperas temporizadas; FIFO hasta 20 pendientes. Las duraciones son diseño, no métricas de aceptación física. ACT-05 a ACT-08 |
| Panel | HTTP estándar y HTML/JS local evitan un framework adicional; una aplicación remota añadiría autenticación y despliegue | Limitar a loopback; no publicar ni ofrecer acceso desde móviles por la red. ACT-11, ACT-14 |
| Simulación | Dobles capturan comandos y permiten provocar fallos sin mover el robot | Separar parser, decisión de cola y adaptación de transporte; no simular postura física. ACT-16 |

## Restricciones y evaluación de viabilidad

Windows y Python 3.12.10 son el entorno ensayado; requirements-bittle.txt fija
las dependencias directas. El modelo español se descarga aparte y la captura del panel
usa PCM mono a 16 kHz. La conexión implementada usa 115200 y LF, que debe verificarse
con el módulo concreto. COM6 es un dato local comunicado, no una configuración universal.
La fuente oficial describe cómo formar comandos, pero no prueba que kup u otras habilidades
del catálogo estén presentes en este firmware. La confirmación nominal del usuario no
sustituye una matriz de compatibilidad.

## Riesgos de las decisiones

Gramática restringida no equivale a comprensión de conversación. Una transcripción
incorrecta que coincida con una orden puede ejecutarse. PARA tiene prioridad incluso
en frases que la contienen sin intención de detener. El riesgo anterior de duplicar una escritura incierta se corrige eliminando el
reenvío automático. Una operación en curso puede demorar la parada. La selección
BLE y el cierre físico no tienen caracterización completa disponible; no se exigen nuevos ensayos. El registro [de asuntos abiertos](../../docs/h1/ASUNTOS_ABIERTOS.md)
define responsables, impacto y resolución sin inventar parámetros acústicos o físicos.
