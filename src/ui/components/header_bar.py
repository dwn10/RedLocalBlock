"""
Barra superior de cabecera con indicadores de estado de red y botón de manual de uso.
"""

from typing import Callable, Optional
import customtkinter as ctk
from src.ui.theme import COLORS, FONTS, SPACING, RADII


class HeaderBar(ctk.CTkFrame):
    """Barra superior que muestra la identidad de la app, los parámetros de red activos y el acceso al manual."""

    def __init__(
        self,
        master,
        ip_local: str,
        mac_local: str,
        ip_gateway: str,
        iface_nombre: str,
        on_abrir_manual: Optional[Callable[[], None]] = None,
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

        self.on_abrir_manual = on_abrir_manual
        self._crear_widgets(ip_local, mac_local, ip_gateway, iface_nombre)

    def _crear_widgets(self, ip_local: str, mac_local: str, ip_gateway: str, iface_nombre: str):
        # Contenedor izquierdo: Marca y título
        info_frame = ctk.CTkFrame(self, fg_color="transparent")
        info_frame.pack(side="left", padx=SPACING["lg"], pady=SPACING["md"])

        titulo = ctk.CTkLabel(
            info_frame,
            text="🛡️ RedLocalBlock",
            font=(FONTS["family_sans"], FONTS["sizes"]["lg"], "bold"),
            text_color=COLORS["text"],
        )
        titulo.pack(anchor="w")

        subtitulo = ctk.CTkLabel(
            info_frame,
            text="Auditoría y Control de Acceso en Capa 2 (ARP)",
            font=(FONTS["family_sans"], FONTS["sizes"]["xs"]),
            text_color=COLORS["text_muted"],
        )
        subtitulo.pack(anchor="w")

        # Contenedor derecho: Pills de estado de red y botón de Manual
        pills_frame = ctk.CTkFrame(self, fg_color="transparent")
        pills_frame.pack(side="right", padx=SPACING["lg"], pady=SPACING["md"])

        # Pill Gateway
        self._crear_pill(pills_frame, "Gateway", ip_gateway, COLORS["warning"])
        # Pill IP Local
        self._crear_pill(pills_frame, "IP Local", ip_local, COLORS["accent"])
        # Pill Interfaz
        self._crear_pill(pills_frame, "Interfaz", iface_nombre, COLORS["border_input"])

        # Botón HelpCircle / Manual desplegable (08-popups)
        if self.on_abrir_manual:
            btn_manual = ctk.CTkButton(
                pills_frame,
                text="📖 Manual",
                font=(FONTS["family_sans"], FONTS["sizes"]["xs"], "bold"),
                fg_color=COLORS["accent"],
                hover_color=COLORS["accent_hover"],
                text_color=COLORS["on_accent"],
                corner_radius=RADII["sm"],
                width=85,
                height=26,
                command=self.on_abrir_manual,
            )
            btn_manual.pack(side="left", padx=(SPACING["sm"], 0), pady=2)


    def _crear_pill(self, master, etiqueta: str, valor: str, color_borde: str):
        pill = ctk.CTkFrame(
            master,
            fg_color=COLORS["bg"],
            corner_radius=RADII["sm"],
            border_width=1,
            border_color=color_borde,
        )
        pill.pack(side="left", padx=SPACING["xs"], pady=2)

        lbl = ctk.CTkLabel(
            pill,
            text=f"{etiqueta}: {valor}",
            font=(FONTS["family_mono"], FONTS["sizes"]["xs"]),
            text_color=COLORS["text"],
            padx=SPACING["sm"],
            pady=2,
        )
        lbl.pack()
