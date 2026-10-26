# RedLocalBlock 🛡️

**Herramienta moderna de auditoría, descubrimiento y control de acceso local en Capa 2 (ARP).**  
Desarrollada en Python con **CustomTkinter** y **Scapy** bajo arquitectura Clean-Room.

---

## 🚀 Características Principales

* **Interfaz Gráfica Moderna (CustomTkinter):**
  * Estética Dark Mode (Cyberpunk / Terminal moderna) con alto contraste accesible (WCAG 2.1 AA/AAA).
  * Selector dinámico de Modo Claro / Modo Oscuro.
  * Escalado automático para pantallas HiDPI y 4K.
* **Descubrimiento Activo de Red (/24):**
  * Barrido asíncrono de la subred local mediante consultas ARP sin congelar la ventana.
  * Resolución local de fabricantes por prefijo MAC (OUI de Apple, Samsung, Intel, TP-Link, Espressif, etc.).
* **Aislamiento Controlado en Capa 2:**
  * Desasociación selectiva de dispositivos no autorizados mediante forjado ARP (`op=2`).
  * Protección anti-autoaislamiento: el Gateway y la máquina del operador están blindados contra bloqueos accidentales.
* **Reconciliación y Restauración Garantizada:**
  * Reestablecimiento inmediato de las tablas ARP al presionar "Restaurar".
  * Invocación de emergencia en hooks del sistema (`atexit`) y al cerrar la ventana (`WM_DELETE_WINDOW`).
* **Multiplataforma Real (Windows / Linux):**
  * Detección nativa de puerta de enlace predeterminada e IP local sin depender de comandos bash específicos.
  * Verificación preventiva de elevación UAC en Windows y root en Linux.
* **Privacidad y Seguridad por Diseño (DSGVO / TDDDG):**
  * Operación 100% *Local-First* sin telemetría ni envío de datos a servidores externos.
  * Fuentes del sistema locales sin peticiones a CDNs.
  * Cero inspección de contenidos de paquetes (No MITM de contraseñas ni tráfico HTTP/HTTPS).

---

## 📋 Requisitos del Sistema

* **Python 3.11+**
* **Windows:**
  * Requiere el controlador **[Npcap 1.90 installer](https://npcap.com/dist/npcap-1.90.exe)** para manipulación de paquetes en Capa 2.
  * *Importante durante la instalación:* Asegurarse de marcar la casilla **`Install Npcap in WinPcap API-compatible Mode`**.
  * Requiere privilegios de Administrador (el script solicitará elevación automática UAC al iniciar).
* **Linux:** Requiere privilegios de superusuario (`sudo`).

---

## 🛠️ Instalación

1. **Clonar o descargar el repositorio:**
   ```bash
   git clone https://github.com/dwn10/RedLocalBlock.git
   cd RedLocalBlock
   ```

2. **Crear y activar un entorno virtual (recomendado):**
   ```bash
   python -m venv venv
   # En Windows:
   .\venv\Scripts\activate
   # En Linux:
   source venv/bin/activate
   ```

3. **Instalar dependencias oficiales:**
   ```bash
   pip install -r requirements.txt
   ```

---

## 💻 Uso

### En Windows:
Ejecuta la consola como **Administrador** (o permite el diálogo de UAC automático):
```bash
python -m src.main
```

### En Linux:
Ejecuta con privilegios de superusuario:
```bash
sudo python -m src.main
```

---

## 🧪 Ejecución de Pruebas Unitarias

Para validar la integridad de los modelos, el motor de red y la resolución OUI:
```bash
python -m unittest discover tests
```

---

## 📂 Estructura del Proyecto

```
RedLocalBlock/
├── src/
│   ├── main.py                     # Entry point y elevación UAC/root
│   ├── core/                       # Motor Scapy, detector de red y permisos
│   ├── models/                     # Entidades y máquina de estados del dispositivo
│   ├── services/                   # Escaneo /24, aislamiento y OUI lookup
│   ├── ui/                         # CustomTkinter GUI, tema y componentes
│   └── utils/                      # Logger thread-safe con cola asíncrona
├── tests/                          # Batería de pruebas unitarias
├── Branding.md                     # Guía de diseño visual y accesibilidad WCAG
├── Project.md                      # Plano arquitectónico del sistema
├── features.csv                    # Matriz de paridad de funcionalidades
├── tokens.json                     # Tokens de diseño semánticos
└── requirements.txt                # Dependencias fijadas para producción
```

---

## ⚖️ Licencia y Uso Ético

Distribuido bajo la **Licencia MIT**.  
Esta herramienta fue diseñada con fines **educativos, defensivos y de administración de redes locales**. Su uso está estrictamente restringido a entornos autorizados y de propiedad del usuario.
