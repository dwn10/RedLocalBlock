"""
Pruebas unitarias para el modelo DispositivoRed y sus invariantes de seguridad.
"""

import unittest
from src.models.device import DispositivoRed, EstadoDispositivo, ActionForbiddenError, InvalidIPError


class TestDispositivoRed(unittest.TestCase):

    def test_creacion_valida(self):
        disp = DispositivoRed(ip="192.168.1.50", mac="aa:bb:cc:dd:ee:ff", vendor="Intel")
        self.assertEqual(disp.ip, "192.168.1.50")
        self.assertEqual(disp.mac, "AA:BB:CC:DD:EE:FF")
        self.assertEqual(disp.estado, EstadoDispositivo.NORMAL)
        self.assertTrue(disp.es_bloqueable)

    def test_ip_invalida_lanza_excepcion(self):
        with self.assertRaises(InvalidIPError):
            DispositivoRed(ip="999.999.999.999", mac="00:11:22:33:44:55")

        with self.assertRaises(InvalidIPError):
            DispositivoRed(ip="texto_no_ip", mac="00:11:22:33:44:55")

    def test_normalizacion_mac_sin_separadores(self):
        disp = DispositivoRed(ip="10.0.0.5", mac="001122334455")
        self.assertEqual(disp.mac, "00:11:22:33:44:55")

    def test_proteccion_gateway_no_aislable(self):
        router = DispositivoRed(
            ip="192.168.1.1",
            mac="00:11:22:33:44:01",
            es_gateway=True,
            vendor="Cisco"
        )
        self.assertFalse(router.es_bloqueable)
        with self.assertRaises(ActionForbiddenError):
            router.cambiar_estado(EstadoDispositivo.AISLADO)

    def test_proteccion_host_local_no_aislable(self):
        host = DispositivoRed(
            ip="192.168.1.100",
            mac="00:11:22:33:44:99",
            es_local=True,
            vendor="Este Equipo"
        )
        self.assertFalse(host.es_bloqueable)
        with self.assertRaises(ActionForbiddenError):
            host.cambiar_estado(EstadoDispositivo.AISLADO)

    def test_transicion_estado_valida(self):
        disp = DispositivoRed(ip="192.168.1.25", mac="00:11:22:33:44:25")
        disp.cambiar_estado(EstadoDispositivo.AISLADO)
        self.assertEqual(disp.estado, EstadoDispositivo.AISLADO)

        disp.cambiar_estado(EstadoDispositivo.NORMAL)
        self.assertEqual(disp.estado, EstadoDispositivo.NORMAL)


    def test_nombre_amigable_prioridad_y_formato(self):
        # 1. Prioridad máxima: alias del usuario
        disp = DispositivoRed(ip="192.168.1.30", mac="70:48:F7:01:DB:F2", vendor="Nintendo", alias="Mi Switch")
        self.assertEqual(disp.nombre_amigable, "Mi Switch")

        # 2. Marca Nintendo
        disp_nintendo = DispositivoRed(ip="192.168.1.30", mac="70:48:F7:01:DB:F2", vendor="Nintendo")
        self.assertEqual(disp_nintendo.nombre_amigable, "Consola Nintendo")

        # 3. Router con marca
        disp_gw = DispositivoRed(ip="192.168.1.1", mac="EC:A9:40:7F:4B:22", vendor="ARRIS / CommScope", es_gateway=True)
        self.assertEqual(disp_gw.nombre_amigable, "Router (ARRIS / CommScope)")

        # 4. Fallback limpio sin 'Genérico / Desconocido'
        disp_desconocido = DispositivoRed(ip="192.168.1.99", mac="00:00:00:11:22:33", vendor="")
        self.assertEqual(disp_desconocido.nombre_amigable, "Dispositivo Red (.99)")


if __name__ == "__main__":

    unittest.main()
