"""Consola H3. El transporte físico queda deliberadamente en preprueba."""
import argparse
import json
from pathlib import Path

from app.controlador import Controlador
from avisos import Avisos
from enlace import EnlaceBittle, FakeSerial
from estado import Estado
from interfaz import construir_vista, como_texto
from registro import Registro
from reloj import FakeReloj, Reloj
from vocabulario import Vocabulario
from voz import FakeRecognizer
from voz.vosk_reconocedor import VoskReconocedor

AYUDA = """/activar /desactivar /capturar /idioma es|en /estado /historial
/fin (solo simulación) /desconectar /reconectar /reposo (solo simulación)
/salir /ayuda. En modo fake escribe una frase; no es reconocimiento de audio.
Las consultas de voz requieren /activar. /capturar toma una locución con Vosk."""


def crear_controlador(args):
    vocab = Vocabulario.cargar()
    reloj = FakeReloj() if args.reconocedor == "fake" else Reloj()
    reco = (FakeRecognizer(reloj) if args.reconocedor == "fake" else
            VoskReconocedor({"es": args.modelo_es, "en": args.modelo_en},
                            {i: [f for f, _ in vocab.admitidas(i)] for i in ("es", "en")},
                            dispositivo=args.dispositivo))
    ruta = Path(args.registro)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    return Controlador(vocab, reco, EnlaceBittle(FakeSerial(), vocab.tokens_permitidos()),
                       Registro(reloj, ruta), Avisos(reloj), reloj, idioma=args.idioma)


def ejecutar(ctrl, linea, escribir=print):
    linea = linea.strip()
    if linea == "/salir":
        cierre = ctrl.cerrar_sesion()
        if not cierre.ok:
            escribir(f"Cierre bloqueado: {cierre.motivo}. /fin o /reposo solo simulan la recuperación.")
        return cierre.ok
    if linea == "/ayuda": escribir(AYUDA)
    elif linea == "/activar": escribir(f"Escucha activada: {ctrl.activar_escucha()}")
    elif linea == "/desactivar": ctrl.desactivar_escucha(); escribir("Escucha desactivada")
    elif linea.startswith("/idioma "):
        idioma = linea.split(maxsplit=1)[1]
        if idioma not in ("es", "en"): escribir("Idioma no admitido")
        else: escribir(f"Cambio de idioma: {ctrl.cambiar_idioma(idioma)}; reactiva la escucha")
    elif linea == "/estado":
        ctrl.vigilar_enlace()
        escribir(como_texto(construir_vista(ctrl)))
        escribir(f"Micrófono/proveedor disponible: {ctrl.reconocedor.disponible()}; modelo listo: {ctrl.modelo_listo}")
    elif linea == "/historial": escribir(json.dumps(ctrl.registro.historial(), ensure_ascii=False))
    elif linea == "/fin":
        if ctrl.enlace.simulado and ctrl.gestor.estado is Estado.EJECUTANDO:
            ctrl.finalizar_accion(False); escribir("Fin SIMULADO; postura estimada")
        else: escribir("No hay acción simulada en curso")
    elif linea == "/reposo":
        escribir(f"Reposo SIMULADO: {ctrl.enlace.simulado and ctrl.confirmar_reposo('Operador de simulación')}")
    elif linea == "/desconectar":
        ctrl.enlace.puerto.desconectar(); ctrl.vigilar_enlace(); escribir("Enlace simulado perdido")
    elif linea == "/reconectar":
        ctrl.enlace.puerto.restablecer()
        escribir(f"Reconexión: {ctrl.reconectar()}; estado físico desconocido")
    else:
        avisos_antes = len(ctrl.avisos.emitidos)
        if not ctrl.gestor.escucha:
            escribir("Escucha desactivada; usa /activar")
            return False
        if linea == "/capturar":
            resultado = ctrl.escuchar()
        elif linea.startswith("/"):
            escribir("Control desconocido; /ayuda")
            return False
        elif isinstance(ctrl.reconocedor, FakeRecognizer):
            if linea: ctrl.reconocedor.encolar(linea)
            else: ctrl.reconocedor.encolar_silencio()
            resultado = ctrl.escuchar()
        else:
            escribir("Usa /capturar para reconocer voz; el texto no sustituye al micrófono")
            return False
        if resultado:
            escribir(f"Resultado: {resultado.resultado}; motivo: {resultado.motivo or '-'}")
            if ctrl.registro.eventos:
                escribir(f"Texto reconocido/simulado: {ctrl.registro.eventos[-1]['texto']}")
            if resultado.detalle is not None:
                escribir(json.dumps(resultado.detalle, ensure_ascii=False))
        else:
            escribir("Captura no disponible; consulta /estado")
        for aviso in ctrl.avisos.emitidos[avisos_antes:]: escribir(aviso.texto)
    return False


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--modo", choices=("simulado", "fisico"), default="simulado")
    parser.add_argument("--reconocedor", choices=("fake", "vosk"), default="fake")
    parser.add_argument("--idioma", choices=("es", "en"), default="es")
    parser.add_argument("--modelo-es", default="modelos/vosk-es")
    parser.add_argument("--modelo-en", default="modelos/vosk-en")
    parser.add_argument("--dispositivo", type=int, default=None)
    parser.add_argument("--registro", default="registros/sesion.jsonl")
    parser.add_argument("--demo", action="store_true")
    args = parser.parse_args(argv)
    if args.modo == "fisico":
        print("MODO FÍSICO BLOQUEADO. No se abre ningún puerto. Pendientes: modelo, firmware, "
              "Bluetooth, protocolo, parámetros aprobados, intervención independiente y autorización de sesión. "
              "Ver docs/H3/preprueba_fisica.md.")
        return 2
    if args.demo and args.reconocedor != "fake":
        parser.error("--demo requiere --reconocedor fake; no captura micrófono")
    print("VOICE-BITTLE | SIMULACIÓN: ningún robot conectado | Proveedor: " + args.reconocedor)
    ctrl = crear_controlador(args)
    if not ctrl.iniciar_sesion():
        print("Inicio incompleto: modelo o enlace no disponible; revisa las rutas locales.")
        ctrl.enlace.cerrar()
        return 1
    print(AYUDA)
    if args.demo:
        frases = (["siéntate", "estado", "historial", "ponte de pie"] if args.idioma == "es"
                  else ["sit", "status", "history", "stand up"])
        for linea in ["/activar", *frases[:3], "corre", "/fin", frases[3], "/fin", "/salir"]:
            print("> " + linea)
            ejecutar(ctrl, linea)
        print("Escrituras simuladas: " + repr(ctrl.enlace.puerto.escrituras))
        return 0
    try:
        while True:
            ctrl.vigilar_enlace()
            if ejecutar(ctrl, input("> ")): return 0
    except (EOFError, KeyboardInterrupt):
        ctrl.desactivar_escucha()
        cierre = ctrl.cerrar_sesion()
        if not cierre.ok:
            print("Sesión simulada interrumpida; estado sin confirmar. Ninguna postura física acreditada.")
            ctrl.enlace.cerrar()
        return 0
