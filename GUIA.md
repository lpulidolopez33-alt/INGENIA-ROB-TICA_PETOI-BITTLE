# Guía: cómo funciona el repositorio y cómo actualizarlo

## 1. La idea en una frase
El robot solo se mueve si una orden de voz **pasa por una cadena de filtros**; cada filtro es un módulo pequeño y se prueba por separado, sin robot ni micrófono.

```
voz ──► traductor ──► controlador ──► estado ──► enlace ──► Bittle
        (¿es una       (orquesta,     (¿puede     (solo       (ksit / kup)
        orden y con    avisa y        moverse     tokens de
        confianza?)    registra)      ahora?)     la lista)
                           │
                    avisos + registro + interfaz
```

## 2. Qué hace cada carpeta

| Carpeta | Qué hace | Cuándo la tocas |
|---|---|---|
| `src/vocabulario/vocabulario.json` | Las órdenes: frase en ES/EN, tipo (movimiento/consulta) y token | Añadir o cambiar una orden |
| `src/voz/` | Convierte audio en texto + confianza. `FakeRecognizer` para pruebas, `vosk_reconocedor.py` para el real | Cambiar de motor de voz |
| `src/traductor/` | Decide si el texto es una orden válida (idioma, vocabulario, umbral U) | Cambiar reglas de validación |
| `src/estado/` | Máquina de estados: DESCONECTADO, REPOSO, EJECUTANDO | Cambiar cuándo se permite mover |
| `src/enlace/` | Envía el token por serie/Bluetooth. `FakeSerial` para pruebas | Conectar el robot real |
| `src/registro/` | Guarda cada evento (fecha, hora, texto, resultado) en JSON Lines | Añadir campos al registro |
| `src/avisos/` | Mensajes al usuario (pantalla y voz) | Cambiar textos |
| `src/interfaz/` | Datos que muestra la pantalla (enlace, idioma, escucha, órdenes) | Cambiar lo que se ve |
| `src/app/controlador.py` | El «director»: implementa los escenarios ESC-01…ESC-12 | Cambiar el comportamiento de un escenario |
| `src/config.py` | Valores U, T_aviso, T_enlace, T_escucha, 3 s | Ajustar números tras los ensayos |
| `tests/` | Las pruebas (cada una lleva TEST-xx, requisitos y escenarios) | Siempre que cambies algo |
| `docs/H3/casos_de_prueba.md` | Lista de casos, automáticos y físicos | Al añadir pruebas |
| `evidencias/` | Resultados y trazabilidad **generados** (no se editan a mano) | Se regeneran |

## 3. Qué pasa cuando dices «siéntate»
1. `voz` devuelve texto «siéntate» y confianza 0,95.
2. `traductor`: ¿está en el vocabulario del idioma activo? ¿confianza ≥ U? → orden válida.
3. `controlador`: es un movimiento, así que pregunta a `estado` si puede moverse (hay enlace y no hay otra acción en curso).
4. `enlace` comprueba que el token (`ksit`) está en la lista permitida y lo escribe.
5. `estado` pasa a EJECUTANDO; `registro` anota «enviada». Si hay cualquier problema (otro idioma, confianza baja, sin enlace, acción en curso) **no se escribe nada** y se avisa al usuario.

Importante: *enviado* no significa *ejecutado*. Solo una persona que mire al robot puede confirmar la postura.

## 4. Tareas típicas
> Solo los bloques marcados `bash` son para el Terminal. Los bloques `python` y `json` son contenido de archivos.

**Probar que todo funciona** (en el Terminal de Mac se usa `python3`, no `python`; y hay que estar dentro de la carpeta del repo)
```bash
cd ruta/a/INGENIA-ROB-TICA_PETOI-BITTLE   # la carpeta donde clonaste el repo
python3 -m pip install pytest
python3 -m pytest -q                  # debe decir: 56 passed
python3 tools/generar_evidencias.py   # regenera evidencias/ y avisa de huecos
```

**Añadir una orden nueva (por ejemplo «túmbate» → `kfd`)**
1. Añade la intención en `vocabulario.json` (con sus frases ES/EN y su token).
2. Añade un caso en `tests/unit/test_nivel1_interpretacion.py` y otro de envío en `tests/integration/test_escenarios.py`.
3. Documenta el caso en `docs/H3/casos_de_prueba.md` con un TEST-xx nuevo.
4. `python3 tools/generar_evidencias.py`: si olvidas documentar o probar algo, lo dice.

**Cambiar un valor (U, tiempos):** `src/config.py`, y vuelve a ejecutar las pruebas.

**Escribir una prueba nueva:** copia una existente *dentro del archivo `.py`* (no se pega en el Terminal). Las marcas indican qué verifica:
```python
@pytest.mark.caso("TEST-33")          # identificador
@pytest.mark.req("RF-04", "RS-01")    # requisitos de H1
@pytest.mark.esc("ESC-09")            # escenarios
@pytest.mark.nivel(2)                 # 1 interpretación, 2 lógica, 3 interfaz hacia el robot
```

**Conectar el robot real (H4):** implementa un `SerialPort` con pyserial (`abrir`, `escribir`, `cerrar`, `abierto`) y pásalo a `EnlaceBittle`; usa `VoskReconocedor` en lugar de `FakeRecognizer`. El controlador no cambia.

## 5. Git paso a paso (flujo recomendado)
```bash
git pull                          # 1. traer lo último
git switch -c mi-cambio           # 2. rama propia para no romper main
# ...editar, y luego:
python3 -m pytest -q               # 3. comprobar que sigue en verde
git status                        # 4. ver qué has cambiado
git add -A
git commit -m "Describe qué y por qué"
git push -u origin mi-cambio      # 5. subir la rama
```
Después abre un *Pull Request* en GitHub y que lo revise tu compañero/a antes de unirlo a `main`. Para marcar la versión de H3 con un commit:
```bash
git log -1 --format=%h            # hash corto, que se apunta en la portada del H1 (OPEN-08)
git tag H3
```

## 6. Reglas para no perderse
- Una sola fuente de verdad por cosa: requisitos en el H1, especificación/plan/tareas en `specs/`, evidencias solo en `evidencias/` (generadas).
- Si cambias un requisito, cambia el caso de prueba y vuelve a generar las evidencias el mismo día.
- No ejecutes movimientos con el robot sin autorización del profesor y supervisión.
