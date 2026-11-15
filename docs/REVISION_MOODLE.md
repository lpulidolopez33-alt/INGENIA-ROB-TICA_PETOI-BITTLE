# Informe de cierre definitivo de VOICE-BITTLE

H1 v0.4, H2, H3 y las evidencias físicas disponibles de H4 se preparan en una entrega
única. Se conservan los 16 requisitos, arquitectura, vocabulario, coreografías y
funcionalidades. Los ensayos físicos ya se realizaron y no se repetirán; los límites
de evidencia no se presentan como tareas físicas obligatorias antes de entregar.

## Correcciones aplicadas

- `bittle_voz.py`: un solo intento de escritura serie; no reconexión ni reenvío
  automáticos. Fallo anterior a write: no_enviado. Excepción durante write, escritura
  parcial, flush o lectura posterior: desconocido. Éxito de I/O: enviado sin
  confirmación física. El último fallo se conserva y bloquea nuevas transmisiones;
  recuperar requiere desconectar/conectar, sin restaurar la cola.
- Cola: descarta también movimientos añadidos detrás de PARA mientras fallaba el
  envío. Una parada explícita sobrevive como solicitud, pero no se transmite por un
  enlace serie bloqueado. Cancelación antes de seleccionar un envío comprobada.
- `bittle_voz.py` y `bittle_web.py`: descartan resultados Vosk vacíos, JSON inválido,
  valores no textuales y resultados parciales; mantienen controles manuales y rechazo
  de resultados tardíos. No se modifica el vocabulario ni se promete resolver todos
  los falsos positivos de reconocimiento.
- `tests/unit/test_cierre_final.py`: 18 casos de regresión añadidos. El doble serie
  del test anterior de formato ASCII se ajusta al contrato real write -> número de bytes.
- H1 y H2 solo reciben aclaraciones puntuales sobre transporte y alcance observado;
  no se crea una nueva versión ni se reescriben sus 16 requisitos.

## Resultados físicos observados

El equipo confirma Bittle normal, Petoi-30AD y COM6 saliente en la sesión comunicada;
funcionamiento por texto, voz individual, panel HTML y varias acciones en cola, y
continuidad de la secuencia al silenciar el micrófono. Las frases, posturas, número
de repeticiones, tiempos, fecha exacta y firmware no están individualizados.
No se atribuyen los tokens de la demostración simulada a una sesión física.

La conversación ajena al catálogo produjo acciones erróneas en simulación con
micrófono, según el usuario. Se conserva ese resultado no satisfactorio. La estrategia
acordada es micrófono apagado salvo dictado, desactivación manual al aceptar la frase
y botón PARA durante ejecución. No es silenciamiento automático ni confirmación
previa. Detalle: [validación del usuario](H3/validacion_usuario.md).

No se registró commit/hash en los ensayos: la versión física exacta no puede
identificarse. `b63ef45` conserva el código anterior como referencia comparativa,
no como prueba del commit utilizado. Las correcciones finales NO se revalidaron
físicamente. [VERSION_ENTREGA](../VERSION_ENTREGA.json) distingue ambas referencias.

## Resultados de software

49/49 pruebas automatizadas PASS: las 31 anteriores se conservan y se añaden 18
regresiones. Se comprueban fallos antes/durante escritura, ausencia de reenvío,
recuperación explícita, escritura parcial, fallo de respuesta, cancelación concurrente,
voz inválida y arranque HTTP sin hardware ni transmisión. Ninguna prueba abre COM
real, micrófono real ni mueve un robot.

Evidencias: [resultados](../evidencias/actual/RESULTADOS.md),
[trazabilidad](H3/TRAZABILIDAD.md), [coherencia](../evidencias/actual/coherencia_documental.json)
y [extracción independiente](../evidencias/actual/extraccion_verificada.json).
La copia extraída se verifica con suite completa, manifiesto, servidor HTTP y
secuencia simulada ksit, kup, ksit, krest, seguida de krest de cierre. El entorno
Python estaba instalado; no se presenta como instalación nueva en otro ordenador.
El número de archivos se obtiene del manifiesto y del registro de extracción, sin
mantener las cifras 94/96 de paquetes anteriores como si fueran las actuales.

## Evidencias anteriores y CR-01

Los registros de 25 pruebas y 94 archivos se conservan con etiqueta HISTORICA en
`evidencias/anteriores/`, con sus resultados originales. Las evidencias vigentes
están en `evidencias/actual/`. El manifiesto identifica todos los archivos del ZIP.
El historial Git portable conserva estados reales; no se han realizado push ni merge.

[CR-01](H3/CR-01.md) sigue siendo la cola con PARA elegida por el equipo, ya
implementada y probada. Se documentó retrospectivamente; no se inventa encargo,
aprobación docente, nuevo desarrollo ni fecha histórica. La corrección final de
robustez se distingue de la incorporación original de la cola.

## Cuestiones no comprobadas

No hay medición de precisión acústica o latencia física, caracterización de todos
los alias/coreografías/BLE, verificación física específica de parada y pérdida de
enlace ni revalidación física de los cambios finales. La aceptación académica y
el reparto individual no se presumen. Se entregan como límites de lo comprobado,
no como condiciones de realizar más ensayos físicos. Una parada software no es
una parada de emergencia ni una confirmación de inmovilidad.

## Cómo utilizar la entrega

Extraer el ZIP; seguir [GUIA.md](../GUIA.md) para instalar dependencias y el modelo
Vosk externo; abrir INICIAR_PANEL.bat y comenzar con Simulación. Para dictar, activar
micrófono, esperar Escuchando y desactivarlo tras aceptar la orden. La cola continúa.
Usar el botón PARA cuando no se escucha. Ante fallo serie, no repetir automáticamente:
revisar el estado y recuperar explícitamente mediante desconectar/conectar.

Carpeta de trabajo y ZIP contienen la misma versión distribuible. No se incluyen
entornos, modelos, cachés, credenciales ni ZIP antiguos. La guía Word exterior
resume el contenido. Los documentos históricos originales se conservan en Git.
