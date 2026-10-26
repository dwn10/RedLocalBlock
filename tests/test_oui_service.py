"""
Pruebas unitarias para el servicio de resolución OUI de fabricantes.
"""

import unittest
from src.services.oui_service import OUIService


class TestOUIService(unittest.TestCase):

    def test_fabricantes_conocidos(self):
        # Apple
        self.assertEqual(OUIService.obtener_fabricante("BC:D0:74:11:22:33"), "Apple")
        self.assertEqual(OUIService.obtener_fabricante("bcd074112233"), "Apple")

        # Samsung
        self.assertEqual(OUIService.obtener_fabricante("00:07:AB:44:55:66"), "Samsung")

        # Intel
        self.assertEqual(OUIService.obtener_fabricante("00:02:B3:AA:BB:CC"), "Intel")

        # Microsoft
        self.assertEqual(OUIService.obtener_fabricante("70:1A:B8:F1:11:20"), "Microsoft")

        # Raspberry Pi
        self.assertEqual(OUIService.obtener_fabricante("B8:27:EB:12:34:56"), "Raspberry Pi")

        # Espressif IoT
        self.assertEqual(OUIService.obtener_fabricante("24:0A:C4:00:11:22"), "Espressif IoT")

    def test_fabricante_desconocido(self):
        self.assertEqual(OUIService.obtener_fabricante("00:00:00:11:22:33"), "Genérico / Desconocido")

    def test_mac_vacia_o_invalida(self):
        self.assertEqual(OUIService.obtener_fabricante(""), "Desconocido")
        self.assertEqual(OUIService.obtener_fabricante("12"), "Desconocido")


if __name__ == "__main__":
    unittest.main()
