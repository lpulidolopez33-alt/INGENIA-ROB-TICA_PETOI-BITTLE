# Validación del primer incremento y de la entrega

Instalación única según [GUIA.md](../../GUIA.md), incluyendo requirements.txt para pruebas.
Desde la raíz ejecutar `python -m pytest -q`. La suite usa sustitutos de hardware.
Ejecutar `python bittle_voz.py --simulado --texto` y escribir siéntate, esperar su envío,
después ponte de pie; finalmente siéntate y vuela. Deben observarse ksit y kup, y rechazo
sin nuevo comando para la tercera frase. Ctrl+C intenta krest al cerrar.

Panel: `python bittle_web.py`; elegir Simulación, Conectar y repetir. PARA debe cancelar
pendientes. No activar el micrófono para esta prueba. La prueba con voz necesita modelo y
micrófono reales y se registra aparte. Ver [casos](../../docs/H3/casos_actuales.md).

Empaquetado y verificación: tools/generar_evidencias_actuales.py,
tools/verificar_documentacion.py y tools/empaquetar.py. Consultar resultados y versión
antes de declarar aceptación. Las copias extraídas no contienen entorno, modelo ni .git.
