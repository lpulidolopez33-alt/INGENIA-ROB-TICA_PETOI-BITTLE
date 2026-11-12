"""Pruebas software del puente; no necesitan Bluetooth, red ni token."""
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
import tempfile

from enlace import EnlaceBittle, FakeSerial
from tools.puente_github import (ACTIONS, REPO, SCHEMA, TITLE, TRUSTED_LOGIN,
                                 TRUSTED_USER_ID, LocalBridge, issue_action, load_cursor)

NOW = datetime(2026, 11, 12, 15, 0, tzinfo=timezone.utc)


def issue(identifier=200, action="sit", **changes):
    d = {"id": identifier, "number": identifier, "title": TITLE, "state": "open",
         "user": {"login": TRUSTED_LOGIN, "id": TRUSTED_USER_ID},
         "created_at": (NOW - timedelta(seconds=5)).isoformat(),
         "body": json.dumps({"schema": SCHEMA, "action": action})}
    d.update(changes)
    return d


def bridge(tmpdir, first=None):
    serial = FakeSerial()
    enlace = EnlaceBittle(serial, ACTIONS.values())
    enlace.conectar()
    obj = LocalBridge(enlace, Path(tmpdir) / "state.json",
                      NOW - timedelta(minutes=1), dry_run=True)
    obj.process(first or [issue(100, action="unknown")], NOW)
    return obj, serial


def test_valid_sit_stand_and_only_valid_tokens():
    with tempfile.TemporaryDirectory() as tmp:
        b, port = bridge(tmp)
        assert b.process([issue(101)], NOW) == [(101, "sit", "SIMULADO (no se movió ningún robot)")]
        assert port.escrituras == [b"ksit"]
        later = NOW + timedelta(seconds=6)
        standing = issue(102, "stand", created_at=(later - timedelta(seconds=2)).isoformat())
        b.process([standing], later)
        assert port.escrituras == [b"ksit", b"kup"]


def test_author_and_payload_must_be_exact():
    assert issue_action(issue(user={"login": "stranger", "id": 1}), NOW, NOW - timedelta(minutes=1)) is None
    assert issue_action(issue(body="ksit;rm -rf ."), NOW, NOW - timedelta(minutes=1)) is None
    assert issue_action(issue(action="flip"), NOW, NOW - timedelta(minutes=1)) is None
    assert issue_action(issue(title="otra orden"), NOW, NOW - timedelta(minutes=1)) is None
    assert issue_action(issue(body=json.dumps({"schema": SCHEMA,"action":"sit","token":"malicioso"})), NOW, NOW - timedelta(minutes=1)) is None
    assert issue_action(issue(created_at=(NOW-timedelta(minutes=4)).isoformat()), NOW, NOW-timedelta(minutes=10)) is None
    assert issue_action(issue(created_at=(NOW-timedelta(minutes=2)).isoformat()), NOW, NOW-timedelta(minutes=1)) is None
    assert issue_action(issue(pull_request={}), NOW, NOW-timedelta(minutes=1)) is None


def test_first_fetch_ignores_existing_and_restart_does_not_repeat():
    with tempfile.TemporaryDirectory() as tmp:
        b, port = bridge(tmp, first=[issue(100)])
        assert port.escrituras == []
        b.process([issue(101)], NOW)
        assert load_cursor(b.state_file) == 101
        restarted = LocalBridge(b.enlace, b.state_file, NOW-timedelta(minutes=1))
        assert restarted.process([issue(101)], NOW) == []
        assert port.escrituras == [b"ksit"]


def test_interval_and_no_link_are_fail_closed():
    with tempfile.TemporaryDirectory() as tmp:
        b, port = bridge(tmp)
        b.process([issue(101), issue(102, "stand")], NOW)
        assert port.escrituras == [b"ksit"]
        assert load_cursor(b.state_file) == 102
        port.desconectar()
        later = NOW+timedelta(seconds=6)
        assert "sin enlace" in b.process([issue(103, created_at=later.isoformat())], later)[0][2]
        assert port.escrituras == [b"ksit"]


def test_unsolicited_issue_not_executed():
    with tempfile.TemporaryDirectory() as tmp:
        b, port = bridge(tmp)
        assert b.process([issue(101, title="Otro asunto")], NOW) == []
        assert port.escrituras == []
