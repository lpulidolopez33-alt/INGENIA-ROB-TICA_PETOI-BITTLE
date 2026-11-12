"""Control local por micrófono + cola FIFO + Bluetooth (solo ksit y kup).

Ejemplos:
  python tools/voz_bittle_cola.py --dry-run --model modelos/vosk-es
  python tools/voz_bittle_cola.py --live --arm --port COM7 --model modelos/vosk-es
  python tools/voz_bittle_cola.py --dry-run --keyboard

No se envían órdenes a GitHub: el reconocimiento y la cola operan localmente.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import sys
from time import monotonic
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from cola_voz import ColaSecuencial, interpretar_voz, frases_vosk
from enlace import EnlaceBittle, FakeSerial, LinkError
from vocabulario import Vocabulario
from voz import MicrofonoNoDisponible, ModeloNoDisponible, Resultado


def opciones(argv=None):
    p = argparse.ArgumentParser(description="Micrófono -> cola FIFO -> Bittle por Bluetooth")
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true", help="no abre Bluetooth real; simula tokens")
    mode.add_argument("--live", action="store_true", help="abre puerto serie Bluetooth real")
    p.add_argument("--arm", action="store_true", help="permiso explícito local para modo real")
    p.add_argument("--port", help="puerto serie Bluetooth saliente, por ejemplo COM7")
    p.add_argument("--baud", type=int, default=115200, help="comprobar baud rate en el firmware")
    p.add_argument("--terminator", choices=["none", "lf"], default="none",
                   help="comprobar terminador exigido por firmware")
    p.add_argument("--model", type=Path, help="directorio local de modelo Vosk español")
    p.add_argument("--keyboard", action="store_true", help="simular reconocimiento escribiendo frases")
    p.add_argument("--confidence", type=float, default=0.8)
    p.add_argument("--interval", type=float, default=5.0,
                   help="tiempo MÍNIMO estimado entre envíos; no comprueba fin físico")
    p.add_argument("--capacity", type=int, default=8)
    return p.parse_args(argv)


def ejecutar(argv=None):
    args = opciones(argv)
    if args.live and (not args.arm or not args.port):
        print("No autorizado: para movimientos físicos usar --live --arm --port PUERTO.")
        return 2
    if not args.keyboard and (not args.model or not args.model.is_dir()):
        print("Falta --model RUTA a un modelo Vosk español descargado y descomprimido.")
        return 2
    if not 0 < args.confidence <= 1:
        print("La confianza mínima debe estar en (0,1].")
        return 2

    vocab = Vocabulario.cargar()
    if args.live:
        from enlace.serial_py import PySerialPort
        puerto = PySerialPort(args.port, args.baud)
    else:
        puerto = FakeSerial()
    enlace = EnlaceBittle(puerto, ["ksit", "kup"],
                         terminador=b"\n" if args.terminator == "lf" else b"")
    reconocedor = None
    if not args.keyboard:
        from voz.vosk_reconocedor import VoskReconocedor
        reconocedor = VoskReconocedor(
            {"es": str(args.model)}, {"es": frases_vosk(vocab)})
        try:
            reconocedor.cargar_modelo("es")
            if not reconocedor.disponible():
                raise MicrofonoNoDisponible("no se detecta micrófono")
        except (ModeloNoDisponible, MicrofonoNoDisponible) as exc:
            print(f"Reconocimiento no disponible: {exc}")
            return 2

    cola = ColaSecuencial(enlace, duracion_minima=args.interval, capacidad=args.capacity,
                         avisar=lambda mensaje: print(mensaje, flush=True))
    try:
        enlace.conectar()
        cola.iniciar()
        print(f"Modo: {'SIMULACIÓN' if args.dry_run else 'BLUETOOTH REAL'}")
        print("Órdenes: 'siéntate', 'ponte de pie', 'siéntate y luego ponte de pie'.")
        print("Controles: 'pausa la cola', 'reanuda la cola', 'vacía la cola'.")
        print("Ctrl+C: descarta pendientes; NO es una parada física de emergencia.")
        while True:
            if cola.estado()["fallo"]:
                print("La cola ha fallado. No se enviarán más comandos.")
                return 1
            if args.keyboard:
                texto = input("Orden de prueba > ")
                ahora = datetime.now()
                resultado = Resultado(texto, 1.0, ahora, ahora)
            else:
                try:
                    resultado = reconocedor.escuchar(5.0)
                except (MicrofonoNoDisponible, OSError) as exc:
                    print(f"Micrófono desconectado: {exc}; se cancela la cola.")
                    return 1
            instruccion = interpretar_voz(resultado, vocab, umbral=args.confidence)
            if instruccion is None:
                if resultado and resultado.texto.strip():
                    print(f"Descartada (no reconocida o baja confianza): {resultado.texto!r}")
                continue
            if instruccion.tipo == "movimiento":
                ok, mensaje = cola.agregar(instruccion.tokens)
                print(mensaje if ok else f"RECHAZADA: {mensaje}")
            elif instruccion.tipo == "vaciar":
                print(f"Canceladas {cola.vaciar()} pendientes. Acción enviada no interrumpida.")
            elif instruccion.tipo == "pausar":
                cola.pausar()
                print("Pausa aplicada a FUTUROS envíos.")
            elif instruccion.tipo == "reanudar":
                print("Cola reanudada." if cola.reanudar() else
                      "Reanudación rechazada: enlace o cola no disponible.")
    except KeyboardInterrupt:
        print("\nCierre solicitado; descartando acciones pendientes.")
        return 0
    except (LinkError, OSError, ValueError) as exc:
        print(f"Error de enlace/entrada: {exc}")
        return 1
    finally:
        cola.detener()
        enlace.cerrar()


if __name__ == "__main__":
    raise SystemExit(ejecutar())
