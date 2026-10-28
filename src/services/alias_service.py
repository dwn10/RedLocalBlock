"""
Servicio de persistencia de alias y nombres personalizados para dispositivos de red.
Almacena y recupera apodos definidos por el usuario en formato JSON local.
"""

import json
import os
import sys
import threading
from typing import Dict, Optional


class AliasService:
    """Gestiona el almacenamiento local de nombres personalizados para direcciones MAC."""

    _lock = threading.RLock()
    _cache: Optional[Dict[str, str]] = None

    @classmethod
    def _obtener_ruta_archivo(cls) -> str:
        """Determina la ruta de persistencia respetando entornos congelados (.exe PyInstaller)."""
        if getattr(sys, "frozen", False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        return os.path.join(base_dir, "device_aliases.json")

    @classmethod
    def _cargar(cls) -> Dict[str, str]:
        with cls._lock:
            if cls._cache is not None:
                return cls._cache
            ruta = cls._obtener_ruta_archivo()
            if os.path.exists(ruta):
                try:
                    with open(ruta, "r", encoding="utf-8") as f:
                        cls._cache = json.load(f)
                        return cls._cache
                except Exception:
                    pass
            cls._cache = {}
            return cls._cache

    @classmethod
    def _guardar(cls) -> None:
        with cls._lock:
            if cls._cache is None:
                return
            try:
                ruta = cls._obtener_ruta_archivo()
                with open(ruta, "w", encoding="utf-8") as f:
                    json.dump(cls._cache, f, indent=2, ensure_ascii=False)
            except Exception:
                pass

    @classmethod
    def obtener_todos_alias(cls) -> Dict[str, str]:
        """Retorna una copia de todos los alias almacenados."""
        with cls._lock:
            return dict(cls._cargar())

    @classmethod
    def obtener_alias(cls, mac: str) -> Optional[str]:
        """Obtiene el nombre personalizado para una MAC dada."""
        if not mac:
            return None
        mac_norm = mac.upper().strip()
        datos = cls._cargar()
        return datos.get(mac_norm)

    @classmethod
    def guardar_alias(cls, mac: str, nombre: str) -> None:
        """Asigna y persiste un nombre personalizado para una MAC."""
        if not mac:
            return
        mac_norm = mac.upper().strip()
        with cls._lock:
            datos = cls._cargar()
            nombre_limpio = nombre.strip()
            if nombre_limpio:
                datos[mac_norm] = nombre_limpio
            else:
                datos.pop(mac_norm, None)
            cls._guardar()

    @classmethod
    def eliminar_alias(cls, mac: str) -> None:
        """Elimina el nombre personalizado de una MAC."""
        cls.guardar_alias(mac, "")
