# Notas de investigación — VOICE-BITTLE

**Versión**: 0.3 · Fuente: H1 v0.2 §2.3 y §2.4 (documentación de Petoi consultada el 2026-10-26: Serial Protocol, Python API, Doc Center). Aquí solo se recogen las decisiones que sostienen el plan; el detalle y las referencias están en el H1.

## Qué puede hacer el robot
- **Hecho (Petoi Serial Protocol):** las *skills* se invocan con un token ASCII que empieza por `k`, sensible a mayúsculas: `ksit` (sentarse), `kup` (ponerse de pie), `kbalance`, marchas `kwkF`/`kwkL`.
- **Incertidumbre:** `kup` está documentado, pero su comportamiento desde sentado o tumbado en nuestro firmware no está comprobado (OPEN-10).
- **Decisión:** solo `ksit` y `kup` entran en el vocabulario por voz; el enlace rechaza cualquier otro token.

## Cómo hablar con el robot
- **Hecho:** la API Python de Petoi exige Python ≥ 3.6, pyserial 3.5 y el repositorio OpenCat completo. La documentación advierte de un posible límite del búfer serie para comandos largos (no afecta a `ksit`/`kup`).
- **Decisión:** usar pyserial directamente y tratar el módulo Bluetooth como un puerto serie. Así el enlace se sustituye por `FakeSerial` en las pruebas y no se depende del repositorio OpenCat.
- **Incertidumbre:** módulo Bluetooth, emparejamiento y puerto (OPEN-15); terminador del comando (OPEN-02/15, T037 histórico).

## Modelo de Bittle
- **Hecho:** la documentación consultada cubre Bittle legacy y Bittle X, no el Bittle X V2 (que tiene guía propia).
- **Incertidumbre:** el modelo del equipo está sin comprobar (OPEN-02). Condiciona comandos, conexiones y latencia.

## Reconocimiento de voz
- **Decisión del equipo:** Vosk con modelos locales ES/EN, cargados por ruta (nunca descargados en ejecución), para cumplir RR-03.
- **Gramática:** decodificación abierta; el traductor valida las frases. No se fuerza una gramática de cuatro órdenes sobre ruido.
- **Confianza:** se calcula como la mínimo de confianza por palabra. Si Vosk no entrega un valor utilizable, hay que replantear el umbral U (OPEN-03/04).
- **Pendiente de validar:** precisión, latencia y funcionamiento sin conexión (OPEN-03; ensayo manual de GUIA.md).

## Diseño sin hardware
- **Decisión:** dos interfaces (`Recognizer`, `SerialPort`) y un reloj inyectable. Permiten verificar lógica, interfaces y tiempos sin micrófono ni robot, y mantienen el núcleo independiente del motor de voz.
- **Límite:** el sustituto no emula posturas ni latencia real; eso exige ensayo físico.

## Revisión 2026-11-12

Fuentes oficiales y límites de aplicabilidad en docs/H3/preprueba_fisica.md.
No se ha identificado el robot real ni confirmado su `kup`, velocidad o terminador.
Vosk seleccionado no significa validado. Fuentes de integración:
[instalación](https://alphacephei.com/vosk/install),
[modelos](https://alphacephei.com/vosk/models),
[ejemplo de captura](https://github.com/alphacep/vosk-api/blob/master/python/example/test_microphone.py).
La gramática restringida es una medida de diseño, no una medición de falsos positivos.
Se mantiene la mínimo de confianza como experimental; no cambiar U sin ensayo/revisión.
La entrega usa consola y avisos visuales; motor de voz y validación de usabilidad pendientes.

Nota de revisión final: captura Vosk nueva por petición, solo resultados finales con palabras coherentes; silencio PCM nulo descartado; identidad y caducidad por captura. Confianza mínima por palabra experimental, no calibrada. Ver docs/H3/ENTREGA_COMPANEROS.md.
