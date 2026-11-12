"""Política de acciones independiente del vocabulario editable."""
from math import isfinite
from types import MappingProxyType

ACCIONES = MappingProxyType({"sentarse": "ksit", "ponerse_de_pie": "kup"})
TOKENS = frozenset(ACCIONES.values())
CONSULTAS = frozenset({"historial", "estado"})


def numero_valido(valor, minimo=0.0, maximo=1.0):
    return (type(valor) in (int, float) and isfinite(valor)
            and minimo <= valor <= maximo)
