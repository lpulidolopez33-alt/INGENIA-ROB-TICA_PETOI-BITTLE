"""Ventana de Windows para controlar micrófono + cola FIFO del Petoi Bittle.

Simulación (sin Bluetooth): python tools/panel_bittle.py --dry-run --model modelos/vosk-es
Robot real (solo después de validar firmware y puerto):
    python tools/panel_bittle.py --live --arm --port COM7 --model modelos/vosk-es

El botón MICRO: OFF/ON solo controla ESTE programa, no el micrófono del ChatGPT.
"""
from __future__ import annotations

import argparse
from pathlib import Path
from queue import Empty, Queue
import sys
import tkinter as tk
from tkinter import messagebox, ttk

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from cola_voz import ColaSecuencial, frases_vosk
from enlace import EnlaceBittle, FakeSerial, LinkError
from panel_voz import ControlMicrofono
from panel_voz.vosk_cancelable import VoskCancelable
from vocabulario import Vocabulario

NOMBRES = {"ksit": "Sentarse", "kup": "Ponerse de pie"}


def argumentos(argv=None):
    p = argparse.ArgumentParser(description="Panel Bittle por micrófono")
    modo = p.add_mutually_exclusive_group(required=True)
    modo.add_argument("--dry-run", action="store_true", help="simulación sin robot")
    modo.add_argument("--live", action="store_true", help="puerto Bluetooth real")
    p.add_argument("--arm", action="store_true", help="confirmación local para modo real")
    p.add_argument("--port", help="puerto COM saliente del robot")
    p.add_argument("--model", type=Path, required=True, help="directorio modelo Vosk español")
    p.add_argument("--baud", type=int, default=115200)
    p.add_argument("--terminator", choices=("none", "lf"), default="none")
    p.add_argument("--interval", type=float, default=8.0)
    p.add_argument("--capacity", type=int, default=8)
    p.add_argument("--confidence", type=float, default=.80)
    return p.parse_args(argv)


