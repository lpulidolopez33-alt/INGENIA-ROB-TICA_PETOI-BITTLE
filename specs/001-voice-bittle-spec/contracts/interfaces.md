# Contratos entre componentes — VOICE-BITTLE

**Versión**: 0.3 · Reflejan las interfaces implementadas en `src/`. Cualquier implementación nueva (por ejemplo, el adaptador Vosk o un puerto pyserial real) debe cumplirlas.

## Reconocedor (`voz.Recognizer`)
- `cargar_modelo(idioma)` — lanza `ModeloNoDisponible` si no puede cargarlo.
- `disponible() -> bool` — hay micrófono.
- `escuchar(timeout) -> Resultado | None` — `Resultado(texto, confianza, inicio, fin)`; `None` si no hay texto en `timeout`; lanza `MicrofonoNoDisponible`.
- **Reglas:** no decide qué es una orden válida; un resultado por sí solo nunca mueve el robot; los modelos se cargan por ruta local (RR-03).
- **Trazas:** RF-01, RR-01, RR-03, RD-02, RFI-01.

## Traductor (`traductor.Traductor`)
- `interpretar(resultado, idioma) -> Interpretacion(intencion, motivo)`.
- **Reglas:** busca la frase en el vocabulario del **idioma activo** tras normalizar; confianza < U → `baja_confianza`; texto vacío o `None` → `silencio`; el resto → `no_reconocida`. Nunca devuelve una carga serie arbitraria.
- **Trazas:** RF-01, RF-04, RS-01.

## Gestor de estado (`estado.Gestor`)
- `puede_mover() -> (bool, motivo)`; `enlace_establecido()`, `enlace_perdido()`, `iniciar_accion()`, `fin_accion()`.
- **Reglas:** sin enlace → `sin_enlace`; acción en curso → `accion_en_curso` (no se encola); transiciones inválidas lanzan `TransicionInvalida`.
- **Trazas:** RF-05, RF-09, RO-02, RS-02.

## Enlace con Bittle (`enlace.EnlaceBittle` sobre `SerialPort`)
- `SerialPort`: `abrir()`, `escribir(bytes)`, `cerrar()`, `abierto`.
- `EnlaceBittle(puerto, tokens_permitidos, terminador=b"")`: `conectar()`, `activo()`, `enviar(token)`, `cerrar()`.
- **Reglas:** `enviar` lanza `ValueError` si el token no está en la lista blanca (`ksit`, `kup`) y `LinkError` si el enlace no está activo o falla la escritura; los tokens son ASCII sensibles a mayúsculas; no hay reintentos; el éxito de la escritura **no** prueba la ejecución física.
- **`FakeSerial`:** registra las escrituras e inyecta `desconectar()` y `fallo_escritura`. No emula posturas.
- **Trazas:** RI-01, RI-02, RS-01, RS-02, RFI-02.

## Registro (`registro.Registro`)
- `registrar(texto, resultado, intencion, confianza, motivo, tipo_error, **extra)`, `historial()`, `errores()`.
- **Reglas:** `resultado` ∈ {`aceptada`, `rechazada`, `enviada`, `error`}; cada evento lleva fecha y hora; `historial()` devuelve órdenes aceptadas, enviadas y rechazadas (RI-06).
- **Trazas:** RM-01, RM-02, RI-06.

## Avisos e interfaz (`avisos.Avisos`, `interfaz.construir_vista`)
- `Avisos.emitir(codigo)` guarda el aviso con su momento y, si hay motor, lo dice por el altavoz.
- `construir_vista(controlador)` devuelve enlace, idioma, escucha, órdenes admitidas con su acción, estado de movimiento y últimos avisos.
- **Reglas:** nunca mostrar «ejecutado» solo por haber enviado un comando; avisar ante fallos de micrófono y de transmisión.
- **Trazas:** RF-06, RI-03…RI-07, RU-01, RU-02.

## Controlador (`app.controlador.Controlador`)
`iniciar_sesion`, `activar_escucha`/`desactivar_escucha`, `cambiar_idioma`, `escuchar`, `procesar`, `finalizar_accion(evidencia_fisica)`, `registrar_no_conformidad`, `vigilar_enlace`, `reconectar`, `cerrar_sesion(esperar_fin)`. Implementa los escenarios ESC-01 a ESC-12.

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
