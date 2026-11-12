"""Tests sin robot, Bluetooth ni Internet para las órdenes de ChatGPT por lotes."""
from datetime import datetime, timedelta, timezone
import json

from enlace import EnlaceBittle, FakeSerial, LinkError
from puente_github import REPO, TRUSTED_LOGIN, TRUSTED_USER_ID
from tools.puente_chatgpt_secuencias import (
    TITLE, SCHEMA, SequenceBridge, parse_issue
)

NOW = datetime(2026, 11, 12, 18, 0, tzinfo=timezone.utc)


def issue(ident=100, actions=None, **overrides):
    payload = {"schema": SCHEMA, "actions": actions if actions is not None else
               ["stand", "sit", "stand"]}
    obj = {
        "id": ident, "number": ident, "title": TITLE, "state": "open",
        "user": {"login": TRUSTED_LOGIN, "id": TRUSTED_USER_ID},
        "created_at": (NOW - timedelta(seconds=5)).isoformat(),
        "body": json.dumps(payload),
    }
    obj.update(overrides)
    return obj


def test_orden_3_movimientos_valida():
    assert parse_issue(issue(), NOW, NOW - timedelta(minutes=1)) == ("kup", "ksit", "kup")


def test_lotes_de_4_y_rechazo_de_5():
    assert parse_issue(issue(actions=["sit"] * 4), NOW, NOW - timedelta(minutes=1)) == ("ksit",) * 4
    assert parse_issue(issue(actions=["sit"] * 5), NOW, NOW - timedelta(minutes=1)) is None


def test_siuu_bloqueado_por_defecto_y_habilitado_solo_si_ensayado():
    obj = issue(actions=["sit", "siuu", "stand"])
    assert parse_issue(obj, NOW, NOW - timedelta(minutes=1)) is None
    assert parse_issue(obj, NOW, NOW - timedelta(minutes=1), siuu_ready=True) == ("ksit", "T", "kup")


def test_acciones_desconocidas_rechazan_lista_entera():
    assert parse_issue(issue(actions=["sit", "flip", "stand"]), NOW,
                       NOW - timedelta(minutes=1)) is None
    assert parse_issue(issue(actions=["sit", "ksit"]), NOW,
                       NOW - timedelta(minutes=1)) is None


def test_emisor_extrano_o_issue_antiguo():
    assert parse_issue(issue(user={"login": "intruso", "id": 1}),
                       NOW, NOW - timedelta(minutes=1)) is None
    assert parse_issue(issue(created_at=(NOW - timedelta(hours=1)).isoformat()),
                       NOW, NOW - timedelta(hours=2)) is None


def test_fifo_y_esperas_entre_comandos(tmp_path):
    serial = FakeSerial()
    link = EnlaceBittle(serial, ["ksit", "kup"])
    link.conectar()
    delays = []
    msgs = []
    bridge = SequenceBridge(link, tmp_path / "cursor.json",
                            NOW - timedelta(minutes=1), delay=2,
                            sleeper=delays.append, announce=msgs.append)
    # Primer barrido solo sincroniza, no mueve el robot.
    assert bridge.process([issue(100)], NOW) == []
    assert serial.escrituras == []
    bridge.process([issue(101, actions=["stand", "sit", "stand", "sit"])], NOW)
    assert serial.escrituras == [b"kup", b"ksit", b"kup", b"ksit"]
    assert delays == [2, 2, 2, 2]
    bridge.process([issue(101, actions=["stand"])], NOW)
    assert len(serial.escrituras) == 4


def test_fallo_enlace_no_reintenta_siguiente_orden(tmp_path):
    serial = FakeSerial()
    link = EnlaceBittle(serial, ["ksit", "kup"])
    link.conectar()
    def sleep_fail(_):
        serial.desconectar()
    bridge = SequenceBridge(link, tmp_path / "cursor.json",
                            NOW - timedelta(minutes=1), delay=1,
                            sleeper=sleep_fail)
    bridge.process([issue(10)], NOW)
    try:
        bridge.process([issue(11, actions=["sit", "stand"])], NOW)
    except LinkError:
        pass
    else:
        assert False, "Debía detenerse ante Bluetooth desconectado"
    assert serial.escrituras == [b"ksit"]
