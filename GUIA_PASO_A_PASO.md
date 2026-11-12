# Guía paso a paso: controlar a Bittle con la voz 🐶🎤

Esta guía explica cómo poner en marcha **a mano** el programa `bittle_voz.py` en un PC con **Windows**, usando **VS Code**.
No hace falta saber programar. Solo tienes que seguir los pasos en orden y copiar los comandos tal cual.

---

## ¿Qué hace el programa?

Tú hablas y Bittle obedece. Por dentro pasa esto:

```
micrófono  →  Vosk (entiende tu voz)  →  comando  →  Bluetooth  →  Bittle
```

1. El **micrófono** del PC escucha todo el rato.
2. **Vosk** convierte tu voz en texto. Funciona **sin Internet**.
3. El programa busca en ese texto una orden conocida (por ejemplo, «siéntate»).
4. Envía la orden a Bittle por **Bluetooth**.
5. **Bittle** hace el movimiento.

---

## Lo que necesitas (lista de comprobación)

- [ ] Un PC con **Windows 10 u 11**, con micrófono (el del portátil sirve) y **Bluetooth**.
- [ ] **Python 3.12 o más nuevo** (en el PC de pruebas se usó Python 3.14).
- [ ] **VS Code** (Visual Studio Code) con la extensión **Python**.
- [ ] La carpeta **`VOICE-BITTLE`**, que contiene el archivo `bittle_voz.py`.
- [ ] El **modelo de voz en español** de Vosk (unos 39 MB, lo descargamos en el paso 7).
- [ ] El robot **Bittle** con la **batería cargada**.
- [ ] Conexión a Internet **solo para instalar** (después ya no hace falta).

---

## Paso 1. Instalar Python

1. Entra en <https://www.python.org/downloads/> y descarga la última versión para Windows.
2. Abre el instalador.
3. **MUY IMPORTANTE:** abajo del todo, marca la casilla **«Add python.exe to PATH»**.
4. Pulsa **«Install Now»** y espera a que termine.

Deberías ver al final un mensaje como **«Setup was successful»**.

> Si ya tenías Python 3.12 o más nuevo, puedes saltarte este paso.

---

## Paso 2. Instalar VS Code y la extensión de Python

1. Entra en <https://code.visualstudio.com/> y descarga VS Code para Windows.
2. Instálalo con las opciones por defecto.
3. Abre VS Code.
4. A la izquierda, pulsa el icono de **Extensiones** (cuatro cuadraditos) o pulsa `Ctrl+Mayús+X`.
5. Busca **Python** e instala la de **Microsoft**.

Deberías ver que la extensión «Python» aparece como instalada.

---

## Paso 3. Abrir la carpeta del proyecto en VS Code

1. En VS Code, ve al menú **File > Open Folder…** (en español: **Archivo > Abrir carpeta…**).
2. Elige la carpeta **`VOICE-BITTLE`** (la que tiene dentro `bittle_voz.py`).
3. Si VS Code pregunta si confías en los autores, pulsa **«Yes, I trust the authors»**.

Deberías ver a la izquierda la lista de archivos, entre ellos **`bittle_voz.py`**.

> Ojo: abre la carpeta `VOICE-BITTLE`, no la carpeta de arriba (`VOICE-BITTLE-ARGOS`).

---

## Paso 4. Abrir la terminal

La **terminal** es una ventana donde escribes órdenes de texto al ordenador.

1. En VS Code, ve al menú **Terminal > New Terminal** (o pulsa `Ctrl+ñ` con teclado español).
2. Se abre un panel abajo.

Deberías ver una línea parecida a esta (es PowerShell):

```
PS C:\...\VOICE-BITTLE>
```

Lo importante es que **termine en `VOICE-BITTLE>`**. Eso significa que estás en la carpeta correcta.

Para comprobar que Python funciona, escribe esto y pulsa **Enter**:

```powershell
py --version
```

Deberías ver algo como `Python 3.14.0` (vale cualquier 3.12 o superior).

> **Cómo usar los comandos de esta guía:** copia el comando, pégalo en la terminal (clic derecho o `Ctrl+V`) y pulsa **Enter**. Uno cada vez.

---

## Paso 5. Crear el entorno virtual

Un **entorno virtual** es una «cajita» con su propio Python y sus librerías, solo para este proyecto, para no mezclarlo con nada más.

```powershell
py -m venv .venv
```

