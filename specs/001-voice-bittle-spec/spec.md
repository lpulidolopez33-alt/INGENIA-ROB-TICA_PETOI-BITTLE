# Especificación: VOICE-BITTLE — control por voz del Petoi Bittle

**Versión**: 0.3 (alineada con H1 v0.2) · **Fecha**: 2026-11-12 · **Estado**: borrador pendiente de revisión del equipo
**Fuente principal**: `docs/h1/H1_v0.2.pdf`. Esta especificación **no modifica el H1**: lo concreta.

**Identificadores.** Se usan los del H1 v0.2 sin renombrar: escenarios `ESC-01…13`, necesidades `NEC-01…07`, requisitos por categoría (`RF`, `RR`, `RS`, `RI`, `RO`, `RFI`, `RU`, `RM`, `RD`) y cuestiones abiertas `OPEN-01…15`. Los `FR-xxx` y `REQ-xx` anteriores quedan como referencias históricas recuperables en el commit aa3ea8a; no se renumeran ni se equiparan a requisitos vigentes.
**Dónde está la trazabilidad**: requisito → prueba → resultado se genera en `evidencias/trazabilidad_H3.md` (no se duplica aquí).

## 1. Alcance

El sistema recibe órdenes de voz en **español o inglés** y las traduce a comandos del protocolo serie de Petoi enviados por Bluetooth. Órdenes de **movimiento**: «sentarse» (`ksit`) y «ponerse de pie» (`kup`). **Consultas** (no mueven el robot): «historial» y «estado». Toda entrada no reconocida, dudosa o ausente se rechaza sin mover el robot.

**Frontera del sistema (SoI)**: Bittle (NyBoard, servos, OpenCat) + módulo Bluetooth + ordenador + micrófono + aplicación Python. Fuera: usuario, supervisor, personas próximas y entorno.
**Fuera de alcance**: más órdenes, personalización de voz, parada por voz (la seguridad física es independiente: ESC-13).

## 2. Historias de usuario y escenarios de aceptación

### US1 — Ordenar un movimiento (P1) · ESC-01, ESC-02
Como usuario quiero decir «siéntate» o «ponte de pie» para que Bittle adopte la postura.
- **Dado** enlace activo, escucha activa y Bittle en reposo, **cuando** digo una orden de movimiento válida (confianza finita entre 0 y 1 y ≥ U), modelo cargado y estado conocido, **entonces** se envía exactamente `ksit` o `kup`, el estado pasa a «en curso» y el evento queda registrado como «enviada».
- **Dado** que no hay enlace al iniciar, **cuando** digo cualquier orden de movimiento, **entonces** se rechaza y se avisa (RO-02).
- El resultado físico lo confirma un observador; enviar **no** acredita ejecutar (RM-01).

### US2 — Rechazo seguro de entradas (P1) · ESC-09, ESC-10, ESC-11
- **Dado** escucha activa, **cuando** la entrada está fuera del vocabulario o del idioma activo, **o** su confianza es < U, **o** hay silencio durante T_escucha, **entonces** no se escribe nada en el enlace, se avisa en ≤ T_aviso pidiendo repetir y se registra como rechazada con su motivo.

### US3 — Consultar historial y estado (P2) · ESC-03
- **Cuando** digo «historial» o «estado», **entonces** se muestra la información (órdenes aceptadas y rechazadas con fecha y hora; estado del enlace y del movimiento) **sin escribir en el enlace**. El estado de movimiento es «estimado» o «desconocido» si no hay evidencia del resultado físico.

### US4 — Cambiar de idioma (P2) · ESC-04
- **Cuando** elijo el otro idioma, **entonces** se detiene la escucha, se carga el modelo, la interfaz muestra el idioma y las frases admitidas, y no se envía ningún comando. Si el modelo no carga, se mantiene el idioma anterior y se avisa.

### US5 — Acción en curso y cierre de sesión (P2) · ESC-05, ESC-07
- **Dado** una acción en curso, **cuando** llega otra orden de movimiento válida, **entonces** se rechaza **sin encolarla**, se avisa y no se ejecuta después.
- **Cuando** cierro la sesión, **entonces** se desactiva la escucha y se cierra el enlace. Si hay una acción en curso que no puede confirmarse terminada, no se cierra y se requiere al supervisor.

