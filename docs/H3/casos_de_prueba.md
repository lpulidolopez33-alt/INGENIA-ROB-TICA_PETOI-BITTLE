# VOICE-BITTLE · Casos de prueba (Paso 5) y plan de verificación H3/H4

Base: **H1 v0.2** (requisitos RF/RR/RS/RI/RO/RFI/RU/RM/RD, escenarios ESC-01 a ESC-13).
Campos de cada caso según la diapositiva «¿Cómo se documenta un caso de prueba?»: identificador, requisito asociado, objetivo, precondición, entrada, procedimiento, resultado esperado, resultado observado y veredicto. El **resultado observado y el veredicto** de los casos automáticos se generan en `evidencias/resultados_H3.md` con `python tools/generar_evidencias.py`; los de los casos físicos se rellenan en el ensayo (§3).

## 1. Estrategia

| Nivel | Qué se comprueba | Evidencia |
|---|---|---|
| 1. Interpretación de entradas | Órdenes válidas bien interpretadas; no reconocidas, otro idioma y confianza < U rechazadas | Resultado de `Traductor.interpretar` |
| 2. Lógica del controlador | Cada entrada produce la decisión prevista (estado, aviso, registro) | Decisión, aviso, registro y estado |
| 3. Interfaz hacia el robot | El software escribe el comando previsto en el adaptador de pruebas y solo ese | Bytes capturados en `FakeSerial` frente a los esperados |

Sustitutos: `FakeRecognizer` (voz guionizada, latencias simuladas), `FakeSerial` (registra escrituras, inyecta desconexión y error de escritura) y `FakeReloj` (tiempos deterministas). `FakeSerial` **no emula posturas del firmware**: enviar un comando no acredita ejecución física (RM-01).

**Valores propuestos (pendientes de validar, OPEN-04/OPEN-12):** U = 0,80 · T_aviso = 2 s · T_enlace = 2 s · T_escucha = 5 s · RR-02 = 3 s. Están en `src/config.py`.

**Supuestos adoptados para poder implementar (revisar en equipo):**
- OPEN-11: las consultas («historial», «estado») se atienden también con un movimiento en curso, porque no generan comandos.
- OPEN-14: sin evidencia observada del resultado físico, el estado de movimiento al terminar una acción es «estimado» (nunca «finalizado»). El fin de acción lo comunica el operador/supervisor (`finalizar_accion`).
- La escucha es un indicador independiente del estado de movimiento (desviación de D-08), porque ESC-07 exige recibir órdenes mientras Bittle ejecuta una.
- El terminador del comando serie es configurable (`EnlaceBittle(terminador=...)`, por defecto vacío): confirmar con la documentación de Petoi en T004.

## 2. Casos automatizados (sin robot)

Todos en `tests/`; el identificador figura como `@pytest.mark.caso("TEST-xx")`.

