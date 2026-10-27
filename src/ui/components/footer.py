"""
Componente Footer estándar para RedLocalBlock.
Basado en la directriz de la habilidad 02d-el-footer.
Centrado con Copyright, año dinámico, nombre de marca y atribución enlazada a ECUADOR-IT.
"""

from datetime import datetime
from typing import Optional
import webbrowser
import customtkinter as ctk

from src.ui.theme import COLORS, FONTS, SPACING


class AppFooter(ctk.CTkFrame):
    """
    Pie de página estandarizado (Footer) para la aplicación.
    Muestra créditos legales, año dinámico y atribución enlazada a ECUADOR-IT.
    """

    URL_ECUADOR_IT = "https://www.ecuador-it.com/"

    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            fg_color="transparent",
            height=26,
            **kwargs,
        )
        self._crear_widgets()

    def _crear_widgets(self):
        # Contenedor centralizado para los elementos del footer
        center_container = ctk.CTkFrame(self, fg_color="transparent")
        center_container.pack(anchor="center", pady=(SPACING["xs"], 2))

        anio_actual = datetime.now().year

        # 1. Texto de Copyright y Marca
        lbl_copyright = ctk.CTkLabel(
            center_container,
            text=f"© {anio_actual} RedLocalBlock • Todos los derechos reservados • Desarrollado por",
            font=(FONTS["family_sans"], FONTS["sizes"]["xs"]),
            text_color=COLORS["text_muted"],
        )
        lbl_copyright.pack(side="left")

        # 2. Enlace interactivo a la agencia ECUADOR-IT
        self.lbl_link = ctk.CTkLabel(
            center_container,
            text="ECUADOR-IT",
            font=(FONTS["family_sans"], FONTS["sizes"]["xs"], "bold"),
            text_color=COLORS["accent"],
            cursor="hand2",
        )
        self.lbl_link.pack(side="left", padx=(SPACING["xs"], 0))

        # Eventos interactivos del enlace
        self.lbl_link.bind("<Button-1>", lambda e: self._abrir_enlace())
        self.lbl_link.bind("<Enter>", lambda e: self.lbl_link.configure(text_color=COLORS["accent_hover"]))
        self.lbl_link.bind("<Leave>", lambda e: self.lbl_link.configure(text_color=COLORS["accent"]))

    def _abrir_enlace(self):
        """Abre el sitio oficial de ECUADOR-IT en el navegador web predeterminado."""
        webbrowser.open_new_tab(self.URL_ECUADOR_IT)
