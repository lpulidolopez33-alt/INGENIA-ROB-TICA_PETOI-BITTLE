# Entrega integral VOICE-BITTLE — ARGOS

Un único proyecto: H1 original, H2 vigente, software y verificación H3. Índice:
[PROYECTO.md](../../PROYECTO.md). Guía única: [GUIA.md](../../GUIA.md).
No se distribuyen tres entregas independientes ni versiones contradictorias activas.

## Funcionalidades

Consola ES/EN, proveedor fake o Vosk local, validación de frases/confianza,
consultas sin escrituras, estados seguros, historial JSONL y enlace simulado.
Arquitectura: voz → traductor → controlador/estado → enlace; consultas → registro/vista.
Puerto pyserial preparado y probado con dobles; consola física bloqueada.

## Resultados de esta revisión

- 124 pruebas automáticas pasan; 37 casos TEST. Incluye regresiones de ruido/silencio
  sintéticos, parciales, capturas repetidas/caducadas e invalidación al desactivar.
- Demo ES/EN y bloqueo físico comprobados; resultados en evidencias/.
- Modelo español vosk-model-small-es-0.42 cargado realmente. Tres señales PCM
  sintéticas de 5 segundos (cero, ruido uniforme, tono 440Hz): texto vacío.
- El usuario comunicó arranque con Vosk y consulta «estado» sin habla intencionada.
  Causa no determinada: falta audio del incidente; no se declara corregida su causa.
- No se ensayó voz humana en esta revisión. Modelo inglés, precisión, condiciones
  acústicas, funcionamiento real sin Internet y rendimiento siguen pendientes.
- Verificación de extracción/instalación del paquete: evidencias/paquete_limpio.json.

## Medidas conservadoras y límites

Reconocedor nuevo por captura, resultados finales con palabras coherentes,
decodificación abierta para no limitar ruido a cuatro órdenes, confianza mínima
por palabra (no calibrada), descarte de silencio digital y consumo único/frescura.
Los controles temporales usan T_escucha provisional; necesitan revisión de equipo.
No garantizan rechazo de todo ruido ni prueban intención humana. No habilitar robot
sobre estos resultados. «Estado»/«historial» nunca producen comandos motrices.

## Recibir, instalar y ejecutar (PowerShell)

Descomprimir; abrir PowerShell en la carpeta VOICE-BITTLE:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe voice_bittle.py --demo
.\.venv\Scripts\python.exe -m pytest -q
```

Para voz instalar requirements-voz.txt y descargar modelo oficial como explica
GUIA.md. No hay rutas personales necesarias ni dependencia de un repositorio Git
para ejecutar la aplicación. Modelos, entorno virtual, cachés y registros locales
se excluyen del ZIP y no deben compartirse como evidencia de otros equipos.

## Qué debe hacer cada compañero

1. Comprobar el manifiesto del ZIP y leer PROYECTO.md / GUIA.md.
2. Crear su entorno, ejecutar demo y pytest; guardar versiones e incidencias.
3. Instalar modelo ES si va a probar voz; verificar entrada de audio elegida.
4. Cuando pueda hablar, ensayar frases/ruido/silencio en FakeSerial, con protocolo
   acordado. No declarar precisión o seguridad por una demostración aislada.
5. Revisar OPEN y preprueba_fisica.md antes de proponer cualquier ensayo físico.

Para el robot faltan identificación de modelo/placa/firmware/módulo, protocolo,
puerto, velocidad y terminador, parámetros aprobados, estado observado, supervisor,
autorización de sesión e intervención independiente. Comunicación, posturas y
sistema físico NO están validados. TTS/avisos sonoros también siguen pendientes.

## Checklist de entrega

- [x] Software y controles comprobados automáticamente; consultas sin movimiento.
- [x] Consola y demos seguras probadas.
- [x] Modelo español cargado; decodificador probado con PCM sintético.
- [x] H1 intacto; H2 vigente conectado con H3; originales históricos identificados.
- [x] Dependencias/rutas/guías portátiles y modelos externos documentados.
- [ ] Reconocimiento representativo con voz humana y ruido ambiental.
- [ ] Validación modelo inglés y reconocimiento real sin Internet.
- [ ] RR-01/RR-02, U y tiempos aprobados/medidos; OPEN-03/04/05/12/13.
- [ ] Bluetooth/serie reales, movimientos, cierre e intervención independiente.
- [ ] Revisión formal del equipo y demás OPEN pendientes.

El resultado de paquete limpio se registra aparte con observaciones concretas;
ninguna casilla de software equivale a aceptación del sistema físico.
