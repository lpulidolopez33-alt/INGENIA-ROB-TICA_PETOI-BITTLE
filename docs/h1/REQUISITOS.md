# Atributos y verificación de requisitos

Enunciados canónicos en [H1 v0.4](H1_v0.4.md), sección 6. Revisión técnica 13/11/2026.
Estado general: implementado; cobertura software por pruebas/inspección, observaciones físicas nominales disponibles y límites de caracterización documentados. Correcciones finales no revalidadas físicamente; no se requieren ensayos adicionales para preparar la entrega. No aprobado académicamente.

## ACT-01

| Atributo | Valor |
|---|---|
| Clase | interfaz y operación |
| Motivación | Evitar activaciones al arrancar |
| Origen | NF-04, NF-05; EF-01; REF-11, REF-12 |
| Método y criterio | Prueba automatizada: ejecutar casos enlazados en la matriz y comparar aserciones con resultado PASS; inspección para los límites indicados. El criterio observable exacto es el enunciado ACT en H1. |
| Restricciones y pendientes | Arranque software, no disponibilidad física. OPEN-02/03/04/07 registran límites y evidencias disponibles; OPEN-08 trata aceptación académica. |
| Estado | Revisado técnicamente; implementado, verificación limitada al alcance de la evidencia vinculada |

## ACT-02

| Atributo | Valor |
|---|---|
| Clase | interfaz |
| Motivación | Seleccionar destino explícito y comunicar apertura fallida |
| Origen | NF-01, NF-05; EF-01, EF-10; REF-11, REF-12 |
| Método y criterio | Prueba automatizada: ejecutar casos enlazados en la matriz y comparar aserciones con resultado PASS; inspección para los límites indicados. El criterio observable exacto es el enunciado ACT en H1. |
| Restricciones y pendientes | COM real comunicado por usuario, no simulado como robot completo. OPEN-02/03/04/07 registran límites y evidencias disponibles; OPEN-08 trata aceptación académica. |
| Estado | Revisado técnicamente; implementado, verificación limitada al alcance de la evidencia vinculada |

## ACT-03

| Atributo | Valor |
|---|---|
| Clase | funcional |
| Motivación | Convertir las órdenes previstas sin perder su orden |
| Origen | NF-01; EF-02, EF-09; REF-01, REF-02, REF-12 |
| Método y criterio | Prueba automatizada: ejecutar casos enlazados en la matriz y comparar aserciones con resultado PASS; inspección para los límites indicados. El criterio observable exacto es el enunciado ACT en H1. |
| Restricciones y pendientes | Parser textual, no precisión acústica ni todos los alias. OPEN-02/03/04/07 registran límites y evidencias disponibles; OPEN-08 trata aceptación académica. |
| Estado | Revisado técnicamente; implementado, verificación limitada al alcance de la evidencia vinculada |

## ACT-04

| Atributo | Valor |
|---|---|
| Clase | funcional |
| Motivación | No ejecutar fragmentos de frases desconocidas |
| Origen | NF-01; EF-02, EF-07, EF-09; REF-01, REF-02, REF-12 |
| Método y criterio | Prueba automatizada: ejecutar casos enlazados en la matriz y comparar aserciones con resultado PASS; inspección para los límites indicados. El criterio observable exacto es el enunciado ACT en H1. |
| Restricciones y pendientes | Desconocidas/negación textual; no garantiza rechazo de audio ruidoso. OPEN-02/03/04/07 registran límites y evidencias disponibles; OPEN-08 trata aceptación académica. |
| Estado | Revisado técnicamente; implementado, verificación limitada al alcance de la evidencia vinculada |

## ACT-05

| Atributo | Valor |
|---|---|
| Clase | funcional |
| Motivación | Encadenar peticiones con límite de memoria |
| Origen | NF-02; EF-03, EF-04; REF-11, REF-12 |
| Método y criterio | Prueba automatizada: ejecutar casos enlazados en la matriz y comparar aserciones con resultado PASS; inspección para los límites indicados. El criterio observable exacto es el enunciado ACT en H1. |
| Restricciones y pendientes | Capacidad y FIFO con sustituto; sin prueba exhaustiva de carreras concurrentes. OPEN-02/03/04/07 registran límites y evidencias disponibles; OPEN-08 trata aceptación académica. |
| Estado | Revisado técnicamente; implementado, verificación limitada al alcance de la evidencia vinculada |