Tarda unos segundos y **no muestra nada** si todo va bien.
Deberías ver que aparece una carpeta nueva llamada **`.venv`** en la lista de archivos de la izquierda.

> Si VS Code pregunta «We noticed a new environment… select it for the workspace?», pulsa **Yes**.

---

## Paso 6. Instalar las librerías

El programa necesita cuatro librerías:

- **vosk**: reconoce la voz.
- **sounddevice**: lee el micrófono.
- **pyserial**: habla con Bittle por puerto COM.
- **bleak**: habla con Bittle por Bluetooth LE.

```powershell
.\.venv\Scripts\python.exe -m pip install vosk sounddevice pyserial bleak
```

Deberías ver cómo se descargan paquetes y al final una línea que empieza por **`Successfully installed`**.

> **Fíjate:** en esta guía **siempre** usamos `.\.venv\Scripts\python.exe` y no `python` a secas. Así usamos el Python de la cajita, que es el que tiene las librerías. **No hace falta «activar» el entorno.**

---

## Paso 7. Descargar el modelo de voz en español

1. Descarga este archivo (unos 39 MB):
   <https://alphacephei.com/vosk/models/vosk-model-small-es-0.42.zip>
2. Dentro de `VOICE-BITTLE`, crea una carpeta llamada **`modelos`** (si no existe ya).
3. Descomprime el zip **dentro de `modelos`**.

Al final la estructura tiene que quedar **exactamente así**:

```
VOICE-BITTLE\
├── bittle_voz.py
└── modelos\
    └── vosk-model-small-es-0.42\
        ├── am\
        ├── conf\
        ├── graph\
        ├── ivector\
        └── README
```

**Error típico: la carpeta doble.** Al descomprimir, Windows a veces crea esto:

```
modelos\vosk-model-small-es-0.42\vosk-model-small-es-0.42\am ...   ← MAL
```

Si te pasa, mueve la carpeta de dentro hacia arriba. La carpeta `vosk-model-small-es-0.42` tiene que tener **directamente** dentro `am`, `conf`, `graph` e `ivector`.

Puedes comprobarlo con este comando:

```powershell
dir modelos\vosk-model-small-es-0.42
```

Deberías ver las carpetas **`am`, `conf`, `graph`, `ivector`** y el archivo `README`.

---

## Paso 8. Primera prueba: modo simulado escribiendo (sin robot, sin micro)

Empezamos sin riesgo: **escribes** las órdenes con el teclado y el programa solo **muestra** lo que enviaría. Bittle no se mueve.

```powershell
.\.venv\Scripts\python.exe bittle_voz.py --simulado --texto
```

Deberías ver:

```
Órdenes: siéntate, de pie/levántate, camina/adelante, corre, atrás, izquierda, derecha, saluda/hola, flexiones, estira, descansa, BAILA, PARA/quieto

⌨  Modo texto: escribe la orden y pulsa Enter (Ctrl+C para salir)

>
```

Escribe `siéntate` y pulsa **Enter**. Deberías ver:

```
🗣  «siéntate» -> sentarse (ksit)
   [SIMULADO] se enviaría: 'ksit'
```

Prueba también `hola`, `baila` y luego `para`. Si escribes algo que no es una orden (por ejemplo `qué tal`), verás `-> no es una orden`.

Para salir, pulsa **`Ctrl+C`**. Verás `Saliendo...`.

---

## Paso 9. Segunda prueba: modo simulado con la voz

Ahora usamos el micrófono, pero todavía sin robot.

```powershell
.\.venv\Scripts\python.exe bittle_voz.py --simulado
```

Tarda unos segundos en cargar el modelo. Deberías ver:

```
🎤 Escuchando... habla cuando quieras (Ctrl+C para salir)
```

Di en voz alta, claro y sin prisa: **«siéntate»**. Deberías ver:

```
🗣  «siéntate» -> sentarse (ksit)
   [SIMULADO] se enviaría: 'ksit'
```

**Si no aparece nada al hablar**, puede que esté usando otro micrófono. Mira la lista de micrófonos:

```powershell
.\.venv\Scripts\python.exe bittle_voz.py --listar
```

En la parte **«Micrófonos:»** verás líneas como `[1] Micrófono (Realtek...)`. El número entre corchetes es el índice. Prueba con él, por ejemplo el 1:

```powershell
.\.venv\Scripts\python.exe bittle_voz.py --simulado --microfono 1
```

Sal con **`Ctrl+C`**.

---

