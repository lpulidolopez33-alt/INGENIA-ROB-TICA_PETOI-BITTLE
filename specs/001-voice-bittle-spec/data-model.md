# Modelo de datos — VOICE-BITTLE

**Versión**: 0.3 · Refleja el código de `src/`.

## Entidades

| Entidad | Campos | Reglas |
|---|---|---|
| **Intención** (`vocabulario`) | `id`, `tipo` (movimiento \| consulta), `token` (solo movimientos), `descripcion`, `frases` por idioma | Vocabulario cerrado en `vocabulario.json`. Solo `ksit` y `kup` son tokens permitidos |
| **Resultado de reconocimiento** (`voz`) | `texto`, `confianza`, `inicio`, `fin` | `None` = silencio. El reconocedor no decide si es una orden válida |
| **Interpretación** (`traductor`) | `intencion`, `motivo` | `motivo`: `None` (válida), `silencio`, `no_reconocida` o `baja_confianza` |
| **Estado** (`estado`) | `DESCONECTADO`, `REPOSO`, `EJECUTANDO`, `DESCONOCIDO` + indicador `escucha` | Sin enlace no se mueve; con acción en curso se rechaza sin encolar |
| **Estado de movimiento** (controlador) | `reposo`, `en_curso`, `finalizado`, `estimado`, `desconocido` | «finalizado» solo con evidencia física observada; enviar no equivale a ejecutar |
| **Evento de registro** (`registro`) | `fecha`, `hora`, `texto`, `intencion`, `confianza`, `resultado`, `motivo`, `tipo_error` (+ campos extra) | `resultado`: `aceptada`, `rechazada`, `enviada` o `error` |
| **Aviso** (`avisos`) | `codigo`, `texto`, `momento` | Visual y, si hay motor, también por voz |
| **No conformidad física** | evento `error` con `tipo_error=resultado_fisico_incorrecto`, `comando`, `observado`, `veredicto` | ESC-06: se registra antes de repetir el ensayo |

## Relaciones

- Una entrada de voz produce un resultado de reconocimiento o ninguno (silencio).
- Una interpretación válida de movimiento, si el estado lo permite, genera un envío de su token; una consulta nunca llega al enlace.
- Cada entrada y cada fallo producen un evento de registro (RM-01, RM-02).
- Una pérdida de enlace pasa el estado a `DESCONECTADO` y el movimiento a `desconocido`; reconectar no reenvía nada.

## Vocabulario de resultados

| Situación | `resultado` | `motivo` / `tipo_error` |
|---|---|---|
| Movimiento enviado | `enviada` | — |
| Consulta atendida | `aceptada` | — |
| Fuera de vocabulario o idioma | `rechazada` | `no_reconocida` |
| Confianza < U | `rechazada` | `baja_confianza` |
| Silencio | `rechazada` | `silencio` |
| Acción en curso | `rechazada` | `accion_en_curso` |
| Sin enlace | `rechazada` | `sin_enlace` |
| Fallo de escritura | `error` | `error_escritura` |
| Pérdida de enlace | `error` | `perdida_enlace` |
| Micrófono caído | `error` | `microfono_no_disponible` |
| Modelo de voz no carga | `error` | `modelo_voz` |

## Extensiones H3 (2026-11-12)

- Resultado: `fin_monotonic` opcional y `origen_tiempo` (simulado/estimado_vosk).
- Confianza finita numérica [0,1], sin booleanos; resultado mal formado rechazado.
- Acciones fijadas en `seguridad.py`, independientes de frases editables.
- `modelo_listo` y escucha activa bloquean movimientos cuando faltan.
- Reconexión deja estado DESCONOCIDO. `confirmar_reposo(evidencia)` es manual;
  no transmite ni confirma una postura por una escritura.
- `PuertoSerieReal(PerfilFisico, fabrica)` permite pruebas con dobles. Construir
  no abre; `habilitar(referencia_sesion)` necesita aprobaciones declaradas por humanos.
- Final físico sin evidencia no libera el bloqueo; simulación puede finalizar con estado estimado.

Nota de revisión final: captura Vosk nueva por petición, solo resultados finales con palabras coherentes; silencio PCM nulo descartado; identidad y caducidad por captura. Confianza mínima por palabra experimental, no calibrada. Ver docs/H3/ENTREGA_COMPANEROS.md.