## ACT-06

| Atributo | Valor |
|---|---|
| Clase | prestación software |
| Motivación | Coordinar acciones con esperas declaradas |
| Origen | NF-02; EF-03; REF-11, REF-12 |
| Método y criterio | Prueba automatizada: ejecutar casos enlazados en la matriz y comparar aserciones con resultado PASS; inspección para los límites indicados. El criterio observable exacto es el enunciado ACT en H1. |
| Restricciones y pendientes | Esperas mínimas y parámetros inválidos probados; no medición física. OPEN-02/03/04/07 registran límites y evidencias disponibles; OPEN-08 trata aceptación académica. |
| Estado | Revisado técnicamente; implementado, verificación limitada al alcance de la evidencia vinculada |

## ACT-07

| Atributo | Valor |
|---|---|
| Clase | funcional |
| Motivación | Terminar solicitudes continuas y respetar coreografías |
| Origen | NF-02; EF-03; REF-11, REF-12 |
| Método y criterio | Prueba automatizada: ejecutar casos enlazados en la matriz y comparar aserciones con resultado PASS; inspección para los límites indicados. El criterio observable exacto es el enunciado ACT en H1. |
| Restricciones y pendientes | Coreografía reducida de prueba; no valida movimientos reales del baile/Cristiano. OPEN-02/03/04/07 registran límites y evidencias disponibles; OPEN-08 trata aceptación académica. |
| Estado | Revisado técnicamente; implementado, verificación limitada al alcance de la evidencia vinculada |

## ACT-08

| Atributo | Valor |
|---|---|
| Clase | seguridad software |
| Motivación | Recuperar control sobre acciones pendientes |
| Origen | NF-03; EF-05, EF-09; REF-11, REF-12 |
| Método y criterio | Prueba automatizada: ejecutar casos enlazados en la matriz y comparar aserciones con resultado PASS; inspección para los límites indicados. El criterio observable exacto es el enunciado ACT en H1. |
| Restricciones y pendientes | No interrupción del I/O en curso ni garantía de parada física. OPEN-02/03/04/07 registran límites y evidencias disponibles; OPEN-08 trata aceptación académica. |
| Estado | Revisado técnicamente; implementado, verificación limitada al alcance de la evidencia vinculada |

## ACT-09

| Atributo | Valor |
|---|---|
| Clase | interfaz |
| Motivación | Permitir decidir cuándo se acepta voz |
| Origen | NF-04; EF-06, EF-11; REF-11, REF-12 |
| Método y criterio | Prueba automatizada: ejecutar casos enlazados en la matriz y comparar aserciones con resultado PASS; inspección para los límites indicados. El criterio observable exacto es el enunciado ACT en H1. |
| Restricciones y pendientes | Carga/captura con sustitutos; uso nominal comunicado por usuario. OPEN-02/03/04/07 registran límites y evidencias disponibles; OPEN-08 trata aceptación académica. |
| Estado | Revisado técnicamente; implementado, verificación limitada al alcance de la evidencia vinculada |

## ACT-10

| Atributo | Valor |
|---|---|
| Clase | fiabilidad software |
| Motivación | Evitar captura acumulada o fallos silenciosos |
| Origen | NF-04; EF-06, EF-07, EF-11; REF-11, REF-12 |
| Método y criterio | Prueba automatizada: ejecutar casos enlazados en la matriz y comparar aserciones con resultado PASS; inspección para los límites indicados. El criterio observable exacto es el enunciado ACT en H1. |
| Restricciones y pendientes | Saturación y errores probados con dobles; no captura real. OPEN-02/03/04/07 registran límites y evidencias disponibles; OPEN-08 trata aceptación académica. |
| Estado | Revisado técnicamente; implementado, verificación limitada al alcance de la evidencia vinculada |

## ACT-11

