"""
Pruebas unitarias para el Servicio Centinela (SentinelService).
Verifica la detección pasiva de tramas ARP, filtrado de broadcasts y ciclo de vida.
"""

from unittest.mock import MagicMock, patch
import unittest
from scapy.layers.l2 import ARP

from src.models.device import DispositivoRed
from src.services.sentinel_service import SentinelService


class TestSentinelService(unittest.TestCase):
    """Batería de pruebas de caja blanca para SentinelService."""

    def setUp(self):
        self.ip_gw = "192.168.1.1"
        self.mac_gw = "AA:BB:CC:11:22:33"
        self.ip_local = "192.168.1.100"
        self.mac_local = "DD:EE:FF:44:55:66"

        self.mock_logger = MagicMock()
        self.mock_on_nuevo = MagicMock()
        self.mock_on_visto = MagicMock()

        self.sentinel = SentinelService(
            ip_gateway=self.ip_gw,
            mac_gateway=self.mac_gw,
            ip_local=self.ip_local,
            mac_local=self.mac_local,
            logger=self.mock_logger,
            on_nuevo_dispositivo=self.mock_on_nuevo,
            on_dispositivo_visto=self.mock_on_visto,
        )

    def test_inicializacion_macs_base(self):
        """Verifica que el Gateway y el host local queden registrados como conocidos al inicio."""
        self.assertIn(self.mac_gw, self.sentinel._macs_conocidas)
        self.assertIn(self.mac_local, self.sentinel._macs_conocidas)
        self.assertFalse(self.sentinel.esta_activo)

    def test_agregar_macs_conocidas(self):
        """Valida el registro en lote de direcciones MAC autorizadas."""
        macs = ["00:11:22:33:44:55", "66:77:88:99:AA:BB"]
        self.sentinel.agregar_macs_conocidas(macs)
        for m in macs:
            self.assertIn(m.upper(), self.sentinel._macs_conocidas)

    def test_procesar_paquete_desconocido_dispara_nuevo_dispositivo(self):
        """Simula la captura de un ARP Announcement de un dispositivo nuevo e intruso."""
        # Activar el servicio para procesar tramas
        self.sentinel._activo = True

        pkt = MagicMock()
        pkt.haslayer.return_value = True
        arp_mock = MagicMock(spec=ARP)
        arp_mock.hwsrc = "3C:22:FB:AA:BB:CC"
        arp_mock.psrc = "192.168.1.150"
        pkt.__getitem__.return_value = arp_mock

        with patch("src.services.sentinel_service.OUIService.obtener_fabricante", return_value="Xiaomi"):
            self.sentinel.procesar_paquete_arp(pkt)

        # Debe llamar a on_nuevo_dispositivo
        self.mock_on_nuevo.assert_called_once()
        disp_creado: DispositivoRed = self.mock_on_nuevo.call_args[0][0]
        self.assertEqual(disp_creado.ip, "192.168.1.150")
        self.assertEqual(disp_creado.mac, "3C:22:FB:AA:BB:CC")
        self.assertEqual(disp_creado.vendor, "Xiaomi")

        # La MAC debe haber sido incorporada a las conocidas
        self.assertIn("3C:22:FB:AA:BB:CC", self.sentinel._macs_conocidas)

    def test_procesar_paquete_conocido_dispara_on_visto(self):
        """Una trama ARP proveniente de un equipo ya registrado debe actualizar su timestamp silenciosamente."""
        self.sentinel._activo = True

        pkt = MagicMock()
        pkt.haslayer.return_value = True
        arp_mock = MagicMock(spec=ARP)
        arp_mock.hwsrc = self.mac_gw
        arp_mock.psrc = self.ip_gw
        pkt.__getitem__.return_value = arp_mock

        self.sentinel.procesar_paquete_arp(pkt)

        # No debe alertar como nuevo
        self.mock_on_nuevo.assert_not_called()
        # Debe invocar on_dispositivo_visto
        self.mock_on_visto.assert_called_once_with(self.mac_gw, self.ip_gw)

    def test_filtrado_broadcast_y_direcciones_nulas(self):
        """Trama broadcast o sondas 0.0.0.0 no deben generar falsas alertas de intrusión."""
        self.sentinel._activo = True

        pkt = MagicMock()
        pkt.haslayer.return_value = True
        arp_mock = MagicMock(spec=ARP)
        arp_mock.hwsrc = "FF:FF:FF:FF:FF:FF"
        arp_mock.psrc = "0.0.0.0"
        pkt.__getitem__.return_value = arp_mock

        self.sentinel.procesar_paquete_arp(pkt)

        self.mock_on_nuevo.assert_not_called()
        self.mock_on_visto.assert_not_called()

    def test_ciclo_de_vida_iniciar_y_detener(self):
        """Valida que iniciar y detener modifiquen el estado atómico del servicio."""
        with patch("threading.Thread") as mock_thread:
            iniciado = self.sentinel.iniciar()
            self.assertTrue(iniciado)
            self.assertTrue(self.sentinel.esta_activo)

            # Iniciar nuevamente cuando ya está activo debe retornar False
            self.assertFalse(self.sentinel.iniciar())

            self.sentinel.detener()
            self.assertFalse(self.sentinel.esta_activo)


if __name__ == "__main__":
    unittest.main()
