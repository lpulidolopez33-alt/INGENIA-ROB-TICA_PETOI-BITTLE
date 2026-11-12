# Guía práctica VOICE-BITTLE (Windows / PowerShell)

## 1. Qué se ha integrado

Se reutilizan el controlador, vocabulario, traductor, estados, avisos, registro e
interfaces existentes. `voice_bittle.py` inicia una consola. `FakeRecognizer`
simula texto/confianza; `VoskReconocedor` usa modelos locales y micrófono.
Ambos alimentan el mismo controlador. `FakeSerial` registra bytes sin hardware.
`PuertoSerieReal` prepara el transporte pyserial para H4, bloqueado sin perfil y
habilitación; la consola no ofrece aún habilitación física.

Flujo: voz → traductor → controlador/estado → enlace. Consultas → vista/registro,
sin pasar por envío. `seguridad.py` fija la política de dos acciones. Los errores,
la confianza inválida, escucha desactivada, modelo ausente o estado desconocido
impiden nuevas escrituras motrices. Los avisos actuales son visuales; TTS pendiente.

## 2. Instalación reproducible

Instalar Python 3.12 de [python.org](https://www.python.org/downloads/windows/)
con el lanzador `py`. Entorno probado: Windows, Python 3.12.10 de 64 bits.
La sintaxis requiere al menos 3.10, pero otras combinaciones no están validadas.
Desde la carpeta que contiene `voice_bittle.py`:

```powershell
py -0p
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip check
```

Dependencias base fijadas: pytest 9.2.0 y pyserial 3.5. Para voz:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-voz.txt
.\.venv\Scripts\python.exe -c "import vosk, sounddevice, serial; print('Imports correctos')"
```

Vosk 0.3.45 y sounddevice 0.5.6 se instalaron e importaron en este entorno.
Las dependencias transitivas instaladas se registran en `evidencias/entorno_H3.txt`;
no constituye validación de todas las plataformas ni de precisión de voz.

## 3. Simulación sin robot ni micrófono

```powershell
.\.venv\Scripts\python.exe voice_bittle.py --demo
.\.venv\Scripts\python.exe voice_bittle.py --demo --idioma en
.\.venv\Scripts\python.exe voice_bittle.py --registro registros\sesion_manual.jsonl
```

La demo escribe solo `ksit` y `kup` en memoria; consultas y entradas rechazadas
no producen bytes nuevos. El reloj fake es determinista y usa fecha ficticia;
los registros de simulación no son mediciones temporales reales.

| Control | Función |
|---|---|
| `/activar`, `/desactivar` | Habilitar/deshabilitar escucha manualmente |
| Frase escrita o línea vacía | Resultado simulado o silencio, solo proveedor fake |
| `/capturar` | Una captura de voz Vosk, si está seleccionado y escucha activa |
| `/idioma es`, `/idioma en` | Cambiar modelo e idioma; reactivar escucha después |
| `/estado`, `/historial` | Inspección manual sin movimientos |
| `estado`, `historial` / `status`, `history` | Consultas por la ruta de reconocimiento |
| `/fin` | Terminar una acción SIMULADA; postura queda estimada |
| `/desconectar`, `/reconectar` | Inyectar fallo y recuperar enlace simulado |
| `/reposo` | Confirmación explícita de reposo SIMULADO tras reconectar |
| `/salir` | Cierre controlado; si está ocupado/desconocido pide resolverlo |

Ejemplo: `/activar` → `siéntate` → `ponte de pie` (rechazada por ocupado)
→ `estado` → `/fin` → `ponte de pie` → `/fin` → `/salir`.
Reconectar no reenvía entradas previas ni acredita inmovilidad.
EOF/Ctrl+C abandona la simulación, dejando constancia visual si el estado no se confirmó.

## 4. Modelos Vosk locales y micrófono (sin robot)

Obtener modelos desde el [catálogo oficial](https://alphacephei.com/vosk/models).
Candidatos pequeños para evaluar: `vosk-model-small-es-0.42` y
`vosk-model-small-en-us-0.15`. Descargar y extraer manualmente fuera del control
Git, por ejemplo en `modelos/vosk-es` y `modelos/vosk-en`. La ruta debe apuntar
a la carpeta del modelo extraído, no al ZIP ni a su directorio padre.
No se incluyen ni descargan modelos automáticamente. Revisar licencia y registrar
nombre, versión y hash del modelo empleado en cada ensayo.

```powershell
.\.venv\Scripts\python.exe -m sounddevice
.\.venv\Scripts\python.exe voice_bittle.py --reconocedor vosk --modelo-es "C:\modelos\vosk-es" --modelo-en "C:\modelos\vosk-en" --dispositivo 1
```

Sustituir las rutas y el índice 1 por los reales. En consola: `/activar`,
`/capturar`, pronunciar una frase. El enlace sigue siendo FakeSerial. Usar `/fin`
para completar acciones simuladas, no para declarar una postura real.
Modelo ausente: salida 1, error registrado y escucha deshabilitada. Fallo de flujo
u overflow: captura descartada, escucha deshabilitada y aviso; recuperar dispositivo
y activar manualmente. No se conserva ni reenvía audio fallido.

### Ensayo manual pendiente (no ejecutado)

1. Registrar commit/huella, Python, bibliotecas, modelo, dispositivo e idioma.
2. Con FakeSerial, comprobar las cuatro frases de cada idioma, desconocidas,
   silencio y desconexión del micrófono. Registrar texto/confianza y resultado.
3. Consultas: verificar cero escrituras nuevas. Movimientos: solo bytes simulados.
4. Repetir con Internet desactivado después de instalar dependencias y modelos.
5. Anotar observado/veredicto/incidencias; restaurar conectividad manualmente.

Este ensayo funcional no sustituye RR-01: siguen pendientes protocolo de 100
muestras, reparto por idioma/intención, usuarios y medida acústica (OPEN-05/13).
El mínimo de confianza por palabra no es una probabilidad calibrada de intención.
El final de palabra Vosk es una estimación del final de voz; buffers y reloj de
captura necesitan calibración. No declarar RR-02 cumplido con estas estimaciones.

## 5. Pruebas y evidencias

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe tools/generar_evidencias.py
git diff --check
```

El generador escribe resultados, trazabilidad y `ejecucion_H3.json` (commit base,
archivos SHA-256, cambios locales, versión Python/pytest y salida de pruebas).
Un caso TEST puede contener varios tests parametrizados. PASS significa que ese
caso pasó; no acredita el requisito completo. Inspección, simulación y dobles
están identificados; pruebas reales de Vosk, Bluetooth y posturas siguen pendientes.
No editar resultados generados a mano. Las pruebas no necesitan modelos ni hardware.

## 6. Configuración futura del enlace físico

Consultar [preprueba_fisica.md](docs/H3/preprueba_fisica.md). `PerfilFisico`
exige puerto, velocidad, terminador, modelo, firmware, referencia del protocolo,
parámetros concretos y referencias de aprobación de parámetros/seguridad.
`PuertoSerieReal` no abre en el constructor: requiere habilitación expresa de sesión.
El perfil es una declaración del responsable, no una aprobación automática o firma.
No hay perfil aprobado distribuido ni opción de consola que lo habilite.

```powershell
.\.venv\Scripts\python.exe voice_bittle.py --modo fisico
```

Resultado esperado: bloqueo y salida 2, sin abrir puertos. No usar scripts de terceros
que detecten o abran automáticamente conexiones para saltar este control.
Identificar Bittle clásico/X/X V2 y placa/firmware reales antes de asignar protocolo.
No asumir 115200 ni un terminador a partir de los valores de los dobles de prueba.

## 7. Cierre, cambios y Git

En simulación, terminar con `/fin` si procede y `/salir`. En hardware será necesario
el procedimiento aprobado que confirme inmovilidad y contemple fallo de enlace;
no se ha validado y no se sustituye por desconectar un puerto.
Los logs son JSONL y pueden contener texto reconocido: conservar los necesarios
para el ensayo, fuera de Git (`registros/` está ignorado).

Antes de cambios: `git status`, revisar rama y cambios. Trabajar en una rama propia,
ejecutar suite/generador y revisar diff. No añadir acciones ni ajustar U para obtener
un resultado favorable. La aprobación de cambios motrices y parámetros es independiente.
Esta entrega contiene commits locales; no se hace push ni merge sin autorización.

## 8. Entrega integral y configuración portátil

Descomprimir `VOICE-BITTLE-ARGOS.zip`, abrir PowerShell en su carpeta `VOICE-BITTLE`.
Seguir la instalación del apartado 2. H1 está en docs/h1; H2 vigente está en specs;
H3 en docs/H3, src, tests y evidencias. Empezar por PROYECTO.md. Los archivos de
docs/historico son originales archivados, NO instrucciones vigentes.

Descargar el ZIP español del catálogo oficial:
https://alphacephei.com/vosk/models/vosk-model-small-es-0.42.zip
Extraer conservando la carpeta `vosk-model-small-es-0.42` dentro de `modelos/`.
No se distribuyen modelos en este paquete; tampoco entornos virtuales ni logs locales.

```powershell
.\.venv\Scripts\python.exe voice_bittle.py --modo simulado --reconocedor vosk --idioma es --modelo-es ".\modelos\vosk-model-small-es-0.42"
.\.venv\Scripts\python.exe tools/ensayo_audio_sintetico.py --modelo ".\modelos\vosk-model-small-es-0.42"
```

El segundo comando no abre el micrófono: ensaya Vosk con PCM sintético. No mide
precisión con voz. Modelo español cargado se ha comprobado, modelo inglés y voz
humana siguen pendientes. En captura real, usar /activar y /capturar; no asumir
que una frase devuelta corresponde a una intención humana.

### Incidente «estado» sin habla intencionada

No disponemos de la grabación ni de una reproducción controlada; no se atribuye
causa al micrófono, ruido o modelo. Se usa ahora decodificación abierta, mínimo de
confianza por palabra y controles de captura final/coherente, frescura y no repetición.
El silencio digital cero se rechaza incluso si un motor simulado devuelve una orden.
Audio no nulo NO demuestra voz humana: el ruido puede aún dar falsos positivos.
U no está calibrado. No habilitar hardware ni declarar validación por estos cambios.

Errores habituales: modelo ausente → revisar carpeta extraída y --modelo-es/en;
No module named vosk → instalar requirements-voz.txt con el Python de .venv;
dispositivo ausente/overflow → comprobar entrada en Windows y volver a activar;
captura invalidada → iniciar otra captura, no reenviar un resultado anterior;
físico bloqueado → comportamiento esperado, ver preprueba_fisica.md.

Si `py -3.12` no encuentra Python pero `python --version` muestra 3.12, usar `python -m venv .venv`. No continuar con otra versión sin verificarla. En las pruebas de procesos se fija UTF-8 explícitamente para evitar diferencias de codificación de Windows.
