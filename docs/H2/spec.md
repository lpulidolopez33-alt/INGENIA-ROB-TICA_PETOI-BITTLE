# Feature Specification: VOICE-BITTLE, control por voz del robot cuadrúpedo Petoi Bittle

**Feature Branch**: `001-voice-bittle`

**Created**: 2026-10-26

**Status**: Draft v0.2 (basado en H1 v0.1 modificado; pendiente de revisión por el equipo)

**Input**: User description: "Sistema que permite controlar un robot cuadrúpedo Petoi Bittle mediante órdenes de voz. Reconoce las órdenes válidas, las convierte en instrucciones del robot, rechaza las entradas no reconocidas, informa del estado del sistema y registra cada interacción. Debe poder verificarse sin robot físico siempre que sea posible."

## Objetivo y alcance

El usuario habla al sistema. Si la orden es válida, el robot ejecuta la acción asociada. Si no lo es, el robot no se mueve y el usuario recibe aviso.

**Dentro del sistema (SoI)**: captura de audio, reconocimiento de voz, interpretación de órdenes, control del estado del sistema, comunicación con el robot, interfaz de usuario, registro de eventos.

**Fuera del sistema**: el robot Bittle (cuadrúpedo, controladora y servomotores), el usuario, el entorno acústico y el procedimiento de supervisión física. El Bittle se trata como un actuador externo con el que el sistema intercambia instrucciones y estado de enlace.

**Fuera del alcance de esta especificación**: la selección final de la tecnología de voz (OPEN-03), las decisiones de implementación (se tratan en plan.md) y las medidas físicas de seguridad del espacio de ensayo (OPEN-09).

## Stakeholders

| ID | Stakeholder | Interés |
|---|---|---|
| STK-01 | Usuario que da órdenes | Obtener la acción pedida con órdenes de voz |
| STK-02 | Personas cercanas al robot | No recibir movimientos inesperados |
| STK-03 | Responsable o propietario del robot | Saber qué ha ocurrido con cada orden y decidir su uso |
| STK-04 | Equipo de desarrollo | Diseñar, implementar y probar el sistema en H1 a H4 |
| STK-05 | Inspección y mantenimiento | Comprobar el equipo y reproducir incidencias |
| STK-06 | Profesorado (cliente y evaluador) | Comprobar los requisitos con pruebas y evidencias reproducibles |

## Necesidades

| ID | Stakeholder | Necesidad | Escenarios |
|---|---|---|---|
| NEC-01 | STK-01 | Que una orden válida produzca la acción esperada sin repetirla | ESC-01, ESC-02 |
| NEC-02 | STK-01 | Que una entrada no reconocida no provoque ningún movimiento | ESC-03, ESC-04 |
| NEC-03 | STK-02 | Que el robot no se mueva de forma inesperada ni sin orden válida | ESC-03 a ESC-07 |
| NEC-04 | STK-03 | Saber si cada orden se ha recibido, rechazado o perdido | ESC-05, ESC-06 |
| NEC-05 | STK-04, STK-06 | Comprobar cada requisito sin disponer del robot físico | Verificación (FR-034) |

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Ordenar sentarse por voz (Priority: P1)

El usuario dice «sentarse» y el robot se sienta.

**Why this priority**: es una de las dos órdenes válidas del encargo.

**Independent Test**: con el robot conectado y el sistema escuchando, se da la orden 10 veces y se cuenta cuántas veces el robot queda sentado.

**Acceptance Scenarios** (ESC-01):

1. **Given** el sistema está escuchando y el robot está conectado, **When** el usuario dice «sentarse» con confianza igual o superior al umbral U, **Then** el robot se sienta y el registro indica «aceptada».

---

### User Story 2 - Ordenar ponerse de pie por voz (Priority: P1)

El usuario dice «ponerse de pie» y el robot se pone de pie.

**Why this priority**: es la segunda orden válida del encargo.

**Independent Test**: con el robot sentado o tumbado, se da la orden 10 veces y se cuenta cuántas veces el robot queda de pie.

