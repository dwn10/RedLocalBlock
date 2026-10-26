"""
Servicio de control de aislamiento (desasociación ARP) y reconciliación de red.
Asegura la restauración atómica de las tablas ARP ante cualquier interrupción.
"""

import atexit
from datetime import datetime
import signal
import threading
import time
from typing import Callable, Dict, Optional, Set

from src.core.network_engine import NetworkEngine
from src.models.device import DispositivoRed, EstadoDispositivo, ActionForbiddenError
from src.utils.logger import AppLogger


class IsolationService:
    """
    Gestiona el ciclo de vida de los bloqueos de red con garantías de restauración estricta.
    """

    def __init__(
        self,
        ip_gateway: str,
        mac_gateway: str,
        mac_local: str,
        logger: Optional[AppLogger] = None,
        intervalo: float = 2.0,
        conteo_restauracion: int = 5,
    ) -> None:
        self.ip_gateway = ip_gateway
        self.mac_gateway = mac_gateway
        self.mac_local = mac_local
        self.logger = logger or AppLogger()
        self.intervalo = intervalo
        self.conteo_restauracion = conteo_restauracion

        # Control de concurrencia y sesiones activas
        self._lock = threading.RLock()
        self._eventos_parada: Dict[str, threading.Event] = {}
        self._hilos: Dict[str, threading.Thread] = {}
        self._dispositivos_aislados: Dict[str, DispositivoRed] = {}

        # Registro del hook de emergencia para restaurar siempre al terminar el proceso
        atexit.register(self.restaurar_todo)

    def aislar_dispositivo(
        self,
        dispositivo: DispositivoRed,
        on_error: Optional[Callable[[str, str], None]] = None,
    ) -> bool:
        """
        Inicia un hilo en segundo plano que emite periódicamente tramas ARP falsificadas
        hacia el objetivo y la puerta de enlace.
        """
        with self._lock:
            # 1. Validar reglas de protección
            if not dispositivo.es_bloqueable:
                self.logger.warn(
                    f"Intento de aislar dispositivo protegido ({dispositivo.ip}). Acción abortada.",
                    dispositivo.ip
                )
                raise ActionForbiddenError(f"No se puede aislar el dispositivo protegido {dispositivo.ip}.")

            # 2. Idempotencia: Si ya está aislado, no duplicar hilos
            if dispositivo.ip in self._eventos_parada:
                self.logger.info(f"El dispositivo {dispositivo.ip} ya se encuentra aislado.", dispositivo.ip)
                return True

            stop_event = threading.Event()
            self._eventos_parada[dispositivo.ip] = stop_event
            self._dispositivos_aislados[dispositivo.ip] = dispositivo
            dispositivo.cambiar_estado(EstadoDispositivo.AISLADO)

            # 3. Lanzar worker en segundo plano
            hilo = threading.Thread(
                target=self._bucle_aislamiento,
                args=(dispositivo, stop_event, on_error),
                daemon=True,
                name=f"Worker-Aislamiento-{dispositivo.ip}"
            )
            self._hilos[dispositivo.ip] = hilo
            hilo.start()

            self.logger.alert(
                f"Aislamiento iniciado sobre {dispositivo.ip} [{dispositivo.mac}] ({dispositivo.vendor}).",
                dispositivo.ip
            )
            return True

    def detener_aislamiento(self, ip_objetivo: str) -> bool:
        """
        Detiene el envío de paquetes maliciosos y fuerza la reconciliación inmediata de la red.
        """
        with self._lock:
            if ip_objetivo not in self._eventos_parada:
                return False

            stop_event = self._eventos_parada.pop(ip_objetivo)
            stop_event.set()

            dispositivo = self._dispositivos_aislados.pop(ip_objetivo, None)
            hilo = self._hilos.pop(ip_objetivo, None)

            if dispositivo:
                dispositivo.cambiar_estado(EstadoDispositivo.RESTAURANDO)

                # Ejecutar restauración garantizada
                self.logger.info(
                    f"Restaurando tablas ARP para {dispositivo.ip} [{dispositivo.mac}]...",
                    dispositivo.ip
                )
                exito = NetworkEngine.emitir_restauracion(
                    ip_objetivo=dispositivo.ip,
                    mac_objetivo=dispositivo.mac,
                    ip_gateway=self.ip_gateway,
                    mac_gateway=self.mac_gateway,
                    count=self.conteo_restauracion
                )
                if exito:
                    dispositivo.cambiar_estado(EstadoDispositivo.NORMAL)
                    self.logger.success(
                        f"Conexión restaurada exitosamente para {dispositivo.ip}.",
                        dispositivo.ip
                    )
                else:
                    self.logger.error(
                        f"Fallo al emitir paquetes de restauración para {dispositivo.ip}.",
                        dispositivo.ip
                    )

            if hilo and hilo.is_alive():
                hilo.join(timeout=1.0)

            return True

    def restaurar_todo(self) -> None:
        """
        Restaura simultáneamente todos los dispositivos actualmente aislados.
        Garantiza que la red vuelva a su estado normal.
        """
        with self._lock:
            ips = list(self._eventos_parada.keys())
            if not ips:
                return

            self.logger.info(f"Iniciando restauración global de {len(ips)} dispositivos aislados...")
            for ip in ips:
                try:
                    self.detener_aislamiento(ip)
                except Exception as e:
                    self.logger.error(f"Error al restaurar {ip}: {e}", ip)

    def esta_aislado(self, ip: str) -> bool:
        """Consulta si una IP tiene un bucle de aislamiento activo."""
        with self._lock:
            return ip in self._eventos_parada

    def _bucle_aislamiento(
        self,
        dispositivo: DispositivoRed,
        stop_event: threading.Event,
        on_error: Optional[Callable[[str, str], None]] = None,
    ) -> None:
        """Bucle de inyección periódica ejecutado en el hilo de trabajo."""
        conteo_rondas = 0
        try:
            while not stop_event.is_set():
                exito = NetworkEngine.emitir_aislamiento(
                    ip_objetivo=dispositivo.ip,
                    mac_objetivo=dispositivo.mac,
                    ip_gateway=self.ip_gateway,
                    mac_local=self.mac_local,
                )
                conteo_rondas += 1

                if not exito:
                    self.logger.warn(f"Ronda #{conteo_rondas}: Fallo al emitir tramas ARP.", dispositivo.ip)
                else:
                    self.logger.info(
                        f"Ronda #{conteo_rondas}: Envenenamiento ARP activo para {dispositivo.ip}.",
                        dispositivo.ip
                    )

                # Esperar el intervalo o reaccionar de inmediato a la señal de parada
                if stop_event.wait(timeout=self.intervalo):
                    break

        except Exception as exc:
            self.logger.error(f"Excepción en worker de aislamiento: {exc}", dispositivo.ip)
            if on_error:
                on_error(dispositivo.ip, str(exc))
        finally:
            # Asegurar la reconciliación incluso si el bucle falló por excepción
            NetworkEngine.emitir_restauracion(
                ip_objetivo=dispositivo.ip,
                mac_objetivo=dispositivo.mac,
                ip_gateway=self.ip_gateway,
                mac_gateway=self.mac_gateway,
                count=self.conteo_restauracion
            )
            dispositivo.cambiar_estado(EstadoDispositivo.NORMAL)
