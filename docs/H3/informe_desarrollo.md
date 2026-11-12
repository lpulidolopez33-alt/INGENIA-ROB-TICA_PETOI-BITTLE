# Informe de desarrollo VOICE-BITTLE — H3

> **Alcance histórico:** este informe y sus resultados se refieren a la entrega
> H3 y a `voice_bittle.py`, cuya consola física permanece bloqueada. El
> repositorio incorpora posteriormente `bittle_voz.py`, secuencias y otras
> interfaces con un alcance diferente. Para el estado actual consulta
> [README.md](../../README.md), [SECUENCIAS.md](../../SECUENCIAS.md) y
> [PANEL_WEB.md](../../PANEL_WEB.md). Este informe no valida sus movimientos.

Fecha de entrega: 2026-11-12 (Europe/Madrid). Estado: software funcional en
simulación; integración física preparada parcialmente y BLOQUEADA. No se ha
conectado ni movido Bittle, ni aprobado parámetros o procedimientos pendientes.

## 1. Base Git y preservación del trabajo

La carpeta inicial `INGENIA-ROB-TICA_PETOI-BITTLE-main` era una copia sin `.git`.
Se conserva intacta. Se creó un checkout auténtico independiente `VOICE-BITTLE`
desde origin/main `bb330a9c2512572257237ff5d61c3b4a44da2205`, inicialmente limpio,
y la rama `h3-completar-voice-bittle`. No se modifica main ni se hace push/merge.

La rama local antigua `001-voice-bittle-h3` y sus T001/T002 no están disponibles;
no se presume que se hayan perdido ni que esta entrega los haya recuperado.
Se revisó `origin/specs-h1-v02` (dbe0a64), reutilizando sus documentos y corrigiendo
alcance/estados. No se adoptó su renumeración de T001–T042: se preservan T001–T050
originales como anexo histórico con una tabla actual de trabajos y pendientes.

Commits locales de implementación/documentación: `fbd8f2c`, `a32d182`.
El commit posterior que contiene este informe registra las evidencias de esos cambios.
Revisión base ensayada: `a32d1829169da21bebcbb9aa3b9ddeb574c88602`.
Huella SHA-256 del conjunto ejecutado: `d10d4c9a096cb5e9ce5d029cdd08b12a06a63b807a7eb60a6a3eddbc7a96a340`.
Ver `evidencias/ejecucion_H3.json` para hashes de cada archivo, entorno y cambios
locales al ejecutar. El informe y las evidencias quedan fuera de la huella para
no introducir una dependencia circular; sí incluye código, tests y configuración.

## 2. Problemas y soluciones implementadas

| Problema constatado | Solución / alcance |
|---|---|
| NaN, infinitos y valores fuera de rango autorizaban envío | Validación de tipo numérico nativo, finitud y [0,1]; booleanos, None, tipos y resultados mal formados rechazados |
| JSON editable controlaba autorización motriz | Política inmutable de correspondencias semánticas en seguridad.py; enlace y puerto real validan tokens independientemente |
| U provisional podía llegar a un puerto real | Perfil físico con parámetros explícitos, referencias de revisión y habilitación de sesión; consola física bloqueada |
| Fallo de modelo permitía activar escucha | Estado modelo_listo, inicio fallido controlado y bloqueo de procesamiento motriz |
| Procesar directamente ignoraba escucha | Validación explícita antes de movimiento; consultas no transmiten |
| Reconectar implicaba reposo | DESCONOCIDO y confirmación manual; sin replay ni liberación automática |
| Fin físico sin evidencia liberaba movimientos | Mantiene desconocido y exige reposo observado; simulación queda estimada |
| Fallos de apertura/lectura/overflow de audio | Captura descartada y excepción de dominio; controlador avisa, registra y desactiva escucha |
| No había transporte pyserial integrado en módulos | PuertoSerieReal con apertura explícita, lista exacta, timeout, detección de escritura parcial, sin reintentos y revocación de habilitación tras error |
| No existía aplicación utilizable | Consola sobre controlador existente, demo ES/EN, controles manuales, consultas, avisos y JSONL |
| Fin de voz confundido con retorno Vosk | Último segmento de palabra sobre reloj de captura monotónico; etiqueta estimado_vosk, sin afirmar calibración |
| Evidencias exageraban verificación | Estados parciales por método; commit completo + manifiesto SHA-256; setup/call/teardown y omisiones considerados |
| Spec Kit desalineado | Reutilización revisada de aportación del equipo; H1 v0.2, RF-10, ESC-01…13, NEC-01…07, OPEN-01…15; historia de tareas preservada |

Se mantiene la arquitectura modular original. Las interfaces de voz y transporte
siguen aisladas del controlador. No se añaden movimientos ni comandos de parada.

## 3. Pruebas realmente ejecutadas