### US6 — Fallos de enlace y de micrófono (P1) · ESC-08, ESC-12
- **Cuando** se pierde el enlace o falla una escritura, **entonces** en ≤ T_enlace se bloquean las órdenes de movimiento, se avisa, se registra el error (fecha, hora, tipo), el estado de movimiento pasa a «desconocido» y **no se reintenta** ni se reenvía nada al reconectar; reconectar requiere acción del usuario.
- **Cuando** el micrófono no está disponible, **entonces** se deshabilita la escucha, se avisa y se registra el error; el usuario la reactiva con el control manual.

### US7 — Intervención de seguridad independiente (P1) · ESC-13
Procedimiento humano (no software): el supervisor puede parar el robot aunque fallen la voz o el enlace (RS-03). Medio, responsable y recuperación **pendientes** (OPEN-09). No existe orden de parada por voz.

### Casos límite
Orden válida en otro idioma → rechazada · texto con mayúsculas, tildes o signos → se normaliza · orden con confianza justo igual a U → aceptada · fallo de escritura durante el envío → pérdida de enlace · consulta durante un movimiento → se atiende (supuesto, OPEN-11) · resultado físico incorrecto (ESC-06) → no conformidad registrada y revisión antes de repetir.

## 3. Requisitos

Texto completo y criterios en H1 v0.2 §5. Modo de verificación según H1 §6.3.

| Categoría | Requisitos | Resumen | Verificación |
|---|---|---|---|
| RF | RF-01…RF-10 | Reconocer el vocabulario en el idioma activo; convertir movimientos en comandos; postura correcta; rechazar no reconocidas; rechazar sin encolar durante una acción; informar de cada entrada; cambio de idioma; cierre sin marcha activa; no interrumpir una acción con otra orden de voz; consultas sin comandos | Software, salvo RF-01 (integración) y RF-03/RF-08/RF-09 (físico) |
| RR | RR-01…RR-03 | ≥ 90 % de reconocimiento (ensayo de referencia); ≥ 95 % transmitido en ≤ 3 s; reconocimiento sin Internet | RR-01 y RR-02: integración; RR-03: software |
| RS | RS-01…RS-03 | Sin movimientos con entradas no válidas; bloqueo ante fallo de enlace; intervención independiente | RS-01/02 software; RS-03 físico |
| RI | RI-01…RI-07 | Bluetooth con protocolo Petoi; mostrar enlace, órdenes admitidas, escucha activa, historial y estado de movimiento | RI-01/02 integración; RI-03…07 software |
| RO | RO-01, RO-02 | Pruebas con movimiento en superficie estable y con supervisión; órdenes inhabilitadas hasta que haya enlace | RO-01 físico; RO-02 software |
| RFI | RFI-01, RFI-02 | Micrófono caído → escucha deshabilitada; errores de transmisión notificados | Software |
| RU | RU-01…RU-03 | Idioma visible; pedir repetir; control manual de escucha | Software |
| RM | RM-01, RM-02 | Registro de cada entrada y de cada fallo (fecha, hora…) | Software |
| RD | RD-01, RD-02 | Python; Vosk con modelos locales ES/EN | Inspección / software |

## 4. Criterios de éxito (medibles)

- **SC-001** Las 4 órdenes del vocabulario se interpretan correctamente en ES y EN (RF-01) — software.
- **SC-002** Ninguna entrada no válida escribe en el enlace y cada una produce aviso en ≤ T_aviso (RF-04, RS-01).
- **SC-003** ≥ 90 % de reconocimiento en el ensayo de referencia (RR-01) — pendiente de audio real.
- **SC-004** ≥ 95 % de órdenes reconocidas transmitidas en ≤ 3 s (RR-02) — simulado en H3; real en H4.
- **SC-005** Reconocimiento sin Internet tras la instalación (RR-03).
- **SC-006** Tras una desconexión y reconexión no se ejecuta ninguna orden anterior (RS-02).
- **SC-007** El 100 % de las entradas figura en el registro con sus campos (RM-01, RM-02).
- **SC-008** Todos los requisitos tienen método de verificación; los no físicos se comprueban sin robot.

## 5. Decisiones y cuestiones abiertas

