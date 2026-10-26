"""
Punto de entrada principal (Entry Point) para RedLocalBlock.
Detecta la red e inicia directamente la interfaz gráfica CustomTkinter.
"""

import os
import sys
import platform
import warnings

# Forzar codificación UTF-8 segura en consolas de Windows para evitar UnicodeEncodeError
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# 1. Silenciar warnings cosméticos de deprecación de Scapy / Cryptography
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", message=".*TripleDES.*")
warnings.filterwarnings("ignore", message=".*No libpcap provider available.*")

# 2. Asegurar que la raíz del proyecto esté en sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.core.permissions import es_administrador, verificar_entorno_captura
from src.core.system_detector import SystemDetector
from src.ui.app import RedLocalBlockApp


def main():
    """Función de arranque de la aplicación."""
    sistema = platform.system()
    tiene_admin = es_administrador()

    # 3. Diagnóstico de privilegios de Administrador
    if tiene_admin:
        print(f"[{sistema}] [OK] Privilegios de Administrador confirmados.")
    else:
        print(f"[{sistema}] [INFO] Modo Usuario activo (Para inyección ARP completa, ejecuta PowerShell como Administrador).")

    # 4. Diagnóstico del entorno de captura de red
    disponible_pcap, msg_captura = verificar_entorno_captura()
    print(f"[{sistema}] {msg_captura}")

    # 5. Detección automática multiplataforma de la red local
    print("Detectando interfaz activa y puerta de enlace predeterminada...")
    info_red = SystemDetector.detectar_red()
    print(
        f"Red detectada -> Interfaz: '{info_red.nombre_interfaz}' | "
        f"IP Local: {info_red.ip_local} | Gateway: {info_red.ip_gateway} | "
        f"Subred: {info_red.subred_cidr}"
    )

    # 6. Lanzar la interfaz gráfica de usuario en primer plano
    app = RedLocalBlockApp(info_red=info_red)

    # Mensajes de diagnóstico dentro de la consola interna de la app
    if not tiene_admin:
        app.logger.warn("Iniciado sin permisos de Administrador. Para aislar dispositivos, abre PowerShell como Administrador.")
    if not disponible_pcap and sistema == "Windows":
        app.logger.warn("Npcap no detectado. Si aún no lo has instalado, descárgalo desde https://npcap.com/dist/npcap-1.90.exe")

    app.mainloop()


if __name__ == "__main__":
    main()
