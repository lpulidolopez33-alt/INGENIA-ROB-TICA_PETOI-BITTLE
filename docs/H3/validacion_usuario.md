# Registro de funcionamiento comunicado por el usuario

Fuente: mensajes de esta conversación; registro inicial del 2026-11-12 y ampliación comunicada el 2026-11-13. La fecha exacta del ensayo no se ha indicado.
No se dispone de vídeo, audio, telemetría ni acta de ensayo completa. Se conserva
el alcance literal y no se atribuyen al usuario mediciones que no facilitó.

| ID | Contexto | Confirmación / dato aportado | Qué permite concluir |
|---|---|---|---|
| USR-01 | Identificación | «bittle normal»; captura COM6 saliente Petoi-30AD | Modelo declarado y puerto de esa sesión |
| USR-02 | Consola física por texto | «vale funciona escribiendo» | Uso nominal comunicado |
| USR-03 | Control por voz | «Vale, ahora mismo funciona» antes de pedir cola | Voz nominal comunicada |
| USR-04 | Cola añadida | «Vale, esto funciona bien ya» antes de pedir HTML | Secuencias funcionando según usuario |
| USR-05 | Panel web | «Vale, ya ha funcionado perfectamente» antes de pedir documentación | Uso del panel satisfactorio comunicado |

No demuestra: prueba individual de cada alias/coreografía; BLE; firmware exacto;
valores de precisión/latencia; condiciones acústicas; manejo de todos los fallos;
parada independiente; cobertura completa H1; aprobación del profesorado.

No mantener como afirmación global «nunca se ha usado voz real o robot». Sí sigue
siendo correcto: las pruebas automáticas y la revisión del agente no operaron hardware.
No se solicitan nuevos ensayos. La cobertura disponible está en [preprueba_fisica.md](preprueba_fisica.md).

## Confirmación física detallada comunicada el 13 de noviembre de 2026

El equipo confirma que ha probado el Bittle físico desde la interfaz HTML:

| ID | Prueba comunicada | Resultado observado por el equipo |
|---|---|---|
| USR-06 | Decir una acción por micrófono desde el panel | La reconoce y el Bittle la realiza correctamente |
| USR-07 | Decir varias acciones por micrófono | Se ponen en cola y el Bittle ejecuta toda la secuencia |
| USR-08 | Silenciar el micrófono mientras se ejecutan las acciones | La secuencia continúa; el equipo utiliza el silencio del micrófono para evitar entradas por ruido externo |

Estado: funcionamiento físico nominal de voz, panel y cola confirmado por el equipo.
Esto acredita una comprobación real comunicada, no solo simulación. No se exige repetirla
para poder describirla como realizada. No se conocen las frases exactas, número de
repeticiones, firmware ni fecha de la sesión; no se completan esos campos por suposición.

La mitigación empleada es manual: activar escucha para dar las órdenes y silenciar
el micrófono tras aceptarse la secuencia. No hay silenciamiento automático durante
la ejecución. Con escucha apagada no se reciben nuevas órdenes de voz, incluida PARA;
para cancelar desde la interfaz se utiliza el botón PARA. Apagar escucha no vacía la cola.
No se ha comunicado todavía el resultado de una entrada no reconocida en esa sesión,
ni ensayos de fallos de enlace o de parada física. Esos casos permanecen sin confirmar.

## USR-09 Conversación ajena al catálogo, comunicado el 13/11/2026

El usuario prueba en simulación con micrófono frases completas de otro contexto y observa acciones reconocidas erróneamente. Resultado: no satisfactorio para rechazo de conversación hablada. No se facilitan frases exactas, transcripciones ni número de intentos. El resultado fallido se conserva. Posteriormente el equipo decide tratar OPEN-03 mediante escucha manual y mantener el software; CR-01 no corrige este fallo.

## Decisión operativa del equipo del 13/11/2026

El usuario decide no modificar el reconocimiento y mantener el micrófono apagado
salvo al dictar una instrucción o secuencia, desactivándolo tras su aceptación.
Esta decisión amplía el procedimiento de silenciado ya comunicado en USR-08.
No es un ensayo nuevo ni acredita una tasa de éxito. USR-09 conserva su resultado
no satisfactorio. OPEN-03 pasa a limitación conocida con mitigación operativa;
no queda una corrección software comprometida. Procedimiento en
[PANEL_WEB](../../PANEL_WEB.md#estrategia-de-escucha-manual-acordada).


## Versión de los ensayos y cierre definitivo

No se registró un commit ni hash durante los ensayos físicos, por lo que su versión
exacta no puede determinarse. La cronología de los mensajes sitúa el uso de voz,
cola y panel antes de las correcciones finales de transporte. La instantánea local
`b63ef45` conserva el código anterior a estas correcciones; es referencia comparativa,
no prueba de que ese commit se ejecutara en el robot.

Las huellas de esa instantánea constan en VERSION_ENTREGA.json. La versión final
elimina reenvío serie, descarta movimientos residuales tras fallo y valida entradas
Vosk. Esos cambios se verifican con simuladores y NO se revalidaron físicamente.

No se pueden inferir posturas concretas del texto «funciona»: siéntate/ponte de pie
figuran explícitamente en la salida de simulación aportada, no en un acta física
que individualice cada movimiento. La evidencia física acredita uso nominal y
secuencias según el equipo, sin catálogo completo ni mediciones.
No se requieren nuevas pruebas físicas para esta entrega.

