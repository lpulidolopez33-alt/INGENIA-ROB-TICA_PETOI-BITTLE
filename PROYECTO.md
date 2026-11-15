# Índice de la entrega final

| Parte | Contenido |
|---|---|
| Aplicación | bittle_web.py, bittle_voz.py, web/index.html, INICIAR_PANEL.bat |
| Instalación y operación | [GUIA](GUIA.md), [panel](PANEL_WEB.md), [secuencias](SECUENCIAS.md) |
| H1 | [Requisitos v0.4](docs/h1/H1_v0.4.md) · [PDF](docs/h1/H1_v0.4.pdf) |
| Evolución de alcance | [Decisiones sobre requisitos](docs/h1/EVOLUCION_REQUISITOS.md) |
| H2 | [Especificación](specs/001-voice-bittle-spec/spec.md), [plan](specs/001-voice-bittle-spec/plan.md), [datos](specs/001-voice-bittle-spec/data-model.md), [contratos](specs/001-voice-bittle-spec/contracts/interfaces.md) |
| Gestión | [Tareas](specs/001-voice-bittle-spec/tasks.md), [decisiones](specs/001-voice-bittle-spec/decision-log.md), [metodología](docs/METODOLOGIA.md) |
| H3 | [Informe](docs/H3/informe_desarrollo.md), [casos](docs/H3/casos_actuales.md), [resultados](evidencias/actual/RESULTADOS.md) |
| Uso físico | [Confirmaciones del usuario](docs/H3/validacion_usuario.md), [caracterización adicional](docs/H3/preprueba_fisica.md) |
| Verificación | tests/unit/, tools/generar_evidencias_actuales.py, tools/verificar_documentacion.py |
| Distribución | tools/empaquetar.py, VERSION_ENTREGA.json, MANIFIESTO_ENTREGA.json |

H1 v0.4 es la línea base vigente: 16 requisitos ACT, compartidos por H2 y la
trazabilidad ejecutable. El [catálogo](docs/COMANDOS.md) corresponde al parser real.
La entrega conserva 49 pruebas de cola y panel; las pruebas de implementaciones
retiradas no se cuentan como cobertura de esta versión.

No se incluyen históricos, código anterior ni plantillas de herramientas sin uso.
El entorno .venv permite ejecutar localmente pero se excluye del ZIP, junto con
modelos, cachés y registros. Los resultados automáticos, la confirmación del usuario
y las mediciones físicas son evidencias diferentes; no se confunden.

Estado de entrega, evolución del alcance y pendientes académicos: [Cierre y H4](docs/H3/CIERRE_Y_H4.md).

Fuentes docentes: [FUENTES](docs/FUENTES.md). Equipo: [integrantes](docs/EQUIPO.md). Riesgos: [OPEN](docs/h1/ASUNTOS_ABIERTOS.md).

Revisión del encargo docente y pendientes: [REVISION_MOODLE](docs/REVISION_MOODLE.md).
