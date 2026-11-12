"""Puente local y de alcance limitado: GitHub Issue -> Bittle por Bluetooth serie.

Ejecutar desde la raíz: python tools/puente_github.py --dry-run
Para movimientos reales: python tools/puente_github.py --live --arm --port COM7

No procesa órdenes anteriores a su arranque; no utiliza GitHub Actions ni almacena
credenciales en el repositorio. No confirma la postura física del robot.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import sys
import tempfile
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

# Permite invocar este archivo desde el directorio raíz sin instalar el paquete.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from enlace import EnlaceBittle, FakeSerial, LinkError

REPO = "lpulidolopez33-alt/INGENIA-ROB-TICA_PETOI-BITTLE"
TRUSTED_LOGIN = "lpulidolopez33-alt"
TRUSTED_USER_ID = 309672387
TITLE = "[BITTLE-CMD v1]"
SCHEMA = "bittle-github-command/v1"
ACTIONS = {"sit": "ksit", "stand": "kup"}
MAX_AGE = timedelta(seconds=180)
MIN_ACTION_GAP = timedelta(seconds=5)
DEFAULT_STATE_FILE = Path.home() / ".bittle" / "github-issue-cursor.json"


def issue_action(issue: dict, now: datetime, session_start: datetime) -> str | None:
    """Acepta únicamente un issue reciente, creado por la identidad GitHub esperada."""
    if not isinstance(issue, dict) or "pull_request" in issue:
        return None
    if issue.get("title") != TITLE or issue.get("state") != "open":
        return None
    author = issue.get("user") or {}
    if author.get("login") != TRUSTED_LOGIN or author.get("id") != TRUSTED_USER_ID:
        return None
    try:
        created = datetime.fromisoformat(issue["created_at"].replace("Z", "+00:00"))
    except (KeyError, AttributeError, ValueError, TypeError):
        return None
    if created.tzinfo is None or not (session_start <= created <= now + timedelta(seconds=15)):
        return None
    if now - created > MAX_AGE:
        return None
    body = issue.get("body")
    if not isinstance(body, str) or len(body) > 512:
        return None
    try:
        payload = json.loads(body)
    except (TypeError, ValueError):
        return None
    if not isinstance(payload, dict) or set(payload) != {"schema", "action"}:
        return None
    if payload["schema"] != SCHEMA or payload["action"] not in ACTIONS:
        return None
    return payload["action"]


def fetch_issues(token: str | None) -> list[dict]:
    # Sin token, la API pública de GitHub está limitada a ~60 solicitudes/hora.
    url = f"https://api.github.com/repos/{REPO}/issues?state=all&sort=created&direction=desc&per_page=100"
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "bittle-local-bridge/1.0",
               "X-GitHub-Api-Version": "2022-11-28"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    with urlopen(Request(url, headers=headers), timeout=12) as resp:
        data = json.load(resp)
    if not isinstance(data, list):
        raise ValueError("GitHub devolvió una respuesta inesperada")
    return data


def load_cursor(path: Path) -> int | None:
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("repo") != REPO or not isinstance(data.get("last_id"), int):
        raise ValueError("archivo de estado no válido")
    return data["last_id"]


def save_cursor(path: Path, last_id: int) -> None:
    """Guarda antes del envío: ante un cierre inesperado prefiere perder a repetir."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(prefix=".cursor-", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump({"repo": REPO, "last_id": last_id}, f)
            f.flush()
            os.fsync(f.fileno())
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


