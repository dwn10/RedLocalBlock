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
    alias: str = ""
    es_gateway: bool = False
    es_local: bool = False
    estado: EstadoDispositivo = EstadoDispositivo.NORMAL
    primer_visto: datetime = field(default_factory=datetime.now)
    ultimo_visto: datetime = field(default_factory=datetime.now)

    @property
    def nombre_amigable(self) -> str:
        """Retorna el nombre más descriptivo y amigable para el usuario."""
        if self.alias:
            return self.alias
        if self.hostname:
            return self.hostname
        if self.es_gateway:
            if self.vendor and self.vendor not in ("Desconocido", "Genérico / Desconocido", ""):
                return f"Router ({self.vendor})"
            return "Router Principal (Gateway)"
        if self.es_local:
            import socket
            try:
                host = socket.gethostname()
                return f"{host} (Este Equipo)"
            except Exception:
                return "Este Equipo (PC Local)"
        if self.vendor and self.vendor not in ("Desconocido", "Genérico / Desconocido", ""):
            v_low = self.vendor.lower()
            if "nintendo" in v_low:
                return "Consola Nintendo"
            if "playstation" in v_low or "sony" in v_low:
                return "Consola / Equipo Sony"
            if "xbox" in v_low:
                return "Consola Xbox"
            if "apple" in v_low:
                return "Dispositivo Apple"
            if "samsung" in v_low:
                return "Dispositivo Samsung"
            if "xiaomi" in v_low or "redmi" in v_low:
                return "Dispositivo Xiaomi"
            if "huawei" in v_low:
                return "Dispositivo Huawei"
            if "lg" in v_low:
                return "Dispositivo LG"
            if "amazon" in v_low or "echo" in v_low or "fire" in v_low:
                return "Dispositivo Amazon"
            if "google" in v_low or "nest" in v_low:
                return "Dispositivo Google"
            if "tp-link" in v_low:
                return "Dispositivo TP-Link"
            if "espressif" in v_low or "tuya" in v_low or "iot" in v_low:
                return "Dispositivo IoT / Domótica"
            if "realtek" in v_low:
                return "Equipo de Red Realtek"
            if "intel" in v_low:
                return "Equipo Intel"
            if "microsoft" in v_low:
                return "Equipo Microsoft"
            if "dell" in v_low:
                return "Equipo Dell"
            if "hp" in v_low:
                return "Equipo HP"
            if "lenovo" in v_low:
                return "Equipo Lenovo"
            if "asus" in v_low:
                return "Equipo ASUS"
            return f"Dispositivo {self.vendor}"
        octeto = self.ip.split(".")[-1] if "." in self.ip else self.ip
        return f"Dispositivo Red (.{octeto})"

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
