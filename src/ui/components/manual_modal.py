"""
Modal emergente interactivo con manual de uso desplegable (Acordeón).
Basado en los estándares de UX y diseño de 08-popups (Patrón Agency-Satoshi).
"""

from typing import List, Tuple
import customtkinter as ctk

from src.ui.theme import COLORS, FONTS, SPACING, RADII


class SeccionDesplegable(ctk.CTkFrame):
    """Componente acordeón desplegable/colapsable con animación visual de estado."""

    def __init__(self, master, titulo: str, contenido_md: str, icono: str = "▶", expandido_inicial: bool = False, **kwargs):
        super().__init__(
            master,
            fg_color=COLORS["bg"],
            corner_radius=RADII["md"],
            border_width=1,
            border_color=COLORS["border"],
            **kwargs,
        )

        self.titulo = titulo
        self.contenido_md = contenido_md
        self.expandido = expandido_inicial

        self._crear_interfaz()

    def _crear_interfaz(self):
        # Cabecera clickeable de la sección
        self.header_btn = ctk.CTkButton(
            self,
            text=f"{'▼' if self.expandido else '▶'}  {self.titulo}",
            font=(FONTS["family_sans"], FONTS["sizes"]["sm"], "bold"),
            fg_color="transparent",
            hover_color=COLORS["surface_hover"],
            text_color=COLORS["text"],
            anchor="w",
            height=36,
            corner_radius=RADII["md"],
            command=self.toggle,
        )
        self.header_btn.pack(fill="x", padx=SPACING["xs"], pady=SPACING["xs"])

        # Contenedor de contenido interno
        self.contenido_frame = ctk.CTkFrame(self, fg_color="transparent")
        if self.expandido:
            self.contenido_frame.pack(fill="x", padx=SPACING["md"], pady=(0, SPACING["md"]))

        # Texto estructurado
        self.lbl_contenido = ctk.CTkLabel(
            self.contenido_frame,
            text=self.contenido_md,
            font=(FONTS["family_sans"], FONTS["sizes"]["xs"]),
            text_color=COLORS["text_muted"],
            justify="left",
            anchor="w",
            wraplength=580,
        )
        self.lbl_contenido.pack(fill="x", anchor="w")

    def toggle(self):
        """Alterna el estado desplegado/plegado del acordeón."""
        if self.expandido:
            self.colapsar()
        else:
            self.expandir()

    def expandir(self):
        if not self.expandido:
            self.expandido = True
            self.header_btn.configure(
                text=f"▼  {self.titulo}",
                text_color=COLORS["accent"],
            )
            self.contenido_frame.pack(fill="x", padx=SPACING["md"], pady=(0, SPACING["md"]))

    def colapsar(self):
        if self.expandido:
            self.expandido = False
            self.header_btn.configure(
                text=f"▶  {self.titulo}",
                text_color=COLORS["text"],
            )
            self.contenido_frame.pack_forget()


