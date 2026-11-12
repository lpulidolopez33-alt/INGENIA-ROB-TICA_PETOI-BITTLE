import json
import subprocess
import sys
from pathlib import Path
import pytest
from app.consola import ejecutar
from conftest import Entorno

pytestmark = [pytest.mark.caso("TEST-35"), pytest.mark.req("RF-10", "RU-03", "RI-06", "RS-01"),
              pytest.mark.esc("ESC-03", "ESC-05"), pytest.mark.nivel(2)]


@pytest.mark.parametrize("idioma", ["es", "en"])
def test_demo_ejecutable(idioma, tmp_path):
    registro = tmp_path / "demo.jsonl"
    proc = subprocess.run([sys.executable, "-X", "utf8", "voice_bittle.py", "--demo", "--idioma", idioma,
                           "--registro", str(registro)], capture_output=True, encoding="utf-8")
    assert proc.returncode == 0, proc.stderr
    assert "[b'ksit', b'kup']" in proc.stdout
    eventos = [json.loads(x) for x in registro.read_text(encoding="utf-8").splitlines()]
    assert sum(e["resultado"] == "enviada" for e in eventos) == 2
    assert sum(e["resultado"] == "aceptada" for e in eventos) == 2


def test_fisico_bloqueado_sin_crear_registro(tmp_path):
    registro = tmp_path / "no.jsonl"
    proc = subprocess.run([sys.executable, "-X", "utf8", "voice_bittle.py", "--modo", "fisico",
                           "--registro", str(registro)], capture_output=True, encoding="utf-8")
    assert proc.returncode == 2
    assert not registro.exists()


def test_controles_consola():
    e = Entorno().arrancar()
    salida = []
    for linea in ("/desactivar", "siéntate", "/idioma en", "/activar", "status", "history"):
        ejecutar(e.ctrl, linea, salida.append)
    assert not e.serie.escrituras
    assert e.ctrl.idioma == "en"
    assert ejecutar(e.ctrl, "/salir", salida.append)
