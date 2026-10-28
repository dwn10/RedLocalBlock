"""
Gestor de la bandeja del sistema (System Tray) con notificaciones nativas de Windows.
Utiliza pystray y Pillow para proporcionar un icono interactivo en el área de notificación
con menú contextual completo y soporte para notificaciones emergentes Toast / Balloon.
"""

from typing import Callable, Optional
from PIL import Image, ImageDraw
import pystray


def crear_icono_red(tamano: int = 64) -> Image.Image:
    """Genera un icono de alta resolución con escudo y nodo de red para la bandeja."""
    img = Image.new("RGBA", (tamano, tamano), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Círculo base oscuro con borde azul eléctrico
    draw.ellipse((2, 2, tamano - 3, tamano - 3), fill="#0f172a", outline="#3b82f6", width=3)

    # Escudo centinela en azul moderno
    puntos_escudo = [
        (tamano * 0.28, tamano * 0.24),
        (tamano * 0.72, tamano * 0.24),
        (tamano * 0.78, tamano * 0.52),
        (tamano * 0.50, tamano * 0.79),
        (tamano * 0.22, tamano * 0.52),
    ]
    draw.polygon(puntos_escudo, fill="#2563eb", outline="#93c5fd")

    # Nodo activo central en verde esmeralda brillante (#10b981)
    cx, cy = tamano * 0.50, tamano * 0.46
    r = tamano * 0.12
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill="#10b981", outline="#ffffff", width=1)

    return img


class TrayManager:
    """
    Controlador del icono en el área de notificación (System Tray).
    Permite operar en segundo plano manteniendo la ventana oculta.
    """

    def __init__(
        self,
        on_mostrar: Callable[[], None],
        on_toggle_centinela: Optional[Callable[[bool], None]] = None,
        on_escanear: Optional[Callable[[], None]] = None,
        on_restaurar_todo: Optional[Callable[[], None]] = None,
        on_salir: Optional[Callable[[], None]] = None,
        centinela_activo_inicial: bool = True,
    ) -> None:
        self.on_mostrar = on_mostrar
        self.on_toggle_centinela = on_toggle_centinela
        self.on_escanear = on_escanear
        self.on_restaurar_todo = on_restaurar_todo
        self.on_salir = on_salir
        self.centinela_activo = centinela_activo_inicial

        self._icon: Optional[pystray.Icon] = None
        self._inicializar_icono()

    def _inicializar_icono(self) -> None:
        imagen = crear_icono_red()
        menu = self._construir_menu()
        self._icon = pystray.Icon(
            name="RedLocalBlock",
            icon=imagen,
            title="RedLocalBlock - Centinela de Red",
            menu=menu,
        )

    def _construir_menu(self) -> pystray.Menu:
        return pystray.Menu(
            pystray.MenuItem("👁️ Mostrar RedLocalBlock", self._accion_mostrar, default=True),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                "🛡️ Modo Centinela",
                self._accion_toggle_centinela,
                checked=lambda item: self.centinela_activo,
            ),
            pystray.MenuItem("🔍 Escanear Red Ahora", self._accion_escanear),
            pystray.MenuItem("🔄 Restaurar Todo (Pánico)", self._accion_restaurar_todo),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("❌ Salir", self._accion_salir),
        )

    def _accion_mostrar(self, icon=None, item=None):
        if self.on_mostrar:
            self.on_mostrar()

    def _accion_toggle_centinela(self, icon=None, item=None):
        self.centinela_activo = not self.centinela_activo
        if self.on_toggle_centinela:
            self.on_toggle_centinela(self.centinela_activo)
        self.actualizar_menu()

    def _accion_escanear(self, icon=None, item=None):
        if self.on_escanear:
            self.on_escanear()

    def _accion_restaurar_todo(self, icon=None, item=None):
        if self.on_restaurar_todo:
            self.on_restaurar_todo()

    def _accion_salir(self, icon=None, item=None):
        if self.on_salir:
            self.on_salir()

    def set_estado_centinela(self, activo: bool) -> None:
        """Actualiza el estado visual del toggle en el menú contextual."""
        self.centinela_activo = activo
        self.actualizar_menu()

    def actualizar_menu(self) -> None:
        """Reconstruye y actualiza dinámicamente el menú del tray."""
        if self._icon:
            try:
                self._icon.menu = self._construir_menu()
                self._icon.update_menu()
            except Exception:
                pass

    def iniciar(self) -> bool:
        """Inicia el icono en la bandeja en modo no bloqueante (detached)."""
        if self._icon:
            try:
                self._icon.run_detached()
                return True
            except Exception:
                return False
        return False

    def detener(self) -> None:
        """Detiene y remueve el icono de la bandeja del sistema."""
        if self._icon:
            try:
                self._icon.stop()
            except Exception:
                pass
            self._icon = None

    def notificar(self, titulo: str, mensaje: str) -> None:
        """
        Emite una notificación emergente nativa de Windows (Toast / Balloon).
        """
        if self._icon:
            try:
                self._icon.notify(message=mensaje, title=titulo)
            except Exception:
                pass
