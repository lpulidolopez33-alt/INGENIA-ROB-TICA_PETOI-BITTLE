# Tareas y criterios de finalización

Revisión 13/11/2026. Generadas/revisadas con el flujo speckit-tasks recuperado.
Una casilla marcada significa criterio software comprobado, no aceptación física.
Responsable: equipo ARGOS; nombres en docs/EQUIPO.md; reparto individual pendiente.
T001-T017 identifican tareas de esta revisión. El seguimiento ACT-T anterior queda en Git.

## Fase Base

- [x] T001 Preservar antecedentes e identificar equipo y fuentes en `docs/EQUIPO.md`.
  Dependencias: ninguna. Requisitos: ACT-16.
  Finalización: Nombres confirmados y fuentes localizadas; originales recuperables en Git. Estado: Hecho.

- [x] T002 Completar H1 y fichas docentes en `docs/h1/H1_v0.4.md`.
  Dependencias: T001. Requisitos: ACT-16.
  Finalización: 11 escenarios, 6 necesidades y 16 requisitos con fuentes, método y riesgos. Estado: Hecho.

- [x] T003 Revisar especificación, arquitectura y contratos en `specs/001-voice-bittle-spec/plan.md`.
  Dependencias: T002. Requisitos: ACT-16.
  Finalización: Historias, primer incremento, interfaces y estrategia de integración identificados. Estado: Hecho.

- [x] T004 Generar tareas y relaciones con Spec Kit en `specs/001-voice-bittle-spec/tasks.md`.
  Dependencias: T003. Requisitos: ACT-16.
  Finalización: Tareas con dependencias, criterio, componente y requisitos; ninguna referencia huérfana. Estado: Hecho.

## Fase I1

- [x] T005 [US1] Verificar interpretación de dos órdenes y entrada desconocida en `tests/unit/test_cola_bittle_voz.py`.
  Dependencias: T004. Requisitos: ACT-03, ACT-04, ACT-15.
  Finalización: ksit/kup en orden; desconocida rechaza lote; CLI disponible sin hardware. Estado: Hecho.

- [x] T006 [US1] Verificar sesión, panel y cierre en `tests/unit/test_panel_web.py`.
  Dependencias: T005. Requisitos: ACT-01, ACT-02, ACT-11, ACT-12, ACT-14, ACT-15.
  Finalización: Inicio apagado, sesión simulada, protección HTTP y desconexión comprobados. Estado: Hecho.

## Fase I2

- [x] T007 [US2] Verificar cola, tiempos, cancelación y error concurrente en `tests/unit/test_contratos_moodle.py`.
  Dependencias: T005. Requisitos: ACT-05, ACT-06, ACT-07, ACT-08, ACT-12, ACT-13.
  Finalización: FIFO/límite, mínimos y PARA tras fallo pasan pruebas; no implica parada física. Estado: Hecho.

## Fase I1

- [x] T008 [US1] Añadir recorrido de aceptación HTTP y adaptación serie en `tests/unit/test_contratos_moodle.py`.
  Dependencias: T006, T007. Requisitos: ACT-02, ACT-03, ACT-04, ACT-08, ACT-13, ACT-14.
  Finalización: Dos órdenes por API producen tokens; desconocida HTTP 400 no añade nada; bytes ASCII+LF correctos. Estado: Hecho.

## Fase I3

- [x] T009 [US3] Verificar captura cancelable, saturación y eventos en `tests/unit/test_contratos_moodle.py`.
  Dependencias: T006. Requisitos: ACT-09, ACT-10, ACT-11.
  Finalización: Dobles de audio, sin dispositivo real: apagado por saturación y últimos 40 eventos. Estado: Hecho.

## Fase I4

- [x] T010 [US4] Regenerar evidencias y trazabilidad en `tools/generar_evidencias_actuales.py`.
  Dependencias: T007, T008, T009. Requisitos: ACT-16.
  Finalización: Suite completa PASS; matriz escenario-necesidad-ACT-tarea-código-prueba-resultado vigente. Estado: Hecho.

- [x] T011 [US4] Revisar coherencia y PDF H1 en `tools/verificar_documentacion.py`.
  Dependencias: T010. Requisitos: ACT-16.
  Finalización: Sin enlaces/trazas rotos; PDF legible y requisitos iguales a spec.md. Estado: Hecho.

- [x] T012 [US4] Registrar versión H3 en Git local en `VERSION_ENTREGA.json`.
  Dependencias: T011. Requisitos: ACT-16.
  Finalización: Commit real de fuentes y evidencias referenciado; sin push ni merge. Estado: Hecho.

- [x] T013 [US4] Verificar ZIP desde extracción independiente en `tools/empaquetar.py`.
  Dependencias: T012. Requisitos: ACT-16.
  Finalización: ZIP íntegro; extracción pasa suite y cuatro acciones simuladas en orden. Estado: Hecho.

## Fase H4

- [x] T014 Consolidar evidencia de voz y escucha manual en `docs/H3/preprueba_fisica.md`.
  Dependencias: T013. Requisitos: ACT-03, ACT-04, ACT-09, ACT-10, ACT-15.
  Finalización: Separar observación comunicada, simulación y aspectos sin registro; sin exigir nuevas sesiones ni atribuir revalidación física. Estado: Cerrada con evidencia disponible y límites; sin nuevos ensayos físicos.

- [x] T015 Consolidar evidencia de Bittle físico y versión utilizada en `docs/H3/preprueba_fisica.md`.
  Dependencias: T014. Requisitos: ACT-02, ACT-06, ACT-07, ACT-08, ACT-12, ACT-13, ACT-15.
  Finalización: Separar observación comunicada, simulación y aspectos sin registro; sin exigir nuevas sesiones ni atribuir revalidación física. Estado: Cerrada con evidencia disponible y límites; sin nuevos ensayos físicos.

- [x] T016 Documentar CR-01 elegido por el equipo: cola secuencial y PARA en `docs/H3/CR-01.md`.
  Dependencias: T013. Requisitos: ACT-16.
  Finalización: origen del equipo, impacto, implementación y regresión documentados; aceptación académica en T017. Estado: Hecho.

- [ ] T017 Confirmar revisión del equipo, remoto y aceptación en `docs/H3/CIERRE_Y_H4.md`.
  Dependencias: T015, T016. Requisitos: ACT-16.
  Finalización: Responsables individuales y defensa confirmados; aceptación académica; publicación solo autorizada. Estado: Pendiente externo.

## Dependencias y primer incremento

Base T001 → T002 → T003 → T004 → US1. US2 depende del parser de US1; US3 depende
de la sesión de US1. US4 cierra las tres historias. H4 requiere H3 más datos y autorizaciones.
I1 es el primer incremento: siéntate, ponte de pie y una entrada no reconocida, con
adaptador de prueba y HTTP local. Se puede demostrar sin micrófono ni robot.

Se pueden revisar en paralelo los documentos de T002 y los casos existentes tras T001,
pero las modificaciones que comparten archivos se integran secuencialmente. T007 y T009
se ejecutan en serie en esta revisión porque comparten test_contratos_moodle.py.
No se marca [P] artificialmente donde hay dependencia o archivo compartido.

## Cierre

H3 requiere T001-T013. T014-T015 consolidan los ensayos disponibles con límites, sin nuevas sesiones; T016 está cerrada técnicamente; T017 mantiene la aceptación académica pendiente.
El empaquetado y la publicación son estados separados: ZIP local no implica push.
Los criterios y dependencias son verificables hoy, no una cronología histórica inventada.
