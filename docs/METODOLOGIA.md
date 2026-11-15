# Proceso de desarrollo y revisión con Spec Kit

El origen incluía configuración Spec Kit y documentos iniciales, recuperados del ZIP original.
La aplicación final recibió ampliaciones de cola y panel con asistencia de Codex; no se
atribuyen invocaciones históricas de Spec Kit a ese trabajo sin registro.

El 13/11/2026 se recuperaron las plantillas, scripts PowerShell y skills de Spec Kit
del material recibido. Se preservó el estado inicial en un commit local real y se
completaron H1, especificación y plan con las fuentes de Moodle. Se aplicó el flujo
speckit-tasks del proyecto para generar historias, dependencias, tareas y criterios.
Los scripts setup-plan, setup-tasks y check-prerequisites proporcionan resolución de
rutas/plantillas; no generan por sí solos el contenido técnico, que revisa el agente/equipo.

La configuración de feature faltaba y se creó .specify/feature.json para la especificación
existente. No hay hooks de extensión configurados. Las nuevas pruebas se derivan de
las tareas de consolidación, sin modificar la lógica del robot. Se registran resultados
en evidencias/actual y el recorrido de herramientas en evidencias/actual/spec_kit.json.

Este uso actual del flujo no demuestra que H1/H2 se elaboraran antes del código.
Los históricos disponibles se preservan en Git; su aceptación académica corresponde al
profesor. En [CIERRE_Y_H4](H3/CIERRE_Y_H4.md) se separa lo verificado de los pendientes.

## Reproducción y versión local

La entrega incluye `.specify/` y `.github/skills/` como recursos del método.
Son plantillas y ayudas de desarrollo, no especificaciones alternativas del producto.
La configuración apunta a `specs/001-voice-bittle-spec`.
Para comprobar los prerrequisitos en Windows desde la raíz:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .specify/scripts/powershell/check-prerequisites.ps1 -Json -RequireSpec -RequireTasks -IncludeTasks
```

H1 se edita en Markdown; su PDF puede regenerarse con
`python tools/generar_h1_pdf.py` tras instalar la dependencia documental opcional
`python -m pip install reportlab==4.4.9`. No es necesaria para usar ni probar la aplicación.
El PDF principal remite a las fichas y anexos Markdown incluidos en docs/h1/.

VERSION_ENTREGA.json identifica el commit de fuentes H3. La copia portable de ese
historial está en `evidencias/actual/historial_h3.bundle`; puede inspeccionarse con
`git bundle verify evidencias/actual/historial_h3.bundle` desde un repositorio Git,
o clonarse en una carpeta nueva con `git clone evidencias/actual/historial_h3.bundle revision-h3`.
Contiene el estado recibido y la consolidación actual, incluidos los originales
recuperados. No crea ni acredita una cronología previa al desarrollo.
Los metadatos posteriores de empaquetado se mantienen separados de ese commit,
para evitar que un archivo intente contener su propia huella. El bundle no es
necesario para ejecutar el programa. No se ha configurado ni publicado un remoto.

## Comprobación independiente del ZIP

Con las dependencias de pruebas instaladas:

```powershell
python tools/verificar_zip.py ../VOICE-BITTLE-ARGOS-ENTREGA-FINAL.zip --destino ../revision_extraida --informe ../auditoria_zip.json
```

Incluye suite, arranque HTTP sin envíos, simulación, enlaces y hashes. El informe externo identifica el ZIP exacto sin autorreferencia. La evidencia interna registra un candidato con los mismos fuentes de ejecución y distingue los metadatos añadidos después.
