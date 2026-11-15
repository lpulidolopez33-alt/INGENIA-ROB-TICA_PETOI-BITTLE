# Casos de prueba actuales

Precondición común: entorno de pruebas instalado, sin COM ni micrófono real.
Hay 49 casos parametrizados: 31 anteriores conservados y 18 regresiones del cierre final. Las unidades de tiempo siguientes
son límites de sincronización de tests, no mediciones del robot.

| Caso | Procedimiento y resultado esperado | ACT | Fuente ejecutable |
|---|---|---|---|
| ACT-TEST-01 | Introducir las ocho frases parametrizadas. Obtener tokens en orden, alias sin duplicación, repetición conservada, parada única o lista vacía según caso. | ACT-03, ACT-04 | [test_interpretacion](../../tests/unit/test_cola_bittle_voz.py) |
| ACT-TEST-02 | Añadir dos frases y esperar cola vacía. Observar ksit, kup, ksit, ksit en ese orden. | ACT-03, ACT-05, ACT-06 | [test_fifo_frases_separadas_y_repeticiones](../../tests/unit/test_cola_bittle_voz.py) |
| ACT-TEST-03 | Iniciar espera de 30 s, enviar para. En <=2 s de timeout de prueba, quedar vacío con ksit y kbalance solamente. | ACT-08 | [test_parada_cancela_espera_y_pendientes](../../tests/unit/test_cola_bittle_voz.py) |
| ACT-TEST-04 | Sustituir baile por dos pasos cortos. Obtener kbalance, khi, ksit; no intercalar la siguiente acción. | ACT-07 | [test_coreografia_completa_antes_de_siguiente](../../tests/unit/test_cola_bittle_voz.py) |
| ACT-TEST-05 | Sustituir baile por pasos con espera larga. Parar tras el primero: solo khi y kbalance, sin siguiente paso ni acción pendiente. | ACT-08 | [test_parada_corta_coreografia](../../tests/unit/test_cola_bittle_voz.py) |
| ACT-TEST-06 | Enviar camina y siéntate con espera corta: kwkF, kbalance, ksit. | ACT-07 | [test_caminar_tiene_fin_temporizado](../../tests/unit/test_cola_bittle_voz.py) |
| ACT-TEST-07 | Hacer fallar el envío de la primera orden. No enviar la segunda y vaciar secuencia. | ACT-13 | [test_error_descarta_secuencia](../../tests/unit/test_cola_bittle_voz.py) |
| ACT-TEST-08 | Capacidad 2; añadir frase de 3 acciones. Rechazar lote y no enviar ningún token. | ACT-05 | [test_limite_rechaza_frase_entera](../../tests/unit/test_cola_bittle_voz.py) |
| ACT-TEST-09 | Cerrar durante primera acción. No enviar segunda, terminar hilo y rechazar agregados posteriores. | ACT-12 | [test_cierre_descarta_pendientes_y_termina_hilo](../../tests/unit/test_cola_bittle_voz.py) |
| ACT-TEST-10 | Crear Panel. Comprobar desconectado/apagado y que ordenar sin sesión lanza ValueError. | ACT-01 | [test_arranque_sin_conexion_ni_escucha](../../tests/unit/test_panel_web.py) |
| ACT-TEST-11 | Conectar simulación, completar dos acciones, conservar última frase, rechazar negación y desconectar. | ACT-02, ACT-12 | [test_simulacion_cola_y_desconexion](../../tests/unit/test_panel_web.py) |
| ACT-TEST-12 | Añadir secuencia al panel y para; esperar cola vacía y comprobar pendientes vacíos. | ACT-08 | [test_parada_visible_descarta_pendientes](../../tests/unit/test_panel_web.py) |
| ACT-TEST-13 | Sustituir transporte por constructor que falla. Mostrar COM ocupado y volver a desconectado. | ACT-02 | [test_error_conexion_restaura_estado](../../tests/unit/test_panel_web.py) |
| ACT-TEST-14 | Activar ruta inexistente: ValueError, micrófono apagado. | ACT-10 | [test_modelo_ausente_no_activa_microfono](../../tests/unit/test_panel_web.py) |
| ACT-TEST-15 | Bloquear carga del modelo, apagar y liberar carga. El flujo de captura no debe abrirse. | ACT-09 | [test_apagar_durante_carga_no_abre_captura](../../tests/unit/test_panel_web.py) |
| ACT-TEST-16 | Captura sustituta falla al abrir. Terminar hilo, mantener apagado y mostrar error. | ACT-10 | [test_microfono_informa_error_de_apertura](../../tests/unit/test_panel_web.py) |
| ACT-TEST-17 | Bloquear reconocimiento final de camina, apagar y liberar. No cambiar última frase ni añadir órdenes. | ACT-09 | [test_resultado_tardio_no_se_encola_al_apagar](../../tests/unit/test_panel_web.py) |
| ACT-TEST-18 | Servidor local efímero. HTML contiene control de micrófono; token falso u origen externo producen 403; token correcto inicia solo simulación. | ACT-11, ACT-14 | [test_http_pagina_estado_y_proteccion_de_acciones](../../tests/unit/test_panel_web.py) |

