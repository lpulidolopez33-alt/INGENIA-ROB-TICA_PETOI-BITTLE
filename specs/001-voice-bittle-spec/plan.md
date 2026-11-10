# Plan de implementación: VOICE-BITTLE

**Versión**: 0.3 (alineado con H1 v0.2 y con el código de `src/`) · **Fecha**: 2026-11-10 · **Spec**: [spec.md](spec.md)

## Resumen

Aplicación de escritorio en Python que escucha órdenes de voz (ES/EN), valida cada una contra un vocabulario cerrado y un umbral de confianza, decide con una máquina de estados si puede ejecutarse y envía `ksit`/`kup` al Bittle por un enlace serie sobre Bluetooth. Toda entrada se registra. El núcleo no depende del micrófono ni del robot: se prueba con sustitutos (`FakeRecognizer`, `FakeSerial`, `FakeReloj`).

## Contexto técnico

| Aspecto | Decisión |
|---|---|
| Lenguaje | Python 3 (RD-01). La API de Petoi pide ≥ 3.6 |
| Dependencias | pyserial 3.5 (enlace), Vosk + sounddevice (voz real), pytest (pruebas) |
| Almacenamiento | Vocabulario en JSON; registro en JSON Lines |
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
| `vocabulario` | Órdenes, frases ES/EN, tokens permitidos (JSON) | RF-01, RS-01 |
| `voz` | Interfaz `Recognizer`; `FakeRecognizer`; adaptador Vosk | RF-01, RR-03, RD-02 |
| `traductor` | ¿Orden válida? (vocabulario, idioma, confianza ≥ U) | RF-04, RS-01 |
| `estado` | DESCONECTADO / REPOSO / EJECUTANDO | RF-05, RF-09, RO-02, RS-02 |
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
| D-03 | Confianza por orden = media de la confianza por palabra de Vosk | Hace posible comparar con U (validar en T010) | Umbral por probabilidad global |
| D-04 | Bluetooth tratado como puerto serie (pyserial) | Permite probar con `FakeSerial` | API de Petoi con repositorio OpenCat completo |
| D-05 | Solo los tokens `ksit` y `kup`; el enlace rechaza cualquier otro | RS-01 | Comandos de bajo nivel por articulación |
| D-06 | Interfaz de ventana mínima sobre un modelo de vista | RU-03, RI-05…07; el modelo se prueba sin pantalla | Consola |
| D-07 | Voz de salida con el motor del sistema operativo (por elegir) | Altavoz del ordenador | Voz pregrabada |
| D-08 | Estado de movimiento con 3 estados y **escucha como indicador aparte** | ESC-07 exige recibir órdenes durante una acción (**desviación** del diseño de 5 estados) | Banderas sueltas |
| D-09 | Registro en JSON Lines | Fácil de contar en pruebas | Base de datos |
| D-10 | Vocabulario en fichero | OPEN-06 puede cambiar sin tocar código | Constantes |
| D-11 | pytest + sustitutos + reloj inyectable | Tiempos deterministas | Solo pruebas manuales |

## Comprobación de la constitución

| Principio | Cómo se cumple |
|---|---|
| I. Seguridad y comportamiento a prueba de fallos | Lista blanca de tokens; bloqueo sin enlace o con acción en curso; sin reintentos; intervención física independiente (RS-03) |
| II. Fiabilidad de la voz | Umbral U, idioma activo, vocabulario cerrado, aviso en ≤ T_aviso |
| III. Trazabilidad y control de versiones | Marcas `caso/req/esc` en cada prueba y `evidencias/trazabilidad_H3.md` con el commit |
| IV. Verificabilidad | 56 pruebas sin robot; casos físicos definidos en `docs/H3/casos_de_prueba.md` |
| V. Diseño modular | Un módulo por responsabilidad; interfaces `Recognizer` y `SerialPort` |
| VI. Gestión explícita de la incertidumbre | Tabla de OPEN en spec.md §5; valores provisionales marcados |

## Riesgos

| Riesgo | Efecto | Mitigación |
|---|---|---|
| Vosk no da confianza utilizable | No se puede aplicar U | Probar en T010; replantear criterio |
| Latencia Bluetooth > 3 s | Incumple RR-02 | Medir en TEST-F06 |
| Modelo de Bittle distinto del supuesto | Comandos o postura inesperados | Verificar en T004 (OPEN-02) |
| Movimiento inesperado en el ensayo | Daño a personas o al robot | OPEN-09 antes de cualquier ensayo; RO-01 |
| `kup` desde sentado falla | ESC-02 incompleto | TEST-F03; documentar alternativa |
| Terminador del comando serie incorrecto | El robot ignora órdenes | `EnlaceBittle(terminador=…)` configurable; confirmar en T004 |

## Estructura del repositorio

```
docs/h1/H1_v0.2.pdf        H1 vigente
specs/001-voice-bittle-spec/   spec, plan, tasks, research, data-model, contracts, quickstart, checklists
docs/H3/casos_de_prueba.md     casos automáticos y físicos
src/  tests/  tools/           código, pruebas, generador de evidencias
evidencias/                    resultados y trazabilidad (generados)
```
