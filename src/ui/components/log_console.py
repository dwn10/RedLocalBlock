"""
Consola de auditoría y eventos en tiempo real para RedLocalBlock.
"""

import customtkinter as ctk

from src.ui.theme import COLORS, FONTS, SPACING, RADII
from src.utils.logger import EventoLog, NivelLog


class LogConsole(ctk.CTkFrame):
    """Consola desplazable para registro de eventos y auditoría de paquetes de red."""

    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            fg_color=COLORS["surface"],
            corner_radius=RADII["lg"],
            border_width=1,
            border_color=COLORS["border"],
            **kwargs,
        )

        self._crear_widgets()

    def _crear_widgets(self):
        # Barra superior de la consola
        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.pack(fill="x", padx=SPACING["md"], pady=(SPACING["sm"], 2))

        lbl_titulo = ctk.CTkLabel(
            top_frame,
            text="Consola de Auditoría y Eventos de Red",
            font=(FONTS["family_sans"], FONTS["sizes"]["xs"], "bold"),
            text_color=COLORS["text_muted"],
        )
        lbl_titulo.pack(side="left")

        btn_limpiar = ctk.CTkButton(
            top_frame,
            text="Limpiar",
            width=60,
            height=20,
            font=(FONTS["family_sans"], FONTS["sizes"]["xs"]),
            fg_color=COLORS["bg"],
            hover_color=COLORS["surface_hover"],
            border_width=1,
            border_color=COLORS["border"],
            corner_radius=RADII["sm"],
            command=self.limpiar_consola,
        )
        btn_limpiar.pack(side="right")

        # Área de texto tipo consola
        self.textbox = ctk.CTkTextbox(
            self,
            fg_color=COLORS["console_bg"],
            text_color=COLORS["text"],
            font=(FONTS["family_mono"], FONTS["sizes"]["xs"]),
            corner_radius=RADII["sm"],
            wrap="word",
        )
        self.textbox.pack(fill="both", expand=True, padx=SPACING["md"], pady=(2, SPACING["sm"]))

        # Mensaje de bienvenida inicial
        self.agregar_log_crudo("[00:00:00] [INFO] Consola de auditoría de RedLocalBlock inicializada.")

    def agregar_evento(self, evento: EventoLog):
        """Agrega un evento formateado con el color correspondiente."""
        self.agregar_log_crudo(evento.formatear())

    def agregar_log_crudo(self, linea: str):
        """Inserta una línea en la consola y hace scroll automático al final."""
        self.textbox.configure(state="normal")
        self.textbox.insert("end", linea + "\n")
        self.textbox.see("end")
        self.textbox.configure(state="disabled")

    def limpiar_consola(self):
        """Borra todo el contenido de la consola."""
        self.textbox.configure(state="normal")
        self.textbox.delete("1.0", "end")
        self.textbox.configure(state="disabled")