Entorno: Windows, Python 3.12.10 64 bits; pytest 9.2.0. Dependencias en `.venv`;
Vosk 0.3.45, sounddevice 0.5.6 y pyserial 3.5 instalados e importados correctamente.
`pip check`: sin dependencias rotas. Listado en `evidencias/entorno_H3.txt`.

| Comprobación | Resultado observado |
|---|---|
| Suite inicial antes de modificar | 56 passed |
| Regresión final completa | **109 passed, 0 failed** |
| Generador de evidencias | **36/36 casos PASS**, salida 0 |
| Demo de consola ES | salida 0; solo `[b'ksit', b'kup']` simulados |
| Demo de consola EN | salida 0; solo `[b'ksit', b'kup']` simulados |
| Vosk sin modelo local | salida 1 y mensaje controlado; no se captura audio |
| Selección modo físico | salida 2 y bloqueo explícito; no se abre puerto |
| git diff --check | sin errores |
| H1 original | SHA-256 conservado: F95C7DB7E33CDB6EEEC067D75323187057EC53F1A7FBC00B58404EC0CC5EE1A5 |

Salidas de las cuatro comprobaciones ejecutables en `evidencias/comprobaciones_consola.json`.
TEST-01…32 se conservan; TEST-27 exige ahora confirmar reposo tras reconexión.
TEST-33…36 añaden seguridad, adaptadores, consola y fiabilidad del generador.
Las 109 pruebas incluyen parametrizaciones; no son 109 casos operacionales.
Durante el desarrollo se corrigió una prueba nueva que intentaba mover tras
solicitar cierre sin reactivar escucha: se conservó el bloqueo del controlador.

Vosk/audio/serial se probaron con dobles, también conectados al controlador para
las ocho frases canónicas y fallos de captura. Ninguna prueba usó modelos reales,
micrófono real, Bluetooth real, controlador físico ni observación de posturas.
Importar una biblioteca no acredita que reconozca voz correctamente.

## 4. Requisitos y límites de cobertura

La matriz generada contiene los 34 requisitos de H1. Los marcadores son relaciones
de cobertura de pruebas, no una aprobación de la matriz ni cumplimiento completo.

- RF-02/04/05/06/07/09/10, RS-01/02, RO-02, RFI-01/02, RI-03…07,
  RU-01…03 y RM-01/02: lógica, estados, consola, registro y rutas de error probadas
  en el alcance de casos simulados. RF-08 tiene cierre lógico parcial.
- RD-01: código Python inspeccionado/ejecutado.
- RD-02: integración del adaptador probada con dobles; faltan modelos ES/EN reales.
- RR-01: no se ha medido precisión. Mantener 5×10×2 hasta resolver OPEN-13.
- RR-02: tiempos simulados y estimación Vosk con dobles; no latencia física, ACK ni postura.
- RR-03: inspección de ruta local; falta ensayo real sin Internet.
- RI-01/02: transporte probado con dobles; compatibilidad del robot no demostrada.
- RF-03, RF-08/09 físicos, RS-03 y RO-01: requieren observación/procedimiento físico.
- TTS no implementado: los avisos de consola son visuales; modalidad sonora/usabilidad pendiente.

Las afirmaciones generales antiguas «Verificado sin robot» se han sustituido por
alcances concretos. No se editaron manualmente veredictos para aparentar cumplimiento.

## 5. Decisiones y bloqueos

Registro detallado en `specs/001-voice-bittle-spec/decision-log.md`. Ningún OPEN
se da por cerrado. La selección de Vosk procede de H1; su validación sigue abierta.
U=0,80 y tiempos siguen provisionales. El perfil físico exige una Config explícita
que coincida con la del controlador; las referencias de aprobación son declaraciones
auditables de responsables, no firmas verificadas por software.

La consola es una elección de implementación autorizada por la misión. La nota
de alineación de la constitución es propuesta, no nueva versión ratificada.
Los modelos no están descargados en el checkout; no se intentó capturar audio.
El ensayo manual reproducible de Vosk ES/EN está en GUIA.md.

## 6. Preparación para H4 y lo que falta exactamente

Ver `docs/H3/preprueba_fisica.md`. Se requieren modelo/placa/firmware, tabla de
skills y comprobación de ksit/kup, Bluetooth/puerto, velocidad/formato/terminador,
parámetros aprobados, zona segura, supervisor, autorización expresa de sesión,
intervención independiente, estado inicial observado y procedimiento de cierre.

El transporte preparado usa pyserial con 8N1 predeterminado, sin control de flujo.
No se afirma que sea compatible con el Bittle disponible. Si su enlace es BLE sin
puerto serie o exige otro formato, habrá que adaptar y verificar el transporte.
`is_open` solo acredita recurso local, no salud del enlace radio. Falta validar
un detector de pérdida y vigilancia independiente de captura para la operación real.
No hay flujo de consola que abra/habilite hardware: se mantiene bloqueado hasta
resolver esas condiciones y revisar la integración operativa. No es una aplicación
física lista para usar mediante un cambio de flag.

