"""
Punto de entrada principal (Entry Point) para RedLocalBlock.
Verifica privilegios elevados, detecta la red e inicia la interfaz CustomTkinter.
"""

import sys
import platform

from src.core.permissions import es_administrador, solicitar_elevacion_admin, verificar_entorno_captura
from src.core.system_detector import SystemDetector
from src.ui.app import RedLocalBlockApp


def main():
    """Función de arranque de la aplicación."""
    sistema = platform.system()

    # 1. Comprobación de privilegios de Administrador / Root
    if not es_administrador():
        print(f"[{sistema}] Se requieren privilegios elevados para manipular paquetes ARP a bajo nivel.")
        if sistema == "Windows":
            print("Solicitando elevación de privilegios mediante UAC...")
            despachado = solicitar_elevacion_admin()
            if despachado:
                # El proceso hijo elevado fue lanzado, cerrar el proceso actual
                sys.exit(0)
            else:
                print("No se pudo elevar privilegios. Por favor, ejecuta la aplicación como Administrador.")
                sys.exit(1)
        else:
            print("Por favor, ejecuta la aplicación utilizando 'sudo python -m src.main'.")
            sys.exit(1)

    # 2. Diagnóstico del entorno de captura de red
    disponible, msg_captura = verificar_entorno_captura()
    print(f"[{sistema}] {msg_captura}")

    # 3. Detección automática multiplataforma de la red local
    print("Detectando interfaz activa y puerta de enlace predeterminada...")
    info_red = SystemDetector.detectar_red()
    print(
        f"Red detectada -> Interfaz: '{info_red.nombre_interfaz}' | "
        f"IP Local: {info_red.ip_local} | Gateway: {info_red.ip_gateway} | "
        f"Subred: {info_red.subred_cidr}"
    )

    # 4. Lanzar la interfaz gráfica de usuario
    app = RedLocalBlockApp(info_red=info_red)
    app.mainloop()


if __name__ == "__main__":
    main()
