# Guía rápida de validación — VOICE-BITTLE

**Versión**: 0.3 · Cómo comprobar el sistema. Para entender y actualizar el repositorio, ver [`GUIA.md`](../../GUIA.md).

## 1. Validación sin robot (H3) — disponible

```bash
python3 -m pip install pytest
python3 -m pytest -q                 # 56 pruebas; deben pasar todas
python3 tools/generar_evidencias.py  # regenera evidencias/ y avisa de huecos
```

Resultado esperado: `56 passed` y `Casos: 32/32 PASS`. Los resultados y la trazabilidad quedan en `evidencias/resultados_H3.md` y `evidencias/trazabilidad_H3.md`, con el commit de la versión probada.

### Qué cubren las pruebas
| Nivel | Qué se comprueba |
|---|---|
| 1. Interpretación | Órdenes válidas en ES/EN; no reconocidas, otro idioma, confianza < U, silencio |
| 2. Lógica del controlador | ESC-01…ESC-12: estado, avisos, registro, bloqueos y pérdida de enlace |
| 3. Interfaz hacia el robot | Bytes capturados en `FakeSerial` frente a los esperados; lista blanca de tokens |

## 2. Validación con hardware (H4) — pendiente

Requisitos previos: autorización del profesor, **procedimiento de intervención independiente aprobado (OPEN-09)**, superficie estable y supervisor presente (RO-01), modelo de Bittle comprobado (T004).

1. Sustituir `FakeSerial` por un `SerialPort` real (pyserial) y `FakeRecognizer` por `VoskReconocedor` con los modelos locales.
2. Ejecutar los casos TEST-F01 a TEST-F10 de `docs/H3/casos_de_prueba.md` §3, rellenando resultado observado y veredicto.
3. Registrar versión del software (commit), conexión y condiciones iniciales en cada ensayo.

## 3. Ensayos de medida (con datos reales)
- **RR-01:** reconocimiento sobre el conjunto de audios de referencia, a 0,5–1 m y con ruido < 45 dBA. El diseño del ensayo está por aclarar (OPEN-13).
- **RR-02:** latencia fin de locución → comando transmitido, con al menos 20 órdenes.
Los objetivos (90 %, 95 % en 3 s) son propuestas del H1 hasta que el profesorado las confirme.
