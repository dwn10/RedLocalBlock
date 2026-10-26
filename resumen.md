# Resumen Técnico y Documentación: RedLocalBlock (Base PinguExit)

Documento consolidado de análisis estático, inspección de capturas y evaluación arquitectónica para el proceso de ingeniería inversa bajo el protocolo Clean-Room (`001-el-ingeniero-inverso`).

---

## 1. 📌 Ficha Técnica y Descripción General

* **Proyecto Original de Referencia:** PinguExit (`https://github.com/Maalfer/PinguExit`)
* **Nombre del Proyecto Destino:** RedLocalBlock
* **Autor / Licencia:** Darwin Paz / Licencia MIT (2026)
* **Pila Tecnológica Original:**
  * **Lenguaje:** Python 3.x
  * **Manipulación de Paquetes:** `scapy` (`ARP`, `Ether`, `send`, `srp`, `conf`)
  * **Interfaz Gráfica:** `tkinter` estándar + `scrolledtext`
  * **Concurrencia:** `threading.Thread(daemon=True)`
  * **Dependencias listadas:** `scapy`, `uuid` (redundante, nativo en stdlib)
* **Objetivo Declarado:** Herramienta gráfica educativa y de administración local para la auditoría, detección y gestión de acceso de dispositivos en redes locales (Capa 2 / Enlace de datos).

---

## 2. 🖼️ Análisis de Evidencias Gráficas (Capturas)

### Imagen 1: Documentación Conceptual y Consideraciones de Seguridad
* **Interfaz Gráfica Intuitiva:** Reducción de la barrera de entrada técnica de Scapy para usuarios sin conocimientos avanzados de consola.
* **Envío de Paquetes ARP:** Mecanismo central para recopilar pares IP / MAC y auditar el estado de los clientes en la subred.
* **Detección de Intrusos:** Inspección y cotejo de respuestas de red para catalogar dispositivos conocidos frente a sospechosos o no autorizados.
* **Aislamiento / Expulsión de Intrusos:** Envío de tramas ARP para desasociar clientes no permitidos de la puerta de enlace predeterminada.
* **Visualización de Resultados:** Consola y registro en tiempo real de actividad y alertas de intrusión.
* **Aviso de Responsabilidad Ética:** Especificación expresa de uso defensivo, pedagógico y restringido a redes con autorización previa explícita.

### Imagen 2: Interfaz de Usuario y Flujo Operativo Observado
* **Título de Ventana:** "Herramienta de ARP Spoofing"
* **Formulario de Entrada:**
  * Etiqueta: `Ingrese la IP objetivo:`
  * Campo de texto simple (`Entry`): Entrada manual de una dirección IPv4 (Ej. `192.168.223.164`).
* **Acciones / Controles:**
  * Botón `Iniciar ARP Spoofing` (dispara hilo en segundo plano).
  * Botón `Cancelar ARP Spoofing` (intenta detener el bucle).
* **Consola de Salida (`ScrolledText`):**
  * Salida secuencial en texto plano: `Enviando ARP spoofing a 192.168.223.164...` cada 2 segundos.
* **Deficiencia observable en UI:** No existe descubrimiento automático ni lista seleccionable de equipos; el operador debe conocer previamente la IP exacta.

---

## 3. ⚙️ Análisis de Arquitectura y Lógica Interna (`script.py`)

### A. Detección de Parámetros de Red
1. **MAC del Host Local:**
   Calculada mediante manipulación a nivel de bits sobre la función nativa `uuid.getnode()`:
   ```python
   mac_atacante = ':'.join(['{:02x}'.format((uuid.getnode() >> i) & 0xff) for i in range(0, 8*6, 8)][::-1])
   ```
2. **Puerta de Enlace (Gateway):**
   Obtenida ejecutando un pipeline de shell dependiente del subsistema Linux:
   ```python
   gateway = os.popen("ip route | grep default | awk '{print $3}'").read().strip()
   ```

### B. Descubrimiento de Dirección Física (MAC)
* Envía un paquete broadcast de consulta ARP de capa 2 utilizando Scapy:
  ```python
  solicitud_arp = ARP(pdst=ip)
  ether = Ether(dst="ff:ff:ff:ff:ff:ff")
  paquete = ether / solicitud_arp
  resultado = srp(paquete, timeout=2, verbose=0)[0]
  ```

### C. Bucle de Aislamiento / Envenenamiento ARP
* Ejecutado en un hilo secundario con `daemon=True` para evitar que la ventana de Tkinter quede congelada.
* Cada 2 segundos forja y envía dos paquetes de respuesta ARP (`op=2`):
  1. **Hacia la víctima:** Le indica que la IP de la puerta de enlace corresponde a la MAC local.
  2. **Hacia la puerta de enlace:** Le indica que la IP de la víctima corresponde a la MAC local.
