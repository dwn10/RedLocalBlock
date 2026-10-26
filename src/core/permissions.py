"""
Verificación de privilegios administrativos y entorno de red.
Provee compatibilidad nativa para Windows (UAC / Npcap) y Linux (root).
"""

import ctypes
import os
import platform
import sys
from typing import Tuple


def es_administrador() -> bool:
    """
    Verifica si el proceso actual tiene permisos de Administrador (Windows) o root (Linux/Unix).
    """
    sistema = platform.system()
    try:
        if sistema == "Windows":
            return bool(ctypes.windll.shell32.IsUserAnAdmin() != 0)
        else:
            return os.geteuid() == 0  # type: ignore[attr-defined]
    except Exception:
        return False


def solicitar_elevacion_admin() -> bool:
    """
    En Windows, solicita la elevación de privilegios mediante UAC ejecutando de nuevo el script con 'runas'.
    Retorna True si la llamada de elevación fue despachada.
    """
    if platform.system() != "Windows":
        return False

    if es_administrador():
        return True

    # Despachar elevación UAC en Windows
    params = " ".join([f'"{arg}"' for arg in sys.argv])
    ret = ctypes.windll.shell32.ShellExecuteW(
        None,
        "runas",
        sys.executable,
        params,
        None,
        1  # SW_SHOWNORMAL
    )
    return int(ret) > 32


def verificar_entorno_captura() -> Tuple[bool, str]:
    """
    Comprueba si el subsistema de captura de paquetes (Npcap / WinPcap o AF_PACKET) está disponible.
    """
    sistema = platform.system()
    if sistema == "Windows":
        # Comprobar presencia de Npcap en System32
        system32 = os.path.join(os.environ.get("SystemRoot", "C:\\Windows"), "System32")
        npcap_dll = os.path.join(system32, "wpcap.dll")
        npcap_dir = os.path.join(system32, "Npcap", "wpcap.dll")
        if os.path.exists(npcap_dll) or os.path.exists(npcap_dir):
            return True, "Npcap / WinPcap detectado correctamente."
        return False, "Npcap no detectado. Instala Npcap (https://npcap.com/) en modo compatible WinPcap."
    return True, "Entorno de captura nativo Linux/Unix disponible."
