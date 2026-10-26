"""
Logger thread-safe basado en colas (queue.Queue) para desacoplar el motor de la GUI.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import queue
import sys
from typing import Optional


class NivelLog(Enum):
    """Nivel semántico de un evento de registro."""
    INFO = "INFO"
    ALERT = "ALERT"
    SUCCESS = "SUCCESS"
    WARN = "WARN"
    ERROR = "ERROR"


@dataclass
class EventoLog:
    """Evento estructurado de registro para la consola de auditoría."""
    timestamp: datetime
    nivel: NivelLog
    mensaje: str
    ip_relacionada: Optional[str] = None

    def formatear(self) -> str:
        """Formatea el log con marca temporal y etiqueta de nivel."""
        hora = self.timestamp.strftime("%H:%M:%S")
        ip_txt = f" [{self.ip_relacionada}]" if self.ip_relacionada else ""
        return f"[{hora}] [{self.nivel.value}]{ip_txt} {self.mensaje}"


class AppLogger:
    """Gestor de logs que despacha a una cola para consumo asíncrono en la interfaz gráfica."""

    def __init__(self, cola: Optional[queue.Queue] = None) -> None:
        self.cola = cola if cola is not None else queue.Queue()

    def registrar(self, nivel: NivelLog, mensaje: str, ip: Optional[str] = None) -> EventoLog:
        """Registra un evento, lo coloca en la cola y lo imprime en stdout."""
        evento = EventoLog(
            timestamp=datetime.now(),
            nivel=nivel,
            mensaje=mensaje,
            ip_relacionada=ip
        )
        self.cola.put(evento)
        # Salida en consola de desarrollo
        print(evento.formatear(), file=sys.stdout if nivel != NivelLog.ERROR else sys.stderr)
        return evento

    def info(self, mensaje: str, ip: Optional[str] = None) -> EventoLog:
        return self.registrar(NivelLog.INFO, mensaje, ip)

    def alert(self, mensaje: str, ip: Optional[str] = None) -> EventoLog:
        return self.registrar(NivelLog.ALERT, mensaje, ip)

    def success(self, mensaje: str, ip: Optional[str] = None) -> EventoLog:
        return self.registrar(NivelLog.SUCCESS, mensaje, ip)

    def warn(self, mensaje: str, ip: Optional[str] = None) -> EventoLog:
        return self.registrar(NivelLog.WARN, mensaje, ip)

    def error(self, mensaje: str, ip: Optional[str] = None) -> EventoLog:
        return self.registrar(NivelLog.ERROR, mensaje, ip)
