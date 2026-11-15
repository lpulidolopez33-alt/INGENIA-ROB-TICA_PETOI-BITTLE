# Catálogo de órdenes implementadas

Extraído de `bittle_voz.COMANDOS` y `GRAMATICA` el 2026-11-12. Las tildes se normalizan.
El panel comparte este parser con la consola; no interpreta lenguaje libre ni duraciones habladas.

| Token / acción | Descripción | Alias textuales del parser |
|---|---|---|
| ksit | sentarse | sientate, sentado, sienta |
| kup | ponerse de pie | ponte de pie, de pie, pie, levantate, arriba |
| kwkF | caminar adelante | camina, adelante, anda |
| ktrF | trotar adelante | corre |
| kbk | caminar hacia atrás | atras, marcha atras |
| kwkL | girar a la izquierda | izquierda |
| kwkR | girar a la derecha | derecha |
| khi | saludar | saluda, hola |
| kpu | flexiones | flexiones |
| kstr | estirarse | estirate, estira |
| krest | descansar (servos relajados) | descansa, duerme |
| BAILE | bailar (coreografía casera) | baila, baile, bailar |
| CRISTIANO | celebración SIUUU de Cristiano | cristiano, ronaldo, siu |
| kbalance | parar / equilibrio | para, quieto, alto, stop |

## Reconocimiento por voz

Gramática enviada a Vosk:

siéntate, sentado, sienta, ponte de pie, de pie, levántate, arriba, camina, adelante, anda, corre, atrás, marcha atrás, izquierda, derecha, saluda, hola, flexiones, estira, descansa, duerme, baila, baile, bailar, cristiano, ronaldo, siu, para, quieto, alto, [unk], y, luego, después, primero, entonces, stop, estírate

Los alias del parser y las frases explícitas de GRAMATICA no son idénticos. Una palabra puede
aparecer dentro de otra frase de la gramática; eso no acredita que todos los alias se reconozcan
con la misma fiabilidad. Las pruebas del parser son de texto, no ensayos acústicos de cada alias.

Conectores: y, luego, después, primero, entonces. La prioridad de para/quieto/alto/stop
es absoluta: si aparecen como palabra, se descartan las otras acciones de esa frase.
Incluso «no pares» no es equivalente a «no para»: el parser compara palabras y no entiende
negación semántica; «no para» solicita equilibrio. Evitar lenguaje ambiguo.

BAILE y CRISTIANO son secuencias programadas (habilidades, articulaciones, esperas y voz
Windows en Cristiano); no se envían como tokens literales. Su existencia no prueba compatibilidad
con todas las placas. Estado/historial y cambio de idioma no forman parte de este catálogo.

Los tiempos y límites están en [SECUENCIAS.md](../SECUENCIAS.md).