| ID | Estado | Decisión / situación |
|---|---|---|
| OPEN-01 OpsCon | Pendiente | Solicitar al profesorado |
| OPEN-02 Modelo de Bittle | Pendiente | Revisar etiqueta/caja (T037 histórico) |
| OPEN-03 Reconocimiento | Adoptado Vosk | Validación técnica pendiente (precisión, latencia, sin conexión) |
| OPEN-04 Umbral U | **Provisional 0,80** | Ajustar con audios reales |
| OPEN-05 Condiciones acústicas | Pendiente | Método de medida de 45 dBA |
| OPEN-06 Frases y sinónimos | Frases canónicas | Sinónimos pendientes |
| OPEN-07 Colectivo de usuario | Pendiente | Consultar al profesorado |
| OPEN-08 Metadatos H1 | Parcial | Falta código documental, autores y hash del commit |
| OPEN-09 Intervención física | Pendiente | **Bloquea los ensayos con movimiento** |
| OPEN-10 `kup` desde sentado/tumbado | Pendiente | Probar en H4 |
| OPEN-11 Avisos y consultas durante movimiento | **Pendiente** | RF-05 ya exige rechazar movimientos sin encolar. Atención de consultas durante movimiento es supuesto de simulación; voz de salida pendiente |
| OPEN-12 Tiempos | **Provisional** | T_aviso 2 s, T_enlace 2 s, T_escucha 5 s, RR-02 3 s |
| OPEN-13 Diseño de RR-01 | Pendiente | Conservar 5×10×2; aclarar el significado de las diez locuciones y reparto por idioma/intención. Alternativa 5×4×5 NO aprobada |
| OPEN-14 Estado físico | **Asumido** | Sin evidencia: «estimado»/«desconocido»; fin de acción lo comunica el operador |
| OPEN-15 Módulo y puerto Bluetooth | Pendiente | Documentar al emparejar |

## 6. Entidades

Ver [data-model.md](./data-model.md).

## 7. Revisión H3 de seguridad y alcance (2026-11-12)

Esta revisión reutiliza el aporte documental de `origin/specs-h1-v02` (dbe0a64),
con correcciones; no es un merge ni una aprobación de sus decisiones.
El SoI sigue H1 v0.2; NyBoard es la descripción del borrador, no identificación
verificada del hardware disponible (OPEN-02).

- Confianza ausente, no numérica, booleana, no finita o fuera de [0,1]: rechazo controlado.
- Resultado mal formado: rechazo sin escritura. La aplicación exige modelo listo y escucha activa para mover.
- El JSON de frases no autoriza acciones: `seguridad.ACCIONES` fija las dos correspondencias.
- Reconectar conserva movimiento desconocido; requiere confirmación manual de reposo.
- Modo físico bloqueado en la consola; el adaptador necesita perfil revisado y autorización de sesión.
- En simulación U=0,80 y tiempos provisionales siguen siendo parámetros de ensayo.
- Consola como interfaz H3 autorizada por la misión; TTS no implementado y aceptación del aviso solo visual pendiente.
- RR-02 se refiere solo a movimientos: duración monotónica estimada desde fin de palabra Vosk
  hasta retorno de escritura; ni ACK del firmware ni ejecución física. Falta calibrar audio/buffer.
- Ningún PASS con dobles verifica por sí solo RD-02, RR-03, RR-01, RR-02, RF-03 o RS-03 completos.

### Matriz H1 v0.2 §6.1 (propuesta del H1, revisión formal pendiente)

| ESC | NEC | Requisitos |
|---|---|---|
| 01 | 04,07 | RO-02, RI-01, RI-03, RI-04, RI-05, RR-03, RU-03 |
| 02 | 01 | RF-01, RF-02, RF-03, RF-06, RR-01, RR-02, RI-02, RM-01 |
| 03 | 04 | RF-10, RI-06, RI-07, RM-01 |
| 04 | 06 | RF-07, RU-01, RI-04, RD-02 |
| 05 | 07 | RF-08, RU-03 |
| 06 | 01,05 | RF-03, RO-01, RM-01 |
| 07 | 03,04 | RF-05, RF-06, RF-09, RI-07 |
| 08 | 03,04 | RS-02, RFI-02, RM-02, RI-03, RO-02 |
| 09 | 02 | RF-04, RF-06, RS-01, RU-02, RM-01 |
| 10 | 02 | RF-04, RS-01, RR-01 |
| 11 | 02 | RF-04, RS-01, RI-05, RU-02 |
| 12 | 04 | RFI-01, RM-02, RU-03 |
| 13 | 03 | RS-03, RO-01, RF-09 |
| Transversal | 05 | RD-01, RD-02 |

Nota de revisión final: captura Vosk nueva por petición, solo resultados finales con palabras coherentes; silencio PCM nulo descartado; identidad y caducidad por captura. Confianza mínima por palabra experimental, no calibrada. Ver docs/H3/ENTREGA_COMPANEROS.md.