class PanelBittle:
    def __init__(self, root: tk.Tk, enlace: EnlaceBittle, cola: ColaSecuencial,
                 controlador: ControlMicrofono, eventos: Queue, *, simulacion: bool):
        self.root = root
        self.enlace, self.cola = enlace, cola
        self.controlador, self.eventos = controlador, eventos
        self.simulacion = simulacion
        self.cerrando = False
        root.title("INGENIA · Petoi Bittle · Micrófono y acciones")
        root.geometry("730x565")
        root.minsize(620, 490)
        root.configure(bg="#f4f6fa")
        self.micro = tk.StringVar(value="DESACTIVADO")
        self.frase = tk.StringVar(value="—")
        self.accion = tk.StringVar(value="Ninguna")
        self.ejecucion = tk.StringVar(value="En reposo")
        self.pendientes = tk.StringVar(value="Cola vacía")
        self.conexion = tk.StringVar(value="SIMULACIÓN · sin robot" if simulacion else
                                    "PUERTO ABIERTO · movimiento no verificado")
        self.mensaje = tk.StringVar(value="Micrófono desactivado al iniciar. Pulsa Activar micrófono.")

        cont = ttk.Frame(root, padding=18)
        cont.pack(fill=tk.BOTH, expand=True)
        ttk.Label(cont, text="PET OI BITTLE · PANEL DE CONTROL", font=("Segoe UI", 18, "bold")).pack(anchor="w")
        ttk.Label(cont, textvariable=self.conexion, font=("Segoe UI", 11)).pack(anchor="w", pady=(4, 12))

        primero = ttk.LabelFrame(cont, text="Micrófono", padding=12)
        primero.pack(fill=tk.X)
        self.estado_micro = ttk.Label(primero, textvariable=self.micro, font=("Segoe UI", 13, "bold"))
        self.estado_micro.pack(side=tk.LEFT)
        self.boton = ttk.Button(primero, text="Activar micrófono", command=self.alternar_microfono)
        self.boton.pack(side=tk.RIGHT)

        estado = ttk.LabelFrame(cont, text="Reconocimiento y ejecución", padding=12)
        estado.pack(fill=tk.X, pady=(14, 6))
        for etiqueta, variable in [
            ("Última frase:", self.frase),
            ("Acción detectada:", self.accion),
            ("Estado de movimiento:", self.ejecucion),
            ("Pendientes:", self.pendientes),
        ]:
            linea = ttk.Frame(estado)
            linea.pack(fill=tk.X, pady=4)
            ttk.Label(linea, text=etiqueta, width=23).pack(side=tk.LEFT)
            ttk.Label(linea, textvariable=variable, wraplength=450).pack(side=tk.LEFT, fill=tk.X, expand=True)

        botones = ttk.Frame(cont)
        botones.pack(fill=tk.X, pady=(6, 10))
        ttk.Button(botones, text="Pausar secuencia", command=self.pausar).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(botones, text="Reanudar", command=self.reanudar).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(botones, text="Vaciar pendientes", command=self.vaciar).pack(side=tk.LEFT)

        ttk.Label(cont, textvariable=self.mensaje, wraplength=660).pack(anchor="w", pady=(0, 8))
        ttk.Label(cont, text="Registro de eventos (ENVIADO ≠ ejecutado físicamente)",
                  font=("Segoe UI", 10, "bold")).pack(anchor="w")
        self.registro = tk.Text(cont, height=8, state="disabled", wrap="word")
        self.registro.pack(fill=tk.BOTH, expand=True)
        ttk.Label(cont, text="Nota: Desactivar micrófono no elimina la cola. Vaciar pendientes "
                  "no detiene una acción ya enviada.", wraplength=650).pack(anchor="w", pady=(8, 0))
        self.root.protocol("WM_DELETE_WINDOW", self.cerrar)
        self.controlador.iniciar()
        self.root.after(100, self.actualizar)

    def escribir(self, mensaje):
        self.registro.configure(state="normal")
        self.registro.insert(tk.END, mensaje + "\n")
        self.registro.see(tk.END)
        self.registro.configure(state="disabled")

    def alternar_microfono(self):
        self.controlador.cambiar(not self.controlador.activo)

    def pausar(self):
        self.cola.pausar()
        self.mensaje.set("Pausada: no se enviarán nuevos movimientos")
        self.escribir("Se ha pausado la secuencia")

    def reanudar(self):
        if self.cola.reanudar():
            self.mensaje.set("Cola reanudada")
            self.escribir("Cola reanudada")
        else:
            self.mensaje.set("No se puede reanudar: comprobar conexión y fallos")
            self.escribir("Reanudación rechazada")

    def vaciar(self):
        num = self.cola.vaciar()
        self.mensaje.set(f"Eliminadas {num} órdenes pendientes")
        self.escribir(f"{num} pendientes eliminadas (no afecta a movimiento ya enviado)")

    def actualizar(self):
        if self.cerrando:
            return
        try:
            while True:
                tipo, valor = self.eventos.get_nowait()
                if tipo == "microfono":
                    self.micro.set(valor)
                    self.boton.configure(text=("Desactivar micrófono" if valor == "ACTIVADO"
                                               else "Activar micrófono"))
                    self.escribir("Micrófono: " + valor)
                elif tipo == "frase":
                    self.frase.set(valor)
                elif tipo == "accion":
                    self.accion.set(valor)
                    self.escribir("Orden detectada: " + valor)
                elif tipo == "mensaje":
                    self.mensaje.set(valor)
                    self.escribir(valor)
                elif tipo == "envio":
                    self.escribir(valor)
        except Empty:
            pass
        estado = self.cola.estado()
        self.pendientes.set(" → ".join(NOMBRES.get(t, t) for t in estado["pendientes"])
                            if estado["pendientes"] else "Cola vacía")
        if estado["fallo"]:
            self.ejecucion.set("ERROR / SECUENCIA DETENIDA")
            self.conexion.set("ERROR DE COMUNICACIÓN: revisar el robot")
            if self.controlador.activo:
                self.controlador.cambiar(False)
        elif estado["enviando_o_esperando"]:
            actual = NOMBRES.get(estado["enviando_o_esperando"],
                                estado["enviando_o_esperando"])
            self.ejecucion.set(f"{actual}: comando enviado; esperando fin estimado")
        elif estado["pausada"]:
            self.ejecucion.set("Cola pausada")
        else:
            self.ejecucion.set("En reposo / sin movimiento pendiente")
        self.root.after(100, self.actualizar)

    def cerrar(self):
        if self.cerrando:
            return
        self.cerrando = True
        self.controlador.cerrar()
        self.cola.detener()
        self.enlace.cerrar()
        self.root.destroy()


def ejecutar(argv=None):
    args = argumentos(argv)
    if args.live and (not args.arm or not args.port):
        print("Modo real requiere --live --arm --port COMx.")
        return 2
    if not args.model.is_dir():
        print(f"Carpeta Vosk no encontrada: {args.model}")
        return 2
    if not 0 < args.confidence <= 1 or not 0 < args.interval <= 120 or not 1 <= args.capacity <= 32:
        print("Confianza, intervalo o capacidad fuera de rango.")
        return 2
    vocabulario = Vocabulario.cargar()
    reconocedor = VoskCancelable({"es": str(args.model)}, {"es": frases_vosk(vocabulario)})
    if args.live:
        from enlace.serial_py import PySerialPort
        puerto = PySerialPort(args.port, args.baud)
    else:
        puerto = FakeSerial()
    enlace = EnlaceBittle(puerto, ["ksit", "kup"],
                         terminador=b"\n" if args.terminator == "lf" else b"")
    eventos = Queue()
    cola = ColaSecuencial(enlace, duracion_minima=args.interval, capacidad=args.capacity,
                         avisar=lambda mensaje: eventos.put(("envio", mensaje)))
    controlador = ControlMicrofono(reconocedor, vocabulario, cola, eventos,
                                   confianza=args.confidence)
    try:
        enlace.conectar()
        cola.iniciar()
        root = tk.Tk()
        PanelBittle(root, enlace, cola, controlador, eventos, simulacion=args.dry_run)
        root.mainloop()
        return 0
    except (LinkError, OSError, tk.TclError) as exc:
        print(f"No se pudo iniciar el panel: {exc}")
        return 1
    finally:
        controlador.cerrar()
        cola.detener()
        enlace.cerrar()


if __name__ == "__main__":
    raise SystemExit(ejecutar())
