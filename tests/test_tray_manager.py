"""
Pruebas unitarias para el componente TrayManager y generación de icono.
Verifica la renderización vectorial con Pillow, creación de menús y callbacks.
"""

from unittest.mock import MagicMock, patch
import unittest
from PIL import Image

from src.ui.components.tray_manager import TrayManager, crear_icono_red


class TestTrayManager(unittest.TestCase):
    """Batería de pruebas para la integración con la bandeja del sistema."""

    def test_crear_icono_red_dimensiones_y_formato(self):
        """Valida que crear_icono_red retorne una imagen RGBA válida con las dimensiones solicitadas."""
        img = crear_icono_red(tamano=64)
        self.assertIsInstance(img, Image.Image)
        self.assertEqual(img.size, (64, 64))
        self.assertEqual(img.mode, "RGBA")

    def test_tray_manager_callbacks_menu(self):
        """Verifica que las opciones del menú contextual invoquen sus callbacks correspondientes."""
        mock_mostrar = MagicMock()
        mock_toggle = MagicMock()
        mock_escanear = MagicMock()
        mock_restaurar = MagicMock()
        mock_salir = MagicMock()

        tray = TrayManager(
            on_mostrar=mock_mostrar,
            on_toggle_centinela=mock_toggle,
            on_escanear=mock_escanear,
            on_restaurar_todo=mock_restaurar,
            on_salir=mock_salir,
            centinela_activo_inicial=True,
        )

        self.assertIsNotNone(tray._icon)
        self.assertTrue(tray.centinela_activo)

        # Probar acciones directas del menú
        tray._accion_mostrar()
        mock_mostrar.assert_called_once()

        tray._accion_toggle_centinela()
        self.assertFalse(tray.centinela_activo)
        mock_toggle.assert_called_once_with(False)

        tray._accion_escanear()
        mock_escanear.assert_called_once()

        tray._accion_restaurar_todo()
        mock_restaurar.assert_called_once()

        tray._accion_salir()
        mock_salir.assert_called_once()

    def test_set_estado_centinela(self):
        """Valida que set_estado_centinela actualice el estado y regenere el menú."""
        tray = TrayManager(on_mostrar=MagicMock())
        tray.set_estado_centinela(False)
        self.assertFalse(tray.centinela_activo)
        tray.set_estado_centinela(True)
        self.assertTrue(tray.centinela_activo)

    def test_notificar_y_detener(self):
        """Valida que notificar invoque al método interno y que detener limpie el icono."""
        tray = TrayManager(on_mostrar=MagicMock())
        tray._icon = MagicMock()

        tray.notificar("Título de Prueba", "Mensaje de Prueba")
        tray._icon.notify.assert_called_once_with(
            message="Mensaje de Prueba",
            title="Título de Prueba"
        )

        tray.detener()
        self.assertIsNone(tray._icon)


if __name__ == "__main__":
    unittest.main()
