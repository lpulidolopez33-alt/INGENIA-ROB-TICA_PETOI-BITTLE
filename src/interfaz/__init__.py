"""Modelo de vista de la interfaz (D-06). La ventana gráfica se limita a pintar esto, de modo que
RI-03 a RI-07 y RU-01 se verifican sin pantalla."""
from estado import Estado


def construir_vista(ctrl) -> dict:
    return {
        "enlace_activo": ctrl.gestor.estado is not Estado.DESCONECTADO,
        "idioma_activo": ctrl.idioma,
        "escucha_activa": ctrl.gestor.escucha,
        "estado_movimiento": ctrl.estado_movimiento,
        "ordenes_admitidas": [{"frase": f, "accion": it.descripcion}
                              for f, it in ctrl.vocabulario.admitidas(ctrl.idioma)],
        "avisos": [a.texto for a in ctrl.avisos.emitidos[-5:]],
    }


def como_texto(vista: dict) -> str:
    lineas = [f"Enlace: {'ACTIVO' if vista['enlace_activo'] else 'INACTIVO'}   "
              f"Idioma: {vista['idioma_activo']}   "
              f"Escucha: {'ACTIVA' if vista['escucha_activa'] else 'inactiva'}   "
              f"Movimiento: {vista['estado_movimiento']}", "Órdenes admitidas:"]
    lineas += [f"  «{o['frase']}» -> {o['accion']}" for o in vista["ordenes_admitidas"]]
    lineas += [f"Aviso: {aviso}" for aviso in vista["avisos"]]
    return "\n".join(lineas)