class ManualModal(ctk.CTkToplevel):
    """
    Ventana modal emergente (Popup) con el manual de uso interactivo desplegable.
    """

    SECCIONES: List[Tuple[str, str]] = [
        (
            "1. Descubrimiento y Nombres de Dispositivos (Subred /24)",
            "• ¿Cómo funciona? Al pulsar 'Escanear Red', el motor envía consultas broadcast ARP a todos los nodos de la subred local (ej. 192.168.0.1 a 192.168.0.254) sin bloquear la interfaz.\n"
            "• Identificación Inteligente: En lugar de textos confusos como 'Genérico / Desconocido', la tabla muestra el Nombre del Dispositivo (ej. 'Router (ARRIS / CommScope)', 'Consola Nintendo', 'Dispositivo Apple', 'DESKTOP-MFGBNR9 (Este Equipo)').\n"
            "• Nombres Personalizados: Selecciona cualquier fila y pulsa '✏️ Renombrar Dispositivo' para asignarle el apodo que quieras (ej. 'Switch del Salón', 'Móvil Papá'). Se almacena localmente y persiste entre reinicios.\n"
            "• Filtro en vivo: Usa la barra de búsqueda superior para filtrar instantáneamente por IP, MAC o nombre de equipo."
        ),

        (
            "2. Control de Acceso y Aislamiento en Capa 2 (ARP Spoofing)",
            "• Mecanismo técnico: La aplicación forja paquetes ARP de respuesta (op=2) dirigidos a la víctima y al router cada 2 segundos.\n"
            "• Efecto en la red: El tráfico del dispositivo objetivo se desvía al host administrador. Al no existir reenvío de paquetes (IP Forwarding deshabilitado), el dispositivo pierde la salida a Internet de inmediato sin afectar al resto de clientes.\n"
            "• Instrucciones: Selecciona un dispositivo en la tabla y pulsa el botón rojo '⛔ Aislar Seleccionado'. El badge cambiará a rojo 'AISLADO'."
        ),
        (
            "3. Reconciliación y Restauración Inmediata de Red",
            "• Garantía de integridad: Es fundamental no dejar tablas ARP contaminadas. Al presionar '🔄 Restaurar Conexión', se emite una ráfaga de 5 paquetes ARP legítimos con las MACs reales para devolver el flujo normal de inmediato.\n"
            "• Restauración Global: El botón '🛡️ Restaurar Toda la Red' normaliza todos los clientes aislados a la vez.\n"
            "• Cierre Seguro: Si cierras la aplicación con la cruz (✕), el hook automático del sistema reconcilia la red antes de apagarse."
        ),
        (
            "4. Reglas de Protección del Sistema (Anti-Autoaislamiento)",
            "• Protección del Router: La puerta de enlace (Gateway) está blindada por software; el botón de aislamiento se desactiva para evitar caídas de toda la red.\n"
            "• Protección del Administrador: La máquina local ('Este Equipo') también está protegida para evitar auto-bloqueos accidentales.\n"
            "• Badges de seguridad: Observa el badge ámbar 'Router (Protegido)' y el azul 'Este Equipo'."
        ),
        (
            "5. Requisitos Técnicos y Marco Ético (DSGVO / TDDDG)",
            "• Privacidad Local-First: Esta herramienta opera 100% en tu ordenador. No envía telemetría, no usa cookies ni conecta con servidores en la nube.\n"
            "• Controlador Npcap: En Windows, Npcap es indispensable para manipulación de sockets raw en Capa 2.\n"
            "• Uso Ético Obligatorio: Diseñado para fines educativos, pruebas de concepto y administración defensiva de redes de tu propiedad o con autorización expresa."
        ),
    ]

    def __init__(self, parent, seccion_inicial: int = 0):
        super().__init__(parent)

        self.title("Manual de Uso & Guía de Auditoría - RedLocalBlock")
        self.geometry("680x580")
        self.minsize(580, 480)
        self.configure(fg_color=COLORS["bg"])

        # Centrar sobre la ventana padre
        self._centrar_en_padre(parent, 680, 580)

        # Modalidad y foco
        self.transient(parent)
        self.grab_set()

        # Tecla Escape para cerrar (Regla UX de 08-popups)
        self.bind("<Escape>", lambda e: self.destroy())

        self._acordeones: List[SeccionDesplegable] = []
        self._crear_widgets(seccion_inicial)

    def _centrar_en_padre(self, parent, ancho: int, alto: int):
        try:
            parent.update_idletasks()
            px = parent.winfo_x()
            py = parent.winfo_y()
            pw = parent.winfo_width()
            ph = parent.winfo_height()
            x = max(0, px + (pw - ancho) // 2)
            y = max(0, py + (ph - alto) // 2)
            self.geometry(f"{ancho}x{alto}+{x}+{y}")
        except Exception:
            pass

    def _crear_widgets(self, seccion_inicial: int):
        # 1. Cabecera del Popup
        header_frame = ctk.CTkFrame(
            self,
            fg_color=COLORS["surface"],
            corner_radius=RADII["lg"],
            border_width=1,
            border_color=COLORS["border"],
        )
        header_frame.pack(fill="x", padx=SPACING["md"], pady=(SPACING["md"], SPACING["xs"]))

        titulo_box = ctk.CTkFrame(header_frame, fg_color="transparent")
        titulo_box.pack(side="left", padx=SPACING["md"], pady=SPACING["md"])

        lbl_tit = ctk.CTkLabel(
            titulo_box,
            text="📖 Manual de Uso y Guía de Auditoría",
            font=(FONTS["family_sans"], FONTS["sizes"]["md"], "bold"),
            text_color=COLORS["text"],
        )
        lbl_tit.pack(anchor="w")

        lbl_sub = ctk.CTkLabel(
            titulo_box,
            text="Haz clic en cualquier sección para desplegar u ocultar los detalles.",
            font=(FONTS["family_sans"], FONTS["sizes"]["xs"]),
            text_color=COLORS["text_muted"],
        )
        lbl_sub.pack(anchor="w")

        # Botón de cerrar cruz '✕'
        btn_cerrar_top = ctk.CTkButton(
            header_frame,
            text="✕",
            width=32,
            height=32,
            font=(FONTS["family_sans"], FONTS["sizes"]["sm"], "bold"),
            fg_color="transparent",
            hover_color=COLORS["surface_hover"],
            text_color=COLORS["text_muted"],
            corner_radius=RADII["sm"],
            command=self.destroy,
        )
        btn_cerrar_top.pack(side="right", padx=SPACING["md"], pady=SPACING["md"])

        # Barra de controles del acordeón: Expandir todos / Colapsar todos
        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.pack(fill="x", padx=SPACING["md"], pady=(SPACING["xs"], 2))

        btn_expandir_todos = ctk.CTkButton(
            toolbar,
            text="Desplegar Todos",
            width=110,
            height=24,
            font=(FONTS["family_sans"], FONTS["sizes"]["xs"]),
            fg_color=COLORS["surface"],
            hover_color=COLORS["surface_hover"],
            text_color=COLORS["text"],
            border_width=1,
            border_color=COLORS["border"],
            corner_radius=RADII["sm"],
            command=self.expandir_todos,
        )
        btn_expandir_todos.pack(side="left", padx=(0, SPACING["xs"]))

        btn_colapsar_todos = ctk.CTkButton(
            toolbar,
            text="Plegar Todos",
            width=100,
            height=24,
            font=(FONTS["family_sans"], FONTS["sizes"]["xs"]),
            fg_color=COLORS["surface"],
            hover_color=COLORS["surface_hover"],
            text_color=COLORS["text"],
            border_width=1,
            border_color=COLORS["border"],
            corner_radius=RADII["sm"],
            command=self.colapsar_todos,
        )
        btn_colapsar_todos.pack(side="left")


        # 2. Contenedor desplazable con las secciones desplegables
        scroll_frame = ctk.CTkScrollableFrame(
            self,
            fg_color=COLORS["surface"],
            corner_radius=RADII["lg"],
            border_width=1,
            border_color=COLORS["border"],
        )
        scroll_frame.pack(fill="both", expand=True, padx=SPACING["md"], pady=SPACING["xs"])

        # Generar las 5 secciones
        for i, (titulo, contenido) in enumerate(self.SECCIONES):
            expandido = (i == seccion_inicial)
            sec = SeccionDesplegable(
                scroll_frame,
                titulo=titulo,
                contenido_md=contenido,
                expandido_inicial=expandido,
            )
            sec.pack(fill="x", pady=SPACING["xs"])
            self._acordeones.append(sec)

        # 3. Barra inferior de confirmación (Patrón SweetAlert / 08-popups)
        bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        bottom_frame.pack(fill="x", padx=SPACING["md"], pady=(SPACING["xs"], SPACING["md"]))

        btn_entendido = ctk.CTkButton(
            bottom_frame,
            text="✓ Entendido",
            font=(FONTS["family_sans"], FONTS["sizes"]["sm"], "bold"),
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"],
            text_color=COLORS["on_accent"],
            corner_radius=RADII["md"],
            height=36,
            command=self.destroy,
        )
        btn_entendido.pack(side="right")


    def expandir_todos(self):
        for sec in self._acordeones:
            sec.expandir()

    def colapsar_todos(self):
        for sec in self._acordeones:
            sec.colapsar()