class LocalBridge:
    def __init__(self, enlace: EnlaceBittle, state_file: Path, session_start: datetime,
                 *, dry_run: bool = True):
        self.enlace = enlace
        self.state_file = state_file
        self.session_start = session_start
        self.dry_run = dry_run
        self.last_id = load_cursor(state_file)
        self.last_action_at = None

    def process(self, issues: list[dict], now: datetime) -> list[tuple[int, str, str]]:
        ids = [i.get("id") for i in issues if type(i.get("id")) is int]
        if self.last_id is None:
            # El primer lote es solo la referencia inicial, nunca órdenes ejecutables.
            self.last_id = max(ids, default=0)
            save_cursor(self.state_file, self.last_id)
            print("Sincronización inicial completa; ahora se admiten órdenes NUEVAS.", flush=True)
            return []
        outcomes = []
        for issue in sorted(issues, key=lambda x: x.get("id", 0)):
            issue_id = issue.get("id")
            if type(issue_id) is not int or issue_id <= self.last_id:
                continue
            # Evita ejecución duplicada tras apagados/reinicios.
            self.last_id = issue_id
            save_cursor(self.state_file, self.last_id)
            action = issue_action(issue, now, self.session_start)
            if action is None:
                continue
            if self.last_action_at is not None and now - self.last_action_at < MIN_ACTION_GAP:
                outcomes.append((issue["number"], action, "rechazado: intervalo de seguridad"))
                continue
            if not self.enlace.activo():
                outcomes.append((issue["number"], action, "rechazado: sin enlace"))
                continue
            self.last_action_at = now
            try:
                self.enlace.enviar(ACTIONS[action])
            except (LinkError, ValueError) as exc:
                outcomes.append((issue["number"], action, f"error: {exc}"))
                # No reconectar ni reenviar automáticamente tras un fallo.
                raise LinkError(f"problema en la comunicación de la orden #{issue['number']}") from exc
            outcomes.append((issue["number"], action,
                             "SIMULADO (no se movió ningún robot)" if self.dry_run else
                             "ENVIADO (postura física no verificada)"))
        return outcomes


def arguments() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Puente seguro GitHub Issues -> Petoi Bittle")
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true", help="simular sin hardware")
    mode.add_argument("--live", action="store_true", help="conectar al Bluetooth real")
    p.add_argument("--arm", action="store_true", help="confirmación local obligatoria para --live")
    p.add_argument("--port", help="Puerto Bluetooth saliente, por ejemplo COM7 o /dev/cu.PetoiSerial")
    p.add_argument("--terminator", choices=["none", "lf"], default="none",
                   help="según firmware Petoi: por defecto no añade fin de línea")
    p.add_argument("--state-file", type=Path, default=DEFAULT_STATE_FILE)
    p.add_argument("--once", action="store_true", help="salir después de una orden aceptada")
    p.add_argument("--list-ports", action="store_true", help="listar puertos serie (requiere pyserial)")
    return p.parse_args()


def main() -> int:
    args = arguments()
    if args.list_ports:
        try:
            from serial.tools.list_ports import comports
        except ImportError:
            print("Instala pyserial con: python -m pip install pyserial==3.5")
            return 2
        for port in comports():
            print(f"{port.device}: {port.description}")
        return 0
    if args.live and (not args.arm or not args.port):
        print("Para habilitar movimientos físicos usa --live --arm --port PUERTO.")
        return 2
    token = os.getenv("GITHUB_TOKEN", "").strip() or None
    interval = 10 if token else 65
    if not token:
        print("Sin GITHUB_TOKEN: consulta pública cada 65 s para respetar el límite de GitHub.")
    if args.live:
        from enlace.serial_py import PySerialPort
        port = PySerialPort(args.port)
    else:
        port = FakeSerial()
    enlace = EnlaceBittle(port, ACTIONS.values(),
                         terminador=b"\n" if args.terminator == "lf" else b"")
    started = datetime.now(timezone.utc)
    try:
        enlace.conectar()
        bridge = LocalBridge(enlace, args.state_file, started, dry_run=args.dry_run)
        # El primer barrido fija el límite de órdenes anteriores a la sesión.
        print(f"Puente {'SIMULACIÓN' if args.dry_run else 'REAL'} iniciado; repo {REPO}.")
        print("Solo acepta órdenes nuevas de la cuenta autorizada: sit / stand.")
        print("Para detener el puente, pulsa Ctrl+C. No existe reenvío automático.")
        while True:
            try:
                issues = fetch_issues(token)
                results = bridge.process(issues, datetime.now(timezone.utc))
                for number, action, status in results:
                    print(f"Issue #{number} | {action}: {status}", flush=True)
                if args.once and any("SIMULADO" in status or "ENVIADO" in status
                                     for _, _, status in results):
                    return 0
            except (HTTPError, URLError, TimeoutError, ValueError) as exc:
                print(f"No se consultó GitHub: {exc}; sin movimiento.", flush=True)
            time.sleep(interval)
    except KeyboardInterrupt:
        print("Puente detenido localmente.")
        return 0
    except (LinkError, OSError) as exc:
        print(f"Puente detenido por seguridad: {exc}")
        return 1
    finally:
        enlace.cerrar()


if __name__ == "__main__":
    raise SystemExit(main())