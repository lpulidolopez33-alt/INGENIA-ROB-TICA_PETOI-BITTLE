# Consolidación final y continuación H4

## Evolución del alcance

La versión final incorpora secuencias FIFO, órdenes durante la ejecución,
PARA prioritario e interfaz web local. Sustituyen el rechazo de nuevas órdenes
mientras se ejecutaba una acción. Se eligió Python con Vosk local y transporte
serie para aprovechar la solución que el usuario confirmó funcionando.
Inglés, consultas habladas de estado/historial, confianza acústica y persistencia
no forman parte del producto final; los objetivos cuantitativos anteriores no
se presentan como medidos. La correspondencia histórica se conserva en
[la evolución de requisitos](../h1/EVOLUCION_REQUISITOS.md).

Estos cambios se consolidan por instrucción del usuario. No consta aprobación
académica del cambio de alcance. Antes de la aceptación académica debe contrastarse
con el enunciado y el profesor si las funciones retiradas eran obligatorias.
CR-01 se formaliza como mejora elegida por el equipo: cola secuencial y PARA.
Está implementada y verificada; queda su aceptación académica. Véase [CR-01](CR-01.md).

## Estado de los requisitos y H4 disponible

H1-H3 se preparan para entrega junto con las evidencias físicas existentes de H4.
El equipo ya probó Bittle real mediante texto, voz, panel y secuencias; véase
[registro de uso](validacion_usuario.md). No se dispone de más ensayos físicos y
la entrega no depende de repetirlos. La corrección final del transporte y del
tratamiento de entradas se verifica con simuladores, no se revalida en el robot.

| Ámbito | Evidencia y límite |
|---|---|
| Voz y movimientos nominales | Órdenes individuales y secuencias físicas correctas según el equipo; no se conocen las frases exactas ni tiempos |
| Escucha manual | El equipo silencia durante ejecución; se acuerda mantener apagado salvo dictado. Conversación con escucha activa produjo falsas acciones en simulación |
| Bittle y enlace | Bittle normal, Petoi-30AD y COM6 saliente comunicados; firmware exacto no documentado |
| Parada, fallo y correcciones finales | Pruebas automáticas con sustitutos; sin observación física específica ni revalidación posterior |
| CR-01 | Cola con PARA elegida por equipo, ya implementada y probada; aceptación académica no acreditada |
| Vídeos, métricas y aprobación | No aportados; no se inventan ni se exigen como condición de preparar este paquete |

## Correcciones y verificación final

Se retiraron componentes antiguos y sus pruebas, preservados en respaldo externo.
Se corrigió la ruta inicial del modelo del panel para usar `modelos/` dentro del
proyecto. Se corrigió el empaquetador: conserva los metadatos reales, valida el
manifiesto y fija metadatos ZIP para reproducir los mismos bytes desde los mismos
archivos. Las evidencias exportadas omiten rutas personales y nombre del equipo.

La suite actual contiene 49 casos. Los resultados están en
[RESULTADOS.md](../../evidencias/actual/RESULTADOS.md) y la matriz completa en
[TRAZABILIDAD.md](TRAZABILIDAD.md). La simulación y extracción se documentan en
[extraccion_verificada.json](../../evidencias/actual/extraccion_verificada.json).
El agente no abrió hardware ni micrófono real durante las comprobaciones automáticas. El entorno de dependencias de pruebas se
reutilizó; extraer y probar no equivale a una instalación nueva desde Internet.

Para reproducir el paquete, desde la carpeta del proyecto:

```powershell
python tools/generar_evidencias_actuales.py
python tools/verificar_documentacion.py
python tools/empaquetar.py --salida ../VOICE-BITTLE-ARGOS-ENTREGA-FINAL.zip
```

Ejecutar nuevas pruebas cambia fechas y resultados de evidencia, y por tanto el hash
del paquete. Empaquetar dos veces los mismos archivos produce el mismo ZIP.

## Complemento frente a Moodle del 13 de noviembre

H1 v0.4 incorpora los campos aplicables de la plantilla, fuentes, escenarios y fichas.
H2 incorpora historias, primer incremento, dependencias y criterios en T001-T017.
H3 conserva los casos anteriores y añade regresiones de cierre. El código final
corrige el reenvío serie, el descarte de movimientos tras fallo concurrente y la
validación de resultados de voz; esas correcciones solo se comprobaron con sustitutos.
Los nombres están confirmados por SEMP_ARGOS_v1.0, usado solo para identidad.

El repositorio local se inició al consolidar esta entrega y conserva los artefactos
recuperados. No prueba commits anteriores a esa fecha. El remoto del equipo está
pendiente de facilitarse; no se ha publicado. Spec Kit se aplica y registra en la
revisión actual, no se acredita retrospectivamente cada operación histórica.

El usuario confirma que no hubo un cambio docente específico. [CR-01](CR-01.md)
registra la cola elegida por el equipo; queda su aceptación académica. La guía
[PREPARAR_H4](PREPARAR_H4.md) permite completar registros sin inventar resultados.

Confirmación ampliada: voz, panel HTML y cola funcionan con el Bittle físico según el equipo; se silencia manualmente el micrófono durante las acciones. Véase [registro de uso](validacion_usuario.md). Esta comprobación nominal ya está realizada; los casos no observados quedan como límites de evidencia y no como nuevos ensayos obligatorios.
