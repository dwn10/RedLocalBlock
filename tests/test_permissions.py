"""
Pruebas unitarias para el módulo de permisos.
"""

import unittest
from src.core.permissions import es_administrador, verificar_entorno_captura


class TestPermissions(unittest.TestCase):

    def test_tipo_retorno_es_administrador(self):
        resultado = es_administrador()
        self.assertIsInstance(resultado, bool)

    def test_verificar_entorno_captura(self):
        disponible, msg = verificar_entorno_captura()
        self.assertIsInstance(disponible, bool)
        self.assertIsInstance(msg, str)
        self.assertTrue(len(msg) > 0)


if __name__ == "__main__":
    unittest.main()
