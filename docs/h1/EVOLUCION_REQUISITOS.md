# Evolución de requisitos: H1 v0.2 → H1 v0.4

La referencia vigente es [H1 v0.4](H1_v0.4.md). Esta tabla es un historial de
cambios autorizado por la petición del usuario de alinear toda la documentación
con el alcance final. No es una lista de funciones obligatorias por implementar.
H1 v0.2 queda sustituido y está en el respaldo externo, no en esta entrega.
No consta aprobación del profesor ni se modifica retrospectivamente evidencia de pruebas.

| ID anterior | Tratamiento en v0.3 | Referencia vigente | Justificación / alcance final |
|---|---|---|---|
| RF-01 | Reformulado | ACT-03, ACT-09 | Reconocimiento español; se retiran inglés y consultas del vocabulario actual. |
| RF-02 | Conservado y ampliado | ACT-03, ACT-07 | Conversión al catálogo ampliado; compatibilidad física limitada al equipo probado. |
| RF-03 | Reformulado | ACT-07, ACT-11 | Solicitud/secuenciación software; resultado físico observado por operador, sin detector automático. |
| RF-04 | Reformulado | ACT-04 | Validación textual y prioridad de parada; sin rechazo por umbral acústico. |
| RF-05 | Sustituido | ACT-05 | Aceptar y encolar durante acción hasta 20 pendientes; ya no rechazar por estar ocupado. |
| RF-06 | Reformulado | ACT-11, ACT-13 | Avisos, última frase, actividad y error; sin registro estructurado por cada fase de envío. |
| RF-07 | Retirado | Fuera de alcance | No se exige cambio a inglés. |
| RF-08 | Reformulado | ACT-12 | Cancelación, intento de descanso y cierre; sin garantía automática de reposo físico. |
| RF-09 | Sustituido | ACT-08 | Órdenes normales esperan; PARA cancela. No es parada física independiente. |
| RF-10 | Retirado | Fuera de alcance | Estado/actividad se consultan visualmente, no con consultas habladas. |
| RR-01 | Objetivo numérico retirado | ACT-16 | No se exige ni se declara medido 90% en una muestra de 100. |
| RR-02 | Objetivo numérico retirado | ACT-05, ACT-06 | Esperas secuenciales sin garantía de envío en 3 s; el tiempo de cola no se oculta. |
| RR-03 | Conservado como diseño local | ACT-09, ACT-14 | Sin dependencia de servicio remoto de voz; ensayo offline no atribuido si no consta. |
| RS-01 | Reformulado | ACT-04 | No enviar por texto inválido salvo prioridad de parada; no garantía de rechazo de todo ruido. |
| RS-02 | Reformulado | ACT-13 | Cancelar secuencia y mostrar excepción; sin reenvío en versión final y recuperación explícita mediante nueva sesión. |
| RS-03 | Conservado como condición de operación | H1 v0.4 §7 | Supervisión y medio independiente; PARA no lo sustituye. |
| RI-01 | Conservado | ACT-02 | Conexión serie Bluetooth del equipo; COM explícito. |
| RI-02 | Conservado y ampliado | ACT-03, ACT-07 | Tokens y secuencias del catálogo. |
| RI-03 | Reformulado | ACT-02, ACT-11 | Estado de sesión/puerto, no monitor físico continuo. |
| RI-04 | Conservado para español | ACT-11 | Órdenes visibles y catálogo del idioma incluido. |
| RI-05 | Conservado | ACT-09, ACT-11 | Apagado, cargando y escuchando. |
| RI-06 | Sustituido | ACT-11 | Actividad visual con hora y hasta 40 eventos; sin consulta hablada, fecha ni persistencia. |
| RI-07 | Reformulado | ACT-11 | Actividad programada y pendientes; no postura/final físico. |
| RO-01 | Conservado como condición de operación | H1 v0.4 §1 y §7 | Superficie estable/seca/despejada y supervisor. |
| RO-02 | Conservado con alcance de sesión | ACT-01, ACT-02 | No aceptar órdenes antes de abrir sesión; apertura de puerto no acredita disponibilidad física. |
| RFI-01 | Conservado en panel | ACT-10 | Error de captura/modelo apaga escucha; no atribuir al CLI controles que no contiene. |
| RFI-02 | Conservado con alcance de transporte | ACT-13 | Mostrar errores que retorna transporte; resultado desconocido si la escritura pudo iniciarse; no se repite. |
| RU-01 | Retirado como función bilingüe | Fuera de alcance | Interfaz/catálogo en español, sin selector EN. |
| RU-02 | Reformulado | ACT-04, ACT-11 | Mostrar no reconocida o error; sin mensaje hablado general de repetición. |
| RU-03 | Conservado en panel | ACT-09 | Activación/desactivación manual independiente de la cola. |
| RM-01 | Sustituido | ACT-11 | Actividad limitada en RAM; historial persistente completo fuera de alcance. |
| RM-02 | Reformulado | ACT-10, ACT-13 | Mensajes/campos de error; no registro persistente estructurado de fallos. |
| RD-01 | Conservado | ACT-03, ACT-09, ACT-14 | Lógica Python y presentación HTML/CSS/JS. |
| RD-02 | Reformulado | ACT-09 | Vosk local español; modelo inglés fuera de alcance. |

Los escenarios EF-01…08 y necesidades NF-01…06 de v0.3 corresponden al uso final.
Los ESC/NEC/OPEN anteriores se conservaron fuera de la entrega en el respaldo previo,
pero no se emplean como criterios activos incompatibles con cola, parada o panel.
