# Informe de la aplicación final

La entrega reúne `bittle_voz.py`, el panel `bittle_web.py` y `web/index.html`.
Comparten parser y una cola de hasta 20 acciones pendientes. PARA cancela la cola
y solicita equilibrio. El panel muestra conexión, escucha, nivel, última frase,
actividad del ejecutor y eventos recientes en memoria.

## Verificación

La suite de esta entrega contiene **49 pruebas**: 31 anteriores conservadas y 18 regresiones de cierre. Se retiraron las 124 pruebas que solo verificaban
el controlador anterior; no se ha eliminado ningún test de la aplicación final.
Resultados: [RESULTADOS.md](../../evidencias/actual/RESULTADOS.md), JUnit XML,
salida, entorno y huellas en la misma carpeta. Trazabilidad: ACT → código → prueba
 o inspección, con alcance y limitaciones.

El usuario confirmó texto, voz, secuencias y panel. Véase
[validacion_usuario.md](validacion_usuario.md). La revisión previa de navegador
comprobó simulación, secuencia, parada y cierre sin conectar hardware ni micrófono.
Las confirmaciones no son una campaña cuantitativa de precisión o seguridad.

## Limpieza de entrega

Se retiraron controlador anterior, sus pruebas/configuración, documentación y
resultados históricos y accesos duplicados. Los recursos Spec Kit se recuperaron
para completar el flujo docente y están en el repositorio, fuera del ZIP de ejecución. Se corrigieron
referencias y herramientas. Se conservó la lógica de ejecución; se corrigió en el HTML la ruta inicial
del modelo para apuntar a `modelos/` dentro del proyecto. Se mantuvo un respaldo previo fuera de la carpeta
de entrega, que no se incluye en el paquete final.

## Alcance y límites

[H1 v0.4](../h1/H1_v0.4.md) define el alcance final. Inglés, consultas habladas,
confianza acústica e historial persistente no se prometen. La interfaz no confirma
fin físico; no hay reenvío automático; persisten falsos positivos de voz. La limpieza no elimina
ni oculta esos límites. No se ha publicado nada en GitHub.

## Revisión final de coherencia

Se contrastaron requisitos, parser, cola, transportes, estados del panel, guías y
contenido distribuible. Se corrigieron referencias al modelo ausente y la afirmación
desactualizada de HTML sin cambios. El README distingue instalación inicial,
simulación textual y simulación con voz. No se promete una instalación automática.

La carga local del modelo español se comprobó sin captura de audio. Esta evidencia
no demuestra precisión de reconocimiento. La entrega está preparada para revisión
H1-H3 y demostración simulada; [H4](CIERRE_Y_H4.md) consolida los ensayos físicos existentes y los límites de evidencia, sin solicitar más sesiones. [CR-01](CR-01.md) registra la cola elegida por el equipo, implementada y verificada. OPEN-03 registra falsos positivos de voz reproducidos por el usuario. El servidor es local,
no una aplicación publicada en Internet.
