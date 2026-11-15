# Contratos de la aplicación actual

Versión documental 0.5 · Describen `bittle_web.py` y `bittle_voz.py`.

## API HTTP

Solo `http://127.0.0.1:8765` por defecto. Se puede cambiar puerto al iniciar.
GET devuelve JSON salvo `/`, que sirve HTML. POST exige token en X-Bittle-Token,
Host local exacto y, si se aporta Origin, el origen local exacto. Las acciones requieren
cuerpo JSON de 1…8192 bytes. No hay CORS abierto ni autenticación de usuarios.

| Método/ruta | Entrada | Resultado |
|---|---|---|
| GET `/` | — | HTML con token efímero del servidor |
| GET `/api/estado` | — | conexion, microfono, nivel, ultima_frase, error, eventos, cola |
| GET `/api/dispositivos` | — | puertos [{id,nombre}], microfonos [{id,nombre}] |
| POST `/api/conectar` | modo simulado/serie; puerto; segundos | Estado actualizado, sin activar micrófono |
| POST `/api/desconectar` | {} | Cancela escucha/cola, intenta descanso y cierra enlace |
| POST `/api/orden` | texto | Estado si aceptada; 400 si inválida o cola llena |
| POST `/api/microfono` | activo booleano; modelo; dispositivo opcional | Cargando si activa; apagado si desactiva |

Errores: 400 para errores de acciones, 403 para origen/Host/token rechazados,
404 ruta no encontrada, 500 fallo durante GET. No interpretar HTTP 200 como éxito
físico. Conectar es síncrono y puede tardar por apertura manual del transporte.

## API Python

- `buscar_comandos(texto) -> list[tuple]`: parser determinista; parada sola si aparece.
- `ColaAcciones(enlace, segundos=3, capacidad=20)`: inicia ejecutor.
- `agregar(comandos) -> bool`: encola lote o rechaza por capacidad/cierre; parada vacía cola.
- `estado()`: instantánea con actual, pendientes y último error.
- `esperar_vacia(timeout)`: espera a cola vacía e inactividad del hilo, no a reposo físico.
- `cerrar()`: cancela y hace join; espera a I/O en curso.
- Enlaces: `enviar(token)` y `cerrar()`. EnlaceSerie abre en su constructor;
  el enlace simulado solo imprime. 

Panel comparte una instancia de cola entre entradas de voz, texto y botones. Apagar
micrófono no cierra cola; desconectar sí. Una frase rechazada no hace un envío nuevo,
pero no detiene acciones previamente aceptadas.


El estado HTTP incluye `transporte` (null si no aplica) con token, fase, resultado
y requiere_reconexion. Los resultados son sin_envio, no_enviado, desconocido y
enviado_sin_confirmacion_fisica. Se conserva el último fallo hasta cerrar la sesión;
no hay ACK de movimiento. Recuperación: desconectar y conectar explícitamente.

