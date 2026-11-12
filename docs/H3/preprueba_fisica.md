# Preprueba física — BLOQUEADA, sin verificaciones físicas realizadas

Fecha: 2026-11-12. Este documento prepara el trabajo H4; no autoriza un ensayo.
La consola `--modo fisico` no abre puertos. No existe perfil aprobado del robot.

| Condición | Evidencia requerida | Estado |
|---|---|---|
| Modelo Bittle clásico/X/X V2, placa y módulos | Etiqueta, identificación de placa y responsable (OPEN-02) | Pendiente |
| Firmware y skills | Versión/commit y tabla de skills aplicable; ksit/kup y posturas iniciales (OPEN-10) | Pendiente |
| Bluetooth | Módulo, emparejamiento, puerto de salida y compatibilidad del SO (OPEN-15) | Pendiente |
| Protocolo | Fuente específica de ese hardware; velocidad, 8N1 u otros parámetros, terminador, comportamiento al abrir/cerrar | Pendiente |
| Parámetros | U y semántica de confianza, tiempos, perfiles concretos y referencia de revisión (OPEN-04/12) | Pendiente |
| Zona de ensayo | Superficie estable, seca, despejada y perímetro (RO-01) | Pendiente |
| Supervisión/autorización | Responsable presente y autorización expresa para esa sesión y movimientos | Pendiente |
| Intervención independiente | Medio, responsable, simulacro y recuperación (RS-03, OPEN-09) | Pendiente |
| Estado inicial/fin | Cómo observar inmovilidad, ocupado, fin y postura; recuperación tras desconexión (OPEN-14) | Pendiente |
| Detección de enlace | Método aplicable al hardware; is_open local NO basta para detectar pérdida de radio | Pendiente |
| Cierre/incidencias | Confirmar no marcha activa, secuencia de cierre y registro de no conformidad | Pendiente |

## Referencias oficiales consultadas el 2026-11-12

- [Petoi Serial Protocol](https://guide.petoi.com/apis/serial-protocol): tokens ASCII
  sensibles a mayúsculas; skills dependen de la tabla del firmware. La página general
  no identifica nuestro robot ni verifica `kup` en él.
- [Bluetooth dual mode](https://guide.petoi.com/communication-modules/dual-mode-bluetooth):
  módulo de transmisión transparente y puerto asignado por el sistema; es necesario
  confirmar que esta documentación corresponde al módulo del equipo.
- [Petoi Python API](https://guide.petoi.com/apis/python-api): muestra conexión por
  NyBoard/BiBoard y posibles puertos Bluetooth; sus demos pueden conectar automáticamente.
  No se han ejecutado. El adaptador propio evita ese inicio automático.

No se fija velocidad ni terminador de producción hasta verificar el modelo. Los
valores de tests son exclusivamente entradas de dobles; no parámetros aprobados.
El adaptador actual contempla puerto serie con parámetros pyserial predeterminados
8N1, sin flow control, y timeout explícito. Si el hardware requiere otra configuración
o BLE sin puerto serie, este adaptador no se considera compatible sin adaptación y pruebas.

## Secuencia propuesta (requiere revisión y aprobación)

1. Completar evidencias de la tabla y revisar el perfil contra Config real de la sesión.
2. Validar primero reconocimiento y UI con FakeSerial, sin abrir el puerto real.
3. Revisar la integración de vigilancia de enlace independiente del bloqueo de captura.
   El bucle físico no está habilitado en la consola H3 y debe revisarse antes de H4.
4. Obtener autorización expresa, supervisor y zona preparada. Verificar mecanismo
   independiente antes de energizar o habilitar movimientos conforme al procedimiento aprobado.
5. Abrir solo el puerto seleccionado, por acción explícita. Abrir no confirma reposo.
6. Confirmar estado observado y ejecutar únicamente el caso autorizado, sin reintentos
   automáticos. Capturar orden, bytes, tiempos, observación, veredicto e incidencias.
7. Ante error, detener nuevas órdenes; estado desconocido. Aplicar el procedimiento
   independiente cuando corresponda. Reconectar no confirma inmovilidad ni reenvía nada.
8. Cerrar solo conforme al procedimiento aprobado. Cerrar el puerto no garantiza parar
   una acción ni sustituye observar el robot. Registrar cualquier discrepancia antes de repetir.

`PerfilFisico` y `habilitar(referencia_sesion)` son controles del software, no una
verificación de autenticidad de las aprobaciones humanas. No rellenar con valores
ficticios fuera de tests. TEST-F01…F10 siguen sin ejecutar; RR-01/RR-02 son objetivos
propuestos, no resultados. El ensayo 5×10×2 se conserva hasta resolver OPEN-13.
