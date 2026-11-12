"""Vocabulario cerrado de órdenes (D-10): se carga de un fichero de configuración."""
import json
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path

IDIOMAS = ("es", "en")
RUTA_POR_DEFECTO = Path(__file__).with_name("vocabulario.json")


def normalizar(texto: str) -> str:
    """Minúsculas, sin tildes ni signos, espacios colapsados."""
    t = unicodedata.normalize("NFD", texto.lower())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    t = re.sub(r"[^a-z0-9 ]+", " ", t)
    return " ".join(t.split())


@dataclass(frozen=True)
class Intencion:
    id: str
    tipo: str            # "movimiento" | "consulta"
    token: str | None    # token serie de Petoi (solo movimientos)
    descripcion: str
    frases: dict         # idioma -> [frase canónica]

    @property
    def es_movimiento(self) -> bool:
        return self.tipo == "movimiento"


class Vocabulario:
    def __init__(self, intenciones: list[Intencion]):
        self.intenciones = intenciones
        self._indice = {}
        for it in intenciones:
            for idioma, frases in it.frases.items():
                for f in frases:
                    self._indice[(idioma, normalizar(f))] = it

    @classmethod
    def cargar(cls, ruta: Path | str | None = None) -> "Vocabulario":
        datos = json.loads(Path(ruta or RUTA_POR_DEFECTO).read_text(encoding="utf-8"))
        return cls([Intencion(d["id"], d["tipo"], d.get("token"), d["descripcion"], d["frases"])
                    for d in datos["intenciones"]])

    def buscar(self, texto: str, idioma: str) -> Intencion | None:
        return self._indice.get((idioma, normalizar(texto)))

    def tokens_permitidos(self) -> frozenset:
        return frozenset(i.token for i in self.intenciones if i.es_movimiento and i.token)

    def admitidas(self, idioma: str) -> list[tuple[str, Intencion]]:
        return [(f, it) for it in self.intenciones for f in it.frases.get(idioma, [])]
