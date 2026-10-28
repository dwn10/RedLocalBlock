"""
Ventana principal de la aplicación RedLocalBlock.
Ensambla los componentes modulares y gestiona el despacho asíncrono thread-safe,
la vigilancia pasiva del Modo Centinela y la bandeja del sistema (System Tray).
"""

import queue
from typing import Dict, List, Optional
import customtkinter as ctk

from src.core.system_detector import InfoRedLocal, SystemDetector
from src.models.device import DispositivoRed, EstadoDispositivo
from src.services.alias_service import AliasService
from src.services.isolation_service import IsolationService
from src.services.oui_service import OUIService
from src.services.scan_service import ScanService
from src.services.sentinel_service import SentinelService
from src.ui.components.control_panel import ControlPanel
from src.ui.components.device_table import DeviceTable
from src.ui.components.header_bar import HeaderBar
from src.ui.components.log_console import LogConsole
from src.ui.components.status_bar import StatusBar
from src.ui.components.manual_modal import ManualModal
from src.ui.components.footer import AppFooter
from src.ui.components.tray_manager import TrayManager
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
        self.geometry("1020x720")
        self.minsize(880, 600)
        self.configure(fg_color=COLORS["bg"])

        self._notificado_bandeja = False

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

        # Servicio Centinela (Escucha Pasiva en Capa 2)
        self.sentinel_service = SentinelService(
            ip_gateway=self.info_red.ip_gateway,
            mac_gateway=self.info_red.mac_gateway,
            ip_local=self.info_red.ip_local,
            mac_local=self.info_red.mac_local,
            iface=self.info_red.nombre_interfaz,
            logger=self.logger,
            on_nuevo_dispositivo=self._al_detectar_nuevo_dispositivo,
            on_dispositivo_visto=self._al_ver_dispositivo_conocido,
        )

        # Gestor de Bandeja del Sistema (System Tray)
        self.tray_manager = TrayManager(
            on_mostrar=self.restaurar_ventana,
            on_toggle_centinela=self._toggle_centinela,
            on_escanear=lambda: self.after(0, self._iniciar_escaneo),
            on_restaurar_todo=lambda: self.after(0, self._restaurar_toda_la_red),
            on_salir=self._al_salir_definitivo,
            centinela_activo_inicial=True,
        )

        self._dispositivos: Dict[str, DispositivoRed] = {}

        # Construcción visual
        self._construir_layout()

        # Interceptar cierre de ventana para minimizar a bandeja manteniendo centinela activo
        self.protocol("WM_DELETE_WINDOW", self._al_cerrar_ventana)

        # Iniciar bucle de despacho de logs thread-safe
        self.after(100, self._procesar_cola_logs)

        # Registrar dispositivo local y router de inicio
        self._inicializar_nodos_base()

    def _construir_layout(self):
        # 1. Barra de cabecera con botón de Manual
        self.header = HeaderBar(
            self,
            ip_local=self.info_red.ip_local,
            mac_local=self.info_red.mac_local,
            ip_gateway=self.info_red.ip_gateway,
            iface_nombre=self.info_red.nombre_interfaz,
            on_abrir_manual=self._abrir_manual_usuario,
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
            on_ayuda=lambda: self._abrir_manual_usuario(seccion_inicial=1),
            on_renombrar=self._renombrar_dispositivo_seleccionado,
            on_minimizar_tray=self.minimizar_a_bandeja,
        )
        self.control_panel.pack(side="right", fill="y", padx=(SPACING["xs"], 0))

        # 3. Consola de auditoría inferior
        self.console = LogConsole(self, height=130)
        self.console.pack(fill="x", padx=SPACING["md"], pady=SPACING["xs"])

        # 4. Barra de estado inferior
        self.status_bar = StatusBar(self, on_cambiar_tema=self._al_cambiar_tema)
        self.status_bar.pack(fill="x", padx=SPACING["md"], pady=(SPACING["xs"], 2))

        # 5. Pie de página estándar (02d-el-footer)
        self.footer = AppFooter(self)
        self.footer.pack(fill="x", padx=SPACING["md"], pady=(0, SPACING["xs"]))

    def _inicializar_nodos_base(self):
        """Agrega el Router y el host local a la tabla al inicio con nombres amigables."""
        gw_alias = AliasService.obtener_alias(self.info_red.mac_gateway) or ""
        gw_vendor = OUIService.obtener_fabricante(self.info_red.mac_gateway)
        disp_gw = DispositivoRed(
            ip=self.info_red.ip_gateway,
            mac=self.info_red.mac_gateway,
            vendor=gw_vendor,
            alias=gw_alias,
            es_gateway=True,
            es_local=False,
        )

        loc_alias = AliasService.obtener_alias(self.info_red.mac_local) or ""
        loc_vendor = OUIService.obtener_fabricante(self.info_red.mac_local)
        disp_local = DispositivoRed(
            ip=self.info_red.ip_local,
            mac=self.info_red.mac_local,
            vendor=loc_vendor,
            alias=loc_alias,
            es_gateway=False,
            es_local=True,
        )
        self._dispositivos[disp_gw.ip] = disp_gw
        self._dispositivos[disp_local.ip] = disp_local
        self.table.actualizar_dispositivos(list(self._dispositivos.values()))
        self._actualizar_metricas()

        # Registrar nodos conocidos en el monitor Centinela
        self.sentinel_service.registrar_mac_conocida(disp_gw.mac)
        self.sentinel_service.registrar_mac_conocida(disp_local.mac)
        self.sentinel_service.agregar_macs_conocidas(AliasService.obtener_todos_alias().keys())

        # Iniciar icono en bandeja y vigilancia en segundo plano
        self.tray_manager.iniciar()
        self.sentinel_service.iniciar()

    def restaurar_ventana(self, seleccionar_ip: Optional[str] = None):
        """Restaura la ventana principal desde la bandeja y la trae al frente."""
        def _restaurar():
            self.deiconify()
            self.lift()
            self.focus_force()
            if seleccionar_ip:
                self.table.seleccionar_dispositivo(seleccionar_ip)
        self.after(0, _restaurar)

    def minimizar_a_bandeja(self):
        """Oculta la ventana y mantiene el centinela vigilando en segundo plano."""
        self.withdraw()
        if not self._notificado_bandeja:
            self._notificado_bandeja = True
            self.tray_manager.notificar(
                titulo="🛡️ RedLocalBlock: Centinela en Segundo Plano",
                mensaje="La aplicación sigue vigilando la red de forma silenciosa.\nHaz doble clic en el icono para abrir."
            )

    def _al_cerrar_ventana(self):
        """Al pulsar la 'X' de la ventana, minimiza a la bandeja del sistema."""
        self.minimizar_a_bandeja()

    def _al_salir_definitivo(self):
        """Cierre definitivo: reconciliación total ARP y liberación de recursos."""
        def _terminar():
            self.logger.info("Cerrando RedLocalBlock: Reconciliando tablas de red y deteniendo Centinela...")
            self.isolation_service.restaurar_todo()
            self.sentinel_service.detener()
            self.tray_manager.detener()
            self.destroy()
        self.after(0, _terminar)

    def _toggle_centinela(self, activo: bool):
        """Pausa o activa el hilo Centinela desde el menú del tray o la interfaz."""
        if activo:
            self.sentinel_service.iniciar()
            self.status_bar.set_estado_centinela(True)
        else:
            self.sentinel_service.detener()
            self.status_bar.set_estado_centinela(False)

    def _al_detectar_nuevo_dispositivo(self, d: DispositivoRed):
        """Callback ejecutado cuando el Centinela detecta una MAC no registrada."""
        def _actualizar_ui():
            self._dispositivos[d.ip] = d
            self.table.agregar_o_actualizar_dispositivo(d)
            self._actualizar_metricas()
            self.status_bar.set_estado(f"Nuevo equipo: {d.nombre_amigable}", COLORS["warning"])

            nombre_detallado = d.nombre_amigable
            if d.vendor and d.vendor not in ("Desconocido", ""):
                nombre_detallado += f" ({d.vendor})"

            self.tray_manager.notificar(
                titulo="🛡️ RedLocalBlock: Nuevo Dispositivo en la Red",
                mensaje=f"IP: {d.ip} | MAC: {d.mac}\n{nombre_detallado}"
            )
        self.after(0, _actualizar_ui)

    def _al_ver_dispositivo_conocido(self, mac: str, ip: str):
        """Callback ejecutado cuando un dispositivo conocido emite tráfico en la red."""
        def _actualizar_tiempo():
            for disp in self._dispositivos.values():
                if disp.mac.upper() == mac.upper():
                    disp.registrar_actividad()
                    break
        self.after(0, _actualizar_tiempo)

    def _renombrar_dispositivo_seleccionado(self):
        """Permite al usuario asignar un nombre personalizado/alias al dispositivo."""
        d = self.table.obtener_seleccionado()
        if not d:
            return

        dialog = ctk.CTkInputDialog(
            text=f"Introduce el nombre o apodo para este equipo ({d.ip}):",
            title="Renombrar Dispositivo"
        )
        nuevo_nombre = dialog.get_input()
        if nuevo_nombre is not None:
            nuevo_limpio = nuevo_nombre.strip()
            d.alias = nuevo_limpio
            AliasService.guardar_alias(d.mac, nuevo_limpio)
            self.table.actualizar_dispositivos(list(self._dispositivos.values()))
            self.control_panel.actualizar_seleccion(d)
            if nuevo_limpio:
                self.logger.info(f"Dispositivo {d.ip} ({d.mac}) nombrado como '{nuevo_limpio}'.", d.ip)
            else:
                self.logger.info(f"Nombre de {d.ip} restablecido a '{d.nombre_amigable}'.", d.ip)

    def _iniciar_escaneo(self):
        """Dispara el escaneo concurrente de la subred."""
        self.control_panel.set_estado_escaneo(True)
        self.status_bar.set_estado("Escaneando subred...", COLORS["accent"])

        def on_dispositivo(d: DispositivoRed):
            self._dispositivos[d.ip] = d
            self.after(0, lambda: self.table.agregar_o_actualizar_dispositivo(d))
            self.after(0, self._actualizar_metricas)

        def on_fin(lista: List[DispositivoRed]):
            self.after(0, lambda: self.control_panel.set_estado_escaneo(False))
            self.after(0, self._actualizar_metricas)
            self.sentinel_service.agregar_macs_conocidas([d.mac for d in lista])

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

    def _abrir_manual_usuario(self, seccion_inicial: int = 0):
        """Abre la ventana modal desplegable con el manual de usuario (Patrón 08-popups)."""
        ManualModal(self, seccion_inicial=seccion_inicial)

    def _al_cambiar_tema(self, modo: str):
        """Notificación de cambio de tema: refresca componentes dinámicos de la interfaz."""
        self.table.actualizar_dispositivos(list(self._dispositivos.values()))
        self.logger.info(f"Tema de interfaz cambiado a {modo.upper()}.")
