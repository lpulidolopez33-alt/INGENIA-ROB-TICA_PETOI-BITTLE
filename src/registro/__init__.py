"""Registro de eventos en JSON Lines (D-09, RM-01, RM-02). El registro de envío no acredita
la ejecución física."""
import json
from pathlib import Path

from reloj import Reloj

RESULTADOS = ("aceptada", "rechazada", "enviada", "error")


class Registro:
    def __init__(self, reloj: Reloj, ruta: Path | str | None = None):
        self.reloj = reloj
        self.ruta = Path(ruta) if ruta else None
        self.eventos: list[dict] = []

    def registrar(self, texto: str, resultado: str, intencion: str | None = None,
                  confianza: float | None = None, motivo: str | None = None,
                  tipo_error: str | None = None, **extra) -> dict:
        assert resultado in RESULTADOS, resultado
        t = self.reloj.ahora()
        ev = {"fecha": t.date().isoformat(), "hora": t.time().isoformat(timespec="milliseconds"),
              "texto": texto, "intencion": intencion, "confianza": confianza,
              "resultado": resultado, "motivo": motivo, "tipo_error": tipo_error, **extra}
        self.eventos.append(ev)
        if self.ruta:
            with self.ruta.open("a", encoding="utf-8") as f:
                f.write(json.dumps(ev, ensure_ascii=False) + "\n")
        return ev

    def historial(self) -> list[dict]:
        """Órdenes aceptadas (incl. enviadas) y rechazadas, con fecha y hora (RI-06)."""
        return [e for e in self.eventos if e["resultado"] in ("aceptada", "enviada", "rechazada")]

    def errores(self) -> list[dict]:
        return [e for e in self.eventos if e["resultado"] == "error"]
