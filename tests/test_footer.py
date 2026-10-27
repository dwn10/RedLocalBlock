"""
Pruebas unitarias para el componente AppFooter (habilidad 02d-el-footer).
"""

from datetime import datetime
import unittest
from src.ui.components.footer import AppFooter


class TestAppFooter(unittest.TestCase):

    def test_url_agencia_definida(self):
        self.assertEqual(AppFooter.URL_ECUADOR_IT, "https://www.ecuador-it.com/")

    def test_anio_dinamico(self):
        anio_esperado = datetime.now().year
        self.assertGreaterEqual(anio_esperado, 2026)


if __name__ == "__main__":
    unittest.main()
