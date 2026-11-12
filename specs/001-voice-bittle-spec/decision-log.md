# Registro actual de decisiones y pendientes (T002)

Fecha 2026-11-12. Documento nuevo del checkout actual. El registro local H3 anterior
no se ha localizado ni se afirma haber recuperado. Responsables de cierre: equipo /
profesorado según H1; no se han recibido aprobaciones durante esta implementación.

| OPEN | Situación / evidencia necesaria | Estado |
|---|---|---|
| 01 | OpsCon oficial del proyecto | Pendiente |
| 02 | Etiqueta, modelo/placa/firmware reales | Pendiente |
| 03 | Vosk seleccionado; importación y dobles probados; faltan modelos/audio/offline | Validación pendiente |
| 04 | U=0,80 solo simulación; fijar con ensayos y revisión | No aprobado |
| 05 | Instrumento/método y registro acústico en micrófono | Pendiente |
| 06 | Cuatro frases canónicas ES/EN implementadas; sinónimos/revisión de alcance | Pendiente |
| 07 | Colectivo final de usuario | Pendiente |
| 08 | Metadatos/autoría/código y revisión H1 | Pendiente; no se modifica H1 |
| 09 | Intervención independiente, responsable y recuperación | Pendiente; bloquea movimientos |
| 10 | Verificar kup desde posturas relevantes en firmware real | Pendiente |
| 11 | Avisos y atención de consultas durante movimiento | Supuesto: consultas permitidas; aviso visual. TTS pendiente |
| 12 | T_aviso, T_enlace, T_escucha | Valores experimentales; no aprobados |
| 13 | Ensayo 5×10×2 y reparto por idioma/intención | Conservar; no se adopta automáticamente 5×4×5 |
| 14 | Ocupado, fin, reposo y confirmación física | Pendiente; reconexión desconocida; recuperación manual |
| 15 | Módulo, emparejamiento y puerto Bluetooth | Pendiente |

Decisiones de implementación autorizadas por la misión, no aprobaciones de H1:
- Reutilizar arquitectura existente; consola sencilla y simulación por defecto.
- Política de acciones independiente del JSON; solo ksit/kup.
- Rechazo de resultados/confianzas inválidos antes del envío.
- Adaptador físico preparado sin autoapertura; interfaz de consola física bloqueada.
- Reloj monotónico para duración real, final acústico Vosk estimado y no calibrado.
- Evidencias con commit base y huella de archivos; no equivalencia PASS=cumplimiento.
- Reutilización revisada de documentos de dbe0a64 sin merge. T001–T050 mantienen identidad.

RF-05 ya exige rechazar sin encolar; no queda abierta una autorización de colas.
Los objetivos RR-01/RR-02 siguen propuestos; su validación requiere ensayos pertinentes.

## Revisión final para entrega

El usuario comunicó carga de modelo ES y consulta «estado» sin hablar intencionadamente.
No se conserva audio del incidente: causa no determinada. Se verificó carga local
ES y tres PCM sintéticos sin texto; no se ensayó voz humana. Cambio conservador:
decodificación abierta y mínimo por palabra (U sin cambiar), validez por captura.
No demuestra ausencia de falsos positivos ni cierra OPEN-03/04/05.