La confianza media y la estimación de fin acústico necesitan datos representativos
para calibrar. No hay aprobación automática, ACK físico ni detección de postura.
Los TEST-F01…F10 están planificados y no ejecutados.

## 7. Cómo reproducir

Desde la raíz `VOICE-BITTLE`, PowerShell:

```powershell
.\.venv\Scripts\python.exe voice_bittle.py --demo
.\.venv\Scripts\python.exe voice_bittle.py
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe tools/generar_evidencias.py
```

Instalación, comandos de consola y modelos en GUIA.md. `/activar` habilita escucha;
`/fin` y `/reposo` solo son controles simulados. Historial y estado no escriben al enlace.

## 8. Inventario de cambios respecto a bb330a9

### Creados

- `docs/H3/informe_desarrollo.md`
- `docs/H3/preprueba_fisica.md`
- `evidencias/comprobaciones_consola.json`
- `evidencias/ejecucion_H3.json`
- `evidencias/entorno_H3.txt`
- `requirements-voz.txt`
- `specs/001-voice-bittle-spec/decision-log.md`
- `specs/001-voice-bittle-spec/environment-decision.md`
- `src/app/consola.py`
- `src/enlace/serie_real.py`
- `src/seguridad.py`
- `tests/integration/test_consola.py`
- `tests/integration/test_seguridad.py`
- `tests/unit/test_adaptadores.py`
- `tests/unit/test_evidencias.py`
- `voice_bittle.py`

### Modificados

- `.gitignore`
- `.specify/memory/constitution.md`
- `GUIA.md`
- `README.md`
- `docs/H3/casos_de_prueba.md`
- `evidencias/resultados_H3.md`
- `evidencias/trazabilidad_H3.md`
- `requirements.txt`
- `specs/001-voice-bittle-spec/checklists/requirements.md`
- `specs/001-voice-bittle-spec/contracts/interfaces.md`
- `specs/001-voice-bittle-spec/data-model.md`
- `specs/001-voice-bittle-spec/plan.md`
- `specs/001-voice-bittle-spec/quickstart.md`
- `specs/001-voice-bittle-spec/research.md`
- `specs/001-voice-bittle-spec/spec.md`
- `specs/001-voice-bittle-spec/tasks.md`
- `src/app/controlador.py`
- `src/avisos/__init__.py`
- `src/config.py`
- `src/enlace/__init__.py`
- `src/estado/__init__.py`
- `src/interfaz/__init__.py`
- `src/reloj.py`
- `src/traductor/__init__.py`
- `src/voz/__init__.py`
- `src/voz/vosk_reconocedor.py`
- `tests/integration/test_escenarios.py`
- `tools/generar_evidencias.py`

No se elimina ningún archivo de la base ni se modifica H1. La copia original se
mantiene aparte. El trabajo queda revisable en commits locales; publicación/merge
reservados al usuario.


## 9. Revisión final y entrega integral (posterior a la sección histórica anterior)

Se conserva íntegro el informe anterior y sus 109 pruebas como hito histórico.
La revisión actual alcanza 124 pruebas / 37 casos. Cambios: confianza mínima por
palabra en lugar de media, decodificación abierta en vez de gramática restringida,
control de silencio PCM nulo, capturas identificadas consumidas una vez, caducidad,
y descarte de captura si se desactiva/reactiva escucha mientras se procesa.
En aquella revisión se añadieron `test_revision_voz.py`, `ensayo_audio_sintetico.py` y `empaquetar.py`; las dos últimas herramientas no están presentes en el `main` revisado.

El modelo ES aportado por el usuario se conserva, se carga y se ensaya con PCM
sintético; tres señales produjeron texto vacío. No se usa micrófono ni se pronuncian
órdenes en esta revisión. La consulta «estado» comunicada por el usuario no puede
atribuirse a una causa sin audio del incidente. Los cambios reducen riesgos de
procesamiento, pero no prueban ausencia de falsos positivos con ruido real.

PROYECTO.md conecta H1, H2 y H3; documentación H2 activa corregida sin alterar
originales históricos. Se archivan spec/plan/tasks de aa3ea8a byte por byte,
separados y marcados no vigentes. El ZIP integral incluye fuentes, documentación,
pruebas, herramientas, configuración y evidencias; excluye .git, .venv, modelos,
cachés y logs locales. Guías explican instalación externa. No push/pull/merge.
Se comunicó el resultado de instalación/ejecución desde extracción limpia en `paquete_limpio.json` (ausente del `main` revisado);
el manifiesto interno SHA-256 permite verificar el contenido distribuido.

La primera extracción detectó dos fallos de tests por codificación heredada entre procesos en Windows (padre UTF-8 e hijo con codificación local). Se fija `-X utf8` y `encoding="utf-8"` en los tests de consola y se repite la verificación en extracción nueva. No era fallo de movimientos ni se eliminaron tests.
