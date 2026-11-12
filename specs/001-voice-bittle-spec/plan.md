# Plan de implementación: VOICE-BITTLE

**Versión**: 0.3 (alineado con H1 v0.2 y con el código de `src/`) · **Fecha**: 2026-11-12 · **Spec**: [spec.md](spec.md)

## Resumen

Aplicación de escritorio en Python que escucha órdenes de voz (ES/EN), valida cada una contra un vocabulario cerrado y un umbral de confianza, decide con una máquina de estados si puede ejecutarse y envía `ksit`/`kup` al Bittle por un enlace serie sobre Bluetooth. Toda entrada se registra. El núcleo no depende del micrófono ni del robot: se prueba con sustitutos (`FakeRecognizer`, `FakeSerial`, `FakeReloj`).

## Contexto técnico

| Aspecto | Decisión |
|---|---|
| Lenguaje | Python 3.12.10 verificado en Windows; sintaxis del código requiere ≥3.10. La API Petoi 3.6+ no fija nuestro entorno |
| Dependencias | pyserial 3.5 (enlace), Vosk + sounddevice (voz real), pytest (pruebas) |
| Almacenamiento | Frases en JSON, acciones en política fija; registro JSON Lines |
| Pruebas | pytest, 3 niveles sin robot; ensayos físicos en H4 |
| Restricciones | Sin Internet tras la instalación (RR-03); sin acción con entradas no válidas (RS-01); sin movimiento sin enlace (RO-02); ensayos con movimiento supervisados (RO-01) |
| Valores provisionales | U = 0,80; T_aviso = 2 s; T_enlace = 2 s; T_escucha = 5 s; RR-02 = 3 s (`src/config.py`) |

## Arquitectura

```
micrófono ─► voz ─► traductor ─► app/controlador ─► estado ─► enlace ─► Bittle
                                      │
                         avisos · registro · interfaz
```

| Módulo (`src/`) | Responsabilidad | Requisitos principales |
|---|---|---|
| `vocabulario` | Frases ES/EN (JSON); autorización separada en seguridad.py | RF-01, RS-01 |
| `voz` | Interfaz `Recognizer`; `FakeRecognizer`; adaptador Vosk | RF-01, RR-03, RD-02 |
| `traductor` | ¿Orden válida? (vocabulario, idioma, confianza ≥ U) | RF-04, RS-01 |
| `estado` | DESCONECTADO / REPOSO / EJECUTANDO / DESCONOCIDO | RF-05, RF-09, RO-02, RS-02 |
| `enlace` | Interfaz `SerialPort`; `FakeSerial`; lista blanca de tokens | RI-01, RI-02, RS-01 |
| `registro` | JSON Lines con fecha, hora, texto, resultado, motivo | RM-01, RM-02 |
| `avisos` | Mensajes visuales y de voz | RF-06, RU-02 |
| `interfaz` | Modelo de vista (enlace, idioma, escucha, órdenes, estado) | RI-03…RI-07, RU-01 |
| `app/controlador` | Orquesta los escenarios ESC-01…12 | RF-02…RF-10 |

## Decisiones de diseño

| ID | Decisión | Motivo | Alternativa descartada |
|---|---|---|---|
| D-01 | Python | RD-01 | — |
| D-02 | Vosk con modelos locales ES/EN, cargados por ruta | RD-02, RR-03 | Reconocimiento en la nube |
| D-03 | Confianza por orden = mínimo de confianza por palabra de Vosk | Hace posible comparar con U (pendiente de OPEN-03/04) | Umbral por probabilidad global |
| D-04 | Bluetooth tratado como puerto serie (pyserial) | Permite probar con `FakeSerial` | API de Petoi con repositorio OpenCat completo |
| D-05 | Solo los tokens `ksit` y `kup`; el enlace rechaza cualquier otro | RS-01 | Comandos de bajo nivel por articulación |
| D-06 | Consola mínima sobre el controlador y modelo de vista | RU-03, RI-05…07; el modelo se prueba sin pantalla | Ventana gráfica aplazada |
| D-07 | Voz de salida con el motor del sistema operativo (por elegir) | Altavoz del ordenador | Voz pregrabada |
| D-08 | Estado de movimiento con 4 estados y **escucha como indicador aparte** | ESC-07 exige recibir órdenes durante una acción (**desviación** del diseño de 5 estados) | Banderas sueltas |
| D-09 | Registro en JSON Lines | Fácil de contar en pruebas | Base de datos |
| D-10 | Vocabulario en fichero | OPEN-06 puede cambiar sin tocar código | Constantes |
| D-11 | pytest + sustitutos + reloj inyectable | Tiempos deterministas | Solo pruebas manuales |

