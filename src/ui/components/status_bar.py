"""
Barra de estado inferior con métricas y selector de tema.
"""

import customtkinter as ctk

from src.ui.theme import COLORS, FONTS, SPACING, RADII


class StatusBar(ctk.CTkFrame):
    """Barra inferior con métricas de red, estado global y selector de modo oscuro/claro."""

    def __init__(self, master, on_cambiar_tema=None, **kwargs):
        super().__init__(
            master,
            fg_color=COLORS["surface"],
            corner_radius=RADII["sm"],
            border_width=1,
            border_color=COLORS["border"],
            height=30,
            **kwargs,
        )

        self.on_cambiar_tema = on_cambiar_tema
        self._crear_widgets()

    def _crear_widgets(self):
        # Métrica de dispositivos
        self.lbl_metricas = ctk.CTkLabel(
            self,
            text="Dispositivos: 0 | Aislados: 0",
            font=(FONTS["family_sans"], FONTS["sizes"]["xs"]),
            text_color=COLORS["text_muted"],
        )
        self.lbl_metricas.pack(side="left", padx=SPACING["md"])

        # Estado global
        self.lbl_estado = ctk.CTkLabel(
            self,
            text="Listo para auditar",
            font=(FONTS["family_sans"], FONTS["sizes"]["xs"]),
            text_color=COLORS["success"],
        )
        self.lbl_estado.pack(side="left", padx=SPACING["lg"])

        # Switch de tema (Modo Oscuro / Claro)
        self.switch_tema = ctk.CTkSwitch(
            self,
            text="Modo Oscuro",
            font=(FONTS["family_sans"], FONTS["sizes"]["xs"]),
            text_color=COLORS["text_muted"],
            progress_color=COLORS["accent"],
            command=self._toggle_tema,
        )
        self.switch_tema.select()  # Dark mode por defecto
        self.switch_tema.pack(side="right", padx=SPACING["md"])

        # Versión
        lbl_version = ctk.CTkLabel(
            self,
            text="v1.0.0",
            font=(FONTS["family_mono"], FONTS["sizes"]["xs"]),
            text_color=COLORS["text_muted"],
        )
        lbl_version.pack(side="right", padx=SPACING["sm"])

    def actualizar_metricas(self, total_dispositivos: int, total_aislados: int):
        self.lbl_metricas.configure(
            text=f"Dispositivos: {total_dispositivos} | Aislados: {total_aislados}"
        )
        if total_aislados > 0:
            self.lbl_estado.configure(
                text=f"⚠️ {total_aislados} dispositivo(s) aislado(s)",
                text_color=COLORS["danger"]
            )
        else:
            self.lbl_estado.configure(
                text="Listo para auditar",
                text_color=COLORS["success"]
            )

    def set_estado(self, texto: str, color: str = COLORS["text"]):
        self.lbl_estado.configure(text=texto, text_color=color)

    def _toggle_tema(self):
        modo = "dark" if self.switch_tema.get() == 1 else "light"
        ctk.set_appearance_mode(modo)
        if self.on_cambiar_tema:
            self.on_cambiar_tema(modo)
