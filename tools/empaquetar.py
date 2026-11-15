"""Exporta el proyecto integral sin entorno, modelos, logs ni metadatos Git."""
import argparse
import hashlib
import json
import subprocess
import zipfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
EXCLUIR = {".git", ".venv", "__pycache__", ".pytest_cache", "modelos", "registros"}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--salida", required=True)
    args = p.parse_args()
    salida = Path(args.salida).resolve()
    if salida.is_relative_to(RAIZ):
        raise SystemExit("El ZIP debe quedar fuera de la carpeta del proyecto")
    if (RAIZ / ".git").exists():
        nombres = subprocess.check_output(["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"], cwd=RAIZ).decode().split("\0")
        revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=RAIZ, text=True).strip()
    else:
        m = json.loads((RAIZ / "MANIFIESTO_ENTREGA.json").read_text(encoding="utf-8"))
        nombres = list(m["archivos"])
        revision = json.loads((RAIZ / "VERSION_ENTREGA.json").read_text(encoding="utf-8"))["commit_base"]
    datos = {}
    for nombre in sorted(set(nombres)):
        if not nombre or nombre in ("VERSION_ENTREGA.json", "MANIFIESTO_ENTREGA.json"): continue
        ruta = Path(nombre)
        if any(c in EXCLUIR for c in ruta.parts) or ruta.suffix in (".pyc", ".zip") or ruta.name.startswith(".env"):
            raise SystemExit(f"Archivo excluido detectado: {nombre}")
        origen = (RAIZ / ruta).resolve()
        if not origen.is_relative_to(RAIZ) or origen.is_symlink(): raise SystemExit("Ruta no segura")
        datos[ruta.as_posix()] = origen.read_bytes()
    datos["VERSION_ENTREGA.json"] = json.dumps({"commit_base": revision, "proyecto": "VOICE-BITTLE ARGOS", "fases": ["H1", "H2", "H3"], "hardware": "pendiente, modo físico bloqueado"}, indent=2, ensure_ascii=False).encode()
    hashes = {n: hashlib.sha256(d).hexdigest() for n, d in datos.items()}
    datos["MANIFIESTO_ENTREGA.json"] = json.dumps({"algoritmo": "SHA-256", "archivos": hashes, "nota": "El manifiesto no se incluye a sí mismo"}, indent=2, ensure_ascii=False).encode()
    with zipfile.ZipFile(salida, "w", zipfile.ZIP_DEFLATED) as z:
        for nombre, contenido in datos.items(): z.writestr("VOICE-BITTLE/" + nombre, contenido)
    with zipfile.ZipFile(salida) as z:
        assert z.testzip() is None
        assert len(z.namelist()) == len(datos)
    print(json.dumps({"archivo": salida.name, "archivos": len(datos), "bytes": salida.stat().st_size, "sha256": hashlib.sha256(salida.read_bytes()).hexdigest()}))


if __name__ == "__main__": main()