| Atributo | Valor |
|---|---|
| Clase | usabilidad |
| Motivación | Dar información suficiente al operador |
| Origen | NF-04, NF-06; EF-02, EF-06; REF-11, REF-12 |
| Método y criterio | Prueba automatizada: ejecutar casos enlazados en la matriz y comparar aserciones con resultado PASS; inspección para los límites indicados. El criterio observable exacto es el enunciado ACT en H1. |
| Restricciones y pendientes | HTTP y 40 eventos probados; medidor y layout por inspección; no telemetría física. OPEN-02/03/04/07 registran límites y evidencias disponibles; OPEN-08 trata aceptación académica. |
| Estado | Revisado técnicamente; implementado, verificación limitada al alcance de la evidencia vinculada |

## ACT-12

| Atributo | Valor |
|---|---|
| Clase | operación |
| Motivación | Liberar recursos tras cancelar la sesión |
| Origen | NF-03; EF-08; REF-11, REF-12 |
| Método y criterio | Prueba automatizada: ejecutar casos enlazados en la matriz y comparar aserciones con resultado PASS; inspección para los límites indicados. El criterio observable exacto es el enunciado ACT en H1. |
| Restricciones y pendientes | Fin del hilo/cola, no reposo físico; efecto de cerrar pestaña por inspección. OPEN-02/03/04/07 registran límites y evidencias disponibles; OPEN-08 trata aceptación académica. |
| Estado | Revisado técnicamente; implementado, verificación limitada al alcance de la evidencia vinculada |

## ACT-13

| Atributo | Valor |
|---|---|
| Clase | fiabilidad software |
| Motivación | No continuar una secuencia cuyo envío falló |
| Origen | NF-03; EF-05, EF-07, EF-10; REF-11, REF-12 |
| Método y criterio | Prueba automatizada: ejecutar casos enlazados en la matriz y comparar aserciones con resultado PASS; inspección para los límites indicados. El criterio observable exacto es el enunciado ACT en H1. |
| Restricciones y pendientes | Sin reenvío, fallos y parada concurrente probados con sustitutos; no revalidado físicamente. OPEN-02/03/04/07 registran límites y evidencias disponibles; OPEN-08 trata aceptación académica. |
| Estado | Revisado técnicamente; implementado, verificación limitada al alcance de la evidencia vinculada |

## ACT-14

| Atributo | Valor |
|---|---|
| Clase | seguridad de acceso |
| Motivación | Restringir acciones al panel local |
| Origen | NF-05; EF-01; REF-11, REF-12 |
| Método y criterio | Prueba automatizada: ejecutar casos enlazados en la matriz y comparar aserciones con resultado PASS; inspección para los límites indicados. El criterio observable exacto es el enunciado ACT en H1. |
| Restricciones y pendientes | Token/origen probados; Host/límite cuerpo/bind inspeccionados, no auditoría de seguridad completa. OPEN-02/03/04/07 registran límites y evidencias disponibles; OPEN-08 trata aceptación académica. |
| Estado | Revisado técnicamente; implementado, verificación limitada al alcance de la evidencia vinculada |

## ACT-15

| Atributo | Valor |
|---|---|
| Clase | interfaz |
| Motivación | Ofrecer modos de operación explícitos |
| Origen | NF-01, NF-05; EF-02; REF-11, REF-12 |
| Método y criterio | Inspección del componente y ejecución documentada de herramientas/CLI según matriz. El criterio observable exacto es el enunciado ACT en H1. |
| Restricciones y pendientes | Inspección de CLI/captura/BLE; sin pruebas físicas BLE ni todos los fallos del CLI. OPEN-02/03/04/07 registran límites y evidencias disponibles; OPEN-08 trata aceptación académica. |
| Estado | Revisado técnicamente; implementado, verificación limitada al alcance de la evidencia vinculada |

## ACT-16

| Atributo | Valor |
|---|---|
| Clase | verificabilidad |
| Motivación | Permitir revisión reproducible del resultado |
| Origen | NF-06; EF-01, EF-02, EF-03, EF-04, EF-05, EF-06, EF-07, EF-08, EF-09, EF-10, EF-11; REF-01, REF-02, REF-12 |
| Método y criterio | Inspección del componente y ejecución documentada de herramientas/CLI según matriz. El criterio observable exacto es el enunciado ACT en H1. |
| Restricciones y pendientes | Ejecución de herramientas y revisión documental; no aceptación formal de H1. OPEN-02/03/04/07 registran límites y evidencias disponibles; OPEN-08 trata aceptación académica. |
| Estado | Revisado técnicamente; implementado, verificación limitada al alcance de la evidencia vinculada |
