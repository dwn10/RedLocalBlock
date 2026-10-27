"""
Servicio de escaneo y descubrimiento concurrente de dispositivos en la subred.
"""

from datetime import datetime
import threading
from typing import Callable, Dict, List, Optional

from src.core.network_engine import NetworkEngine
from src.models.device import DispositivoRed, EstadoDispositivo
from src.services.oui_service import OUIService
from src.services.alias_service import AliasService
from src.utils.logger import AppLogger


class ScanService:
    """Escanea la subred local mediante consultas broadcast ARP concurrentes."""

    def __init__(
        self,
        subred_cidr: str,
        ip_gateway: str,
        ip_local: str,
        mac_local: str,
        logger: Optional[AppLogger] = None,
        timeout: float = 2.5,
    ) -> None:
        self.subred_cidr = subred_cidr
        self.ip_gateway = ip_gateway
        self.ip_local = ip_local
        self.mac_local = mac_local
        self.logger = logger or AppLogger()
        self.timeout = timeout

        self._escaneando = False
        self._lock = threading.RLock()
        self._hilo_actual: Optional[threading.Thread] = None

    @property
    def esta_escaneando(self) -> bool:
        with self._lock:
            return self._escaneando

    def iniciar_escaneo_asincrono(
        self,
        on_dispositivo_encontrado: Optional[Callable[[DispositivoRed], None]] = None,
        on_completado: Optional[Callable[[List[DispositivoRed]], None]] = None,
    ) -> bool:
        """
        Lanza el escaneo en un hilo de trabajo independiente para no bloquear la interfaz.
        """
        with self._lock:
            if self._escaneando:
                self.logger.warn("Ya hay un escaneo de red en progreso.")
                return False

            self._escaneando = True
            hilo = threading.Thread(
                target=self._ejecutar_escaneo,
                args=(on_dispositivo_encontrado, on_completado),
                daemon=True,
                name="Worker-Escaneo-Subred"
            )
            self._hilo_actual = hilo
            hilo.start()
            self.logger.info(f"Iniciando escaneo ARP en la subred {self.subred_cidr}...")
            return True

    def _ejecutar_escaneo(
        self,
        on_dispositivo_encontrado: Optional[Callable[[DispositivoRed], None]],
        on_completado: Optional[Callable[[List[DispositivoRed]], None]],
    ) -> None:
        dispositivos: List[DispositivoRed] = []
        try:
            resultados_crudos = NetworkEngine.escanear_subred(
                subred_cidr=self.subred_cidr,
                timeout=self.timeout
            )

            # Si el host local o el gateway no respondieron al broadcast, incluirlos explícitamente
            ips_encontradas = {r[0] for r in resultados_crudos}

            # Procesar hallazgos de red
            for ip, mac in resultados_crudos:
                es_gw = (ip == self.ip_gateway)
                es_loc = (ip == self.ip_local or mac.upper() == self.mac_local.upper())
                fabricante = OUIService.obtener_fabricante(mac)
                alias = AliasService.obtener_alias(mac) or ""

                disp = DispositivoRed(
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
                dispositivos.append(disp)
                if on_dispositivo_encontrado:
                    on_dispositivo_encontrado(disp)

            self.logger.success(
                f"Escaneo finalizado. {len(dispositivos)} dispositivo(s) activos descubiertos en {self.subred_cidr}."
            )

        except Exception as exc:
            self.logger.error(f"Error durante el escaneo de red: {exc}")
        finally:
            with self._lock:
                self._escaneando = False
            if on_completado:
                on_completado(dispositivos)
