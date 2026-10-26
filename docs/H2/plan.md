# Implementation Plan: VOICE-BITTLE, control por voz del robot cuadrúpedo Petoi Bittle

**Branch**: `001-voice-bittle` | **Date**: 2026-10-26 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/001-voice-bittle/spec.md`

## Summary

Aplicación de escritorio en Python que escucha órdenes de voz en español (y en inglés si FR-007 se confirma), valida cada orden contra un vocabulario cerrado, decide si la orden puede ejecutarse según el estado del sistema y envía la instrucción correspondiente al robot Petoi Bittle por un enlace serie (cable o módulo Bluetooth). Toda entrada queda registrada. El reconocimiento de voz funciona sin Internet con modelos locales de Vosk. El núcleo se prueba con un puerto serie simulado y un reconocedor simulado (FR-034).

## Technical Context

**Language/Version**: Python 3 (versión concreta a fijar en la tarea T003; la API de Petoi requiere 3.6 o superior)

**Primary Dependencies**: Vosk (reconocimiento offline, modelos español e inglés); pyserial 3.5 (enlace serie); pytest (pruebas); librería de interfaz gráfica a elegir (ver D-06); motor TTS del sistema operativo para la voz de salida (ver D-07)

**Storage**: Ficheros locales: vocabulario en JSON, registro en JSON Lines

**Testing**: pytest con FakeSerial y FakeRecognizer; ensayos físicos en H4

**Target Platform**: Ordenador del equipo con micrófono, altavoz y puerto serie o Bluetooth

**Project Type**: Aplicación de escritorio, proyecto único

**Performance Goals**: 90 % de reconocimiento en el ensayo de referencia (FR-012); 95 % de órdenes transmitidas en 3 s o menos (FR-013); aviso ante entrada no reconocida en 2 s o menos (FR-011)

**Constraints**: Sin Internet después de la instalación (FR-014); sin acción con órdenes no validadas (FR-015); sin acción sin enlace establecido (FR-026); las pruebas con movimiento requieren supervisión (FR-025)

**Scale/Scope**: Dos órdenes válidas en H1; ampliación en H2 por configuración; un robot, un usuario por sesión

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

`.specify/memory/constitution.md` no tiene principios ratificados. No hay gates que comprobar. Recomendación: ratificar la constitución antes de H3 con los principios de seguridad (FR-015 a FR-017) y de verificabilidad (FR-034).

## Project Structure

### Documentation (this feature)

```text
specs/001-voice-bittle/
├── spec.md
├── plan.md
└── tasks.md
```

### Source Code (repository root)

```text
src/
├── vocabulario/      vocabulario.json: órdenes válidas, acción asociada, idioma
├── captura/          captura de audio con marcas de inicio y fin
├── voz/              interfaz Recognizer; implementación Vosk; implementación simulada
├── traductor/        validación de órdenes, umbral U y decisión de aceptación
├── estado/           máquina de estados y reglas de bloqueo
├── enlace/           interfaz SerialPort; adaptador pyserial; FakeSerial
├── interfaz/         ventana principal (ver D-06)
├── avisos/           mensajes al usuario (visual y voz de salida)
└── registro/         registro en JSON Lines y consulta del historial

