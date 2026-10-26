"""
Pruebas unitarias para las secciones desplegables del manual de usuario (08-popups).
"""

import unittest
from src.ui.components.manual_modal import ManualModal


class TestManualModalData(unittest.TestCase):

    def test_secciones_definidas(self):
        self.assertTrue(len(ManualModal.SECCIONES) >= 5)
        for titulo, contenido in ManualModal.SECCIONES:
            self.assertIsInstance(titulo, str)
            self.assertIsInstance(contenido, str)
            self.assertTrue(len(titulo) > 0)
            self.assertTrue(len(contenido) > 0)


if __name__ == "__main__":
    unittest.main()