## Resultado observado y veredicto

Para cada función, la salida de la ejecución real, sus parametrizaciones y PASS/FAIL
están en [RESULTADOS.md](../../evidencias/actual/RESULTADOS.md) y
[JUnit XML](../../evidencias/actual/pytest.xml). No rellenar manualmente los resultados generados.
La trazabilidad JSON indica qué queda limitado a inspección, incluido overflow,
valores mínimos de espera y BLE; no se inventa cobertura automática.

Reproducir con `python tools/generar_evidencias_actuales.py` usando el entorno de
pruebas. Físico: [preprueba](preprueba_fisica.md). Uso comunicado:
[validacion_usuario.md](validacion_usuario.md).


## Contratos adicionales derivados de Moodle

Fuente: tests/unit/test_contratos_moodle.py. Precondición: entorno de pruebas, sin hardware.

| Caso | Entrada y procedimiento | Esperado | ACT |
|---|---|---|---|
| MOD-01 | Conectar HTTP simulado; siéntate; ponte de pie; siéntate y vuela; desconectar | ksit, kup; HTTP 400 sin nuevo token; krest al cerrar | ACT-02, ACT-03, ACT-04, ACT-12 |
| MOD-02 | Sustituir serie y escribir ksit/kup | Bytes ASCII terminados en LF, sin abrir puerto | ACT-02 |
| MOD-03 | Bloquear envío ksit, solicitar PARA y provocar excepción | Solo ksit y kbalance; error expuesto; sin kup | ACT-08, ACT-13 |
| MOD-04 | Captura falsa añade nueve bloques antes de consumir | Saturación apaga escucha, nivel cero y ninguna orden | ACT-10 |
| MOD-05 | Registrar 45 eventos | Conservar últimos 40, más reciente primero | ACT-11 |
| MOD-06 | Esperas mínimas y parámetros cero/negativo/NaN/infinito | Mínimos 4/4/6 s; parámetros inválidos rechazados | ACT-06 |

Resultado observado y PASS/FAIL por nombre de función: evidencias/actual/ejecucion.json.

## Regresiones del cierre definitivo

[test_cierre_final.py](../../tests/unit/test_cierre_final.py) añade 18 casos:
cuatro fases de envío incierto, fallo previo con recuperación manual, fallo serie
con cierre sin nuevos envíos, PARA concurrente con descarte de movimientos añadidos,
cancelación anterior al envío, ocho resultados Vosk vacíos/inválidos, reactivación
de captura sin residuos y arranque HTTP sin abrir hardware ni transmitir.
Los casos usan puertos y audio falsos; no son ensayos físicos.

