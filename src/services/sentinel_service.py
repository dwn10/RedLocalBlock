"""
Servicio Centinela (SentinelService) para la escucha pasiva de Capa 2 (ARP).
Detecta dispositivos entrantes en tiempo real mediante ARP Probes y Announcements
(RFC 5227) sin emitir paquetes a la red (0 bytes inyectados).
"""

from datetime import datetime
import threading
import time
from typing import Callable, Iterable, Optional, Set
from scapy.all import ARP, sniff

from src.models.device import DispositivoRed, EstadoDispositivo
from src.services.oui_service import OUIService
from src.services.alias_service import AliasService
from src.utils.logger import AppLogger


class SentinelService:
    """
    Monitor pasivo de red local basado en sniffing continuo de tramas ARP.
    No inyecta tráfico en la red (0 sobrecarga de red).
    """

    def __init__(
        self,
        ip_gateway: str,
        mac_gateway: str,
        ip_local: str,
        mac_local: str,
        iface: Optional[str] = None,
        logger: Optional[AppLogger] = None,
        on_nuevo_dispositivo: Optional[Callable[[DispositivoRed], None]] = None,
        on_dispositivo_visto: Optional[Callable[[str, str], None]] = None,
    ) -> None:
        self.ip_gateway = ip_gateway
        self.mac_gateway = mac_gateway.upper().strip() if mac_gateway else ""
        self.ip_local = ip_local
        self.mac_local = mac_local.upper().strip() if mac_local else ""
        self.iface = iface
        self.logger = logger or AppLogger()
        self.on_nuevo_dispositivo = on_nuevo_dispositivo
        self.on_dispositivo_visto = on_dispositivo_visto

        self._macs_conocidas: Set[str] = set()
        if self.mac_gateway:
            self._macs_conocidas.add(self.mac_gateway)
        if self.mac_local:
            self._macs_conocidas.add(self.mac_local)

        self._activo = False
        self._hilo: Optional[threading.Thread] = None
        self._lock = threading.RLock()

    @property
    def esta_activo(self) -> bool:
        with self._lock:
            return self._activo

    def registrar_mac_conocida(self, mac: str) -> None:
        """Registra una MAC como autorizada/conocida para evitar alertas redundantes."""
        if not mac:
            return
        with self._lock:
            self._macs_conocidas.add(mac.upper().strip())

    def agregar_macs_conocidas(self, macs: Iterable[str]) -> None:
        """Registra un lote de MACs conocidas en memoria."""
        with self._lock:
            for m in macs:
                if m:
                    self._macs_conocidas.add(m.upper().strip())

    def iniciar(self) -> bool:
        """Inicia el hilo trabajador centinela si no está ya en ejecución."""
        with self._lock:
            if self._activo:
                return False
            self._activo = True
            hilo = threading.Thread(
                target=self._bucle_escucha_pasiva,
                daemon=True,
                name="Worker-Centinela-Pasivo",
            )
            self._hilo = hilo
            hilo.start()
            self.logger.info("🛡️ Modo Centinela activado. Escuchando anuncios ARP en Capa 2 (0 bytes emitidos)...")
            return True

    def detener(self) -> None:
        """Detiene de forma segura el hilo trabajador centinela."""
        with self._lock:
            if not self._activo:
                return
            self._activo = False
            self.logger.info("🛡️ Modo Centinela pausado.")

    def _bucle_escucha_pasiva(self) -> None:
        """Bucle de captura con timeouts cortos para responder rápidamente a detener()."""
        while self.esta_activo:
            try:
                # Sniff con timeout de 1 segundo para no congelar el hilo y permitir parada limpia
                kwargs = {
                    "filter": "arp",
                    "store": 0,
                    "timeout": 1.0,
                    "prn": self.procesar_paquete_arp,
                }
                if self.iface:
                    kwargs["iface"] = self.iface

                sniff(**kwargs)
            except Exception as exc:
                if self.esta_activo:
                    # En caso de error transitorio de captura, esperar brevemente y reintentar
                    time.sleep(1.0)

    def procesar_paquete_arp(self, pkt) -> None:
        """Callback invocado por Scapy por cada trama ARP recibida."""
        if not self.esta_activo:
            return

        try:
            if not pkt.haslayer(ARP):
                return

            arp = pkt[ARP]
            hwsrc = getattr(arp, "hwsrc", None)
            psrc = getattr(arp, "psrc", None)

            if not hwsrc or not psrc:
                return

            mac = str(hwsrc).strip().upper()
            ip = str(psrc).strip()

            # Filtrar direcciones no válidas, broadcast o paquetes sonda sin IP origen asignada
            if mac in ("FF:FF:FF:FF:FF:FF", "00:00:00:00:00:00") or not ip or ip == "0.0.0.0":
                return

            with self._lock:
                ya_conocida = mac in self._macs_conocidas

            if ya_conocida:
                # Dispositivo ya registrado: actualizar timestamp en silencio
                if self.on_dispositivo_visto:
                    self.on_dispositivo_visto(mac, ip)
            else:
                # ¡Nuevo dispositivo detectado en la subred!
                with self._lock:
                    self._macs_conocidas.add(mac)

                fabricante = OUIService.obtener_fabricante(mac)
                alias = AliasService.obtener_alias(mac) or ""
                es_gw = (mac == self.mac_gateway or ip == self.ip_gateway)
                es_loc = (mac == self.mac_local or ip == self.ip_local)

                nuevo_disp = DispositivoRed(
                    ip=ip,
                    mac=mac,
                    vendor=fabricante,
                    alias=alias,
                    es_gateway=es_gw,
                    es_local=es_loc,
                    estado=EstadoDispositivo.NORMAL,
                    primer_visto=datetime.now(),
                    ultimo_visto=datetime.now(),
                )

                self.logger.info(
                    f"🚨 [CENTINELA] Nuevo dispositivo detectado: {nuevo_disp.nombre_amigable} ({ip} / {mac})",
                    ip=ip,
                )

                if self.on_nuevo_dispositivo:
                    self.on_nuevo_dispositivo(nuevo_disp)

        except Exception:
            pass
