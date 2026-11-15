"""Comprueba referencias, IDs, hashes y trazas. No acredita ausencia de todo defecto."""
import ast
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import unquote

RAIZ = Path(__file__).resolve().parents[1]
EXCLUIDOS = {".git", ".venv", "__pycache__", ".pytest_cache", "modelos", "registros", "historico"}


def archivos_distribuibles():
    return sorted(p for p in RAIZ.rglob("*") if p.is_file()
                  and not set(p.relative_to(RAIZ).parts) & EXCLUIDOS
                  and p.name != "MANIFIESTO_ENTREGA.json")


def manifiesto():
    hashes = {p.relative_to(RAIZ).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in archivos_distribuibles()}
    (RAIZ / "MANIFIESTO_ENTREGA.json").write_text(json.dumps({
        "algoritmo": "SHA-256", "alcance": "carpeta actual distribuible; no describe los ZIP anteriores",
        "exclusiones": sorted(EXCLUIDOS) + ["MANIFIESTO_ENTREGA.json (autorreferencia)"],
        "archivos": hashes}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def verificar():
    fallos = []
    docs = [*RAIZ.glob("*.md"), *(RAIZ / "specs").rglob("*.md"),
            *(RAIZ / "docs").rglob("*.md"), *(RAIZ / "evidencias").rglob("*.md")]
    revisados = 0
    for p in docs:
        if "historico" in p.relative_to(RAIZ).parts:
            continue
        revisados += 1
        for destino in re.findall(r"\[[^\]]*\]\(([^)]+)\)", p.read_text(encoding="utf-8")):
            destino = destino.strip().strip("<>")
            if destino.startswith(("http:", "https:", "mailto:", "#")):
                continue
            ruta = unquote(destino.split("#")[0])
            if ruta and not (p.parent / ruta).exists():
                fallos.append(f"Enlace inexistente: {p.relative_to(RAIZ)} -> {ruta}")
    traza = json.loads((RAIZ / "specs/001-voice-bittle-spec/trazabilidad_actual.json").read_text(encoding="utf-8"))
    ids = {x["id"] for x in traza}
    if len(traza) != 16 or ids != {f"ACT-{n:02}" for n in range(1, 17)}:
        fallos.append("IDs ACT incompletos o duplicados")
    spec = (RAIZ / "specs/001-voice-bittle-spec/spec.md").read_text(encoding="utf-8")
    if set(re.findall(r"\| (ACT-\d{2}) \|", spec)) != ids:
        fallos.append("Spec y trazabilidad ACT no coinciden")
    h1_final = (RAIZ / "docs/h1/H1_v0.4.md").read_text(encoding="utf-8")
    requisitos = lambda texto: {m.group(1): m.group(2).strip() for m in re.finditer(
        r"^\| (ACT-\d{2}) \| (.+) \|$", texto, re.M)}
    if requisitos(h1_final) != requisitos(spec) or set(requisitos(h1_final)) != ids:
        fallos.append("H1 v0.4 y H2 no contienen los mismos requisitos finales")
    pdf = RAIZ / "docs/h1/H1_v0.4.pdf"
    if not pdf.exists() or not pdf.read_bytes().startswith(b"%PDF"):
        fallos.append("Falta PDF de H1 vigente")
    for fila in traza:
        for ruta in fila["codigo"]:
            if not (RAIZ / ruta).is_file():
                fallos.append(f"Fuente inexistente: {ruta}")
        for referencia in fila["pruebas"]:
            ruta, nombre = referencia.split("::")
            p = RAIZ / ruta
            nombres = {n.name for n in ast.walk(ast.parse(p.read_text(encoding="utf-8-sig"))) if isinstance(n, ast.FunctionDef)} if p.exists() else set()
            if nombre not in nombres:
                fallos.append(f"Prueba inexistente: {referencia}")
    tareas = json.loads((RAIZ / "specs/001-voice-bittle-spec/tareas.json").read_text(encoding="utf-8"))
    por_id = {t["id"]: t for t in tareas}
    texto_tareas = (RAIZ / "specs/001-voice-bittle-spec/tasks.md").read_text(encoding="utf-8")
    if len(por_id) != len(tareas):
        fallos.append("Tareas duplicadas")
    for tarea in tareas:
        if tarea["id"] not in texto_tareas or not tarea["criterio"]:
            fallos.append("Tarea sin criterio o sin registro Markdown: " + tarea["id"])
        if not (RAIZ / tarea["archivo"]).is_file():
            fallos.append("Archivo de tarea inexistente: " + tarea["archivo"])
        if not set(tarea["requisitos"]) <= ids:
            fallos.append("Requisito inexistente en tarea: " + tarea["id"])
        if any(d not in por_id for d in tarea["dependencias"]):
            fallos.append("Dependencia inexistente: " + tarea["id"])
    visitadas, pila = set(), set()
    def recorrer(tid):
        if tid in pila:
            fallos.append("Ciclo en dependencias: " + tid)
            return
        if tid in visitadas or tid not in por_id:
            return
        pila.add(tid)
        for dep in por_id[tid]["dependencias"]:
            recorrer(dep)
        pila.remove(tid)
        visitadas.add(tid)
    for tid in por_id:
        recorrer(tid)
    for fila in traza:
        if not fila.get("tareas") or not fila.get("necesidades") or not fila.get("escenarios") or not fila.get("fuentes"):
            fallos.append("Traza incompleta: " + fila["id"])
        for campo, patron, documento in (
            ("escenarios", r"EF-\d{2}", "docs/h1/ESCENARIOS.md"),
            ("necesidades", r"NF-\d{2}", "docs/h1/H1_v0.4.md"),
            ("fuentes", r"REF-\d{2}", "docs/FUENTES.md")):
            definidos = set(re.findall(patron, (RAIZ / documento).read_text(encoding="utf-8")))
            if not set(fila.get(campo, [])) <= definidos:
                fallos.append("Referencia desconocida en " + campo + ": " + fila["id"])
        for tid in fila.get("tareas", []):
            if tid not in por_id or fila["id"] not in por_id[tid]["requisitos"]:
                fallos.append("Traza tarea-ACT incoherente: " + tid + " / " + fila["id"])
    h1 = (RAIZ / "docs/h1/EVOLUCION_REQUISITOS.md").read_text(encoding="utf-8")
    esperados = {f"{prefijo}-{n:02}" for prefijo, cantidad in [("RF",10),("RR",3),("RS",3),("RI",7),("RO",2),("RFI",2),("RU",3),("RM",2),("RD",2)] for n in range(1,cantidad+1)}
    if set(re.findall(r"\| ((?:RF|RR|RS|RI|RO|RFI|RU|RM|RD)-\d{2}) \|", h1)) != esperados:
        fallos.append("Historial de H1 v0.2 no cubre los 34 IDs")
    # Catálogo coherente con constantes del parser, sin ejecutar módulos ni hardware.
    arbol = ast.parse((RAIZ / "bittle_voz.py").read_text(encoding="utf-8-sig"))
    comandos = next(ast.literal_eval(n.value) for n in arbol.body if isinstance(n, ast.Assign)
                    and any(isinstance(t, ast.Name) and t.id == "COMANDOS" for t in n.targets))
    catalogo = (RAIZ / "docs/COMANDOS.md").read_text(encoding="utf-8")
    filas_catalogo = {}
    for linea in catalogo.splitlines():
        if linea.startswith("| "):
            columnas = [c.strip() for c in linea.split("|")[1:-1]]
            if len(columnas) == 3:
                filas_catalogo[columnas[0]] = [c.strip() for c in columnas[2].split(",")]
    for frase, (token, descripcion) in comandos.items():
        if frase not in filas_catalogo.get(token, []):
            fallos.append(f"Alias omitido o token incorrecto en catálogo: {frase} -> {token}")
    ejecucion = RAIZ / "evidencias/actual/ejecucion.json"
    if not ejecucion.exists():
        fallos.append("Falta ejecución actual de pruebas")
    else:
        evidencia = json.loads(ejecucion.read_text(encoding="utf-8"))
        if evidencia["codigo_salida"] != 0 or evidencia["pasadas"] != evidencia["total"]:
            fallos.append("La suite actual no tiene resultado completo PASS")
        for ruta, hash_esperado in evidencia["fuentes_sha256"].items():
            p = RAIZ / ruta
            if not p.exists() or hashlib.sha256(p.read_bytes()).hexdigest() != hash_esperado:
                fallos.append(f"Evidencia desactualizada respecto a fuente: {ruta}")
    informe = {"documentos_con_enlaces_revisados": revisados,
               "linea_base_vigente": "H1 v0.4", "requisitos_H1_vigentes": len(ids),
               "requisitos_H1_v02_con_tratamiento_historico": len(esperados),
               "requisitos_actuales": len(ids),
               "fallos": fallos, "limite": "comprobacion estructural y de integridad; no prueba ausencia absoluta de defectos semanticos"}
    return informe


if __name__ == "__main__":
    resultado = verificar()
    salida = RAIZ / "evidencias/actual/coherencia_documental.json"
    salida.parent.mkdir(parents=True, exist_ok=True)
    salida.write_text(json.dumps(resultado, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if not resultado["fallos"]:
        manifiesto()
    print(json.dumps(resultado, ensure_ascii=False, indent=2))
    raise SystemExit(bool(resultado["fallos"]))