tests/
├── unit/
└── integration/
```

**Structure Decision**: proyecto único. El núcleo (traductor, estado, enlace) no depende del micrófono ni del robot.

## Phase 0: Research

Cada decisión responde a un requisito de H1 v0.1 (columna «Requisito» en la última columna). Las alternativas descartadas se anotan para que la revisión sea trazable.

| ID | Decisión | Justificación | Alternativas consideradas | Requisitos |
|---|---|---|---|---|
| D-01 | Python 3 para toda la lógica | H1 RD-01 lo exige. La API de Petoi requiere 3.6 o superior (CTX-03). | — | RD-01, FR-034 |
| D-02 | Vosk con modelos locales para español e inglés | H1 RD-02 y RR-03 lo exigen. Funciona sin Internet. | Reconocimiento en la nube (descartado por RR-03) | RD-02, FR-001, FR-014 |
| D-03 | Confianza por orden disponible en la salida del reconocedor | FR-010 necesita comparar con U. Si Vosk no entrega confianza utilizable, FR-010 debe replantearse con el equipo (OPEN-03). | Umbral sobre probabilidad de palabra (a validar) | FR-010 |
| D-04 | Enlace serie con pyserial 3.5; el módulo Bluetooth se usa como puerto serie virtual | H1 RI-01 pide un módulo Bluetooth compatible. El código trata el enlace como serie, lo que permite probarlo con un puerto simulado. | Librería de Petoi con dependencia del repositorio OpenCat (descartada: exige el repositorio completo) | FR-018, FR-019 |
| D-05 | Protocolo de comunicación del fabricante: acciones `ksit` (sentarse) y `kup` (ponerse de pie) | Verificadas en la documentación de Petoi (Serial Protocol y Python API). `kup` desde postura sentada pendiente (OPEN-10). | Envío de comandos de bajo nivel por articulación (descartado: más complejo y sin requisito) | FR-002, FR-003, FR-019 |
| D-06 | Interfaz gráfica mínima en lugar de consola | H1 exige control manual de escucha (RU-03), señal visible de escucha activa (RI-05), historial (RI-06) y estado de movimiento (RI-07). Una consola no cubre bien estos puntos. | Consola (descartada por RU-03 y RI-05) | FR-020 a FR-024, FR-031 |
| D-07 | Voz de salida con el motor TTS del sistema operativo | H1 indica que la voz se reproduce por el altavoz del ordenador. Elegir motor concreto en T012. | Voz pregrabada (descartada: menos flexible) | FR-006, FR-011, FR-030 |
| D-08 | Estado del sistema como máquina de estados: REPOSO, ESCUCHA, PROCESANDO, EJECUTANDO, DESCONECTADO | Un único estado permite bloquear órdenes durante una acción (FR-009), sin enlace (FR-026) o tras un fallo (FR-016). | Banderas independientes (descartadas: estados incoherentes) | FR-005, FR-009, FR-016, FR-026 |
| D-09 | Registro en JSON Lines | Una línea por entrada, legible y fácil de contar en las pruebas. | Base de datos (descartada: sin requisito de consulta compleja) | FR-032, FR-033 |
| D-10 | Vocabulario en fichero de configuración | «sentarse» y «ponerse de pie» pueden cambiar (OPEN-06) sin tocar código. | Constantes en código (descartado) | FR-001, FR-004, FR-015 |
| D-11 | Pruebas con pytest, FakeSerial y FakeRecognizer | Permiten verificar el núcleo sin robot ni micrófono. | Pruebas solo manuales (descartadas por FR-034) | FR-034 |

**Controladora del robot (OPEN-02)**: RF-02 de H1 menciona NyBoard; la documentación de Petoi consultada menciona NyBoard y BiBoard como placas de conexión. La placa del robot del equipo debe verificarse antes de fijar la configuración del enlace (tarea T004).

## Phase 1: Design

### Modelo de datos

- **Orden válida**: `{frase, idioma, accion, token}`. Ejemplo: `{"frase": "sentarse", "idioma": "es", "accion": "sentar", "token": "ksit"}`.
- **Resultado de reconocimiento**: `{texto, confianza, inicio, fin}`.
- **Estado del sistema**: `REPOSO | ESCUCHA | PROCESANDO | EJECUTANDO | DESCONECTADO`.
- **Registro de evento**: `{fecha, hora, texto, confianza, accion_enviada, resultado, tipo_error}`, con `resultado` en `aceptada | rechazada | no reconocida | error`.

Transiciones válidas:
- REPOSO → ESCUCHA: el usuario activa la escucha (RU-03).
- ESCUCHA → PROCESANDO: termina la captura con texto.
- ESCUCHA → REPOSO: tiempo de escucha agotado (ESC-07).
- PROCESANDO → EJECUTANDO: orden válida con confianza ≥ U y sin acción en curso.
- PROCESANDO → REPOSO: orden no válida o confianza < U (aviso, ESC-03 y ESC-04).
- EJECUTANDO → REPOSO: fin de la acción.
- Cualquiera → DESCONECTADO: pérdida de enlace (ESC-06). DESCONECTADO → REPOSO solo con enlace restablecido y sin ejecución automática (FR-016).

### Contratos entre componentes

**Reconocedor (`voz/`)**: entrada: audio de la captura. Salida: `Resultado de reconocimiento`. Error: micrófono no disponible → evento que deshabilita la escucha (FR-027).

**Enlace (`enlace/`)**: entrada: `accion_enviada` (token). Salida: confirmación de escritura o error de transmisión (FR-028). Notifica pérdida de conexión al estado (ESC-06).

**Registro (`registro/`)**: entrada: `Registro de evento`. Salida: línea JSON Lines. Consulta del historial por voz (FR-023).

### Escenario de validación rápida

Ver tarea T042: con FakeSerial y FakeRecognizer se ejecutan ESC-01 a ESC-07 y se comprueba el resultado de cada uno sin robot.

## Riesgos técnicos

| Riesgo | Efecto | Mitigación | Requisito |
|---|---|---|---|
| Vosk no entrega confianza utilizable | FR-010 no se puede aplicar | Probar en T010; si falla, replantear el criterio con el equipo | FR-010 |
| Latencia del enlace Bluetooth | Se supera el 3 s de FR-013 | Medir en T020 y T044; registrar tiempos en el registro | FR-013 |
| Modelo de robot distinto del supuesto | Comandos o postura inesperados | Verificar la placa y el firmware en T004 | FR-019, ESC-08 |
| Movimiento no esperado en el ensayo | Riesgo para personas y el robot | FR-025, FR-017 y procedimiento de intervención independiente | FR-017, FR-025 |
| `kup` desde postura sentada no funciona | ESC-02 incompleto | Probar en T019; documentar alternativa | OPEN-10 |

## Complexity Tracking

| Abstracción | Por qué se necesita | Alternativa más simple rechazada y por qué |
|---|---|---|
| Interfaz `Recognizer` | Permite probar sin micrófono y cambiar de motor de voz | Llamar a Vosk directamente: impide las pruebas sin hardware (FR-034) |
| Interfaz `SerialPort` | Permite probar sin robot | Usar pyserial directamente: impide las pruebas sin robot |
