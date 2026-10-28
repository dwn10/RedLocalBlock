"""
Tabla interactiva de dispositivos descubiertos en la subred con selección y filtrado.
"""

from typing import Callable, Dict, List, Optional
import customtkinter as ctk

from src.models.device import DispositivoRed, EstadoDispositivo
from src.ui.theme import COLORS, FONTS, SPACING, RADII


class DeviceTable(ctk.CTkFrame):
    """Componente que presenta el inventario de equipos y permite su selección interactiva."""

    def __init__(
        self,
        master,
        on_seleccion: Optional[Callable[[Optional[DispositivoRed]], None]] = None,
        **kwargs,
    ):
        super().__init__(
            master,
            fg_color=COLORS["surface"],
            corner_radius=RADII["lg"],
            border_width=1,
            border_color=COLORS["border"],
            **kwargs,
        )

        self.on_seleccion = on_seleccion
        self._dispositivos: Dict[str, DispositivoRed] = {}
        self._dispositivo_seleccionado: Optional[DispositivoRed] = None
        self._filas_widgets: Dict[str, ctk.CTkFrame] = {}

        self._crear_interfaz()

    def _crear_interfaz(self):
        # Barra de búsqueda y título de tabla
        top_bar = ctk.CTkFrame(self, fg_color="transparent")
        top_bar.pack(fill="x", padx=SPACING["md"], pady=(SPACING["md"], SPACING["xs"]))

        lbl_seccion = ctk.CTkLabel(
            top_bar,
            text="Dispositivos en la Subred",
            font=(FONTS["family_sans"], FONTS["sizes"]["base"], "bold"),
            text_color=COLORS["text"],
        )
        lbl_seccion.pack(side="left")

        self.entry_busqueda = ctk.CTkEntry(
            top_bar,
            placeholder_text="Filtrar por IP, MAC o Fabricante...",
            width=240,
            font=(FONTS["family_sans"], FONTS["sizes"]["xs"]),
            fg_color=COLORS["bg"],
            border_color=COLORS["border_input"],
            text_color=COLORS["text"],
            placeholder_text_color=COLORS["text_muted"],
            corner_radius=RADII["sm"],
        )
        self.entry_busqueda.pack(side="right")
        self.entry_busqueda.bind("<KeyRelease>", lambda e: self._aplicar_filtro())


        # Cabecera de columnas
        header_frame = ctk.CTkFrame(self, fg_color=COLORS["bg"], height=32, corner_radius=RADII["sm"])
        header_frame.pack(fill="x", padx=SPACING["md"], pady=(SPACING["xs"], 2))

        col_configs = [
            ("IP", 0.22),
            ("Dirección MAC", 0.26),
            ("Nombre del Dispositivo", 0.32),
            ("Estado", 0.20),
        ]
        for texto, peso in col_configs:
            lbl = ctk.CTkLabel(
                header_frame,
                text=texto,
                font=(FONTS["family_sans"], FONTS["sizes"]["xs"], "bold"),
                text_color=COLORS["text_muted"],
                anchor="w",
            )
            lbl.pack(side="left", expand=True, fill="x", padx=SPACING["sm"])

        # Contenedor scrollable para las filas de dispositivos
        self.scroll_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color=COLORS["border"],
            scrollbar_button_hover_color=COLORS["border_input"],
        )
        self.scroll_frame.pack(fill="both", expand=True, padx=SPACING["md"], pady=SPACING["sm"])

    def actualizar_dispositivos(self, dispositivos: List[DispositivoRed]):
        """Actualiza la lista interna de dispositivos y redibuja la tabla."""
        self._dispositivos = {d.ip: d for d in dispositivos}
        self._aplicar_filtro()

    def agregar_o_actualizar_dispositivo(self, dispositivo: DispositivoRed):
        """Agrega o refresca un único dispositivo de forma dinámica."""
        self._dispositivos[dispositivo.ip] = dispositivo
        self._aplicar_filtro()

    def obtener_seleccionado(self) -> Optional[DispositivoRed]:
        return self._dispositivo_seleccionado

    def seleccionar_dispositivo(self, ip_o_mac: str) -> Optional[DispositivoRed]:
        """Selecciona programáticamente un dispositivo por IP o MAC y notifica a la UI."""
        target = ip_o_mac.strip().upper()
        candidato = None
        for d in self._dispositivos.values():
            if d.ip == ip_o_mac or d.mac.upper() == target:
                candidato = d
                break
        if candidato:
            self._seleccionar(candidato)
        return candidato

    def _aplicar_filtro(self):
        termino = self.entry_busqueda.get().strip().lower()

        # Limpiar filas existentes
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        self._filas_widgets.clear()

        # Si no hay dispositivos
        if not self._dispositivos:
            vacio_lbl = ctk.CTkLabel(
                self.scroll_frame,
                text="No hay dispositivos detectados. Haz clic en 'Escanear Red'.",
                font=(FONTS["family_sans"], FONTS["sizes"]["sm"]),
                text_color=COLORS["text_muted"],
            )
            vacio_lbl.pack(pady=SPACING["xl"])
            return

        for ip, d in self._dispositivos.items():
            # Filtrado por búsqueda
            if termino:
                coincide = (
                    termino in d.ip.lower()
                    or termino in d.mac.lower()
                    or termino in d.nombre_amigable.lower()
                    or termino in d.vendor.lower()
                )
                if not coincide:
                    continue

            self._renderizar_fila(d)

    def _renderizar_fila(self, d: DispositivoRed):
        es_sel = (self._dispositivo_seleccionado and self._dispositivo_seleccionado.ip == d.ip)
        color_fondo = COLORS["surface_hover"] if es_sel else COLORS["bg"]

        fila = ctk.CTkFrame(
            self.scroll_frame,
            fg_color=color_fondo,
            corner_radius=RADII["sm"],
            border_width=1 if es_sel else 0,
            border_color=COLORS["accent"],
            height=36,
        )
        fila.pack(fill="x", pady=2)
        self._filas_widgets[d.ip] = fila

        # Callback de clic en toda la fila
        fila.bind("<Button-1>", lambda e, disp=d: self._seleccionar(disp))

        # Columna 1: IP
        lbl_ip = ctk.CTkLabel(
            fila,
            text=d.ip,
            font=(FONTS["family_mono"], FONTS["sizes"]["sm"], "bold"),
            text_color=COLORS["text"],
            anchor="w",
        )
        lbl_ip.pack(side="left", expand=True, fill="x", padx=SPACING["sm"])
        lbl_ip.bind("<Button-1>", lambda e, disp=d: self._seleccionar(disp))

        # Columna 2: MAC
        lbl_mac = ctk.CTkLabel(
            fila,
            text=d.mac,
            font=(FONTS["family_mono"], FONTS["sizes"]["xs"]),
            text_color=COLORS["text_muted"],
            anchor="w",
        )
        lbl_mac.pack(side="left", expand=True, fill="x", padx=SPACING["sm"])
        lbl_mac.bind("<Button-1>", lambda e, disp=d: self._seleccionar(disp))

        # Columna 3: Nombre del Dispositivo
        lbl_nombre = ctk.CTkLabel(
            fila,
            text=d.nombre_amigable,
            font=(FONTS["family_sans"], FONTS["sizes"]["xs"], "bold"),
            text_color=COLORS["text"],
            anchor="w",
        )
        lbl_nombre.pack(side="left", expand=True, fill="x", padx=SPACING["sm"])
        lbl_nombre.bind("<Button-1>", lambda e, disp=d: self._seleccionar(disp))

        # Columna 4: Badge de Estado
        badge_frame = ctk.CTkFrame(fila, fg_color="transparent")
        badge_frame.pack(side="left", expand=True, fill="x", padx=SPACING["sm"])

        txt_badge, color_badge = self._obtener_info_badge(d)
        badge = ctk.CTkLabel(
            badge_frame,
            text=txt_badge,
            font=(FONTS["family_sans"], FONTS["sizes"]["xs"], "bold"),
            fg_color=color_badge,
            text_color=COLORS["on_accent"],
            corner_radius=RADII["sm"],
            padx=SPACING["sm"],
            pady=2,
        )
        badge.pack(anchor="w")
        badge.bind("<Button-1>", lambda e, disp=d: self._seleccionar(disp))

    def _obtener_info_badge(self, d: DispositivoRed):
        if d.estado == EstadoDispositivo.AISLADO:
            return "AISLADO", COLORS["danger"]
        elif d.estado == EstadoDispositivo.RESTAURANDO:
            return "Restaurando...", COLORS["warning"]
        elif d.es_gateway:
            return "Router (Protegido)", COLORS["warning"]
        elif d.es_local:
            return "Este Equipo", COLORS["accent"]
        return "Conectado", COLORS["success"]

    def _seleccionar(self, d: DispositivoRed):
        self._dispositivo_seleccionado = d
        self._aplicar_filtro()
        if self.on_seleccion:
            self.on_seleccion(d)
