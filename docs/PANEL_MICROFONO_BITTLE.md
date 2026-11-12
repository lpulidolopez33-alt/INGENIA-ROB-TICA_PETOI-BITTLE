# Panel de control de micrófono y acciones (Windows)

Se ha añadido una **ventana local de Python/Tkinter**, separada del modo de voz de ChatGPT. El micrófono del ordenador está **DESACTIVADO** al abrir la ventana y solo escucha cuando se pulsa «Activar micrófono». Funciona con Vosk y la cola FIFO del Petoi Bittle.

## Qué se ve en la pantalla

- **Micrófono:** ACTIVADO / DESACTIVADO / ERROR, con botón para cambiar su estado.
- **Última frase:** texto reconocido por Vosk.
- **Acción detectada:** nombre de las acciones aceptadas, o rechazo si no se reconoce.
- **Estado del movimiento:** reposo, acción enviada y en espera del intervalo, cola pausada o error.
- **Pendientes:** lista de movimientos aún no enviados, en el mismo orden de ejecución.
- **Registro:** mensajes sobre envíos y errores.
- **Botones de pausa, reanudación y vaciado** de la cola pendiente.

**Importante:** que aparezca «enviando o esperando» no demuestra que el robot haya realizado la maniobra. No existe confirmación de postura física.

## Instalación

En Windows, desde la raíz del repositorio:

```powershell
git pull origin main
python -m pip install -r requirements.txt
python -m pytest -q
```

Requiere Python con Tkinter (`python -m tkinter` debe abrir una ventana de prueba), un micrófono funcional y un modelo español Vosk descomprimido. El archivo de modelo local debe estar en `modelos/vosk-es`, o indicar otra ruta con `--model`.

## Primera prueba: sin robot, con micrófono

```powershell
python tools/panel_bittle.py --dry-run --model modelos/vosk-es
```

1. Comprobar que aparece **Micrófono: DESACTIVADO** y «SIMULACIÓN · sin robot».
2. Pulsar **Activar micrófono** y decir «siéntate».
3. Comprobar «Última frase», «Acción detectada: Sentarse» y el registro de envío simulado. Puede tardar varios segundos en reconocer.
4. Decir «ponte de pie» o «siéntate y luego ponte de pie»: la cola envía una acción después de otra.
5. Pulsar **Desactivar micrófono**: no debe reconocer nuevas órdenes. La captura de audio se cancela y los resultados tardíos se descartan.
6. Utilizar **Pausar secuencia**, **Reanudar** y **Vaciar pendientes** para gestionar las órdenes que aún no se han enviado.

## Prueba física tras validar Bluetooth y protocolo

Primero emparejar Petoi Bittle con el ordenador y comprobar que su módulo ofrece un puerto COM saliente compatible con pyserial. Confirmar en el firmware los comandos `ksit` y `kup`, los baudios y el terminador. En el proyecto sigue pendiente validar `kup` en el robot físico.

Con supervisión, superficie despejada y autorización para las pruebas:

```powershell
python tools/panel_bittle.py --live --arm --port COM7 --model modelos/vosk-es --interval 8
```

Cambiar **COM7** por el puerto real. El intervalo de ocho segundos es provisional y no significa que la maniobra haya terminado físicamente.

## Consideraciones de seguridad

- La ventana inicia con micrófono **apagado** y, en simulación, no abre el puerto Bluetooth.
- Desactivar micrófono **no vacía** una cola que ya contenga acciones; existe un botón independiente «Vaciar pendientes».
- «Vaciar pendientes» o cerrar la ventana detienen **nuevos envíos**, pero no detienen un movimiento que Bittle ya esté ejecutando. Debe existir un medio local de cortar la alimentación de forma segura.
- Si se pierde la conexión Bluetooth, el programa descarta las órdenes restantes y detiene la cola. Si el micrófono falla, lo desactiva y pausa la cola.
- Los comandos se limitan a `ksit` y `kup`. **El SIUU no está implementado en este panel**: requiere crear, comprobar y autorizar una skill física.
- Este panel **no escucha directamente el micrófono del chat de ChatGPT**; usa el micrófono del ordenador desde la aplicación Python. Si se desea controlar a través del chat, el puente GitHub de secuencias es una vía distinta.
