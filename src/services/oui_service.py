"""
Servicio local de resolución de fabricantes (OUI Lookup).
Operación 100% offline sin telemetría ni consumo de APIs externas (DSGVO).
"""

from typing import Dict
import re


class OUIService:
    """Resuelve el nombre del fabricante a partir del prefijo MAC (OUI de 24 bits)."""

    # Base de datos local optimizada de fabricantes comunes
    _OUI_DATABASE: Dict[str, str] = {
        # Apple
        "00:03:93": "Apple", "00:05:02": "Apple", "00:0A:27": "Apple", "00:0A:95": "Apple",
        "00:11:24": "Apple", "00:14:51": "Apple", "00:17:F2": "Apple", "00:1C:B3": "Apple",
        "00:1E:C2": "Apple", "00:23:12": "Apple", "00:25:00": "Apple", "00:26:08": "Apple",
        "28:CF:E9": "Apple", "34:36:3B": "Apple", "3C:07:54": "Apple", "40:6C:8F": "Apple",
        "50:BC:96": "Apple", "68:96:7B": "Apple", "70:EF:00": "Apple", "7C:04:D0": "Apple",
        "84:38:35": "Apple", "98:01:A7": "Apple", "A4:83:E7": "Apple", "BC:D0:74": "Apple",
        "DC:A9:04": "Apple", "F0:18:98": "Apple", "F4:0F:24": "Apple", "F8:FF:C2": "Apple",

        # Samsung
        "00:07:AB": "Samsung", "00:12:47": "Samsung", "00:15:99": "Samsung", "00:17:C9": "Samsung",
        "00:1D:25": "Samsung", "00:21:19": "Samsung", "00:23:D7": "Samsung", "08:08:C2": "Samsung",
        "14:49:E0": "Samsung", "30:CD:A7": "Samsung", "44:78:3E": "Samsung", "50:01:D9": "Samsung",
        "78:47:1D": "Samsung", "84:25:DB": "Samsung", "94:63:72": "Samsung", "A0:0B:BA": "Samsung",
        "BC:44:86": "Samsung", "CC:07:AB": "Samsung", "E8:50:8B": "Samsung", "F4:7B:5E": "Samsung",

        # Intel
        "00:02:B3": "Intel", "00:03:47": "Intel", "00:04:23": "Intel", "00:0E:0C": "Intel",
        "00:13:E8": "Intel", "00:1B:21": "Intel", "00:1E:64": "Intel", "00:21:6A": "Intel",
        "00:23:14": "Intel", "08:11:96": "Intel", "34:13:E8": "Intel", "48:51:B7": "Intel",
        "68:05:CA": "Intel", "7C:B0:C2": "Intel", "8C:85:90": "Intel", "A4:4E:31": "Intel",
        "AC:74:B1": "Intel", "C8:5B:76": "Intel", "F8:63:3F": "Intel",

        # Microsoft
        "00:03:FF": "Microsoft", "00:0D:3A": "Microsoft", "00:12:5A": "Microsoft", "00:15:5D": "Microsoft",
        "00:17:FA": "Microsoft", "00:22:48": "Microsoft", "28:18:78": "Microsoft", "60:45:BD": "Microsoft",
        "70:1A:B8": "Microsoft", "7C:ED:8D": "Microsoft", "DC:B4:C4": "Microsoft",

        # TP-Link
        "00:1D:0F": "TP-Link", "00:21:27": "TP-Link", "00:23:CD": "TP-Link", "14:CC:20": "TP-Link",
        "18:A6:F7": "TP-Link", "50:C7:BF": "TP-Link", "60:32:B1": "TP-Link", "74:DA:38": "TP-Link",
        "98:DA:C4": "TP-Link", "B0:4E:26": "TP-Link", "C0:25:E9": "TP-Link", "E8:48:B8": "TP-Link",

        # Huawei / Honor
        "00:1E:10": "Huawei", "00:25:9E": "Huawei", "04:25:C5": "Huawei", "20:08:89": "Huawei",
        "28:6E:D4": "Huawei", "40:4D:8E": "Huawei", "4C:54:99": "Huawei", "70:7B:E8": "Huawei",

        # Xiaomi
        "00:EC:0A": "Xiaomi", "04:CF:8C": "Xiaomi", "18:59:36": "Xiaomi", "28:6C:07": "Xiaomi",
        "34:80:0D": "Xiaomi", "50:64:2B": "Xiaomi", "64:CC:2E": "Xiaomi", "74:23:44": "Xiaomi",

        # Raspberry Pi Foundation
        "28:CD:C1": "Raspberry Pi", "B8:27:EB": "Raspberry Pi", "DC:A6:32": "Raspberry Pi",
        "E4:5F:01": "Raspberry Pi",

        # Espressif (ESP8266 / ESP32 IoT)
        "18:FE:34": "Espressif IoT", "24:0A:C4": "Espressif IoT", "24:62:AB": "Espressif IoT",
        "24:6F:28": "Espressif IoT", "30:AE:A4": "Espressif IoT", "84:0D:8E": "Espressif IoT",
        "A4:CF:12": "Espressif IoT", "CC:50:E3": "Espressif IoT",

        # Cisco
        "00:00:0C": "Cisco", "00:01:42": "Cisco", "00:02:4A": "Cisco", "00:04:4D": "Cisco",
        "00:0C:85": "Cisco", "00:17:59": "Cisco", "00:24:97": "Cisco",

        # Realtek
        "00:07:0E": "Realtek", "00:0C:43": "Realtek", "00:10:A4": "Realtek", "00:14:D1": "Realtek",
        "00:18:4D": "Realtek", "00:E0:4C": "Realtek", "52:54:00": "QEMU/Realtek Virtual",
        "E4:46:B0": "Realtek GbE",

        # Google / Amazon
        "3C:5A:37": "Google Nest", "54:60:09": "Google", "F4:F5:DB": "Google",
        "44:65:0D": "Amazon Echo", "68:54:FD": "Amazon Fire", "AC:63:BE": "Amazon",
    }

    @classmethod
    def obtener_fabricante(cls, mac: str) -> str:
        """
        Deduce el fabricante a partir de los primeros 3 octetos de la MAC.
        Retorna 'Desconocido' si no se encuentra en el diccionario.
        """
        if not mac:
            return "Desconocido"

        # Limpiar y normalizar formato XX:XX:XX
        mac_limpia = re.sub(r"[^0-9A-Fa-f]", "", mac).upper()
        if len(mac_limpia) >= 6:
            prefijo = f"{mac_limpia[0:2]}:{mac_limpia[2:4]}:{mac_limpia[4:6]}"
            return cls._OUI_DATABASE.get(prefijo, "Genérico / Desconocido")

        return "Desconocido"
