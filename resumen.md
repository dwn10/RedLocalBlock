¿Qué es PinguExit?
Es una herramienta en Python con interfaz gráfica (Tkinter) para realizar ataques de ARP Spoofing / DoS local (corte de conexión a internet a un dispositivo específico dentro de la misma red Wi-Fi o LAN). Es el equivalente minimalista y educativo de herramientas clásicas como NetCut o TuxCut.

El repositorio es muy pequeño y directo:

script.py: Contiene toda la lógica (116 líneas de código).
requirements.txt: Dependencias (scapy, uuid).
README.md: Breve descripción y captura de pantalla.
2. ⚙️ ¿Cómo funciona internamente?
Detección del Gateway (Router): Ejecuta un comando del sistema para extraer la IP de la puerta de enlace predeterminada.
Escaneo de MAC objetivo (obtener_mac): Envía un paquete ARP broadcast (ff:ff:ff:ff:ff:ff) con Scapy a la IP que el usuario escribe en la interfaz para averiguar su dirección física MAC.
Bucle de Envenenamiento ARP (spoofing_arp): En un hilo secundario (threading.Thread), cada 2 segundos envía paquetes ARP falsificados (op=2):
A la víctima le dice que el router tiene la MAC del atacante.
Al router le dice que la víctima tiene la MAC del atacante.
Al no tener habilitado el reenvío de paquetes (IP forwarding), la víctima queda completamente sin acceso a internet.
3. ✅ Aspectos Positivos
Sencillo y directo: Muy didáctico para comprender ataques a nivel de capa 2 (enlace de datos).
Uso de hilos: Implementa threading.Thread(daemon=True) para evitar que la ventana de Tkinter se congele mientras dura el bucle de envío de paquetes.
Función de restauración presente: Tiene codificada la función restaurar_conexion() para enviar paquetes ARP legítimos y devolver las tablas ARP a su estado normal.
4. ⚠️ Errores Críticos y Oportunidades de Mejora
Si quisieras usarlo o mejorarlo, estos son los puntos débiles que tiene actualmente:

1. Incompatibilidad fuera de Linux (Fallo en Windows / macOS)
En la línea 91 obtiene la puerta de enlace así:

python
gateway = os.popen("ip route | grep default | awk '{print $3}'").read().strip()
Esto solo funciona en Linux que tenga iproute2. En Windows o macOS fallará completamente devolviendo un string vacío.
Solución multiplataforma con Scapy nativo:
python
from scapy.all import conf
gateway = conf.route.route("0.0.0.0")[2]
2. El botón "Cancelar" no restaura la red (Bug de usabilidad)
En la función detener_spoofing():

python
def detener_spoofing():
    global ataque_en_curso
    ataque_en_curso = False
    widget_salida.insert(tk.END, "Ataque cancelado.\n")
Solo cambia el flag booleano a False, pero se le olvidó llamar a restaurar_conexion(ip_objetivo).
Consecuencia: Cuando el usuario pulsa "Cancelar ARP Spoofing", la víctima sigue sin internet durante varios minutos hasta que la caché ARP del router/dispositivo caduque sola.
3. uuid en requirements.txt
uuid es un módulo que viene integrado por defecto en la biblioteca estándar de Python desde la versión 2.5. Ponerlo en requirements.txt es redundante.

4. Thread-Safety con Tkinter
El hilo en segundo plano modifica directamente los widgets (widget_salida.insert(...)). En Tkinter esto puede causar condiciones de carrera, errores gráficos o congelamientos esporádicos; lo ideal es despacharlo mediante ventana.after().

5. Requisitos de Privilegios Elevados
Al manipular tramas de red a bajo nivel con Scapy, se requieren permisos de Root / Administrador (y Npcap en Windows). El script no comprueba si el usuario tiene privilegios antes de arrancar.