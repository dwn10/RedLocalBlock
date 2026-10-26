"""
Modelo de entidad DispositivoRed y máquina de estados.
Cumple con las restricciones de atomicidad y tipado estricto.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import ipaddress
import re
from typing import Optional


class EstadoDispositivo(Enum):
    """Estados del ciclo de vida de un dispositivo en la red."""
    NORMAL = "Normal"
    AISLADO = "Aislado"
    RESTAURANDO = "Restaurando"


class ActionForbiddenError(Exception):
    """Excepción lanzada cuando se intenta aislar un dispositivo protegido."""
    pass


class InvalidIPError(ValueError):
    """Excepción para direcciones IP con formato incorrecto."""
    pass


@dataclass
class DispositivoRed:
    """
    Entidad que representa un nodo descubierto en la subred local.
    """
    ip: str
    mac: str
    vendor: str = "Desconocido"
    hostname: str = ""
    es_gateway: bool = False
    es_local: bool = False
    estado: EstadoDispositivo = EstadoDispositivo.NORMAL
    primer_visto: datetime = field(default_factory=datetime.now)
    ultimo_visto: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        # Validación rigurosa de formato IPv4
        try:
            ipaddress.IPv4Address(self.ip)
        except ValueError as err:
            raise InvalidIPError(f"Dirección IP no válida: '{self.ip}'") from err

        # Normalización de dirección MAC en mayúsculas
        self.mac = self.mac.upper().strip()
        if not re.match(r"^([0-9A-F]{2}[:-]){5}([0-9A-F]{2})$", self.mac):
            # Si no tiene delimitadores estándar, intentar normalizar
            clean_mac = re.sub(r"[^0-9A-Fa-f]", "", self.mac)
            if len(clean_mac) == 12:
                self.mac = ":".join(clean_mac[i:i+2] for i in range(0, 12, 2)).upper()

    @property
    def es_bloqueable(self) -> bool:
        """Determina si el dispositivo puede ser aislado sin comprometer la infraestructura."""
        return not (self.es_gateway or self.es_local)

    def cambiar_estado(self, nuevo_estado: EstadoDispositivo) -> None:
        """Transición de estado con verificación de invariantes."""
        if nuevo_estado == EstadoDispositivo.AISLADO and not self.es_bloqueable:
            raise ActionForbiddenError(
                f"Acción denegada: La IP {self.ip} está protegida (Gateway/Host Local)."
            )
        self.estado = nuevo_estado
        self.ultimo_visto = datetime.now()

    def registrar_actividad(self) -> None:
        """Actualiza la marca de tiempo de la última detección."""
        self.ultimo_visto = datetime.now()
