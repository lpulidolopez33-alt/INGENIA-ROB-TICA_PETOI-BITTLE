# VOICE-BITTLE — ARGOS

Entrega final: control por voz española, secuencias de acciones y panel web local.

## Primera instalación

El ZIP no incluye `.venv` ni el modelo de voz. Antes del primer arranque:

1. Instala Python y las dependencias siguiendo [GUIA.md](GUIA.md).
2. Para usar voz, descarga y extrae `vosk-model-small-es-0.42` en
   `modelos/vosk-model-small-es-0.42`, como explica la sección «Modelo de español».
3. Abre `INICIAR_PANEL.bat` y selecciona **Simulación** para comprobarlo sin robot.

La simulación con texto o botones no necesita el modelo. La simulación con voz sí
lo necesita y usa el micrófono real. No hay un instalador automático del modelo.

## Ejecutar

Abre **INICIAR_PANEL.bat** o ejecuta desde esta carpeta:

```powershell
.\.venv\Scripts\python.exe -X utf8 bittle_web.py
```

El panel se abre en http://127.0.0.1:8765, sin conexión y con micrófono apagado.
Primera instalación y modelo externo: [GUIA.md](GUIA.md).
Uso: [PANEL_WEB.md](PANEL_WEB.md). Cola: [SECUENCIAS.md](SECUENCIAS.md).

## Documentación de entrega

- [Índice integral](PROYECTO.md).
- [H1 vigente](docs/h1/H1_v0.4.md) · [PDF](docs/h1/H1_v0.4.pdf).
- [Especificación H2](specs/001-voice-bittle-spec/spec.md) y [arquitectura](specs/001-voice-bittle-spec/plan.md).
- [Informe H3](docs/H3/informe_desarrollo.md) y [resultados](evidencias/actual/RESULTADOS.md).
- [Metodología y uso real de Spec Kit](docs/METODOLOGIA.md).

La carpeta incluye solo aplicación final, documentación vigente y sus pruebas.
El código y documentos anteriores no son necesarios para ejecutarla y no se distribuyen.
El modelo Vosk y las dependencias se instalan aparte. El modelo instalado en el
ordenador de desarrollo no se incorpora al ZIP; cada destinatario debe instalarlo.

PARA solicita equilibrio y cancela pendientes; no garantiza parada física.
Desconectar intenta descanso. Cerrar la pestaña no cierra Python ni el micrófono.

Estado de entrega, evolución del alcance y pendientes académicos: [Cierre y H4](docs/H3/CIERRE_Y_H4.md).

## Uso de voz acordado

Usar el panel con el micrófono apagado salvo al dictar: activar, esperar Escuchando,
decir la orden o secuencia, comprobar su aceptación y desactivar inmediatamente.
La cola sigue ejecutándose con la escucha apagada; para cancelar se pulsa PARA en
el panel. Es una operación manual, no un modo automático ni una confirmación previa.
Procedimiento y límites: [estrategia de escucha](PANEL_WEB.md#estrategia-de-escucha-manual-acordada).

