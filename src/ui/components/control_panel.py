"""
Panel lateral de control y acciones para RedLocalBlock.
"""

from typing import Callable, Optional
import customtkinter as ctk

from src.models.device import DispositivoRed, EstadoDispositivo
from src.ui.theme import COLORS, FONTS, SPACING, RADII


class ControlPanel(ctk.CTkFrame):
    """Panel con botones de acción para escaneo, aislamiento y reconciliación de red."""

    def __init__(
        self,
        master,
        on_escanear: Optional[Callable[[], None]] = None,
        on_aislar: Optional[Callable[[], None]] = None,
        on_restaurar: Optional[Callable[[], None]] = None,
        on_restaurar_todo: Optional[Callable[[], None]] = None,
        on_ayuda: Optional[Callable[[], None]] = None,
        on_renombrar: Optional[Callable[[], None]] = None,
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

        self.on_escanear = on_escanear
        self.on_aislar = on_aislar
        self.on_restaurar = on_restaurar
        self.on_restaurar_todo = on_restaurar_todo
        self.on_ayuda = on_ayuda
        self.on_renombrar = on_renombrar

        self._crear_widgets()

    def _crear_widgets(self):
        # Título de panel con HelpCircle (Patrón Agency-Satoshi de 08-popups)
        top_row = ctk.CTkFrame(self, fg_color="transparent")
        top_row.pack(fill="x", padx=SPACING["md"], pady=(SPACING["md"], SPACING["sm"]))

        lbl_titulo = ctk.CTkLabel(
            top_row,
            text="Panel de Control",
            font=(FONTS["family_sans"], FONTS["sizes"]["base"], "bold"),
            text_color=COLORS["text"],
        )
        lbl_titulo.pack(side="left")

        if self.on_ayuda:
            btn_help = ctk.CTkButton(
                top_row,
                text="?",
                width=24,
                height=24,
                font=(FONTS["family_sans"], FONTS["sizes"]["xs"], "bold"),
                fg_color=COLORS["bg"],
                hover_color=COLORS["surface_hover"],
                text_color=COLORS["text_muted"],
                border_width=1,
                border_color=COLORS["border"],
                corner_radius=RADII["pill"],
                command=self.on_ayuda,
            )
            btn_help.pack(side="right")

        # Tarjeta de dispositivo seleccionado
        self.card_info = ctk.CTkFrame(
            self,
            fg_color=COLORS["bg"],
            corner_radius=RADII["md"],
            border_width=1,
            border_color=COLORS["border"],
        )
        self.card_info.pack(fill="x", padx=SPACING["md"], pady=SPACING["xs"])

        self.lbl_target_ip = ctk.CTkLabel(
            self.card_info,
            text="Ningún dispositivo seleccionado",
            font=(FONTS["family_sans"], FONTS["sizes"]["sm"], "bold"),
            text_color=COLORS["text_muted"],
        )
        self.lbl_target_ip.pack(anchor="w", padx=SPACING["sm"], pady=(SPACING["xs"], 0))

        self.lbl_target_details = ctk.CTkLabel(
            self.card_info,
            text="Haz clic en una fila de la tabla",
            font=(FONTS["family_sans"], FONTS["sizes"]["xs"]),
            text_color=COLORS["text_muted"],
        )
        self.lbl_target_details.pack(anchor="w", padx=SPACING["sm"], pady=(0, SPACING["xs"]))

        # Separador visual
        ctk.CTkFrame(self, fg_color=COLORS["border"], height=1).pack(
            fill="x", padx=SPACING["md"], pady=SPACING["md"]
        )

        # Botón Escanear Red
        self.btn_escanear = ctk.CTkButton(
            self,
            text="🔍 Escanear Red",
            font=(FONTS["family_sans"], FONTS["sizes"]["sm"], "bold"),
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"],
            corner_radius=RADII["md"],
            height=36,
            command=self._accion_escanear,
        )
        self.btn_escanear.pack(fill="x", padx=SPACING["md"], pady=SPACING["xs"])

        # Botón Aislar
        self.btn_aislar = ctk.CTkButton(
            self,
            text="⛔ Aislar Seleccionado",
            font=(FONTS["family_sans"], FONTS["sizes"]["sm"], "bold"),
            fg_color=COLORS["danger"],
            hover_color=COLORS["danger_hover"],
            corner_radius=RADII["md"],
            height=36,
            state="disabled",
            command=self._accion_aislar,
        )
        self.btn_aislar.pack(fill="x", padx=SPACING["md"], pady=SPACING["xs"])

        # Botón Restaurar Seleccionado
        self.btn_restaurar = ctk.CTkButton(
            self,
            text="🔄 Restaurar Conexión",
            font=(FONTS["family_sans"], FONTS["sizes"]["sm"], "bold"),
            fg_color=COLORS["surface_hover"],
            hover_color=COLORS["border"],
            text_color=COLORS["text"],
            border_width=1,
            border_color=COLORS["border_input"],
            corner_radius=RADII["md"],
            height=36,
            state="disabled",
            command=self._accion_restaurar,
        )
        self.btn_restaurar.pack(fill="x", padx=SPACING["md"], pady=SPACING["xs"])

        # Botón Restaurar Todo
        self.btn_restaurar_todo = ctk.CTkButton(
            self,
            text="🛡️ Restaurar Toda la Red",
            font=(FONTS["family_sans"], FONTS["sizes"]["xs"]),
            fg_color=COLORS["bg"],
            hover_color=COLORS["surface_hover"],
            text_color=COLORS["text"],
            border_width=1,
            border_color=COLORS["border"],
            corner_radius=RADII["md"],
            height=32,
            command=self._accion_restaurar_todo,
        )
        self.btn_restaurar_todo.pack(fill="x", padx=SPACING["md"], pady=(SPACING["xs"], SPACING["xs"]))

        # Botón Renombrar Dispositivo
        self.btn_renombrar = ctk.CTkButton(
            self,
            text="✏️ Renombrar Dispositivo",
            font=(FONTS["family_sans"], FONTS["sizes"]["xs"]),
            fg_color="transparent",
            hover_color=COLORS["surface_hover"],
            text_color=COLORS["text"],
            border_width=1,
            border_color=COLORS["border"],
            corner_radius=RADII["md"],
            height=28,
            state="disabled",
            command=self._accion_renombrar,
        )
        self.btn_renombrar.pack(fill="x", padx=SPACING["md"], pady=(0, SPACING["md"]))


    def actualizar_seleccion(self, d: Optional[DispositivoRed]):
        """Habilita o deshabilita botones según el dispositivo seleccionado y su estado."""
        if not d:
            self.lbl_target_ip.configure(
                text="Ningún dispositivo seleccionado",
                text_color=COLORS["text_muted"]
            )
            self.lbl_target_details.configure(text="Haz clic en una fila de la tabla")
            self.btn_aislar.configure(state="disabled")
            self.btn_restaurar.configure(state="disabled")
            self.btn_renombrar.configure(state="disabled")
            return

        self.lbl_target_ip.configure(text=f"{d.nombre_amigable}", text_color=COLORS["text"])
        self.lbl_target_details.configure(text=f"IP: {d.ip} | MAC: {d.mac}")
        self.btn_renombrar.configure(state="normal")

        if not d.es_bloqueable:
            self.btn_aislar.configure(state="disabled")
            self.btn_restaurar.configure(state="disabled")
        elif d.estado == EstadoDispositivo.AISLADO:
            self.btn_aislar.configure(state="disabled")
            self.btn_restaurar.configure(state="normal")
        else:
            self.btn_aislar.configure(state="normal")
            self.btn_restaurar.configure(state="disabled")

    def set_estado_escaneo(self, escaneando: bool):
        if escaneando:
            self.btn_escanear.configure(text="⏳ Escaneando...", state="disabled")
        else:
            self.btn_escanear.configure(text="🔍 Escanear Red", state="normal")

    def _accion_escanear(self):
        if self.on_escanear:
            self.on_escanear()

    def _accion_aislar(self):
        if self.on_aislar:
            self.on_aislar()

    def _accion_restaurar(self):
        if self.on_restaurar:
            self.on_restaurar()

    def _accion_restaurar_todo(self):
        if self.on_restaurar_todo:
            self.on_restaurar_todo()

    def _accion_renombrar(self):
        if self.on_renombrar:
            self.on_renombrar()