* Al carecer el sistema local de reenvío de paquetes activo (IP forwarding deshabilitado), la víctima pierde conectividad efectiva al exterior.

### D. Rutina de Restauración
* Envía 5 ráfagas legítimas (`count=5`) cruzando las direcciones MAC reales de la víctima y del router para reestablecer las tablas ARP legítimas.

---

## 4. ⚠️ Hallazgos Críticos, Defectos y Oportunidades de Mejora

| ID | Área | Problema Detectado en el Original | Impacto | Solución Propuesta para RedLocalBlock |
|:---|:---|:---|:---|:---|
| **BUG-01** | Portabilidad | Llamada a comando Linux `ip route` en `obtener_puerta_enlace()` | Falla fatal e inmediata en Windows y macOS (devuelve cadena vacía). | Utilizar resolución nativa de Scapy: `conf.route.route("0.0.0.0")[2]` o `netifaces`/`psutil`. |
| **BUG-02** | Lógica de Red | `detener_spoofing()` solo cambia la bandera booleana a `False` | La víctima permanece sin conexión durante varios minutos hasta la expiración natural del TTL de la caché ARP. | Invocar automáticamente `restaurar_conexion(ip_objetivo)` dentro de `detener_spoofing()` y al evento de cierre de ventana `WM_DELETE_WINDOW`. |
| **BUG-03** | Thread Safety | El hilo de Scapy manipula directamente widgets de Tkinter (`widget_salida.insert`) | Fallos intermitentes de renderizado, memory leaks o congelamiento del hilo principal GUI. | Despachar actualizaciones a la interfaz mediante cola segura (`queue.Queue`) o `ventana.after()`. |
| **BUG-04** | Dependencias | Inclusión de `uuid` en `requirements.txt` | Innecesario y mala práctica (es módulo estándar de Python desde 2.5). | Limpiar `requirements.txt` dejando únicamente librerías externas necesarias. |
| **BUG-05** | Privilegios | No hay chequeo de permisos de Administrador / root ni presencia de Npcap/WinPcap | En Windows arroja error de socket raw silencioso o bloquea el inicio. | Implementar verificación inicial con `ctypes.windll.shell32.IsUserAnAdmin()` (Windows) / `os.geteuid()` (Unix) con mensaje instructivo. |
| **BUG-06** | UX / Usabilidad | Ingreso manual de dirección IP sin escaneo de red | Experiencia arcaica propensa a errores tipográficos. | Integrar un escáner de red ARP broadcast (`/24`) con presentación en tabla (`Treeview` / `CustomTkinter`). |

---

## 5. 📋 Matriz de Requerimientos y Funcionalidades (Para `features.csv`)

### Priorización MoSCoW para RedLocalBlock:

1. **Must Have (P0 - Crítico):**
   * Detección automática multiplataforma de interfaz de red activa, IP local y Gateway (Windows / Linux).
   * Verificación preventiva de privilegios administrativos antes de ejecutar operaciones de socket raw.
   * Aislamiento controlado de dispositivo específico mediante forjado ARP.
   * Restauración inmediata y garantizada de tablas ARP al detener la acción o salir del programa.
   * Manejo de hilos asíncrono y desacoplado de la interfaz gráfica.

2. **Should Have (P1 - Importante):**
   * Escaneo rápido de la subred local (`x.x.x.0/24`) con tabla de dispositivos: IP, MAC, Fabricante (OUI lookup).
   * Interfaz gráfica moderna con soporte de modo oscuro/claro (migración a `CustomTkinter`).
   * Registro de eventos con marca de tiempo y control de estado (Conectado / Aislado / En Restauración).

3. **Could Have (P2 - Deseable):**
   * Identificación de nombres de host (resolución inversa mDNS / NetBIOS / DNS local).
   * Lista blanca de dispositivos autorizados (para evitar aislamiento accidental del router o del propio equipo).
   * Exportación de inventario de dispositivos a formato CSV o JSON.

4. **Won't Have (Fuera de alcance inicial):**
   * Modificación o inspección de paquetes en tránsito (Man-in-the-Middle con captura de tráfico).
   * Reenvío selectivo de paquetes (IP Forwarding complejo).

---

## 6. 🚀 Plan de Acción para `/001-el-ingeniero-inverso`

1. **Paso 1:** Generar la matriz oficial `features.csv` alineada a los estándares de la habilidad.
2. **Paso 2:** Elaborar el informe técnico completo `REVERSE_ENGINEERING_REPORT.md` bajo directrices Clean-Room.
3. **Paso 3:** Realizar la entrega formal a `01-el-arquitecto` para la concepción de la arquitectura modular y desacoplada de **RedLocalBlock**.