**Acceptance Scenarios** (ESC-02):

1. **Given** el robot está conectado y sentado o tumbado, **When** el usuario dice «ponerse de pie» con confianza igual o superior a U, **Then** el robot se pone de pie y el registro indica «aceptada».

---

### User Story 3 - Entradas no reconocidas sin movimiento (Priority: P1)

El usuario dice algo que no es una orden válida. El robot no se mueve y el sistema lo indica.

**Why this priority**: evita actuaciones por error; es el requisito básico de seguridad.

**Independent Test**: se pronuncian 20 frases no válidas y se comprueba que no se envía ningún comando y que cada una produce aviso.

**Acceptance Scenarios**:

1. **Given** el sistema está escuchando, **When** el usuario dice una frase que no es una orden válida (ESC-03), **Then** no se envía ningún comando, el usuario recibe aviso en 2 s como máximo y el registro indica «no reconocida».
2. **Given** el sistema está escuchando, **When** una orden válida se reconoce con confianza inferior a U (ESC-04), **Then** se trata como entrada no reconocida y no se ejecuta nada.

---

### User Story 4 - Captura sin orden (Priority: P2)

El sistema escucha y no recibe ninguna orden en el tiempo máximo de escucha.

**Independent Test**: se inicia una captura sin hablar y se comprueba que termina sin acción del robot.

**Acceptance Scenarios**:

1. **Given** el sistema inicia una captura, **When** transcurre el intervalo máximo de escucha sin texto reconocido (ESC-07), **Then** la captura termina sin movimiento y el sistema queda disponible para un nuevo intento.

---

### User Story 5 - Orden durante una acción en curso (Priority: P2)

El usuario da una orden válida mientras el robot ejecuta otra acción.

**Independent Test**: se da una orden durante una acción simulada y se comprueba el rechazo.

**Acceptance Scenarios**:

1. **Given** el robot ejecuta una acción, **When** el usuario dice una orden válida (ESC-05), **Then** la orden se rechaza, no se encola, y el usuario recibe aviso.

---

### User Story 6 - Pérdida de conexión con el robot (Priority: P2)

El enlace con el robot se pierde durante la ejecución.

**Independent Test**: se simula una desconexión y una reconexión y se comprueba que no hay acciones sin orden nueva.

**Acceptance Scenarios**:

1. **Given** el robot ejecuta una orden, **When** se pierde el enlace (ESC-06), **Then** el sistema informa en 2 s como máximo y no reenvía comandos sin confirmación del usuario.
2. **Given** el enlace se ha restablecido, **When** no hay una orden nueva, **Then** no se ejecuta ninguna orden anterior.

---

### User Story 7 - Resultado físico incorrecto (Priority: P2)

El robot recibe el comando, pero la postura o el movimiento observados no son los esperados.

**Independent Test**: en el ensayo físico se registra la discrepancia como prueba no conforme.

**Acceptance Scenarios**:

1. **Given** el usuario ha dado una orden válida, **When** el robot no adopta la postura esperada (ESC-08), **Then** la prueba queda no conforme, la incidencia queda pendiente de revisión y el envío del comando no se considera evidencia suficiente.

---

### User Story 8 - Estado visible del sistema (Priority: P3)

El usuario ve en la interfaz cómo empezar, si la escucha está activa, si el enlace está activo y en qué estado está el robot.

**Independent Test**: se inicia y finaliza una captura y se comprueba la interfaz en cada estado.

**Acceptance Scenarios**:

1. **Given** la aplicación acaba de abrirse, **When** el usuario mira la interfaz, **Then** ve las órdenes admitidas, la acción asociada a cada una y cómo iniciar la escucha.
2. **Given** una captura está en curso, **When** el usuario mira la interfaz, **Then** ve una señal de escucha activa; al terminar, la señal desaparece.
3. **Given** el robot está conectado o desconectado, **When** el usuario mira la interfaz, **Then** ve si el enlace está activo y el estado de movimiento del robot.

---

### User Story 9 - Registro e historial (Priority: P3)

El responsable revisa cada entrada de voz y cada fallo de comunicación.

