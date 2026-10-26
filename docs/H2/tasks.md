# Tasks: VOICE-BITTLE, control por voz del robot cuadrúpedo Petoi Bittle

**Input**: Design documents from `/specs/001-voice-bittle/` (spec.md v0.2, plan.md v0.2)

**Organization**: Tareas agrupadas por fase y, dentro de las fases de historias, por historia de usuario (US1 a US9), como indica spec.md. Cada tarea enlaza con los requisitos FR que cubre.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: puede ejecutarse en paralelo (ficheros distintos, sin dependencias)
- **[Story]**: historia de usuario de spec.md (US1 a US9)
- Los identificadores de requisito (FR-xxx) se indican al final de cada tarea.

## Phase 1: Setup

- [ ] T001 Crear el repositorio y la estructura `src/`, `tests/`, `evidencias/` según plan.md — NEC-05
- [ ] T002 Documentar en README.md el flujo de Spec Kit y las instrucciones de instalación — NEC-05, FR-034
- [ ] T003 Fijar la versión de Python y crear `requirements.txt` con vosk, pyserial 3.5 y pytest — D-01, FR-034
- [ ] T004 Verificar la placa y el firmware del robot (NyBoard o BiBoard) y registrar el resultado en `evidencias/` — OPEN-02, FR-018, FR-019

## Phase 2: Foundational (bloqueante)

- [ ] T005 [P] Descargar los modelos Vosk de español e inglés y comprobar que funcionan sin Internet en `src/voz/` — FR-001, FR-014
- [ ] T006 [P] Crear `src/vocabulario/vocabulario.json` con «sentarse» y «ponerse de pie», idioma, acción y token — FR-001, FR-002, D-10
- [ ] T007 [P] Definir la interfaz `SerialPort` y `FakeSerial` en `src/enlace/` — FR-018, FR-034
- [ ] T008 [P] Definir la interfaz `Recognizer` y `FakeRecognizer` en `src/voz/` — FR-001, FR-034
- [ ] T009 Implementar la máquina de estados (REPOSO, ESCUCHA, PROCESANDO, EJECUTANDO, DESCONECTADO) en `src/estado/` — FR-005, FR-009, FR-016, FR-026
- [ ] T010 Comprobar con T005 que Vosk entrega una confianza utilizable por orden; registrar el resultado en `evidencias/` — FR-010, OPEN-03
- [ ] T011 [P] Implementar el registro en JSON Lines en `src/registro/` — FR-032, FR-033, D-09
- [ ] T012 Elegir el motor TTS del sistema operativo para la voz de salida y registrar la decisión — FR-006, FR-011, D-07

## Phase 3: US1 y US2 — órdenes obligatorias (P1, MVP)

- [ ] T013 [US1] [US2] Implementar el traductor que valida la frase contra el vocabulario y devuelve la acción en `src/traductor/` — FR-001, FR-002, FR-004, FR-015
- [ ] T014 [US1] Implementar el envío del token `ksit` por la interfaz `SerialPort` en `src/enlace/` — FR-002, FR-003, FR-019
- [ ] T015 [US2] Implementar el envío del token `kup` por la interfaz `SerialPort` en `src/enlace/` — FR-002, FR-003, FR-019
- [ ] T016 [US1] [US2] Implementar la decisión de aceptación según el estado y la confianza en `src/traductor/` — FR-005, FR-009
- [ ] T017 [US1] [US2] Escribir las pruebas ESC-01 y ESC-02 con FakeSerial y FakeRecognizer en `tests/integration/` — FR-001, FR-002, FR-003
- [ ] T018 [US1] Mostrar en el registro el resultado «aceptada» o «rechazada» de cada orden — FR-006, FR-032
- [ ] T019 [US2] Probar `kup` desde postura sentada y tumbada, y registrar el resultado en `evidencias/` — OPEN-10, FR-003
- [ ] T020 [US1] [US2] Medir el tiempo entre el fin de la locución y el envío del comando con FakeSerial — FR-013

## Phase 4: US3 — entradas no reconocidas (P1)

- [ ] T021 [US3] Implementar el umbral U configurable en `src/traductor/` y el tratamiento de confianza inferior a U como no reconocida — FR-010, OPEN-04
- [ ] T022 [US3] Implementar el aviso visual y de voz en 2 s o menos ante una entrada no reconocida en `src/avisos/` — FR-011, FR-030
- [ ] T023 [US3] Escribir las pruebas ESC-03 y ESC-04: ninguna escritura serie y registro «no reconocida» en `tests/integration/` — FR-004, FR-010, FR-011
- [ ] T024 [US3] Implementar la petición de repetir la orden tras una entrada no reconocida en `src/avisos/` — FR-030

## Phase 5: US4 y US5 — captura sin orden y orden durante una acción (P2)

