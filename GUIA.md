# Instalación y uso — aplicación actual

Windows / PowerShell. Entorno constatado: Python 3.12.10 de 64 bits. No se afirma
compatibilidad probada con Python 3.14 por el comentario que traía el ZIP original.

## Instalar

Abre una terminal en la carpeta que contiene `bittle_web.py`:

```powershell
python --version
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-bittle.txt
.\.venv\Scripts\python.exe -m pip check
```

Si ya tienes `.venv` funcionando, no necesitas recrearlo. Las dependencias de uso
son Vosk, sounddevice, pyserial y bleak, con versiones en ese archivo. Para pruebas:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

El HTML, CSS y JavaScript se sirven desde Python; no necesitas Node, npm, Flask,
Internet durante la ejecución ni una cuenta en un servicio de voz.

## Modelo de español

Descarga `vosk-model-small-es-0.42` del [catálogo oficial](https://alphacephei.com/vosk/models)
y extrae la carpeta dentro de `modelos/`. Debe contener, entre otras, `am/`.
No se distribuye el modelo ni el entorno virtual. Usa una ruta de carpeta, no el ZIP.

```powershell
$modelo = ".\modelos\vosk-model-small-es-0.42"
Test-Path "$modelo\am"
```

El panel propone `modelos/vosk-model-small-es-0.42`, dentro del proyecto.
Descarga y extrae el modelo antes de activar el micrófono, o indica otra carpeta válida.
Las rutas relativas se resuelven desde el directorio donde arrancas Python;
`INICIAR_PANEL.bat` cambia automáticamente a la carpeta del programa.

## Panel web (opción principal)

```powershell
.\.venv\Scripts\python.exe -X utf8 bittle_web.py
```

O doble clic en `INICIAR_PANEL.bat`. Sigue [PANEL_WEB.md](PANEL_WEB.md).
No abras `web/index.html` como archivo: requiere el servidor Python.

## Consola alternativa

```powershell
.\.venv\Scripts\python.exe -X utf8 bittle_voz.py --simulado --texto
.\.venv\Scripts\python.exe -X utf8 bittle_voz.py --simulado --modelo $modelo --microfono 1
.\.venv\Scripts\python.exe -X utf8 bittle_voz.py --listar
```

El índice 1 fue el usado durante la sesión; elige el real que enumere tu equipo.
La consola de voz escucha continuamente al arrancar: no usa `/activar` ni `/capturar`.
Por teclado, escribe la frase y pulsa Enter. No hay consultas «estado»/«historial»
por voz en esta aplicación. 

## Bittle real por Bluetooth serie

Empareja el robot en Windows y revisa Más opciones de Bluetooth → Puertos COM.
Selecciona el **saliente** asociado a Petoi; no el menor número ni una dirección
BLE sin identificar. El usuario identificó Bittle normal, Petoi-30AD y COM6 saliente.
Ese número puede cambiar entre ordenadores o emparejamientos.
Cierra otras aplicaciones que usen el puerto. No ejecutes panel y consola sobre
el mismo robot a la vez.

```powershell
.\.venv\Scripts\python.exe -X utf8 bittle_voz.py --puerto COM6 --texto
.\.venv\Scripts\python.exe -X utf8 bittle_voz.py --puerto COM6 --modelo $modelo --microfono 1
```

Estos comandos abren hardware y pueden provocar movimiento. El código usa 115200
baudios y añade LF a cada token; en consola se puede cambiar `--baudios`, en panel no.
Son parámetros de esta implementación y del uso comunicado, no una garantía para
todos los firmwares. La apertura espera hasta 10 s por «Ready» pero continúa sin
recibirlo. No requiere un perfil físico adicional.

BLE está disponible solo en la consola (`--ble --direccion-ble DIRECCION_REAL`).
No se ha verificado aquí con el robot. Sin dirección, selecciona un candidato por
nombre y puede recurrir a cualquier característica escribible: no asumir identidad
ni compatibilidad a partir de una búsqueda. El panel ofrece solo COM y simulación.

## Cierre y problemas frecuentes

PARA solicita equilibrio y cancela pendientes. Apagar micrófono no cancela la cola.
Ctrl+C en consola, o Desconectar en panel, cancela pendientes e intenta `krest`;
puede mover el robot y no confirma inmovilidad. Cerrar la pestaña deja el servidor
funcionando. Detalles y límites: [SECUENCIAS.md](SECUENCIAS.md).

| Problema | Comprobación |
|---|---|
| Falta una biblioteca | Instalar los requirements con el Python de `.venv` |
| No encuentra modelo | Revisar carpeta extraída y ruta en el panel o `--modelo` |
| COM ocupado | Cerrar consola, app Petoi o monitor serie que use ese puerto |
| No reconoce | Revisar dispositivo, medidor, frase recibida y catálogo; probar primero en simulación |
| Micrófono apagado tras error | Revisar mensaje, dispositivo y volver a activar |
| Panel no abre | Mantener terminal abierta, usar 127.0.0.1; cambiar `--puerto-web 8766` si está ocupado |
| «Puerto abierto» pero no responde | No acredita robot operativo; revisar enlace, batería, firmware y procedimiento físico |

## Verificación reproducible sin robot

```powershell
.\.venv\Scripts\python.exe -X utf8 tools/generar_evidencias_actuales.py
.\.venv\Scripts\python.exe -X utf8 tools/verificar_documentacion.py
```

El primer comando ejecuta las 49 pruebas de la aplicación final y genera resultados.
El segundo revisa vínculos, requisitos, catálogo y huellas. El test HTTP necesita
conexiones locales a 127.0.0.1; un sandbox que las prohíba no acredita un fallo del panel.

## Uso de voz acordado

Usar el panel con el micrófono apagado salvo al dictar: activar, esperar Escuchando,
decir la orden o secuencia, comprobar su aceptación y desactivar inmediatamente.
La cola sigue ejecutándose con la escucha apagada; para cancelar se pulsa PARA en
el panel. Es una operación manual, no un modo automático ni una confirmación previa.
Procedimiento y límites: [estrategia de escucha](PANEL_WEB.md#estrategia-de-escucha-manual-acordada).


## Recuperación tras un fallo serie

No se reenvían comandos automáticamente. Si el error indica resultado desconocido,
no se sabe si el robot recibió la orden. Desactivar escucha, revisar el estado y
desconectar; tras revisar la situación, conectar manualmente una nueva sesión.
La cola anterior se descarta: solo las nuevas órdenes explícitas se aceptan en ella.
Si el enlace está bloqueado, ni PARA ni el descanso de cierre se transmiten.
La escritura completa no confirma que el movimiento físico se haya realizado.

