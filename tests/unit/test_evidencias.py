from types import SimpleNamespace
import pytest
from generar_evidencias import Recolector, estado_requisito

pytestmark = [pytest.mark.caso("TEST-36"), pytest.mark.req("RD-01"), pytest.mark.nivel(1)]


@pytest.mark.parametrize("fase,estado,esperado", [("teardown", "failed", "FAIL"),
                                               ("setup", "skipped", "NO EJECUTADO COMPLETO"),
                                               ("call", "passed", "PASS")])
def test_veredicto_incluye_todas_las_fases(fase, estado, esperado):
    r = Recolector()
    r.casos["TEST-99"] = {"tests": ["prueba"]}
    for f in ("setup", "call", "teardown"):
        r.pytest_runtest_logreport(SimpleNamespace(nodeid="prueba", when=f,
                                                  outcome=estado if f == fase else "passed"))
    assert r.veredictos()["TEST-99"] == esperado


def test_no_acredita_vosk_real():
    assert "falta" in estado_requisito("RD-02")
    assert "sin Internet" in estado_requisito("RR-03")
