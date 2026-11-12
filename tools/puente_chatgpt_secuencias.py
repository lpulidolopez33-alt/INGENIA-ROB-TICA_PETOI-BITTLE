"""Puente de SECUENCIAS: ChatGPT -> GitHub Issue -> Bluetooth Petoi.

Reutiliza la consulta autenticada y cursor del puente v1.
NO permite comandos serie arbitrarios ni replay de órdenes antiguas.
No afirma que un comando enviado equivale a movimiento físico confirmado.

Inicio simulado:
  python tools/puente_chatgpt_secuencias.py --dry-run
Real (tras ensayo y verificación firmware):
  python tools/puente_chatgpt_secuencias.py --live --arm --port COM7

Para "siuu", crear/ensayar primero una skill Petoi en Skill Composer;
la última skill exportada se invoca con T, solo tras activación explícita.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import sys
import time
from typing import Callable

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from enlace import EnlaceBittle, FakeSerial, LinkError
from puente_github import (REPO, TRUSTED_LOGIN, TRUSTED_USER_ID,
                           fetch_issues, load_cursor, save_cursor)

TITLE = "[BITTLE-SEQUENCE v1]"
SCHEMA = "bittle-chatgpt-sequence/v1"
DEFAULT_STATE = Path.home() / ".bittle" / "chatgpt-sequence-cursor.json"
MAX_ACTIONS = 4
MAX_AGE = timedelta(seconds=180)
BASE_ACTIONS = {"sit": "ksit", "stand": "kup", "balance": "kbalance"}
CUSTOM_SIUU_TOKEN = "T"  # Reproduce la última skill exportada de Petoi; NO viene verificada.


def parse_issue(issue: dict, now: datetime, started: datetime,
                *, siuu_ready: bool = False) -> tuple[str, ...] | None:
    """Validación atómica: si una acción no está autorizada, se rechaza TODA la lista."""
    if not isinstance(issue, dict) or "pull_request" in issue:
        return None
    if issue.get("title") != TITLE or issue.get("state") != "open":
        return None
    author = issue.get("user")
    if not isinstance(author, dict) or author.get("login") != TRUSTED_LOGIN:
        return None
    if type(author.get("id")) is not int or author["id"] != TRUSTED_USER_ID:
        return None
    try:
        creation = datetime.fromisoformat(issue["created_at"].replace("Z", "+00:00"))
    except (KeyError, AttributeError, TypeError, ValueError):
        return None
    if creation.tzinfo is None or not started <= creation <= now + timedelta(seconds=15):
        return None
    if now - creation > MAX_AGE:
        return None
    body = issue.get("body")
    if not isinstance(body, str) or len(body) > 512:
        return None
    try:
        payload = json.loads(body)
    except (TypeError, ValueError):
        return None
    if not isinstance(payload, dict) or set(payload) != {"schema", "actions"}:
        return None
    if payload["schema"] != SCHEMA:
        return None
    actions = payload["actions"]
    if not isinstance(actions, list) or not 1 <= len(actions) <= MAX_ACTIONS:
        return None
    if any(type(action) is not str for action in actions):
        return None
    approved = BASE_ACTIONS | ({"siuu": CUSTOM_SIUU_TOKEN} if siuu_ready else {})
    if any(action not in approved for action in actions):
        return None
    return tuple(approved[action] for action in actions)


class SequenceBridge:
    def __init__(self, enlace: EnlaceBittle, state_file: Path,
                 started: datetime, *, siuu_ready: bool = False,
                 dry_run: bool = True, delay: float = 8.0,
                 sleeper: Callable[[float], None] = time.sleep,
                 announce: Callable[[str], None] = print):
        if not 1 <= delay <= 120:
            raise ValueError("intervalo entre envíos permitido: 1 a 120 segundos")
        self.enlace = enlace
        self.state_file = state_file
        self.started = started
        self.siuu_ready = siuu_ready
        self.dry_run = dry_run
        self.delay = delay
        self.sleeper = sleeper
        self.announce = announce
        self.last_id = load_cursor(state_file)

    def process(self, issues: list[dict], now: datetime) -> list[tuple[int, str]]:
        ids = [i.get("id") for i in issues if type(i.get("id")) is int]
        if self.last_id is None:
            # Nunca ejecutar órdenes existentes al encender el puente.
            self.last_id = max(ids, default=0)
            save_cursor(self.state_file, self.last_id)
            self.announce("Sincronización inicial. A partir de ahora se aceptan órdenes NUEVAS.")
            return []
        outcomes: list[tuple[int, str]] = []
        for issue in sorted(issues, key=lambda x: x.get("id") if type(x.get("id")) is int else -1):
            number = issue.get("number", -1)
            identifier = issue.get("id")
            if type(identifier) is not int or identifier <= self.last_id:
                continue
            # Cursor DURABLE antes del movimiento: no repetir tras reinicio.
            self.last_id = identifier
            save_cursor(self.state_file, self.last_id)
            actions = parse_issue(issue, now, self.started, siuu_ready=self.siuu_ready)
            if actions is None:
                continue
            if not self.enlace.activo():
                raise LinkError("sin Bluetooth; la orden se descarta sin reintento")
            self.announce(f"Issue #{number}: {len(actions)} acción(es) válidas.")
            for index, token in enumerate(actions, start=1):
                if not self.enlace.activo():
                    raise LinkError("Bluetooth perdido; detener todas las acciones pendientes")
                try:
                    self.enlace.enviar(token)
                except (LinkError, ValueError, OSError) as exc:
                    raise LinkError("envío fallido; secuencia descartada sin reintento") from exc
                message = "SIMULADO" if self.dry_run else "ENVIADO (sin confirmación física)"
                outcomes.append((number, token))
                self.announce(f"  {index}/{len(actions)}: {token} — {message}")
                # Intervalo de seguridad: no equivale a respuesta/acuse del firmware.
                self.sleeper(self.delay)
                if not self.enlace.activo():
                    raise LinkError("Bluetooth perdido tras el último envío")
        return outcomes


def parse_cli(argv=None):
    p = argparse.ArgumentParser(description="ChatGPT via GitHub -> secuencias Bittle")
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true", help="simular, sin usar Bluetooth")
    group.add_argument("--live", action="store_true", help="conexión Bluetooth real")
    p.add_argument("--arm", action="store_true", help="confirmación local de movimientos reales")
    p.add_argument("--port", help="puerto COM Bluetooth saliente")
    p.add_argument("--baud", type=int, default=115200)
    p.add_argument("--terminator", choices=["none", "lf"], default="none")
    p.add_argument("--interval", type=float, default=8.0)
    p.add_argument("--state-file", type=Path, default=DEFAULT_STATE)
    p.add_argument("--allow-siuu", action="store_true",
                   help="habilitar T SOLO si la última skill exportada es SIUU y ya se verificó")
    p.add_argument("--confirm-siuu", default="", help="escribir SIUU_VERIFICADO para habilitarlo")
    p.add_argument("--once", action="store_true", help="salir tras la primera secuencia ejecutada")
    return p.parse_args(argv)


def main(argv=None):
    args = parse_cli(argv)
    if args.live and (not args.arm or not args.port):
        print("Para movimiento real: --live --arm --port PUERTO; no se ha conectado el robot.")
        return 2
    if args.allow_siuu and args.confirm_siuu != "SIUU_VERIFICADO":
        print("SIUU no habilitado: preparar y probar la skill, y confirmar su revisión local.")
        return 2
    if args.interval < 1 or args.interval > 120:
        print("Intervalo válido entre 1 y 120 segundos.")
        return 2
    if args.live:
        from enlace.serial_py import PySerialPort
        port = PySerialPort(args.port, args.baud)
    else:
        port = FakeSerial()
    allowed = list(BASE_ACTIONS.values())
    if args.allow_siuu:
        allowed.append(CUSTOM_SIUU_TOKEN)
    enlace = EnlaceBittle(port, allowed,
                         terminador=b"\n" if args.terminator == "lf" else b"")
    token = os.getenv("GITHUB_TOKEN", "").strip() or None
    polling_interval = 10 if token else 65
    started = datetime.now(timezone.utc)
    try:
        enlace.conectar()
        bridge = SequenceBridge(enlace, args.state_file, started,
                                siuu_ready=args.allow_siuu, dry_run=args.dry_run,
                                delay=args.interval)
        print(f"SECUENCIAS {'SIMULADAS' if args.dry_run else 'REALES'}; repo {REPO}")
        print("ChatGPT puede enviar hasta cuatro acciones por orden; Ctrl+C detiene FUTUROS envíos.")
        print("SIUU habilitado:", args.allow_siuu)
        print("Al iniciar, se ignoran Issues antiguos; no hay cola persistida.")
        while True:
            try:
                outcomes = bridge.process(fetch_issues(token), datetime.now(timezone.utc))
                if args.once and outcomes:
                    return 0
            except (OSError, ValueError) as exc:
                print(f"Fallo consultando GitHub: {exc}; sin movimientos adicionales.")
            time.sleep(polling_interval)
    except KeyboardInterrupt:
        print("Parada solicitada; no es parada física de emergencia.")
        return 0
    except (LinkError, OSError) as exc:
        print(f"Error de Bluetooth: {exc}. Puente detenido.")
        return 1
    finally:
        enlace.cerrar()


if __name__ == "__main__":
    raise SystemExit(main())