**Independent Test**: se realizan 10 interacciones y se comprueba que cada una deja una línea con los campos obligatorios.

**Acceptance Scenarios**:

1. **Given** una entrada de voz procesada, **When** termina su tratamiento, **Then** el registro contiene fecha, hora, texto reconocido y resultado (aceptada o rechazada).
2. **Given** se produce un fallo de comunicación, **When** se detecta, **Then** el registro guarda fecha, hora y tipo de error.
3. **Given** el usuario pide el historial por voz, **When** el sistema responde, **Then** muestra las actividades aceptadas y rechazadas.

---

### Edge Cases

- **Micrófono no disponible**: la escucha se deshabilita, se notifica el fallo y no se intenta mover el robot (FR-027).
- **Confianza justo por debajo de U**: se trata como no reconocida (FR-010).
- **Orden válida durante una acción**: se rechaza y no se encola (FR-005).
- **Postura final distinta de la esperada**: la prueba es no conforme y se registra (ESC-08).
- **Silencio prolongado**: la captura termina sin movimiento (ESC-07).
- **Enlace perdido con otra orden pendiente**: no se envía nada y se informa (ESC-06).

## Requirements *(mandatory)*

### Functional Requirements

La columna «Origen» indica el identificador de H1. Los requisitos marcados como «añadido» se derivan de los escenarios ESC-03 a ESC-07 y no figuraban como requisito explícito en H1 v0.1 (ver sección de correcciones).

| FR | Origen | Requisito |
|---|---|---|
| FR-001 | RF-01 | El sistema MUST reconocer los comandos de voz definidos en el idioma seleccionado. |
| FR-002 | RF-02 | El sistema MUST convertir las órdenes válidas en instrucciones compatibles con el robot. |
| FR-003 | RF-03 | El robot MUST iniciar la acción al recibir cada instrucción validada. |
| FR-004 | RF-04 | El sistema MUST rechazar las órdenes desconocidas sin enviar comandos de movimiento. |
| FR-005 | RF-05 | El sistema MUST rechazar las órdenes recibidas mientras hay una acción en curso. Origen: ESC-05 (añadido). |
| FR-006 | RF-06 | El sistema MUST informar si cada instrucción fue reconocida, rechazada o enviada. |
| FR-007 | RF-07 | El sistema MUST permitir cambiar el idioma activo entre español e inglés. *[NEEDS CLARIFICATION: el encargo y las escenas describen solo español; confirmar si el inglés es obligatorio.]* |
| FR-008 | RF-08 | El sistema MUST finalizar la sesión sin dejar una acción activa, según un procedimiento de cierre validado. |
| FR-009 | RF-09 | Una acción iniciada MUST NOT interrumpirse por otra orden. |
| FR-010 | RF-10 | El sistema MUST tratar como no reconocida toda orden con confianza inferior al umbral U. Origen: ESC-04 (añadido; U se fija en OPEN-04). |
| FR-011 | RF-11 | Ante una entrada no reconocida, el sistema MUST avisar al usuario en 2 s como máximo. Origen: ESC-03 (añadido). |
| FR-012 | RR-01 | El sistema MUST reconocer al menos el 90 % de 100 órdenes válidas en el ensayo de referencia (cinco usuarios, 10 órdenes, dos repeticiones, 0,5–1 m, ruido inferior a 45 dBA). |
| FR-013 | RR-02 | El sistema MUST transmitir al controlador el 95 % de las órdenes válidas reconocidas en 3 s como máximo desde el fin de la locución. |
| FR-014 | RR-03 | El reconocimiento de voz MUST seguir funcionando sin acceso a Internet tras la instalación y descarga de modelos. |
| FR-015 | RS-01 | El sistema MUST NOT iniciar movimientos con órdenes desconocidas o no validadas. |
| FR-016 | RS-02 | El sistema MUST bloquear la aceptación de nuevas acciones cuando detecte un fallo del enlace. |
| FR-017 | RS-03 | El procedimiento de operación MUST disponer de una intervención de seguridad independiente del reconocimiento de voz y del enlace con el ordenador. |
| FR-018 | RI-01 | El sistema MUST comunicarse con el robot mediante un enlace compatible con el robot. |
| FR-019 | RI-02 | El sistema MUST transmitir las acciones con el protocolo de comunicación del fabricante del robot. |
| FR-020 | RI-03 | La interfaz MUST mostrar si el enlace con el robot está activo. |
| FR-021 | RI-04 | La interfaz MUST mostrar las órdenes admitidas y la acción asociada a cada una. |
| FR-022 | RI-05 | La interfaz MUST mostrar una señal que indique que la escucha está activa. |
| FR-023 | RI-06 | La interfaz MUST mostrar el historial de actividades aceptadas y rechazadas cuando se pida por voz. |
| FR-024 | RI-07 | La interfaz MUST mostrar el estado de movimiento del robot. |
| FR-025 | RO-01 | Las pruebas con movimiento MUST realizarse en una superficie estable, seca y despejada, con supervisión presencial. |
| FR-026 | RO-02 | Al iniciar la aplicación, las órdenes de movimiento MUST permanecer inhabilitadas hasta que exista comunicación con el robot. |
| FR-027 | RFI-01 | Si el micrófono no está disponible, la aplicación MUST deshabilitar la escucha y notificar el fallo. |
| FR-028 | RFI-02 | Los errores de transmisión serie MUST notificarse al usuario. |
| FR-029 | RU-01 | La aplicación MUST indicar de forma visible si el reconocimiento está configurado en español o en inglés. |
| FR-030 | RU-02 | Ante una instrucción no reconocida, el sistema MUST pedir al usuario que la repita. |
| FR-031 | RU-03 | El usuario MUST poder activar y desactivar la escucha mediante un control manual. |
| FR-032 | RM-01 | El sistema MUST registrar fecha, hora, texto reconocido y resultado (aceptada o rechazada) de cada instrucción. |
| FR-033 | RM-02 | El sistema MUST registrar los fallos de comunicación con fecha, hora y tipo de error. |
| FR-034 | RD-03 (añadido) | Las funciones de selección y tratamiento de órdenes MUST poder verificarse sin robot físico, con un sustituto de software que registre las instrucciones enviadas. Origen: REQ-12 de H1 v0.1 y NEC-05. |