| ID | Req. | ESC | Niv. | Precondición | Entrada / procedimiento | Resultado esperado | Archivo de prueba |
|---|---|---|---|---|---|---|---|
| TEST-01 | RF-01, RD-02 | 02, 03, 04 | 1 | Idioma activo | Las 8 frases canónicas (4 intenciones × ES/EN) con confianza ≥ U | Intención correcta en su idioma | nivel1_interpretacion |
| TEST-02 | RF-04, RS-01 | 09 | 1 | — | «corre», «salta», frase de otro idioma, «kbalance», dos órdenes juntas | No válida (`no_reconocida`) | nivel1_interpretacion |
| TEST-03 | RF-04, RS-01, RF-01 | 10 | 1 | — | «siéntate» con confianza = U y U − 0,01 | = U aceptada; < U `baja_confianza` | nivel1_interpretacion |
| TEST-04 | RF-01 | 02 | 1 | — | «¡Siéntate!», «SIENTATE», con espacios, con punto | Todas válidas (normalización) | nivel1_interpretacion |
| TEST-05 | RS-01, RS-03, RI-02 | 13 | 1 | — | Inspección del vocabulario | Solo `ksit`/`kup`; 4 intenciones; sin orden de parada por voz | nivel1_interpretacion |
| TEST-06 | RF-04 | 11 | 1 | — | `None`, `""`, `"   "` | `silencio` | nivel1_interpretacion |
| TEST-07 | RS-01, RI-02, RF-02 | 02 | 3 | Enlace conectado | Enviar `kbalance`, `m0 30`, `ksit\nkup`, `""`, `KSIT`; después `ksit`, `kup` | Las cinco primeras → `ValueError` sin escritura; después `[b"ksit", b"kup"]` | nivel3_interfaz_robot |
| TEST-08 | RI-01, RFI-02, RS-02 | 08 | 3 | — | Enviar sin conectar; con `fallo_escritura` | `LinkError`, 0 escrituras | nivel3_interfaz_robot |
| TEST-09 | RM-01, RM-02 | 03, 08 | 3 | Registro en fichero | Registrar un envío y un error | JSONL con fecha, hora, texto, resultado (y `tipo_error`) | nivel3_interfaz_robot |
| TEST-10 | RR-03, RD-01 | 01 | 3 | — | **Inspección de código** del adaptador Vosk | Sin red; modelo por ruta local; solo Python | nivel3_interfaz_robot |
| TEST-11 | RO-02, RI-03, RI-05, RU-03, RS-01 | 01 | 2 | Puerto no disponible | Iniciar sesión, activar escucha, «siéntate» | Rechazada `sin_enlace`, 0 escrituras, aviso | escenarios |
| TEST-12 | RO-02, RI-03/04/05, RU-03, RU-01 | 01 | 2 | Aplicación cerrada | Iniciar con enlace y activar escucha | Vista: enlace activo, escucha activa, idioma y 4 órdenes; movimientos habilitados | escenarios |
| TEST-13 | RU-03, RS-01 | 01, 05 | 2 | Sesión activa | Desactivar escucha y decir «siéntate» | No se procesa; 0 escrituras | escenarios |
| TEST-14 | RF-01, RF-02, RF-06, RI-02, RM-01 | 02 | 2 | Sesión activa en reposo | 4 órdenes de movimiento (ES/EN) | Se escribe exactamente `ksit`/`kup`; estado EJECUTANDO / «en_curso»; evento `enviada` | escenarios |
| TEST-15 | RF-06, RF-03, RM-01 | 02, 06 | 2 | Orden enviada | Terminar acción sin y con evidencia física | «estimado» sin evidencia; «finalizado» solo con ella | escenarios |
| TEST-16 | RR-02 | 02 | 2 | Sesión activa | 20 órdenes con latencias simuladas (1 de 20 > 3 s) | ≥ 95 % transmitidas en ≤ 3 s *(la latencia real se mide en TEST-F06)* | escenarios |
| TEST-17 | RF-10, RI-06, RI-07, RM-01 | 03 | 2 | Una orden enviada y una rechazada | «historial» / «estado» (ES y EN) | 0 escrituras nuevas; historial con fecha y hora; estado del enlace y movimiento | escenarios |
| TEST-18 | RI-07, RF-10 | 03, 07 | 2 | Movimiento en curso | «estado» | Se atiende (OPEN-11); sin escrituras nuevas | escenarios |
| TEST-19 | RF-07, RU-01, RI-04, RF-01 | 04 | 2 | Modelos ES y EN | Cambiar a inglés; decir «siéntate» y «sit» | Sin escrituras al cambiar; escucha parada; frases del idioma activo; «siéntate» rechazada, «sit» enviada | escenarios |
| TEST-20 | RF-07, RU-01 | 04 | 2 | Modelo EN no carga | Cambiar a inglés | Se mantiene ES, aviso, 0 escrituras | escenarios |
| TEST-21 | RF-08, RU-03 | 05 | 2 | Reposo | Cerrar sesión | Cierre correcto: escucha off, enlace cerrado, registro completo | escenarios |
| TEST-22 | RF-08, RS-03 | 05, 13 | 2 | Acción en curso | Cerrar sin y con confirmación de fin | Sin confirmación: no cierra y pide supervisor; con ella cierra | escenarios |
| TEST-23 | RM-01, RF-03 | 06 | 2 | Orden enviada | Registrar discrepancia física | Evento no conforme con orden, comando y observado; nunca «finalizado» | escenarios |
| TEST-24 | RF-05, RF-06, RF-09, RI-07 | 07 | 2 | `kup` en curso | «siéntate» | Rechazada, no encolada, aviso; tras el fin de acción no se ejecuta | escenarios |
| TEST-25 | RS-02, RFI-02, RM-02, RI-03, RO-02 | 08 | 2 | Orden en curso | Desconectar el puerto; vigilar cada 0,5 s | Detectada ≤ T_enlace; movimientos bloqueados; «desconocido»; error con fecha/hora/tipo; sin reintento | escenarios |
| TEST-26 | RS-02, RFI-02, RM-02 | 08 | 2 | Sesión activa | Error de escritura al enviar | Estado desconectado, 0 escrituras, aviso y registro | escenarios |
| TEST-27 | RS-02, RF-05 | 08 | 2 | Pérdida de enlace con orden rechazada | Restablecer y reconectar | Nada se reenvía; solo una orden nueva se ejecuta (SC-006) | escenarios |
| TEST-28 | RF-04, RF-06, RS-01, RU-02, RM-01 | 09 | 2 | Escucha activa | Cuatro entradas no reconocidas | 0 escrituras; aviso en ≤ T_aviso que pide repetir; evento `rechazada` | escenarios |
| TEST-29 | RF-04, RS-01, RR-01 | 10 | 2 | Escucha activa | «siéntate» con confianza 0,55 | Rechazada `baja_confianza`, 0 escrituras, aviso ≤ T_aviso | escenarios |
| TEST-30 | RF-04, RS-01, RI-05, RU-02 | 11 | 2 | Escucha activa | Silencio | Captura cerrada tras T_escucha; sin movimiento; aviso; nuevo intento posible | escenarios |
| TEST-31 | RFI-01, RM-02, RU-03 | 12 | 2 | Escucha activa | Micrófono desconectado, luego recuperado | Escucha off, aviso, error registrado; se reactiva manualmente | escenarios |
| TEST-32 | RM-01, RM-02 | 02, 08–12 | 2 | Sesión activa | Mezcla de 6 entradas (válidas, inválidas, baja confianza, silencio) | 100 % en el registro con fecha, hora y resultado (SC-007) | escenarios |

