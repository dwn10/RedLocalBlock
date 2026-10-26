"""
Detección multiplataforma robusta de la interfaz activa, Gateway y parámetros de red.
Combina Scapy nativo con capas de contingencia para Windows y Linux.
"""

from dataclasses import dataclass
import ipaddress
import os
import platform
import re
import socket
import subprocess
from typing import Optional, Tuple
import uuid

from scapy.all import conf, get_if_hwaddr, ARP, Ether, srp


@dataclass
class InfoRedLocal:
    """Información consolidada de la red local activa."""
    nombre_interfaz: str
    ip_local: str
    mac_local: str
    ip_gateway: str
    mac_gateway: str
    subred_cidr: str


class SystemDetector:
    """Detecta y expone la configuración de red activa del host."""

    @staticmethod
    def obtener_mac_local(iface: Optional[str] = None) -> str:
        """Obtiene la dirección MAC de la máquina local de forma infalible."""
        # 1. Intentar con Scapy
        if iface:
            try:
                mac = get_if_hwaddr(iface)
                if mac and mac != "00:00:00:00:00:00":
                    return mac.upper()
            except Exception:
                pass

        # 2. Fallback estándar con uuid.getnode()
        node = uuid.getnode()
        mac = ":".join(["{:02x}".format((node >> i) & 0xFF) for i in range(0, 8 * 6, 8)][::-1])
        return mac.upper()

    @staticmethod
    def _detectar_gateway_windows() -> Tuple[Optional[str], Optional[str]]:
        """Extrae el Gateway y la IP local desde la tabla de enrutamiento de Windows."""
        try:
            out = subprocess.check_output("route print 0.0.0.0", shell=True, text=True, stderr=subprocess.DEVNULL)
            match = re.search(r"0\.0\.0\.0\s+0\.0\.0\.0\s+(\d+\.\d+\.\d+\.\d+)\s+(\d+\.\d+\.\d+\.\d+)", out)
            if match:
                gw, ip = match.groups()
                if gw != "0.0.0.0":
                    return gw, ip
        except Exception:
            pass
        return None, None

    @staticmethod
    def _detectar_gateway_linux() -> Tuple[Optional[str], Optional[str]]:
        """Extrae el Gateway desde /proc/net/route en sistemas Linux."""
        try:
            with open("/proc/net/route", "r", encoding="utf-8") as f:
                for line in f.readlines()[1:]:
                    parts = line.strip().split()
                    if len(parts) >= 3 and parts[1] == "00000000":
                        # Formato little-endian hex
                        gw_hex = parts[2]
                        gw_ip = socket.inet_ntoa(bytes.fromhex(gw_hex)[::-1])
                        return gw_ip, None
        except Exception:
            pass
        return None, None

    @classmethod
    def detectar_red(cls) -> InfoRedLocal:
        """
        Orquesta la detección completa de la red local aplicando fallbacks progresivos.
        """
        sistema = platform.system()
        ip_gw = None
        ip_local = None
        iface_name = str(conf.iface)

        # Capa 1: Scapy conf.route
        try:
            route_info = conf.route.route("0.0.0.0")
            if route_info and len(route_info) >= 3:
                cand_iface, cand_local, cand_gw = route_info[0], route_info[1], route_info[2]
                if cand_gw and cand_gw != "0.0.0.0":
                    ip_gw = cand_gw
                    ip_local = cand_local
                    iface_name = str(cand_iface)
        except Exception:
            pass

        # Capa 2: Fallback por Sistema Operativo
        if not ip_gw or ip_gw == "0.0.0.0":
            if sistema == "Windows":
                win_gw, win_ip = cls._detectar_gateway_windows()
                if win_gw:
                    ip_gw = win_gw
                    ip_local = win_ip or ip_local
            elif sistema == "Linux":
                lin_gw, lin_ip = cls._detectar_gateway_linux()
                if lin_gw:
                    ip_gw = lin_gw
                    ip_local = lin_ip or ip_local

        # Capa 3: Fallback de IP local mediante socket UDP
        if not ip_local or ip_local == "0.0.0.0":
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                ip_local = s.getsockname()[0]
                s.close()
            except Exception:
                ip_local = "127.0.0.1"

        # Si aún no hay gateway, inferir el .1 de la subred local
        if not ip_gw or ip_gw == "0.0.0.0":
            if ip_local != "127.0.0.1":
                octetos = ip_local.split(".")
                ip_gw = f"{octetos[0]}.{octetos[1]}.{octetos[2]}.1"
            else:
                ip_gw = "127.0.0.1"

        # Calcular Subred CIDR (/24 estándar para redes LAN/Wi-Fi)
        try:
            octetos = ip_local.split(".")
            subred_cidr = f"{octetos[0]}.{octetos[1]}.{octetos[2]}.0/24"
        except Exception:
            subred_cidr = "192.168.1.0/24"

        mac_local = cls.obtener_mac_local(iface_name)

        # Resolver MAC del Gateway (silencioso al arranque)
        mac_gw = cls.resolver_mac(ip_gw, timeout=1.5) or "00:00:00:00:00:00"

        return InfoRedLocal(
            nombre_interfaz=iface_name,
            ip_local=ip_local,
            mac_local=mac_local,
            ip_gateway=ip_gw,
            mac_gateway=mac_gw,
            subred_cidr=subred_cidr,
        )

    @staticmethod
    def resolver_mac(ip: str, timeout: float = 2.0) -> Optional[str]:
        """
        Envía un paquete ARP broadcast para descubrir la dirección MAC física de una IP.
        """
        try:
            solicitud = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=ip)
            respuestas, _ = srp(solicitud, timeout=timeout, verbose=0)
            for _, recibido in respuestas:
                if recibido and hasattr(recibido, "hwsrc"):
                    return str(recibido.hwsrc).upper()
        except Exception:
            pass
        return None
