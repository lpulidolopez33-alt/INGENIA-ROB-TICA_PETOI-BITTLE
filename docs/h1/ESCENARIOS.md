# Fichas de escenarios operacionales

Complementan H1 v0.4. Fuentes en [FUENTES](../FUENTES.md); riesgos en [asuntos abiertos](ASUNTOS_ABIERTOS.md).

## EF-01 Inicio y selección de sesión

| Campo | Contenido |
|---|---|
| Tipo | nominal |
| Actores | Usuario STK-01 |
| Precondición | Programa cerrado |
| Disparador | Abrir panel y elegir simulación o COM |
| Interacciones | Abrir; comprobar apagado/desconectado; seleccionar destino; conectar |
| Estado final | Sesión simulada o puerto abierto, sin activar micrófono |
| Variantes y cuestiones abiertas | COM ocupado: EF-10 |
| Fuente | REF-01, REF-11 |
| Requisitos | ACT-01, ACT-02, ACT-14 |

## EF-02 Dos órdenes válidas

| Campo | Contenido |
|---|---|
| Tipo | nominal |
| Actores | Usuario STK-01 y supervisor STK-02 si hay robot |
| Precondición | Sesión abierta; voz solo si escucha activa |
| Disparador | Solicitar siéntate o ponte de pie |
| Interacciones | Recibir texto; interpretar; encolar; enviar ksit o kup; mostrar actividad |
| Estado final | Acción enviada; resultado físico se observa aparte |
| Variantes y cuestiones abiertas | Palabra desconocida: EF-09; compatibilidad: OPEN-02 |
| Fuente | REF-01 p. 5, REF-02 p. 18, REF-11 |
| Requisitos | ACT-03, ACT-04, ACT-11, ACT-15 |

## EF-03 Secuencia

| Campo | Contenido |
|---|---|
| Tipo | nominal |
| Actores | Usuario STK-01 |
| Precondición | Sesión abierta |
| Disparador | Solicitar dos o cuatro acciones |
| Interacciones | Interpretar de izquierda a derecha; encolar; ejecutar cada acción y su espera |
| Estado final | Cola vacía tras terminar pasos software |
| Variantes y cuestiones abiertas | Cola llena: EF-04; PARA: EF-05 |
| Fuente | REF-11, ampliación solicitada |
| Requisitos | ACT-05, ACT-06, ACT-07 |

## EF-04 Nueva orden y límite

| Campo | Contenido |
|---|---|
| Tipo | alternativo |
| Actores | Usuario STK-01 |
| Precondición | Ejecutor ocupado |
| Disparador | Llega otra frase válida |
| Interacciones | Comprobar capacidad; añadir lote al final si cabe; rechazar entero si excede 20 pendientes |
| Estado final | Pendientes preservados en orden o mensaje de rechazo |
| Variantes y cuestiones abiertas | No cuenta acción en curso; no trunca el lote |
| Fuente | REF-11, decisión de diseño |
| Requisitos | ACT-05 |

## EF-05 Cancelación

| Campo | Contenido |
|---|---|
| Tipo | excepcional |
| Actores | Usuario STK-01 o supervisor STK-02 |
| Precondición | Hay acción o pendientes |
| Disparador | Recibir para, quieto, alto o stop |
| Interacciones | Invalidar pendientes/resto coreografía; terminar I/O comprometido; solicitar equilibrio |
| Estado final | Sin pendientes previos; no garantiza postura ni tiempo físico |
| Variantes y cuestiones abiertas | Error concurrente EF-10; OPEN-04 |
| Fuente | REF-11, necesidad de intervención |
| Requisitos | ACT-08, ACT-13 |

## EF-06 Activar y apagar escucha

