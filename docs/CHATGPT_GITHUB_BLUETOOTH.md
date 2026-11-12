# Control de Bittle desde ChatGPT con GitHub y Bluetooth (prototipo seguro)

## Alcance y límites

ChatGPT, mediante el conector de GitHub, crea un **Issue** estructurado. Un programa que ejecutáis **localmente en vuestro ordenador** consulta esos Issues, valida identidad, tiempo y acción, y escribe únicamente el token autorizado en el **puerto serie Bluetooth saliente** de Petoi. GitHub **no** controla el Bluetooth por sí solo; el ordenador debe permanecer encendido y ejecutar el programa.

En esta primera versión se admiten solo las órdenes **sentarse** (`ksit`) y **ponerse de pie** (`kup`). No hay ejecución de código desde los Issues, ni comandos libres, ni caminata remota. El puente no consulta ni modifica las pruebas de voz H3: reutiliza la protección de `EnlaceBittle`, pero **no finge que una orden de chat haya sido reconocida por Vosk**. Esta modalidad de control es experimental y no forma parte de la validación física H4.

**Privacidad:** los Issues del repositorio actual son públicos. El contenido del comando es público; **nunca** escribir tokens, contraseñas, datos personales o claves en ellos.

## 1. Emparejar el robot con el ordenador

1. Encended Bittle y emparejad el módulo Petoi desde los ajustes Bluetooth. El nombre suele contener `Petoi` o `Bittle`.
2. En **Windows**, abrid las opciones avanzadas de Bluetooth y consultad el **puerto COM saliente** (no el entrante), por ejemplo `COM7`. Algunos BiBoard aparecen como `Bittle..._BLE` y Windows les asigna COM; no seleccionéis por intuición `..._SSP` si la documentación de vuestra placa indica lo contrario.
3. En **macOS**, el puerto compatible puede ser `/dev/cu.PetoiSerial` o `/dev/cu.Bittle...` (no `tty`). No todas las placas BLE exponen un puerto SPP/serie virtual: si no aparece uno, hace falta confirmar la placa/firmware y usar un adaptador compatible; este puente **no implementa BLE GATT nativo**.
4. Dejad cerradas la aplicación Petoi, el monitor serie y cualquier otra aplicación que ocupe el mismo puerto.

Documentación oficial: [Bluetooth Petoi](https://docs.petoi.com/communication-modules/dual-mode-bluetooth), [BiBoard](https://docs.petoi.com/bluetooth-connection/biboard), [Protocolo serie](https://docs.petoi.com/apis/serial-protocol).

## 2. Preparar el ordenador

En terminal/PowerShell dentro de la carpeta del repositorio, después de actualizar a la versión que incorpore este PR:

```bash
python -m pip install pyserial==3.5 pytest
python -m pytest -q
python tools/puente_github.py --dry-run --list-ports
```

En macOS puede ser `python3` en vez de `python`. Para **simulación**:

```bash
python tools/puente_github.py --dry-run
```

La primera consulta solo establece la referencia inicial y descarta todo lo anterior. **Esperad a que aparezca el mensaje de inicio y se complete la primera consulta** antes de crear una orden. Sin token, el puente consulta cada **65 s** debido a los límites de GitHub. Para consultas cada **10 s**, generad en GitHub un *fine-grained personal access token* con permiso **Issues: read-only** para este repositorio y configuradlo **solo en el ordenador**:

PowerShell (Windows):

```powershell
$env:GITHUB_TOKEN="PEGAD_AQUI_EL_TOKEN_SOLO_EN_VUESTRO_ORDENADOR"
python tools/puente_github.py --dry-run
```

macOS/Linux:

```bash
export GITHUB_TOKEN="PEGAD_AQUI_EL_TOKEN_SOLO_EN_VUESTRO_ORDENADOR"
python3 tools/puente_github.py --dry-run
```

Nunca compartáis ese token en ChatGPT o GitHub. Si no creáis token, también funciona, con mayor latencia y dentro del límite público.

## 3. Crear una orden desde ChatGPT

Pedid explícitamente a ChatGPT: «Crea la orden de GitHub para que Bittle se siente». Con el conector de GitHub conectado, ChatGPT deberá crear un Issue en `lpulidolopez33-alt/INGENIA-ROB-TICA_PETOI-BITTLE` con:

**Título exacto:**

```text
[BITTLE-CMD v1]
```

**Cuerpo exacto:**

```json
{"schema":"bittle-github-command/v1","action":"sit"}
```

Para ponerse de pie, sustituir `sit` por `stand`. El puente **solo acepta** Issues creados por la cuenta GitHub `lpulidolopez33-alt` (ID verificada 309672387), abiertos, creados tras arrancar el puente, de menos de 180 segundos, con JSON exacto y acciones autorizadas. Rechaza entradas arbitrarias y los comandos se procesan una sola vez. Espera al menos 5 segundos entre movimientos. **Una orden enviada no equivale a haber confirmado la postura física.**

Si ChatGPT crea el Issue con otra identidad de GitHub, el puente lo rechazará: nunca desactivéis el filtro de identidad para resolverlo.

## 4. Activar el robot real (solo con un supervisor presente)

Situad Bittle sobre superficie firme, seca, sin obstáculos, lejos de bordes; cargad batería y mantened una persona capaz de detenerlo localmente. Probad antes las órdenes en simulación. En una segunda terminal, comprobad qué COM hay disponible:

```bash
python tools/puente_github.py --dry-run --list-ports
```

Con el puerto correcto, **cerrad la simulación** y abrid **una sola** sesión real (Windows, ejemplo COM7):

```bash
python tools/puente_github.py --live --arm --port COM7
```

macOS (puerto de ejemplo):

```bash
python3 tools/puente_github.py --live --arm --port /dev/cu.PetoiSerial
```

El adaptador utiliza `115200` baudios. Por defecto no añade final de línea, coherente con el monitor serie NyBoard de Petoi; si vuestro firmware necesita LF, añadid `--terminator lf` **solo tras verificarlo**. Comprobad primero la acción de sentado, con supervisión, y no interpretéis `ENVIADO` como confirmación física. `Ctrl+C` detiene la escucha en el ordenador; **no es una parada de emergencia del movimiento que ya esté ejecutándose**. Usad el apagado/parada física según el manual y el responsable del ensayo.

## 5. Seguridad, limitaciones y próximos pasos

- El modo por defecto es simulación, y para movimientos reales se necesita la doble opción local `--live --arm` y un puerto explícito.
- Ante fallo de Bluetooth o error de escritura, el puente se detiene, sin reintentos de movimiento ni reconexión automática.
- Las órdenes antiguas se descartan; se guarda el ID de Issue **antes** de escribir al puerto. Esto prefiere perder una orden antes que repetirla después de un fallo.
- El estado queda en `~/.bittle/github-issue-cursor.json`, fuera del repositorio. El puente no puede verificar si el robot se ha sentado o levantado, solo si ha intentado transmitir.
- La API GitHub es un **canal de transporte experimental, no un sistema de control de tiempo real**. Su latencia depende de la red, límites y estado del ordenador.
- El agente solo lee los 100 Issues más recientes; si el repositorio recibe un volumen extraordinario de Issues antes de un sondeo puede perder órdenes, nunca reenviarlas.
- GitHub Issues es público en este repositorio; para un despliegue estable conviene migrar a un canal privado y autenticado con confirmaciones y límites de control más sólidos.
- Pendiente: verificar modelo de placa, puerto SPP real y comportamiento de los tokens en pruebas físicas autorizadas (H4); no se ha probado sobre un robot físico desde ChatGPT.