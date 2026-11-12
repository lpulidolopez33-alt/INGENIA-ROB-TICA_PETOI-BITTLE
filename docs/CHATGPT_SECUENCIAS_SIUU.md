# Dar órdenes a Bittle hablando con ChatGPT: secuencias de 1 a 4 acciones

La idea es **hablar con ChatGPT** y que este cree un Issue estructurado en GitHub para un programa que está abierto en el ordenador. El ordenador debe estar emparejado por Bluetooth serie con Petoi Bittle. **Ni el chat ni GitHub se conectan directamente al Bluetooth.** La ejecución desde el modo Voz de ChatGPT depende del soporte para acciones de aplicaciones y puede necesitar confirmar una acción desde la pantalla. Siempre puede enviarse la orden por texto.

## Flujo

1. En el ordenador, arrancar el puente. Antes de modo real, probar con simulación.
2. ChatGPT crea un GitHub Issue con título **exacto** `[BITTLE-SEQUENCE v1]` y cuerpo JSON con esta estructura:

```json
{"schema":"bittle-chatgpt-sequence/v1","actions":["stand","sit","stand","sit"]}
```

3. El programa solo recoge Issues **nuevos y recientes** de la cuenta propietaria autorizada, comprueba el JSON exacto, limita la lista a **cuatro** movimientos y ejecuta los tokens por orden.
4. Cada token se transmite con separación temporal. **El intervalo no garantiza que el robot haya terminado físicamente la acción**.
5. Si se desconecta Bluetooth, se interrumpe la secuencia y se descartan los pasos no enviados.

**Acciones admitidas:** `sit` → `ksit`, `stand` → `kup`, `balance` → `kbalance` (verificar en el firmware), y `siuu` → `T` **solo tras crear, cargar y verificar la rutina personalizada**.

## El SIUU de Cristiano Ronaldo

No existe garantía de que Bittle tenga el movimiento SIUU de fábrica. Para crearlo:

1. Abrir **Petoi Desktop App → Skill Composer**, eligiendo el modelo real de Bittle.
2. Diseñar una celebración **estable y segura**, por ejemplo una pose, un gesto con una pata y una vuelta a la postura de equilibrio. Un salto con giro no debe ejecutarse sin analizar estabilidad y riesgos.
3. Exportar y reproducir la skill de prueba con supervisión. Petoi documenta que **`T` reproduce la última skill exportada**, que puede ser sobrescrita por otras exportaciones: https://docs.petoi.com/desktop-app/skill-composer
4. **Solo si se ha verificado** que la última skill exportada es SIUU, activar `--allow-siuu --confirm-siuu SIUU_VERIFICADO`. Si no, el programa rechazará por completo las secuencias que contengan `siuu`.

## Preparación (Windows)

Con el repositorio actualizado:

```powershell
git pull origin main
python -m pip install -r requirements.txt
python -m pytest -q tests/unit/test_puente_chatgpt_secuencias.py
```

Los cambios se incorporan a `main` solo tras revisar la propuesta correspondiente.

**Prueba simulada sin robot:**

```powershell
python tools/puente_chatgpt_secuencias.py --dry-run
```

Mantener el programa abierto. **Esperar a ver «Sincronización inicial» antes de crear un nuevo Issue**; las órdenes previas se ignoran.

El puente puede utilizarse sin `GITHUB_TOKEN` porque el repositorio es público, pero entonces consulta GitHub aproximadamente cada 65 segundos para respetar límites de la API. Para consultas más frecuentes, configurar un token con **acceso de solo lectura a Issues** como variable de entorno local `GITHUB_TOKEN`, nunca ponerlo en el chat ni subirlo al repositorio. Incluso con token, GitHub no garantiza latencia en tiempo real.

**Ejemplo de prueba real supervisada, tras comprobar modelo, puerto COM, terminador y baudios del firmware:**

```powershell
python tools/puente_chatgpt_secuencias.py --live --arm --port COM7 --interval 8
```

Cambiar `COM7` por el puerto Bluetooth saliente real. El intervalo de 8 segundos es **provisional**. La prueba inicial debe ser un único movimiento antes de secuencias largas.

**Ejemplo de prueba real con SIUU verificado:**

```powershell
python tools/puente_chatgpt_secuencias.py --live --arm --port COM7 --interval 8 --allow-siuu --confirm-siuu SIUU_VERIFICADO
```

No ejecutar este último comando mientras la habilidad personalizada no esté validada.

## Seguridad y límites

- Solo se admiten las cuatro acciones semánticas exactas; no se envía texto arbitrario al robot.
- El primer barrido fija un cursor. Cada Issue se marca procesado **antes** de enviar movimientos, de modo que un reinicio no repite órdenes.
- La cola se ejecuta en el programa local. El chat no recibe confirmación física real del robot. El cierre con Ctrl+C **no detiene de forma segura una acción ya enviada**.
- Se exige supervisión presencial y posibilidad de cortar alimentación cuando sea necesario.
- No abrir el puerto COM simultáneamente desde Petoi Desktop App y desde el puente.
- Un fallo de comunicación interrumpe los envíos restantes, sin reintento automático.
- Los Issues son públicos: **no escribir información privada ni claves**.
- El modo Live de ChatGPT y la capacidad para crear Issues en GitHub durante una conversación de voz deben comprobarse en vuestra sesión. Si no están disponibles, se puede utilizar texto o una futura app puente privada.

## Ejemplo para pedir una secuencia a ChatGPT

«Crea una orden nueva para Bittle con cuatro movimientos, en este orden: ponerse de pie, sentarse, ponerse de pie, sentarse».

ChatGPT debe crear, con la conexión GitHub habilitada, **un Issue nuevo** en `lpulidolopez33-alt/INGENIA-ROB-TICA_PETOI-BITTLE`, título `[BITTLE-SEQUENCE v1]`, y cuerpo:

```json
{"schema":"bittle-chatgpt-sequence/v1","actions":["stand","sit","stand","sit"]}
```

Cuando la rutina esté aprobada, el cuarto elemento podrá ser `siuu`.

## Verificación pendiente

El código es un prototipo de integración. Antes de afirmar que funciona con el Bittle físico hay que ejecutar pytest, revisar los resultados, confirmar Bluetooth SPP, el modelo de placa, las órdenes del firmware y la rutina SIUU. Sin telemetría de fin de movimiento, cada siguiente orden se envía por un intervalo estimado, no por confirmación real.
