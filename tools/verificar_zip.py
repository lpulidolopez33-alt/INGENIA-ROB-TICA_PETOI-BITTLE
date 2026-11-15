"""Verifica ZIP independiente sin hardware. Usar el Python con requirements.txt instalado."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
import zipfile


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('zip')
    ap.add_argument('--destino', required=True, help='Carpeta independiente para extraer, fuera del proyecto')
    ap.add_argument('--informe', required=True, help='JSON fuera del ZIP y del proyecto')
    args = ap.parse_args()
    zip_path, destino, informe = Path(args.zip).resolve(), Path(args.destino).resolve(), Path(args.informe).resolve()
    proyecto = Path(__file__).resolve().parents[1]
    if destino.is_relative_to(proyecto) or informe.is_relative_to(proyecto):
        raise SystemExit('Extracción e informe deben estar fuera del proyecto')
    with zipfile.ZipFile(zip_path) as z:
        assert z.testzip() is None
        assert all((destino / n).resolve().is_relative_to(destino) for n in z.namelist())
        # Puede reutilizarse el directorio de esta misma verificación; archivos
        # ajenos o sobrantes hacen fallar el manifiesto, no se borran a ciegas.
        z.extractall(destino)
    root = destino / 'VOICE-BITTLE'
    manifest = json.loads((root / 'MANIFIESTO_ENTREGA.json').read_text(encoding='utf-8'))
    actual = {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in root.rglob('*') if p.is_file() and p.name != 'MANIFIESTO_ENTREGA.json'}
    assert actual == manifest['archivos'], 'Manifiesto no coincide con extracción'
    evidencia = json.loads((root / 'evidencias/actual/ejecucion.json').read_text(encoding='utf-8'))
    env = {**os.environ, 'PYTHONUTF8': '1', 'PYTHONDONTWRITEBYTECODE': '1'}
    suite = subprocess.run([sys.executable, '-X', 'utf8', '-m', 'pytest', '-q', '-p', 'no:cacheprovider', 'tests'],
                           cwd=root, env=env, capture_output=True, text=True, encoding='utf-8', timeout=90)
    assert suite.returncode == 0, suite.stdout + suite.stderr
    assert f"{evidencia['total']} passed" in suite.stdout
    proceso = subprocess.Popen([sys.executable, '-u', '-X', 'utf8', 'bittle_voz.py', '--simulado', '--texto',
                                '--segundos-accion', '0.1'], cwd=root, env=env, stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')
    try:
        proceso.stdin.write('siéntate y ponte de pie y siéntate y descansa\n')
        proceso.stdin.flush()
        time.sleep(3)
        salida, error = proceso.communicate(timeout=15)
    finally:
        if proceso.poll() is None:
            proceso.kill()
            proceso.communicate()
    assert proceso.returncode == 0, salida + error
    tokens = re.findall(r"se enviaría: '([^']+)'", salida)
    assert tokens == ['ksit', 'kup', 'ksit', 'krest', 'krest'], salida
    check = subprocess.run([sys.executable, 'tools/verificar_documentacion.py'], cwd=root, env=env,
                           capture_output=True, text=True, encoding='utf-8', timeout=30)
    assert check.returncode == 0, check.stdout + check.stderr
    resultado = {'estado': 'PASS', 'zip_sha256': hashlib.sha256(zip_path.read_bytes()).hexdigest(),
                 'archivos': len(actual) + 1, 'hashes_verificados': len(actual),
                 'pruebas': evidencia['total'], 'suite': suite.stdout.strip(), 'cli_tokens': tokens,
                 'simulacion': salida, 'coherencia': json.loads(check.stdout),
                 'http': 'Verificado en suite: página, API y arranque sin hardware ni envíos',
                 'limite': 'Extracción independiente con dependencias ya instaladas; sin micrófono ni COM reales; no revalidación física'}
    informe.parent.mkdir(parents=True, exist_ok=True)
    informe.write_text(json.dumps(resultado, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: resultado[k] for k in ('estado','zip_sha256','archivos','hashes_verificados','pruebas','cli_tokens')}, ensure_ascii=False))


if __name__ == '__main__':
    main()
