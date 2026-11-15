# Decisiones del alcance final

Revisión 0.5 · 2026-11-12. El usuario solicita expresamente modificar H1 y la
restante documentación para que la entrega final describa lo implementado.
La línea base vigente es [H1 v0.4](../../docs/h1/H1_v0.4.md). No se atribuye al
profesor evaluación o aprobación de esta revisión.

| Decisión | Resultado vigente |
|---|---|
| DF-01 Idioma | Español; inglés y selector de idioma fuera de alcance |
| DF-02 Órdenes | Catálogo ampliado en COMANDOS.md; voz, texto y botones |
| DF-03 Acción en curso | Se admiten nuevas acciones en cola FIFO, hasta 20 pendientes |
| DF-04 Parada | PARA cancela pendientes/resto de secuencia y solicita equilibrio |
| DF-05 Interfaz | Panel local con conexión, escucha, frase, cola y actividad |
| DF-06 Historial | Hasta 40 eventos en memoria; sin persistencia ni consultas habladas |
| DF-07 Reconocimiento | Vosk local español y validación textual; sin umbral de confianza |
| DF-08 Tiempos | Esperas programadas; se retiran los objetivos numéricos antiguos de precisión/latencia |
| DF-09 Estado | Actividad del ejecutor y sesión/puerto; sin sensor de fin físico |
| DF-10 Errores | Se informa excepción y cancela secuencia; sin reenvío serie; fallo bloquea el transporte hasta desconectar/conectar manualmente |
| DF-11 Entrega | H1 v0.4, H2 y H3 alineados; versiones previas fuera de la entrega, en respaldo externo |

## Límites operativos que permanecen visibles

La parada puede demorarse por I/O o un paso ya seleccionado; no sustituye
intervención física independiente. Ruido puede reconocerse como una orden válida.
La escritura incierta puede repetirse. Cerrar pestaña no termina servidor ni escucha.
La cola y la actividad no sobreviven al cierre. BLE está en CLI y no se ha validado
aquí con el robot. Son límites del prototipo, no funciones añadidas a escondidas
como obligaciones pendientes de esta entrega.

## Información y ensayos por completar si se requieren afirmaciones adicionales

Identificación exacta de firmware/módulo; mediciones de precisión y latencia;
compatibilidad de todas las habilidades; fallos físicos, intervención y recuperación;
ensayo offline registrado. La ausencia de medición no se convierte en resultado PASS.
La configuración y el uso comunicado están en validacion_usuario.md y environment-decision.md.

La relación de OPEN/criterios de H1 v0.2 se conserva en el respaldo externo.
No permanece como lista activa que exija inglés, confianza o historial persistente.

## CR-01 elegido por el equipo, 13/11/2026

El usuario confirma que el profesor no indicó un cambio concreto y autoriza registrar la cola con PARA como CR-01. La implementación precede a esta formalización; no se atribuye aprobación docente. Impacto y pruebas en [CR-01](../../docs/H3/CR-01.md). OPEN-03 se gestiona por separado.

## Escucha manual acordada el 13/11/2026

La estrategia de uso elegida por el equipo mantiene el micrófono apagado salvo al
dictar instrucciones desde el panel. Tras aceptar una orden o secuencia, se desactiva
manualmente la escucha; la cola continúa. PARA se pulsa en pantalla cuando no se escucha.
No hay silenciamiento automático ni confirmación previa: las acciones pueden comenzar
al aceptarse. Persiste la posibilidad de transcripción errónea con escucha activa.
OPEN-03 documenta una limitación conocida con mitigación operativa, no una corrección
software pendiente. El ensayo fallido de conversación se conserva como tal.

Decisión autorizada por el usuario; no supone aceptación académica ni corrección del motor Vosk. Se conserva CR-01 como cambio de cola, separado de esta decisión operativa.

## Corrección final limitada

Se elimina el reenvío serie tras escritura incierta; cualquier fallo exige nueva
sesión explícita y no recupera pendientes. Se conserva el vocabulario y la escucha
manual. Los resultados Vosk inválidos se descartan. Regresión con simuladores;
no se revalidan físicamente estas correcciones. H4 consolida lo ya observado.

