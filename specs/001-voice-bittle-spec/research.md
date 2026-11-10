# Notas de investigación — VOICE-BITTLE

**Versión**: 0.3 · Fuente: H1 v0.2 §2.3 y §2.4 (documentación de Petoi consultada el 2026-10-26: Serial Protocol, Python API, Doc Center). Aquí solo se recogen las decisiones que sostienen el plan; el detalle y las referencias están en el H1.

## Qué puede hacer el robot
- **Hecho (Petoi Serial Protocol):** las *skills* se invocan con un token ASCII que empieza por `k`, sensible a mayúsculas: `ksit` (sentarse), `kup` (ponerse de pie), `kbalance`, marchas `kwkF`/`kwkL`.
- **Incertidumbre:** `kup` está documentado, pero su comportamiento desde sentado o tumbado en nuestro firmware no está comprobado (OPEN-10).
- **Decisión:** solo `ksit` y `kup` entran en el vocabulario por voz; el enlace rechaza cualquier otro token.

## Cómo hablar con el robot
- **Hecho:** la API Python de Petoi exige Python ≥ 3.6, pyserial 3.5 y el repositorio OpenCat completo. La documentación advierte de un posible límite del búfer serie para comandos largos (no afecta a `ksit`/`kup`).
- **Decisión:** usar pyserial directamente y tratar el módulo Bluetooth como un puerto serie. Así el enlace se sustituye por `FakeSerial` en las pruebas y no se depende del repositorio OpenCat.
- **Incertidumbre:** módulo Bluetooth, emparejamiento y puerto (OPEN-15); terminador del comando (T004).

## Modelo de Bittle
- **Hecho:** la documentación consultada cubre Bittle legacy y Bittle X, no el Bittle X V2 (que tiene guía propia).
- **Incertidumbre:** el modelo del equipo está sin comprobar (OPEN-02). Condiciona comandos, conexiones y latencia.

## Reconocimiento de voz
- **Decisión del equipo:** Vosk con modelos locales ES/EN, cargados por ruta (nunca descargados en ejecución), para cumplir RR-03.
- **Gramática:** el adaptador limita Vosk a las frases del vocabulario más `[unk]`, para reducir falsos positivos.
- **Confianza:** se calcula como la media de la confianza por palabra. Si Vosk no entrega un valor utilizable, hay que replantear el umbral U (T012, OPEN-03).
- **Pendiente de validar:** precisión, latencia y funcionamiento sin conexión (T011, T031).

## Diseño sin hardware
- **Decisión:** dos interfaces (`Recognizer`, `SerialPort`) y un reloj inyectable. Permiten verificar lógica, interfaces y tiempos sin micrófono ni robot, y mantienen el núcleo independiente del motor de voz.
- **Límite:** el sustituto no emula posturas ni latencia real; eso exige ensayo físico.