**Limitaciones declaradas:** TEST-10 es una inspección de código (no demuestra funcionamiento sin Internet; eso se prueba en T005). TEST-16 usa latencias simuladas. RR-01 (≥ 90 % de reconocimiento) **no** puede verificarse sin audio real.

## 3. Casos físicos y de integración (H4) — a ejecutar con supervisión

Requieren autorización del profesor (movimientos), superficie estable y supervisor presencial (RO-01). Rellenar *Resultado observado* y *Veredicto* (cumple / no cumple / no concluyente) siguiendo el protocolo de ensayo de la presentación (requisito y prueba, configuración, entrada, esperado, observado, incidencias, veredicto).

| ID | Req. | ESC | Objetivo / procedimiento | Resultado esperado | Observado | Veredicto |
|---|---|---|---|---|---|---|
| TEST-F01 | RI-01, RFI-02 | 01 | Conectar por Bluetooth con el módulo real y comprobar el puerto | Enlace activo; órdenes habilitadas | | |
| TEST-F02 | RF-03, RF-01 | 02 | «siéntate» a 0,5–1 m con el robot de pie | Bittle se sienta | | |
| TEST-F03 | RF-03, RF-01 | 02 | «ponte de pie» desde sentado (y desde tumbado: OPEN-10) | Bittle se pone de pie | | |
| TEST-F04 | RF-03 | 06 | Provocar/observar discrepancia y registrarla | No conformidad registrada; ensayo no repetido sin revisión | | |
| TEST-F05 | RS-02, RO-02 | 08 | Apagar el módulo Bluetooth durante un movimiento | Detección ≤ T_enlace, bloqueo, estado «desconocido» | | |
| TEST-F06 | RR-02 | 02 | Medir latencia fin de locución → comando (≥ 20 órdenes) | ≥ 95 % ≤ 3 s | | |
| TEST-F07 | RR-01, RF-01 | 02, 10 | Ensayo de referencia: 100 órdenes (diseño por aclarar, OPEN-13), ruido < 45 dBA | ≥ 90 % reconocidas | | |
| TEST-F08 | RF-08, RF-09 | 05, 07 | Cerrar la aplicación con y sin acción en curso | Sin marcha activa al cerrar | | |
| TEST-F09 | RS-03, RO-01 | 13 | Simulacro de intervención independiente (medio definido en OPEN-09) | Situación controlada sin depender de voz ni de enlace | | |
| TEST-F10 | RR-03 | 01 | Reconocimiento con Internet desactivado tras la instalación | Funciona (SC-005) | | |

## 4. Gestión de cambios (CR-01)

Cuando se conozca CR-01: (1) comprender el cambio; (2) marcar los ESC, requisitos, tareas y pruebas afectados en `evidencias/trazabilidad_H3.md`; (3) actualizar H1/spec/plan/tasks; (4) implementar; (5) volver a ejecutar `python tools/generar_evidencias.py` como prueba de regresión y añadir los casos nuevos.