## Paso 10. Emparejar Bittle con el PC

1. **Cierra la app de Petoi del móvil** (o apaga el Bluetooth del móvil). Bittle solo acepta **una conexión a la vez**.
2. **Enciende Bittle** (batería cargada).
3. En Windows: **Configuración > Dispositivos > Bluetooth y otros dispositivos** (en Windows 11: **Configuración > Bluetooth y dispositivos**).
4. Pulsa **«Agregar Bluetooth u otro dispositivo» > Bluetooth**.
5. Espera a que aparezca Bittle y pulsa sobre él.

En el PC de pruebas apareció con estos nombres (en el tuyo cambian las últimas letras):

| Nombre que aparece | Tipo de Bluetooth | Cómo se conecta |
|---|---|---|
| `Petoi-30AD` | Bluetooth clásico | Crea un **puerto COM** (aquí fue `COM7`) → usar `--puerto` |
| `PetoiBLE-30AD` | Bluetooth LE | Sin puerto COM → usar `--ble` |

Deberías ver Bittle en la lista de dispositivos como **«Emparejado»** o **«Conectado»**.

> Si pide un PIN, prueba `0000` o `1234`.

---

## Paso 11. Averiguar el puerto COM

Solo hace falta si usas el **Bluetooth clásico** (`Petoi-XXXX`).

**Opción A: con el programa**

```powershell
.\.venv\Scripts\python.exe bittle_voz.py --listar
```

Deberías ver tres listas:

```
Puertos COM:
  COM7: Vínculo serie estándar a través de Bluetooth (COM7)
  ...
Dispositivos Bluetooth LE cercanos (5 s):
  XX:XX:XX:XX:XX:XX  PetoiBLE-30AD
  ...
Micrófonos:
  [1] Micrófono (...)
```

Si salen **dos** puertos «a través de Bluetooth», normalmente uno es de entrada y otro de salida. Prueba primero el de número más bajo; si no conecta, el otro.

**Opción B: con el Administrador de dispositivos**

1. Clic derecho en el botón de Inicio > **Administrador de dispositivos**.
2. Despliega **Puertos (COM y LPT)**.
3. Busca «Vínculo serie estándar a través de Bluetooth (COMx)».

También puedes verlo en **Panel de control > Dispositivos e impresoras > clic derecho en Bittle > Propiedades > pestaña Servicios / Hardware**.

---

## Paso 12. ¡Ahora sí! Ejecutar con el robot de verdad ⚠

Antes de empezar:

- Pon a Bittle **en el suelo**, con **espacio libre** alrededor (lejos del borde de la mesa).
- **«Para»** cancela la cola y solicita equilibrio; la parada física depende del reconocimiento y del enlace.

**Si tu Bittle tiene puerto COM** (cambia `COM7` por el tuyo):

```powershell
.\.venv\Scripts\python.exe bittle_voz.py --puerto COM7
```

Deberías ver:

```
Conectando a COM7 a 115200 baudios...
Conectado. Bittle listo.
```

Al abrir el puerto, **la placa de Bittle se reinicia** (puede pitar o moverse un poco). El programa espera hasta que Bittle dice «Ready!» (máximo 10 segundos). Si en lugar de «Bittle listo» pone «Conectado (sin confirmación de arranque)», normalmente funciona igual.

**Si tu Bittle es Bluetooth LE:**

```powershell
.\.venv\Scripts\python.exe bittle_voz.py --ble
```

Deberías ver:

```
Buscando Bittle por Bluetooth LE (10 s)...
Encontrado: PetoiBLE-30AD (XX:XX:XX:XX:XX:XX)
Conectado por BLE.
```

Si hay varios robots en clase, indica parte del nombre del tuyo:

```powershell
.\.venv\Scripts\python.exe bittle_voz.py --ble --nombre-ble 30AD
```

Después verás `🎤 Escuchando...`. Di **«de pie»** y luego **«saluda»**. 🎉

**Para terminar:** pulsa **`Ctrl+C`**. El programa deja a Bittle **en reposo** (`krest`) antes de cerrarse.

---

## Tabla de órdenes de voz

Puedes decir «siéntate y después ponte de pie» o dar órdenes por separado;
se guardan en una cola y se ejecutan en orden. Usa las órdenes de la tabla y
los conectores de [SECUENCIAS.md](SECUENCIAS.md). Allí se explican los tiempos,
la cancelación y las pruebas pendientes. El PDF es anterior a este cambio.