Los requisitos RD-01 y RD-02 de H1 (uso de Python y de Vosk) son decisiones de diseño y se tratan en plan.md, no aquí.

### Key Entities

- **Orden de voz**: texto reconocido, confianza y marcas de inicio y fin de la captura.
- **Orden válida**: una de las órdenes admitidas por el sistema («sentarse», «ponerse de pie»), con su acción asociada.
- **Instrucción de movimiento**: acción del robot que el sistema envía tras validar una orden.
- **Estado del sistema**: escucha activa o inactiva, enlace activo o inactivo, acción en curso o parado.
- **Registro de evento**: línea con fecha, hora, texto, resultado y, si procede, tipo de error.
- **Aviso**: mensaje al usuario sobre una entrada no reconocida, una orden rechazada o un fallo.

## Success Criteria *(mandatory)*

- **SC-001**: Las órdenes «sentarse» y «ponerse de pie» producen la acción correcta en 10 de 10 intentos cada una en el sustituto de software (FR-001 a FR-003).
- **SC-002**: Ninguna entrada no válida de prueba envía comandos al robot, y cada una produce aviso en 2 s o menos (FR-004, FR-011, FR-015).
- **SC-003**: El 90 % o más de 100 órdenes válidas se reconocen en el ensayo de referencia (FR-012).
- **SC-004**: El 95 % o más de las órdenes reconocidas se transmiten en 3 s o menos desde el fin de la locución (FR-013).
- **SC-005**: El reconocimiento funciona sin Internet tras la instalación (FR-014).
- **SC-006**: Tras una desconexión y reconexión, ninguna orden anterior se ejecuta sin orden nueva (FR-016, FR-026).
- **SC-007**: El 100 % de las entradas aparece en el registro con sus campos obligatorios (FR-032, FR-033).
- **SC-008**: Todos los requisitos tienen método de verificación y pueden comprobarse sin robot, salvo los indicados como físicos (FR-034).

