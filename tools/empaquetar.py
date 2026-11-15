"""Empaqueta la entrega verificada, sin modificar sus metadatos."""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile
from verificar_documentacion import RAIZ, archivos_distribuibles, verificar


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--salida", required=True)
    salida = Path(parser.parse_args().salida).resolve()
    if salida.is_relative_to(RAIZ):
        raise SystemExit("El ZIP debe estar fuera del proyecto")
    fallos = verificar()["fallos"]
    if fallos:
        raise SystemExit("Verificacion fallida: " + str(fallos))
    manifest_path = RAIZ / "MANIFIESTO_ENTREGA.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    datos = {}
    for ruta in archivos_distribuibles():
        nombre = ruta.relative_to(RAIZ).as_posix()
        if ruta.is_symlink() or not ruta.resolve().is_relative_to(RAIZ):
            raise SystemExit("Ruta no segura: " + nombre)
        if ruta.suffix in {".zip", ".pyc"} or ruta.name.startswith(".env"):
            raise SystemExit("Archivo no distribuible: " + nombre)
        datos[nombre] = ruta.read_bytes()
    hashes = {n: hashlib.sha256(d).hexdigest() for n, d in datos.items()}
    if hashes != manifest["archivos"]:
        raise SystemExit("Manifiesto desactualizado; ejecutar verificar_documentacion.py")
    datos["MANIFIESTO_ENTREGA.json"] = manifest_path.read_bytes()
    with zipfile.ZipFile(salida, "w", zipfile.ZIP_DEFLATED) as z:
        for nombre, contenido in datos.items():
            info = zipfile.ZipInfo("VOICE-BITTLE/" + nombre, date_time=(2026, 11, 12, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            z.writestr(info, contenido)
    with zipfile.ZipFile(salida) as z:
        assert z.testzip() is None
        assert len(z.namelist()) == len(datos)
    print(json.dumps({"archivo": str(salida), "archivos": len(datos),
                      "sha256": hashlib.sha256(salida.read_bytes()).hexdigest()}))


if __name__ == "__main__":
    main()