- [ ] T025 [US4] Implementar el tiempo máximo de escucha y la finalización de la captura sin movimiento en `src/captura/` — ESC-07, OPEN-16
- [ ] T026 [US4] Implementar la deshabilitación de la escucha y la notificación si el micrófono no está disponible en `src/captura/` — FR-027
- [ ] T027 [US5] Implementar el rechazo, sin encolar, de órdenes válidas recibidas durante una acción en `src/traductor/` y `src/estado/` — FR-005, FR-009
- [ ] T028 [US5] Escribir las pruebas ESC-05 con una acción simulada en `tests/integration/` — FR-005, FR-009

## Phase 6: US6 y US7 — enlace y resultado físico (P2)

- [ ] T029 [US6] Detectar la pérdida de conexión en 2 s o menos, informar al usuario y no reenviar comandos en `src/enlace/` — FR-016, FR-028
- [ ] T030 [US6] Implementar la reconexión sin ejecución automática de órdenes anteriores en `src/estado/` — FR-016, FR-026
- [ ] T031 [US6] Deshabilitar las órdenes de movimiento al iniciar la aplicación hasta que exista comunicación con el robot en `src/estado/` — FR-026
- [ ] T032 [US7] Registrar la discrepancia física (ESC-08) como prueba no conforme con orden, comando y comportamiento observado en `evidencias/` — ESC-08, FR-025

## Phase 7: US8 y US9 — interfaz, idioma y registro (P3)

- [ ] T033 [US8] Mostrar en la interfaz las órdenes admitidas y la acción de cada una en `src/interfaz/` — FR-021
- [ ] T034 [US8] Mostrar el estado del enlace y el estado de movimiento del robot en `src/interfaz/` — FR-020, FR-024
- [ ] T035 [US8] Mostrar una señal de escucha activa y un control manual para activar o desactivar la escucha en `src/interfaz/` — FR-022, FR-031
- [ ] T036 [US8] Mostrar las instrucciones para iniciar la escucha antes de la primera captura en `src/interfaz/` — FR-022
- [ ] T037 [US8] Permitir cambiar el idioma entre español e inglés y mostrar el idioma activo, si FR-007 se confirma — FR-007, FR-029
- [ ] T038 [US8] Implementar el cierre de sesión sin dejar una acción activa en `src/estado/` — FR-008
- [ ] T039 [US9] Registrar fecha, hora, texto reconocido y resultado de cada entrada en `src/registro/` — FR-032
- [ ] T040 [US9] Registrar fecha, hora y tipo de error de cada fallo de comunicación en `src/registro/` — FR-028, FR-033
- [ ] T041 [US9] Implementar el historial por voz de actividades aceptadas y rechazadas en `src/registro/` y `src/interfaz/` — FR-023

## Phase 8: Validación y ensayos (H3–H4)

- [ ] T042 Ejecutar ESC-01 a ESC-07 con FakeSerial y FakeRecognizer según quickstart y registrar resultados en `evidencias/` — FR-034, SC-008
- [ ] T043 Medir la tasa de reconocimiento en el ensayo de referencia (100 órdenes válidas) y registrar el resultado — FR-012, SC-003
- [ ] T044 Medir la latencia y el porcentaje de órdenes transmitidas en 3 s o menos en ensayos reales — FR-013, SC-004
- [ ] T045 Definir y aprobar con el profesorado el procedimiento de intervención física independiente y las condiciones de superficie — FR-017, FR-025, OPEN-09
- [ ] T046 Ejecutar los ensayos físicos de ESC-01 y ESC-02 con supervisión presencial y registrar resultados en `evidencias/` — FR-003, FR-025
- [ ] T047 Verificar la trazabilidad completa: cada FR tiene al menos una tarea y una prueba asociada — SC-008

## Dependencies & Execution Order

- Phase 1 antes que todo.
- Phase 2 bloquea las fases de historias. T010 depende de T005. T012 bloquea T022 y T037.
- T013 depende de T006 y T008. T014 y T015 dependen de T007. T016 depende de T009 y T013.
- T021 depende de T010. T023 depende de T021 y T022.
- T027 depende de T009 y T016. T029 depende de T007 y T009.
- T042 a T046 dependen de las fases de historias y de T004 para los ensayos físicos.

## Parallel Example

Phase 2: T005, T006, T007, T008, T011 pueden hacerse en paralelo, porque tocan ficheros distintos.

## Implementation Strategy

- **MVP**: Phase 1, Phase 2, Phase 3 y Phase 4. Entrega sentarse, ponerse de pie y el tratamiento de entradas no reconocidas con pruebas sin robot.
- **Incremental**: después, Phase 5 y Phase 6 (seguridad de enlace y captura), Phase 7 (interfaz y registro), y por último Phase 8 (ensayos).