| Di… | Bittle hace… | Código enviado |
|---|---|---|
| **siéntate**, sentado | Se sienta | `ksit` |
| **de pie**, pie, ponte de pie, levántate, arriba | Se pone de pie | `kup` |
| **camina**, adelante, anda | Camina hacia delante | `kwkF` |
| **corre** | Trota hacia delante | `ktrF` |
| **atrás**, marcha atrás | Camina hacia atrás | `kbk` |
| **izquierda** | Gira a la izquierda | `kwkL` |
| **derecha** | Gira a la derecha | `kwkR` |
| **saluda**, hola | Saluda con la pata | `khi` |
| **flexiones** | Hace flexiones | `kpu` |
| **estira** (no «estírate») | Se estira | `kstr` |
| **descansa**, duerme | Se tumba con los motores relajados | `krest` |
| **baila**, baile, bailar | Baile casero de unos 24 segundos | `BAILE` |
| **cristiano**, ronaldo, siu | Celebración «SIUUU»: se levanta sobre las patas traseras, pone las delanteras en X y el PC grita «SIUUU» | `CRISTIANO` |
| **para**, quieto, alto | **Se para** (postura de equilibrio). **Siempre tiene prioridad** y corta cualquier baile | `kbalance` |

> ¿Por qué «estira» y no «estírate»? Porque «estírate» no está en el vocabulario del modelo de voz y no lo reconocería. (En el modo `--texto` sí funciona escribirlo.)

---

## Cómo añadir tu propio comando

Vamos a crear la orden **«gira»**, que hace a Bittle dar pasitos girando a la izquierda durante 3 segundos y luego quedarse quieto.

Abre `bittle_voz.py` en VS Code y haz **tres cambios**:

**1) La secuencia de movimientos**, en `COREOGRAFIAS`. Cada paso es `("orden", segundos de espera)`. Añade estas líneas dentro de las llaves `{ }`, por ejemplo justo antes de `"BAILE": [`:

```python
    "GIRO": [
        ("kvtL", 3.0),      # pasitos girando a la izquierda durante 3 s
        ("kbalance", 0.5),  # y se queda quieto
    ],
```

**2) La frase que la lanza**, en `COMANDOS`. La frase va **en minúsculas y sin tildes**:

```python
    "gira": ("GIRO", "dar una vuelta (casero)"),
```

**3) La palabra para el reconocedor**, en la lista `GRAMATICA`. Aquí va **con tildes** si las tiene (antes de `"[unk]"`):

```python
"gira",
```

Guarda (`Ctrl+S`) y prueba primero en simulado:

```powershell
.\.venv\Scripts\python.exe bittle_voz.py --simulado --texto
```

Escribe `gira`. Deberías ver `-> dar una vuelta (casero) (GIRO)` y `[SIMULADO] se enviaría: 'kvtL'`.

**¿Existe mi palabra en el modelo?** Si una palabra no está en el vocabulario, Vosk nunca la reconocerá por voz. Para comprobarlo:

1. En `bittle_voz.py`, cambia temporalmente `SetLogLevel(-1)` por `SetLogLevel(0)`.
2. Ejecuta el modo voz simulado (paso 9).
3. Si ves una línea como `WARNING ... Ignoring word missing in vocabulary: 'tu palabra'`, esa palabra **no vale**: elige otra.
4. Vuelve a dejar `SetLogLevel(-1)`.

Otras habilidades de Bittle que puedes usar en tus secuencias (sacadas del propio programa): `ksit`, `kup`, `kbalance`, `khi`, `kpu`, `kstr`, `krest`, `kvtF`, `kvtL`, `kvtR`, `kmw` (moonwalk), `kbuttUp`, `kchr`, y `m0 45` (girar la cabeza a 45°).

---

## Problemas frecuentes y soluciones

