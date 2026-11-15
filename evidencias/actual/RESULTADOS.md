# Resultados actuales y trazabilidad

Ejecución UTC: 2026-11-13T10:33:51.146284+00:00.
Python 3.12.10. 49/49 pruebas PASS. Salida: 0.

Suite vigente: 49 casos parametrizados de la aplicación final.
Los casos ejecutados exactos están en [ejecucion.json](ejecucion.json), [pytest.xml](pytest.xml) y [salida](pytest.txt).
Línea base vigente: H1 v0.4. No se operó robot ni micrófono. PASS no acredita resultado físico ni partes de un ACT limitadas a inspección.

| Requisito actual | Pruebas vinculadas y resultado | Alcance adicional / pendiente |
|---|---|---|
| ACT-01 | test_arranque_sin_conexion_ni_escucha: PASS; test_arranque_http_no_abre_hardware_ni_transmite: PASS | Arranque software, no disponibilidad física. |
| ACT-02 | test_simulacion_cola_y_desconexion: PASS; test_error_conexion_restaura_estado: PASS; test_dos_ordenes_y_desconocida_por_http: PASS; test_formato_serie_ascii_lf_sin_puerto: PASS; test_fallo_previo_no_escribe_y_recuperacion_es_explicita: PASS | COM real comunicado por usuario, no simulado como robot completo. |
| ACT-03 | test_interpretacion: PASS; test_fifo_frases_separadas_y_repeticiones: PASS; test_dos_ordenes_y_desconocida_por_http: PASS | Parser textual, no precisión acústica ni todos los alias. |
| ACT-04 | test_interpretacion: PASS; test_dos_ordenes_y_desconocida_por_http: PASS; test_resultado_vosk_vacio_invalido_no_es_orden: PASS | Desconocidas/negación textual; no garantiza rechazo de audio ruidoso. |
| ACT-05 | test_fifo_frases_separadas_y_repeticiones: PASS; test_limite_rechaza_frase_entera: PASS | Capacidad y FIFO con sustituto; sin prueba exhaustiva de carreras concurrentes. |
| ACT-06 | test_fifo_frases_separadas_y_repeticiones: PASS; test_esperas_minimas_y_parametro_invalido: PASS | Esperas mínimas y parámetros inválidos probados; no medición de finalización física. |
| ACT-07 | test_caminar_tiene_fin_temporizado: PASS; test_coreografia_completa_antes_de_siguiente: PASS | Coreografía reducida de prueba; no valida movimientos reales del baile/Cristiano. |
| ACT-08 | test_parada_cancela_espera_y_pendientes: PASS; test_parada_corta_coreografia: PASS; test_parada_visible_descarta_pendientes: PASS; test_parada_preservada_durante_error: PASS; test_cancelacion_antes_de_seleccionar_envio_no_ejecuta_orden: PASS; test_fallo_con_parada_no_conserva_movimientos_añadidos: PASS | No interrupción del I/O en curso ni garantía de parada física. |
| ACT-09 | test_apagar_durante_carga_no_abre_captura: PASS; test_resultado_tardio_no_se_encola_al_apagar: PASS; test_audio_invalido_no_envia_y_nueva_activacion_no_reutiliza: PASS | Carga/captura con sustitutos; uso nominal comunicado por usuario. |
| ACT-10 | test_modelo_ausente_no_activa_microfono: PASS; test_microfono_informa_error_de_apertura: PASS; test_audio_saturado_apaga_sin_aceptar_orden: PASS | Errores de apertura/modelo y saturación probados con dobles; no captura real. |
| ACT-11 | test_http_pagina_estado_y_proteccion_de_acciones: PASS; test_eventos_limitados_conservan_mas_recientes: PASS | HTTP y límite de 40 eventos probados; medidor y disposición por inspección, no telemetría física. |
| ACT-12 | test_cierre_descarta_pendientes_y_termina_hilo: PASS; test_simulacion_cola_y_desconexion: PASS; test_dos_ordenes_y_desconocida_por_http: PASS; test_fallo_serie_descarta_cola_y_no_transmite_al_cerrar: PASS | Fin del hilo/cola, no reposo físico; efecto de cerrar pestaña por inspección. |
| ACT-13 | test_error_descarta_secuencia: PASS; test_parada_preservada_durante_error: PASS; test_envio_incierto_no_repite_y_conserva_resultado: PASS; test_fallo_previo_no_escribe_y_recuperacion_es_explicita: PASS; test_fallo_con_parada_no_conserva_movimientos_añadidos: PASS | Sin reenvío y recuperación manual comprobados con puerto falso; resultado físico desconocido, corrección no revalidada en Bittle. |
| ACT-14 | test_http_pagina_estado_y_proteccion_de_acciones: PASS | Token/origen probados; Host/límite cuerpo/bind inspeccionados, no auditoría de seguridad completa. |
| ACT-15 | Inspección; sin prueba automática específica | Inspección de CLI/captura/BLE; sin pruebas físicas BLE ni todos los fallos del CLI. |
| ACT-16 | Inspección; sin prueba automática específica | Ejecución de herramientas y revisión documental; no aceptación formal de H1. |

El uso físico comunicado se conserva en [validacion_usuario.md](../../docs/H3/validacion_usuario.md).
Los requisitos finales están en [H1 v0.4](../../docs/h1/H1_v0.4.md); los cambios de alcance en [el historial](../../docs/h1/EVOLUCION_REQUISITOS.md).
Las huellas identifican las fuentes al ejecutar; regenerar después de modificar código/pruebas/herramientas.