## Assumptions

- La tecnología de reconocimiento y el valor del umbral U no están fijados; se decidirán en plan.md y en H2 (OPEN-03, OPEN-04).
- Las frases exactas aceptadas se definen en la implementación (OPEN-06).
- El modelo exacto del robot y su firmware se confirman antes de los ensayos físicos (OPEN-02).
- Los valores de 2 s y 3 s son propuestas pendientes de ensayo (OPEN-12).
- Las medidas físicas de seguridad se definen con el profesorado (OPEN-09).
- El colectivo de usuario final no está definido; se asume un usuario genérico (OPEN-07).
- El OpsCon del proyecto no está disponible (OPEN-01).
- El tipo de confirmación al usuario y la decisión de rechazar o encolar están pendientes (OPEN-11).

## Correcciones aplicadas a H1 v0.1 (registro de consistencia)

| # | Inconsistencia encontrada en H1 | Decisión tomada en esta especificación |
|---|---|---|
| 1 | La sección 2.2 trata el Bittle como externo; la sección 5 lo incluye en el SoI | El Bittle es externo. El SoI es la aplicación, el micrófono y el enlace. |
| 2 | La sección 3.2 dice «seis escenarios»; hay ocho (ESC-01 a ESC-08) | Se describen ocho escenarios. |
| 3 | Los requisitos RF a RD no están vinculados a los escenarios ESC-07 y ESC-08 | Se mantienen ESC-07 y ESC-08 como escenarios de la historia correspondiente. |
| 4 | Los requisitos RF, RS, RI, RO, RFI, RU y RM citan escenarios OP-N01 a OP-N07 y OP-E01 a OP-E05 que no existen | Se asignan a ESC-01 a ESC-08 según el contenido: OP-N y OP-E de conexión, escucha y órdenes se asocian al escenario equivalente. |
| 5 | La matriz de trazabilidad y la sección 6 usan REQ-01 a REQ-12, y la equivalencia con RF-01 a RNF-04 ya no es válida | Se usan solo los identificadores RF a RD. La matriz se reconstruye en plan.md. |
| 6 | Falta un requisito de umbral de confianza, aunque ESC-04 y el resto de escenarios dependen de U | Se añade FR-010 (RF-10). |
| 7 | Falta el aviso en 2 s ante entrada no reconocida, aunque ESC-03 lo exige | Se añade FR-011 (RF-11). |
| 8 | Falta un requisito de verificación sin robot, aunque el H1 lo pide en NEC-05 | Se añade FR-034 (RD-03). |
| 9 | Latencia: RR-02 fija 3 s desde el fin de la locución; ESC-06 y RFI-02 usan 2 s para detectar pérdida de enlace | Son criterios distintos y no se contradicen. Se mantienen. La latencia de orden a movimiento queda en RR-02 (3 s). |
| 10 | RF-01 y RF-07 exigen español e inglés; el encargo solo habla de español | Se marca como duda (FR-007). |
| 11 | RF-05, RI-04 a RI-07 no tienen escenario de origen | Se asignan a ESC-05 (RF-05) y a la historia 8 (RI-04 a RI-07). |
| 12 | RD-01 (Python), RD-02 (Vosk) y RI-01 y RI-02 (Bluetooth, protocolo Petoi) son decisiones de diseño | Se trasladan a plan.md. La spec mantiene el requisito funcional (comunicación compatible con el robot). |
| 13 | El robot se nombra como «NyBoard» en RF-02 y como «Bittle» en el resto del documento | Se usa «robot» en la spec. La controladora concreta se verifica en plan.md (OPEN-02). |
| 14 | Nombres de órdenes: H1 usa «sentarse» y «ponerse de pie»; el catálogo de versiones anteriores usa «Siéntate» y «Levántate» | Se usan las formas de H1. El catálogo no forma parte de H1 v0.1 y no se incluye. |
