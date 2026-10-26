"""
Ventana principal de la aplicación RedLocalBlock.
Ensambla los componentes modulares y gestiona el despacho asíncrono thread-safe.
"""

import queue
from typing import Dict, Optional
import customtkinter as ctk

from src.core.system_detector import InfoRedLocal, SystemDetector
from src.models.device import DispositivoRed, EstadoDispositivo
from src.services.isolation_service import IsolationService
from src.services.scan_service import ScanService
from src.ui.components.control_panel import ControlPanel
from src.ui.components.device_table import DeviceTable
from src.ui.components.header_bar import HeaderBar
from src.ui.components.log_console import LogConsole
from src.ui.components.status_bar import StatusBar
from src.ui.theme import COLORS, SPACING
from src.utils.logger import AppLogger


class RedLocalBlockApp(ctk.CTk):
    """Aplicación de escritorio principal para RedLocalBlock."""

    def __init__(self, info_red: Optional[InfoRedLocal] = None):
        super().__init__()

        # Configuración de apariencia y ventana
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.title("RedLocalBlock - Auditoría y Control de Red Local")
        self.geometry("1020x700")
        self.minsize(880, 580)
        self.configure(fg_color=COLORS["bg"])

        # Detectar red si no fue inyectada
        self.info_red = info_red or SystemDetector.detectar_red()

        # Cola para comunicación thread-safe entre hilos de Scapy y la GUI
        self.cola_logs: queue.Queue = queue.Queue()
        self.logger = AppLogger(self.cola_logs)

        # Servicios de red
        self.isolation_service = IsolationService(
            ip_gateway=self.info_red.ip_gateway,
            mac_gateway=self.info_red.mac_gateway,
            mac_local=self.info_red.mac_local,
            logger=self.logger,
        )

        self.scan_service = ScanService(
            subred_cidr=self.info_red.subred_cidr,
            ip_gateway=self.info_red.ip_gateway,
            ip_local=self.info_red.ip_local,
            mac_local=self.info_red.mac_local,
            logger=self.logger,
        )

        self._dispositivos: Dict[str, DispositivoRed] = {}

        # Construcción visual
        self._construir_layout()

        # Interceptar cierre de ventana para reconciliación obligatoria
        self.protocol("WM_DELETE_WINDOW", self._al_cerrar_ventana)

        # Iniciar bucle de despacho de logs thread-safe
        self.after(100, self._procesar_cola_logs)

        # Registrar dispositivo local y router de inicio
        self._inicializar_nodos_base()

    def _construir_layout(self):
        # 1. Barra de cabecera
        self.header = HeaderBar(
            self,
            ip_local=self.info_red.ip_local,
            mac_local=self.info_red.mac_local,
            ip_gateway=self.info_red.ip_gateway,
            iface_nombre=self.info_red.nombre_interfaz,
        )
        self.header.pack(fill="x", padx=SPACING["md"], pady=(SPACING["md"], SPACING["xs"]))

        # 2. Cuerpo central: Tabla interactiva (Izquierda) + Panel de Control (Derecha)
        body_frame = ctk.CTkFrame(self, fg_color="transparent")
        body_frame.pack(fill="both", expand=True, padx=SPACING["md"], pady=SPACING["xs"])

        self.table = DeviceTable(
            body_frame,
            on_seleccion=self._al_seleccionar_dispositivo
        )
        self.table.pack(side="left", fill="both", expand=True, padx=(0, SPACING["xs"]))

        self.control_panel = ControlPanel(
            body_frame,
            width=260,
            on_escanear=self._iniciar_escaneo,
            on_aislar=self._aislar_seleccionado,
            on_restaurar=self._restaurar_seleccionado,
            on_restaurar_todo=self._restaurar_toda_la_red,
        )
        self.control_panel.pack(side="right", fill="y", padx=(SPACING["xs"], 0))

        # 3. Consola de auditoría inferior
        self.console = LogConsole(self, height=130)
        self.console.pack(fill="x", padx=SPACING["md"], pady=SPACING["xs"])

        # 4. Barra de estado inferior
        self.status_bar = StatusBar(self)
        self.status_bar.pack(fill="x", padx=SPACING["md"], pady=(SPACING["xs"], SPACING["sm"]))

    def _inicializar_nodos_base(self):
        """Agrega el Router y el host local a la tabla al inicio."""
        disp_gw = DispositivoRed(
            ip=self.info_red.ip_gateway,
            mac=self.info_red.mac_gateway,
            vendor="Gateway de Red",
            es_gateway=True,
            es_local=False,
        )
        disp_local = DispositivoRed(
            ip=self.info_red.ip_local,
            mac=self.info_red.mac_local,
            vendor="Host Administrador",
            es_gateway=False,
            es_local=True,
        )
        self._dispositivos[disp_gw.ip] = disp_gw
        self._dispositivos[disp_local.ip] = disp_local
        self.table.actualizar_dispositivos(list(self._dispositivos.values()))
        self._actualizar_metricas()

    def _iniciar_escaneo(self):
        """Dispara el escaneo concurrente de la subred."""
        self.control_panel.set_estado_escaneo(True)
        self.status_bar.set_estado("Escaneando subred...", COLORS["accent"])

        def on_dispositivo(d: DispositivoRed):
            self._dispositivos[d.ip] = d
            self.after(0, lambda: self.table.agregar_o_actualizar_dispositivo(d))
            self.after(0, self._actualizar_metricas)

        def on_fin(lista):
            self.after(0, lambda: self.control_panel.set_estado_escaneo(False))
            self.after(0, self._actualizar_metricas)

        self.scan_service.iniciar_escaneo_asincrono(
            on_dispositivo_encontrado=on_dispositivo,
            on_completado=on_fin,
        )

    def _al_seleccionar_dispositivo(self, d: Optional[DispositivoRed]):
        self.control_panel.actualizar_seleccion(d)

    def _aislar_seleccionado(self):
        d = self.table.obtener_seleccionado()
        if not d or not d.es_bloqueable:
            return

        def on_error(ip, err):
            self.after(0, lambda: self.table.actualizar_dispositivos(list(self._dispositivos.values())))
            self.after(0, self._actualizar_metricas)

        exito = self.isolation_service.aislar_dispositivo(d, on_error=on_error)
        if exito:
            self.table.actualizar_dispositivos(list(self._dispositivos.values()))
            self.control_panel.actualizar_seleccion(d)
            self._actualizar_metricas()

    def _restaurar_seleccionado(self):
        d = self.table.obtener_seleccionado()
        if not d:
            return

        exito = self.isolation_service.detener_aislamiento(d.ip)
        if exito:
            self.table.actualizar_dispositivos(list(self._dispositivos.values()))
            self.control_panel.actualizar_seleccion(d)
            self._actualizar_metricas()

    def _restaurar_toda_la_red(self):
        self.isolation_service.restaurar_todo()
        for d in self._dispositivos.values():
            if d.estado == EstadoDispositivo.AISLADO:
                d.cambiar_estado(EstadoDispositivo.NORMAL)
        self.table.actualizar_dispositivos(list(self._dispositivos.values()))
        self.control_panel.actualizar_seleccion(self.table.obtener_seleccionado())
        self._actualizar_metricas()

    def _actualizar_metricas(self):
        total = len(self._dispositivos)
        aislados = sum(1 for d in self._dispositivos.values() if d.estado == EstadoDispositivo.AISLADO)
        self.status_bar.actualizar_metricas(total, aislados)

    def _procesar_cola_logs(self):
        """Consume los eventos de registro encolados de manera segura en el hilo principal de Tkinter."""
        try:
            while True:
                evento = self.cola_logs.get_nowait()
                self.console.agregar_evento(evento)
        except queue.Empty:
            pass
        finally:
            self.after(100, self._procesar_cola_logs)

    def _al_cerrar_ventana(self):
        """Garantiza la reconciliación total de la red antes de cerrar la aplicación."""
        self.isolation_service.restaurar_todo()
        self.destroy()