## Comprobación de la constitución

| Principio | Cómo se cumple |
|---|---|
| I. Seguridad y comportamiento a prueba de fallos | Lista blanca de tokens; bloqueo sin enlace o con acción en curso; sin reintentos; intervención física independiente (RS-03) |
| II. Fiabilidad de la voz | Umbral U, idioma activo, vocabulario cerrado, aviso en ≤ T_aviso |
| III. Trazabilidad y control de versiones | Marcas `caso/req/esc` en cada prueba y `evidencias/trazabilidad_H3.md` con el commit |
| IV. Verificabilidad | Suite automática sin robot (recuento vigente en evidencias/resultados_H3.md); casos físicos definidos en `docs/H3/casos_de_prueba.md` |
| V. Diseño modular | Un módulo por responsabilidad; interfaces `Recognizer` y `SerialPort` |
| VI. Gestión explícita de la incertidumbre | Tabla de OPEN en spec.md §5; valores provisionales marcados |

## Riesgos

| Riesgo | Efecto | Mitigación |
|---|---|---|
| Vosk no da confianza utilizable | No se puede aplicar U | Ensayo Vosk pendiente; replantear criterio |
| Latencia Bluetooth > 3 s | Incumple RR-02 | Medir en TEST-F06 |
| Modelo de Bittle distinto del supuesto | Comandos o postura inesperados | Verificar en T037 histórico (OPEN-02) |
| Movimiento inesperado en el ensayo | Daño a personas o al robot | OPEN-09 antes de cualquier ensayo; RO-01 |
| `kup` desde sentado falla | ESC-02 incompleto | TEST-F03; documentar alternativa |
| Terminador del comando serie incorrecto | El robot ignora órdenes | `EnlaceBittle(terminador=…)` configurable; confirmar antes de H4 |

## Estructura del repositorio

```
docs/h1/H1_v0.2.pdf        H1 vigente
specs/001-voice-bittle-spec/   spec, plan, tasks, research, data-model, contracts, quickstart, checklists
docs/H3/casos_de_prueba.md     casos automáticos y físicos
src/  tests/  tools/           código, pruebas, generador de evidencias
evidencias/                    resultados y trazabilidad (generados)
```

## Integración implementada y condiciones de H4

`voice_bittle.py` → `app/consola.py` compone módulos existentes. La simulación
es el modo predeterminado. Vosk puede alimentar FakeSerial mediante `/capturar`.
El transporte `PuertoSerieReal` no abre al construirse; requiere PerfilFisico
completo, referencias de aprobación y habilitación expresa por sesión. La consola
física solo informa bloqueos: no tiene aún un flujo operativo aprobado que abra puertos.

Reconexión y fin de acción física sin evidencia mantienen estado desconocido.
No se implementan reintentos automáticos ni comandos adicionales.
`is_open` solo refleja el recurso local: no acredita conectividad Bluetooth extremo a extremo.
Un supervisor periódico independiente de la captura y un mecanismo de detección física
aplicable al hardware deben validarse antes de habilitar un bucle de operación real.

D-03 (mínimo de confianza), D-07 (TTS), OPEN-04/09/12/14/15 siguen pendientes;
las pruebas con dobles no aprueban estas decisiones. Ver decision-log.md.

Nota de revisión final: captura Vosk nueva por petición, solo resultados finales con palabras coherentes; silencio PCM nulo descartado; identidad y caducidad por captura. Confianza mínima por palabra experimental, no calibrada. Ver docs/H3/ENTREGA_COMPANEROS.md.
