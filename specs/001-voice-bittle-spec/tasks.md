# Tareas: VOICE-BITTLE

**Versión**: 0.3 · **Entrada**: [spec.md](spec.md), [plan.md](plan.md) · Estado a 2026-11-10.
`[x]` hecho · `[ ]` pendiente. Las pruebas citadas (TEST-xx) están en `docs/H3/casos_de_prueba.md`.
Los requisitos son los del H1 v0.2.

## Fase 1 — Preparación

- [x] T001 Estructura `src/`, `tests/`, `tools/`, `evidencias/` — NEC-05
- [x] T002 `README.md` y `GUIA.md` con instalación y flujo de trabajo — NEC-05
- [x] T003 `requirements.txt` (pyserial 3.5, pytest, vosk, sounddevice) — RD-01
- [ ] T004 Verificar modelo de Bittle, placa, firmware y terminador del comando serie; anotarlo en `evidencias/` — OPEN-02, RI-01

## Fase 2 — Base (bloqueante)

- [x] T005 Vocabulario en JSON (4 intenciones, ES/EN) — RF-01, OPEN-06
- [x] T006 `Recognizer` y `FakeRecognizer` — RF-01
- [x] T007 `SerialPort`, `FakeSerial` y `EnlaceBittle` con lista blanca — RI-02, RS-01
- [x] T008 Máquina de estados — RF-05, RF-09, RO-02
- [x] T009 Registro en JSON Lines — RM-01, RM-02
- [x] T010 Configuración (U, tiempos) y reloj inyectable — OPEN-04, OPEN-12
- [ ] T011 Descargar modelos Vosk ES/EN y comprobar que funcionan sin Internet — RR-03, RD-02, OPEN-03
- [ ] T012 Comprobar con T011 que Vosk entrega una confianza utilizable por orden — OPEN-03, OPEN-04
- [ ] T013 Elegir el motor de voz de salida (TTS) del sistema operativo — RF-06, RU-02

## Fase 3 — US1 y US2: movimiento y rechazo seguro (P1)

- [x] T014 Traductor: vocabulario, idioma y umbral U — RF-01, RF-04, RS-01 (TEST-01…06)
- [x] T015 Envío de `ksit`/`kup` según estado — RF-02, RI-02 (TEST-07, TEST-14)
- [x] T016 Rechazo de entradas no reconocidas, con aviso y registro — RF-04, RF-06, RU-02 (TEST-28, TEST-29)
- [x] T017 Silencio y T_escucha — RF-04 (TEST-30)
- [x] T018 Medida de latencia con enlace simulado — RR-02 (TEST-16)

## Fase 4 — US3, US4, US5: consultas, idioma, acción en curso, cierre (P2)

- [x] T019 Consultas «historial» y «estado» sin comandos — RF-10, RI-06, RI-07 (TEST-17, TEST-18)
- [x] T020 Cambio de idioma ES/EN y fallo de modelo — RF-07, RU-01 (TEST-19, TEST-20)
- [x] T021 Rechazo sin encolar durante una acción — RF-05, RF-09 (TEST-24)
- [x] T022 Cierre de sesión — RF-08 (TEST-21, TEST-22)

## Fase 5 — US6: fallos de enlace y micrófono (P1)

- [x] T023 Detección de pérdida de enlace en ≤ T_enlace, bloqueo y sin reintentos — RS-02, RFI-02, RM-02 (TEST-25, TEST-26)
- [x] T024 Reconexión sin reenviar órdenes anteriores — RS-02 (TEST-27)
- [x] T025 Inicio sin enlace: movimientos inhabilitados — RO-02 (TEST-11)
- [x] T026 Micrófono no disponible — RFI-01 (TEST-31)
- [x] T027 Registro del 100 % de las entradas — RM-01, RM-02 (TEST-32)

## Fase 6 — Interfaz y voz real

- [x] T028 Modelo de vista (enlace, idioma, escucha, órdenes, estado) — RI-03…07, RU-01 (TEST-12)
- [ ] T029 Ventana gráfica que pinta el modelo de vista, con control manual de escucha — RU-03, RI-05
- [ ] T030 Conectar la voz de salida (T013) a `Avisos` — RF-06
- [ ] T031 Probar `VoskReconocedor` con micrófono real — RF-01, RR-01

## Fase 7 — H4: integración física y aceptación

- [ ] T032 Definir y aprobar con el profesorado el procedimiento de intervención independiente y las condiciones de superficie — RS-03, RO-01, OPEN-09 (**bloquea T033 a T037**)
- [ ] T033 TEST-F01 Enlace Bluetooth real — RI-01
- [ ] T034 TEST-F02/F03 Posturas «sentarse» y «ponerse de pie»; `kup` desde sentado y tumbado — RF-03, OPEN-10
- [ ] T035 TEST-F04/F05 Discrepancia física y pérdida de enlace física — RM-01, RS-02
- [ ] T036 TEST-F06 Latencia real fin de locución → comando — RR-02
- [ ] T037 TEST-F07 Ensayo de reconocimiento de referencia (aclarar OPEN-13) — RR-01
- [ ] T038 TEST-F08/F09/F10 Cierre sin marcha activa, simulacro de intervención, sin Internet — RF-08, RS-03, RR-03
- [ ] T039 Gestión del cambio CR-01 según `docs/H3/casos_de_prueba.md` §4

## Fase 8 — Cierre

- [x] T040 Generar trazabilidad automática: `python3 tools/generar_evidencias.py`
- [ ] T041 Completar portada del H1: código documental, autores y hash del commit — OPEN-08
- [ ] T042 Revisar con el equipo los valores provisionales (U, T_aviso, T_enlace, T_escucha) — OPEN-04, OPEN-12

## Dependencias

- T011 → T012 → T031. T013 → T030.
- T032 bloquea todo ensayo con movimiento (T033…T038).
- T004 condiciona T033 y T034.
- T040 se repite tras cada cambio de código o de requisitos.
