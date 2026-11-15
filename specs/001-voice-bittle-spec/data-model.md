# Modelo de datos actual

Versión documental 0.5 · Datos en memoria, no esquema de base de datos.

| Entidad | Campos / estructura | Semántica |
|---|---|---|
| Comando | tupla (token, descripción) | Procede de COMANDOS, no de carga serie arbitraria del usuario |
| Frase | cadena normalizada; lista de comandos | Orden de aparición; desconocida rechaza lote salvo parada |
| Cola | deque de comandos, generación, cerrada, activa, actual, error | 20 pendientes por defecto; acción actual aparte; error conserva último texto |
| Coreografía | lista (orden, espera) | Habilidad, articulación, ESPERA o DI:; tiempos en segundos |
| Conexión del panel | desconectado / conectando / simulado / conectado / desconectando | Estado de sesión/apertura, no vigilancia física continua |
| Micrófono | apagado / cargando / escuchando; Event de cancelación | Apagado indica que no acepta voz; el cierre material del hilo puede terminar después |
| Audio del panel | queue de 8 pares (PCM bytes, estado del dispositivo) | 4000 muestras/bloque; descarta sesión al saturarse |
| Nivel | entero 0…100 | RMS escalado; no dBA, confianza ni detección garantizada de habla |
| Última frase | texto | Incluye voz, teclado o botón, aceptado o rechazado |
| Evento web | hora HH:MM:SS, texto | Máximo 40; más reciente primero; sin fecha, intención estructurada ni persistencia |
| Error de sesión | cadena | Último error de conexión/micrófono; puede persistir hasta nueva activación/conexión |

`Panel.estado()` entrega instantánea bajo bloqueo; `ColaAcciones.estado()` contiene
actual, pendientes y error. No existe campo ACK, postura observada o fin físico.
Los errores de cola no son necesariamente entradas en la lista de eventos: se exponen
por su propio campo. La lista satisface el alcance de actividad reciente ACT-11, no un registro persistente completo; esa obligación anterior se retiró.



El transporte serie conserva token/fase/resultado y un bloqueo tras fallo. Estado
inicial sin_envio; no_enviado antes de write; desconocido si write ya se invocó;
enviado_sin_confirmacion_fisica tras completar I/O. El bloqueo no se elimina por una
nueva orden: se crea una sesión nueva al desconectar/conectar. No se persiste la cola.