| Campo | Contenido |
|---|---|
| Tipo | nominal |
| Actores | Usuario STK-01 |
| Precondición | Sesión abierta y modelo instalado |
| Disparador | Activar micrófono y después desactivar |
| Interacciones | Mantener apagado salvo dictado; activar y esperar escuchando; dictar orden o secuencia; comprobar aceptación y desactivar manualmente; rechazar resultados tardíos. Cancelación mediante botón PARA con escucha apagada |
| Estado final | Micrófono apagado; acciones ya aceptadas siguen |
| Variantes y cuestiones abiertas | Carga/captura falla EF-11 |
| Fuente | REF-11 |
| Requisitos | ACT-09, ACT-10, ACT-11 |

## EF-07 Clasificación de fallos

| Campo | Contenido |
|---|---|
| Tipo | excepcional |
| Actores | Usuario STK-01 |
| Precondición | Aplicación iniciada |
| Disparador | Entrada o dispositivo falla |
| Interacciones | Distinguir entrada inválida, conexión y captura; aplicar EF-09, EF-10 o EF-11 |
| Estado final | Error visible o frase rechazada, según caso |
| Variantes y cuestiones abiertas | No confundir disponibilidad física con estado de sesión |
| Fuente | REF-01 p. 9, REF-02 p. 13 |
| Requisitos | ACT-04, ACT-10, ACT-13 |

## EF-08 Cierre

| Campo | Contenido |
|---|---|
| Tipo | nominal |
| Actores | Usuario STK-01 |
| Precondición | Sesión abierta |
| Disparador | Desconectar o cerrar servidor |
| Interacciones | Apagar escucha; cancelar cola; esperar ejecutor; intentar descanso; cerrar enlace |
| Estado final | Sesión desconectada; comprobar robot aparte |
| Variantes y cuestiones abiertas | Cerrar pestaña no desconecta; I/O puede demorar |
| Fuente | REF-11, restricción operacional |
| Requisitos | ACT-12 |

## EF-09 Entrada no reconocida

| Campo | Contenido |
|---|---|
| Tipo | excepcional |
| Actores | Usuario STK-01 |
| Precondición | Sesión abierta |
| Disparador | Introducir siéntate y vuela o no camina |
| Interacciones | Validar frase completa; rechazar desconocida/negación; no añadir acciones |
| Estado final | No se envía acción originada por esa frase; las ya aceptadas siguen |
| Variantes y cuestiones abiertas | Si contiene palabra de parada, ACT-08 prevalece; audio mal transcrito OPEN-03 |
| Fuente | REF-01 p. 5, REF-02 pp. 12 y 18 |
| Requisitos | ACT-03, ACT-04, ACT-08 |

## EF-10 Conexión o envío fallido

| Campo | Contenido |
|---|---|
| Tipo | excepcional |
| Actores | Usuario STK-01 y supervisor STK-02 |
| Precondición | Conectar o ejecutar una acción |
| Disparador | COM ocupado o excepción de envío |
| Interacciones | Apertura fallida vuelve a desconectado; fallo de envío descarta pendientes; muestra error |
| Estado final | No se envía el resto de la secuencia fallida; se conserva PARA concurrente |
| Variantes y cuestiones abiertas | Reintento serie y aceptación de nuevas órdenes: OPEN-04 |
| Fuente | REF-01 p. 9, REF-12 |
| Requisitos | ACT-02, ACT-13 |

## EF-11 Modelo o captura no disponibles

| Campo | Contenido |
|---|---|
| Tipo | excepcional |
| Actores | Usuario STK-01 |
| Precondición | Sesión abierta |
| Disparador | Modelo ausente, fallo captura o audio saturado |
| Interacciones | Mostrar error; terminar escucha; no aceptar resultados posteriores a cancelación |
| Estado final | Micrófono apagado; nivel cero; la cola anterior no se cancela por apagar |
| Variantes y cuestiones abiertas | La consola tiene controles distintos al panel |
| Fuente | REF-01 p. 9, REF-12 |
| Requisitos | ACT-09, ACT-10 |