| Lo que ves | Qué pasa | Solución |
|---|---|---|
| `No encuentro el modelo Vosk en ...` | La carpeta del modelo no está donde debe | Revisa el paso 7. Debe existir `modelos\vosk-model-small-es-0.42\am` (cuidado con la carpeta doble). |
| `No module named vosk` (o `serial`, `bleak`...) | Has usado otro Python, no el del entorno virtual | Ejecuta siempre con `.\.venv\Scripts\python.exe`. Si sigue, repite el paso 6. |
| `py` no se reconoce como comando | Python no está instalado o falta el PATH | Repite el paso 1 marcando «Add python.exe to PATH» y cierra y abre VS Code. |
| `No puedo abrir COM7: could not open port 'COM7'`, mensajes sobre **semáforo** o «**Se ha quitado el dispositivo**» | Bittle apagado, batería baja, demasiado lejos, o el puerto lo usa otro programa | Carga la batería, acércalo, cierra la app Petoi y otras terminales. Si sigue, quita Bittle en Bluetooth y vuelve a emparejarlo (paso 10) y comprueba el puerto (paso 11). |
| `Se perdió la conexión con Bittle. Reconectando...` | Se cortó el Bluetooth | El programa reintenta solo. Si se repite, **carga la batería**. |
| `No encuentro a Bittle. Dispositivos BLE vistos: ...` | Con `--ble` no lo encuentra | Comprueba que está encendido y que la app del móvil está cerrada. Usa `--nombre-ble` con parte del nombre que salga en la lista. |
| `Bittle: ?0` | Bittle no entendió una orden concreta | Normalmente no pasa nada; repite la orden. Si ocurre con un comando casero, revisa cómo está escrita la orden. |
| Hablo y no sale nada | El programa escucha otro micrófono, o hay mucho ruido | Usa `--listar`, elige otro con `--microfono N`, acércate y habla claro. |
| `«...» -> no es una orden` | Ha oído algo que no está en la tabla | Usa exactamente las palabras de la tabla de órdenes. |
| PowerShell dice que **no se permite ejecutar scripts** (al intentar activar el entorno) | Windows bloquea `Activate.ps1` | **No hace falta activar nada.** Llama directamente a `.\.venv\Scripts\python.exe` como en esta guía. |
| La terminal no termina en `VOICE-BITTLE>` | Estás en otra carpeta | Repite el paso 3 (Abrir carpeta) y abre una terminal nueva. |

---

## Seguridad 🛟

- **Prueba siempre primero con `--simulado`.** Solo muestra lo que enviaría; Bittle no se mueve.
- Deja **espacio libre** alrededor del robot y nunca lo pongas en el borde de una mesa.
- Di **«para»** (o «quieto», «alto») para detenerlo en cualquier momento. Esta orden **siempre gana** a las demás.
- **Carga la batería** antes de la celebración de Cristiano: ponerse de pie sobre dos patas gasta mucho y con batería baja puede caerse.
- Para salir, **`Ctrl+C`**: Bittle se queda en reposo.

---

## Glosario

- **Terminal:** ventana donde escribes órdenes de texto al ordenador en vez de usar el ratón. En VS Code está abajo y usa **PowerShell**.
- **Python:** el lenguaje de programación en el que está escrito `bittle_voz.py`. Hay que instalarlo para poder ejecutar el programa.
- **Entorno virtual (`.venv`):** una «cajita» con su propio Python y sus librerías solo para este proyecto.
- **Librería:** código ya hecho por otras personas que nuestro programa usa (por ejemplo, Vosk para la voz).
- **Puerto COM:** una «puerta» de comunicación que Windows crea al emparejar Bittle por Bluetooth clásico (por ejemplo, `COM7`). El programa envía las órdenes por ahí.
- **Bluetooth LE (Low Energy):** un tipo de Bluetooth que gasta menos batería. No crea puerto COM; por eso se usa la opción `--ble`.
- **Modelo de voz:** los archivos que Vosk necesita para entender el español (la carpeta `vosk-model-small-es-0.42`). Funciona sin Internet.
- **Vosk:** la librería que convierte tu voz en texto.

---

## Resumen de opciones del programa

| Opción | Para qué sirve |
|---|---|
| `--simulado` | No envía nada al robot, solo muestra lo que enviaría |
| `--texto` | Escribes las órdenes en vez de hablarlas |
| `--puerto COMx` | Conecta con Bittle por el puerto COM indicado (Bluetooth clásico) |
| `--ble` | Conecta con Bittle por Bluetooth LE |
| `--nombre-ble NOMBRE` | Con `--ble`, busca un Bittle cuyo nombre contenga ese texto |
| `--listar` | Muestra puertos COM, dispositivos Bluetooth LE cercanos y micrófonos |
| `--microfono N` | Usa el micrófono número N (ver `--listar`) |
| `--modelo CARPETA` | Usa un modelo de voz guardado en otra carpeta |
| `--help` | Muestra la ayuda del programa |

Ver la ayuda:

```powershell
.\.venv\Scripts\python.exe bittle_voz.py --help
```
