# VOICE-BITTLE — proyecto integral ARGOS

Una única entrega: requisitos → diseño → implementación → pruebas y evidencias.

| Fase | Fuente vigente | Conexión con la siguiente fase |
|---|---|---|
| H1 | docs/h1/H1_v0.2.pdf, intacto y pendiente de revisión formal | 13 ESC, 7 NEC, 34 requisitos y OPEN-01…15 |
| H2 | specs/001-voice-bittle-spec/spec.md y plan.md | Matriz H1 §6.1, módulos existentes y tareas históricas conservadas |
| H3 | src/, voice_bittle.py, tests/, tools/, docs/H3/ | Casos TEST-01…37, resultados y manifiesto de código en evidencias/ |
| H4 pendiente | docs/H3/preprueba_fisica.md y TEST-F01…F10 | Voz real, Bluetooth, posturas, seguridad y aceptación no acreditadas |

Para la consola histórica H3, [GUIA.md](GUIA.md) explica instalación y uso.
[README.md](README.md) distingue esa consola de `bittle_voz.py`; para este
último, consulta [GUIA_PASO_A_PASO.md](GUIA_PASO_A_PASO.md),
[SECUENCIAS.md](SECUENCIAS.md) y la situación del panel en [PANEL_WEB.md](PANEL_WEB.md).
ENTREGA_COMPANEROS.md resume esta revisión. El informe de desarrollo conserva el
historial: sus recuentos anteriores están fechados y no sustituyen los resultados
actuales generados. docs/historico conserva originales sin modificar y no es normativo.
La constitución tiene una nota de alineación propuesta; no se ha ratificado una nueva versión.

No hay carpeta H2 duplicada: la documentación H2 vigente es specs/. No se inventan
equivalencias entre REQ históricos y RF/RR/RS vigentes. No se cierran OPEN por tener
pruebas verdes con dobles. Un comando escrito no acredita una postura física.

El ZIP excluye .git, .venv, modelos, cachés, secretos y logs locales. Incluye herramientas
Spec Kit originales para referencia; sus operaciones Git requieren un checkout Git,
pero la aplicación, pytest y el generador funcionan desde el ZIP sin Git.
