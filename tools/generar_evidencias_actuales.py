"""Ejecuta toda la suite sin hardware y publica evidencia trazable, no aceptación H1."""
import hashlib
from importlib import metadata
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
from datetime import datetime, timezone
import xml.etree.ElementTree as ET

RAIZ = Path(__file__).resolve().parents[1]


def main():
    destino = RAIZ / "evidencias/actual"
    destino.mkdir(parents=True, exist_ok=True)
    # Un arranque fallido de pytest no debe reutilizar el XML de una ejecución anterior.
    (destino / "pytest.xml").unlink(missing_ok=True)
    comando = [sys.executable, "-X", "utf8", "-m", "pytest", "-q", "-p", "no:cacheprovider",
               "--junitxml=" + "evidencias/actual/pytest.xml", "tests"]
    resultado = subprocess.run(comando, cwd=RAIZ, capture_output=True, text=True,
                               encoding="utf-8", errors="replace", env={**os.environ, "PYTHONUTF8": "1"})
    salida = resultado.stdout + resultado.stderr
    salida = salida.replace(str(RAIZ), "<PROYECTO>").replace(str(Path.home()), "<USUARIO>")
    (destino / "pytest.txt").write_text(salida, encoding="utf-8")
    print(salida)
    casos = []
    if (destino / "pytest.xml").exists():
        arbol_xml = ET.parse(destino / "pytest.xml")
        for suite in arbol_xml.iter("testsuite"):
            suite.attrib.pop("hostname", None)
        arbol_xml.write(destino / "pytest.xml", encoding="utf-8", xml_declaration=True)
        for caso in arbol_xml.iter("testcase"):
            estado = "FAIL" if caso.find("failure") is not None or caso.find("error") is not None else (
                "SKIP" if caso.find("skipped") is not None else "PASS")
            casos.append({"clase": caso.get("classname"), "nombre": caso.get("name"), "resultado": estado})
    archivos = [*RAIZ.glob("*.py"), *RAIZ.glob("requirements*.txt"), RAIZ / "pytest.ini", RAIZ / "INICIAR_PANEL.bat"]
    archivos.append(RAIZ / "specs/001-voice-bittle-spec/trazabilidad_actual.json")
    archivos.append(RAIZ / "docs/h1/H1_v0.4.md")
    for carpeta in ("tests", "tools", "web"):
        archivos += [p for p in (RAIZ / carpeta).rglob("*") if p.is_file() and p.suffix in (".py", ".json", ".html", ".css", ".js")]
    huellas = {p.relative_to(RAIZ).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(set(archivos))}
    informe = {"fecha_utc": datetime.now(timezone.utc).isoformat(), "python": platform.python_version(),
               "interprete": "python", "sistema": platform.platform(), "comando": ["python", *comando[1:]],
               "codigo_salida": resultado.returncode, "total": len(casos),
               "pasadas": sum(c["resultado"] == "PASS" for c in casos),
               "alcance": "suite completa; sin hardware ni microfono real; incluye servidor HTTP localhost",
               "fuentes_sha256": huellas, "casos": casos,
               "dependencias_entorno_pruebas": sorted({f"{d.metadata['Name']}=={d.version}" for d in metadata.distributions()})}
    (destino / "ejecucion.json").write_text(json.dumps(informe, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    traza = json.loads((RAIZ / "specs/001-voice-bittle-spec/trazabilidad_actual.json").read_text(encoding="utf-8"))
    lineas = ["# Resultados actuales y trazabilidad", "", f"Ejecución UTC: {informe['fecha_utc']}.",
              f"Python {informe['python']}. {informe['pasadas']}/{informe['total']} pruebas PASS. Salida: {resultado.returncode}.",
              "", f"Suite vigente: {len(casos)} casos parametrizados de la aplicación final.",
              "Los casos ejecutados exactos están en [ejecucion.json](ejecucion.json), [pytest.xml](pytest.xml) y [salida](pytest.txt).",
              "Línea base vigente: H1 v0.4. No se operó robot ni micrófono. PASS no acredita resultado físico ni partes de un ACT limitadas a inspección.",
              "", "| Requisito actual | Pruebas vinculadas y resultado | Alcance adicional / pendiente |", "|---|---|---|"]
    matriz = ["# Trazabilidad integral H1-H2-H3", "", "Generada desde trazabilidad_actual.json y los resultados de esta ejecución.", "", "| Escenario | Necesidad | ACT | Tareas | Componente | Prueba y resultado | Límite |", "|---|---|---|---|---|---|---|"]
    trazabilidad_ok = True
    for fila in traza:
        estados = []
        for referencia in fila["pruebas"]:
            modulo, nombre = referencia.split("::")
            clase = modulo.removesuffix(".py").replace("/", ".")
            encontrados = [c for c in casos if c["clase"] == clase and c["nombre"].split("[")[0] == nombre]
            if not encontrados:
                estado = "NO EJECUTADO"
                trazabilidad_ok = False
            else:
                estado = "PASS" if all(c["resultado"] == "PASS" for c in encontrados) else "INCOMPLETO/FALLO"
            estados.append(f"{nombre}: {estado}")
        lineas.append(f"| {fila['id']} | {'; '.join(estados) or 'Inspección; sin prueba automática específica'} | {fila['limites']} |")
        matriz.append("| " + " | ".join([", ".join(fila["escenarios"]), ", ".join(fila["necesidades"]), fila["id"], ", ".join(fila["tareas"]), ", ".join(fila["codigo"]), "; ".join(estados) or "Inspección; sin test específico", fila["limites"]]) + " |")
    (RAIZ / "docs/H3/TRAZABILIDAD.md").write_text("\n".join(matriz) + "\n", encoding="utf-8")
    lineas += ["", "El uso físico comunicado se conserva en [validacion_usuario.md](../../docs/H3/validacion_usuario.md).",
               "Los requisitos finales están en [H1 v0.4](../../docs/h1/H1_v0.4.md); los cambios de alcance en [el historial](../../docs/h1/EVOLUCION_REQUISITOS.md).",
               "Las huellas identifican las fuentes al ejecutar; regenerar después de modificar código/pruebas/herramientas."]
    (destino / "RESULTADOS.md").write_text("\n".join(lineas) + "\n", encoding="utf-8")
    return 0 if resultado.returncode == 0 and trazabilidad_ok and casos else 1


if __name__ == "__main__":
    raise SystemExit(main())
