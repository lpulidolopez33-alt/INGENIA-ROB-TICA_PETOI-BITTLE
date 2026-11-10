"""Ejecuta las pruebas y genera evidencias/resultados_H3.md y evidencias/trazabilidad_H3.md.

Uso:  python tools/generar_evidencias.py
Vincula: requisito (H1 v0.2) -> casos TEST-xx -> resultado -> versión (commit Git).
Además comprueba que los TEST-xx de docs/H3/casos_de_prueba.md y de tests/ coinciden.
"""
import re
import subprocess
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent

# Requisitos de H1 v0.2 y modo de verificación previsto (H1 6.3)
REQUISITOS = {
    "software": "RF-02 RF-04 RF-05 RF-06 RF-07 RF-10 RS-01 RS-02 RO-02 RFI-01 RFI-02 RU-01 RU-02 "
                "RU-03 RM-01 RM-02 RI-03 RI-04 RI-05 RI-06 RI-07 RR-03 RD-01 RD-02".split(),
    "integración": "RF-01 RR-01 RI-01 RI-02 RR-02".split(),
    "físico": "RF-03 RF-08 RF-09 RO-01 RS-03".split(),
}
MODO = {r: m for m, rs in REQUISITOS.items() for r in rs}
# Requisitos que, además de su modo principal, tienen parte verificable sin robot
PARTE_SOFTWARE = {"RR-02", "RF-08", "RF-09", "RS-03", "RF-01", "RI-02"}


class Recolector:
    def __init__(self):
        self.casos = {}          # TEST-xx -> dict
        self.resultados = defaultdict(list)

    def pytest_collection_modifyitems(self, items):
        for it in items:
            m = it.get_closest_marker("caso")
            if not m:
                continue
            tid = m.args[0]
            info = self.casos.setdefault(tid, {"reqs": set(), "escs": set(), "nivel": None,
                                               "tests": []})
            for nombre, clave in (("req", "reqs"), ("esc", "escs")):
                mk = it.get_closest_marker(nombre)
                if mk:
                    info[clave].update(mk.args)
            nv = it.get_closest_marker("nivel")
            info["nivel"] = nv.args[0] if nv else None
            info["tests"].append(it.nodeid)
            it.caso_id = tid

    def pytest_runtest_logreport(self, report):
        if report.when == "call" or (report.when == "setup" and report.failed):
            tid = None
            for t, info in self.casos.items():
                if report.nodeid in info["tests"]:
                    tid = t
            if tid:
                self.resultados[tid].append(report.outcome)


def commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=RAIZ,
                                       text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return "sin-commit"


def ids_en_documento() -> set:
    doc = (RAIZ / "docs/H3/casos_de_prueba.md").read_text(encoding="utf-8")
    return set(re.findall(r"\bTEST-\d{2}\b", doc))


def main() -> int:
    rec = Recolector()
    rc = pytest.main(["-q", "-p", "no:cacheprovider", str(RAIZ / "tests")], plugins=[rec])
    veredicto = {t: ("PASS" if r and all(x == "passed" for x in r) else "FAIL")
                 for t, r in rec.resultados.items()}
    ahora = datetime.now().strftime("%Y-%m-%d %H:%M")
    cab = f"Versión del software: commit `{commit()}` (+ cambios sin commitear si los hay) · {ahora}\n"

    # ---- resultados
    L = ["# Resultados de pruebas H3 (sin robot)\n", cab,
         "| Caso | Nivel | Requisitos | Escenarios | Pruebas | Veredicto |", "|---|---|---|---|---|---|"]
    for t in sorted(rec.casos):
        c = rec.casos[t]
        L.append(f"| {t} | {c['nivel']} | {', '.join(sorted(c['reqs']))} | "
                 f"{', '.join(sorted(c['escs']))} | {len(c['tests'])} | **{veredicto.get(t, 'NO EJECUTADO')}** |")
    total = len(rec.casos); ok = sum(v == "PASS" for v in veredicto.values())
    L += ["", f"**{ok}/{total} casos PASS.**", ""]
    (RAIZ / "evidencias/resultados_H3.md").write_text("\n".join(L), encoding="utf-8")

    # ---- trazabilidad
    por_req = defaultdict(list)
    for t, c in rec.casos.items():
        for r in c["reqs"]:
            por_req[r].append(t)
    T = ["# Trazabilidad requisito → prueba → resultado (H3)\n", cab,
         "| Requisito | Modo de verificación (H1 6.3) | Casos sin robot | Estado H3 |", "|---|---|---|---|"]
    huecos = []
    for r in sorted(MODO, key=lambda x: (x[:2], int(x.split("-")[1]))):
        casos = sorted(por_req.get(r, []))
        modo = MODO[r]
        if casos and all(veredicto.get(c) == "PASS" for c in casos):
            estado = "Verificado sin robot" if (modo == "software") else \
                     "Parte software verificada; falta ensayo con hardware"
        elif casos:
            estado = "**FALLO**"; huecos.append(r)
        else:
            estado = "Pendiente (ensayo físico/integración)" if modo != "software" else "**SIN PRUEBA**"
            if modo == "software":
                huecos.append(r)
        T.append(f"| {r} | {modo} | {', '.join(casos) or '—'} | {estado} |")
    T += ["", "Los requisitos de modo «integración» y «físico» se cierran en H4 (docs/H3/casos_de_prueba.md §3).", ""]
    (RAIZ / "evidencias/trazabilidad_H3.md").write_text("\n".join(T), encoding="utf-8")

    # ---- coherencia documento <-> tests
    en_doc = ids_en_documento()
    auto_doc = {i for i in en_doc if int(i[-2:]) >= 1}
    solo_doc = auto_doc - set(rec.casos)
    solo_tests = set(rec.casos) - auto_doc
    print(f"Casos: {ok}/{total} PASS")
    if solo_doc: print("En el documento pero sin prueba automática:", sorted(solo_doc))
    if solo_tests: print("En tests pero no documentados:", sorted(solo_tests))
    if huecos: print("Requisitos software sin prueba o con fallo:", huecos)
    return 0 if (rc == 0 and not solo_doc and not solo_tests and not huecos) else 1


if __name__ == "__main__":
    sys.exit(main())
