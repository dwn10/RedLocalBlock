# RedLocalBlock 🛡️

**Herramienta moderna de auditoría, descubrimiento y control de acceso local en Capa 2 (ARP).**  
Desarrollada en Python con **CustomTkinter** y **Scapy** bajo arquitectura Clean-Room.

<p align="center">
  <a href="./Project.md"><img src="https://img.shields.io/badge/Visitar-Arquitectura-blue?style=for-the-badge"></a>
</p>

---


## 🚀 Características Principales

* **Interfaz Gráfica Moderna (CustomTkinter):**
  * Estética Dark Mode (Cyberpunk / Terminal moderna) y Light Mode con alto contraste accesible (WCAG 2.1 AA/AAA).
  * Selector dinámico integral de Modo Claro / Modo Oscuro que actualiza todas las tarjetas, tablas y consola.
  * Escalado automático para pantallas HiDPI y 4K.
* **Descubrimiento Activo de Red (/24) e Identificación Inteligente:**
  * Barrido asíncrono de la subred local mediante consultas ARP sin congelar la ventana.
  * Resolución local de fabricantes por prefijo MAC (OUI de Apple, Samsung, Intel, TP-Link, Espressif, Nintendo, Sony, ARRIS, etc.).
  * Nombres amigables para dispositivos y soporte para asignar **apodos personalizados persistentes** ("✏️ Renombrar Dispositivo") almacenados localmente en `device_aliases.json`.
* **🛡️ Modo Centinela (Sentinel) & Bandeja del Sistema (System Tray):**
  * Escucha pasiva en Capa 2 (0 sobrecarga de red / 0 bytes inyectados) que detecta en tiempo real cuando cualquier dispositivo nuevo o intruso se conecta y emite anuncios ARP (RFC 5227).
  * Notificaciones emergentes nativas de Windows (Toast / Balloon) con IP, MAC y fabricante detectado.
  * Operación silenciosa en segundo plano junto al reloj del sistema con menú contextual (`Mostrar`, `Modo Centinela`, `Escanear`, `Restaurar Todo`, `Salir`).
* **Aislamiento Controlado en Capa 2:**
  * Desasociación selectiva de dispositivos no autorizados mediante forjado ARP (`op=2`).
  * Protección anti-autoaislamiento: el Gateway y la máquina del operador están blindados contra bloqueos accidentales.
* **Reconciliación y Restauración Garantizada:**
  * Reestablecimiento inmediato de las tablas ARP al presionar "Restaurar" (ráfaga de 5 paquetes legítimos).
  * Invocación de emergencia en hooks del sistema (`atexit`) y al cerrar la ventana (`WM_DELETE_WINDOW`).
* **Manual de Uso Interactivo Desplegable (08-popups):**
  * Ventana modal accesible desde el botón `📖 Manual` con acordeones explicativos de cada función del sistema.
* **Pie de Página Estandarizado (02d-el-footer):**
  * Footer con Copyright, año dinámico y atribución enlazada a la agencia desarrolladora **[ECUADOR-IT](https://www.ecuador-it.com/)**.
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

### En Windows (Tres variantes disponibles):

#### 🚀 Opción 1: Lanzador 1-Clic (`Iniciar.bat` - Recomendado)
* **Doble clic** sobre [`Iniciar.bat`](file:///c:/Users/Student/Documents/DEV/RedLocalBlock/Iniciar.bat).
* **Ventajas:** Inicio instantáneo (<0.5 segundos), utiliza `pythonw.exe` sin molestas ventanas negras de consola y solicita elevación de Administrador (UAC) automáticamente si es necesario.

#### 📦 Opción 2: Compilación a Ejecutable Portable (`.exe`)
Si deseas generar un archivo independiente para distribuir o ejecutar sin invocar Python directamente:
1. Haz doble clic en [`compilar_exe.bat`](file:///c:/Users/Student/Documents/DEV/RedLocalBlock/compilar_exe.bat) (o ejecuta `.\compilar_exe.bat` en la terminal).
2. Se generará el binario en `dist/RedLocalBlock.exe` con todas las dependencias (`customtkinter`, `scapy`, etc.) empaquetadas en un único archivo.
> *Nota:* Cualquier equipo donde se ejecute el `.exe` debe tener instalado el driver de captura **Npcap**.

#### 🛠️ Opción 3: Modo Terminal / Desarrollo
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

Para validar la integridad de los modelos, el motor de red, la resolución OUI, el modal y el footer:
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
│   │   ├── network_engine.py       # Creación e inyección de paquetes Scapy (ARP/Ether)
│   │   ├── system_detector.py      # Detección multiplataforma de Gateway, IP y MAC local
│   │   └── permissions.py          # Chequeo preventivo de privilegios Administrador/Root
│   ├── models/                     # Entidades y máquina de estados del dispositivo
│   │   └── device.py               # Modelo DispositivoRed y nombres amigables
│   ├── services/                   # Servicios de red, alias y resolución OUI
│   │   ├── scan_service.py         # Escaneo concurrente de subred /24 con progreso
│   │   ├── sentinel_service.py     # Escucha pasiva en Capa 2 y detección de intrusos (RFC 5227)
│   │   ├── isolation_service.py    # Ciclo de vida de aislamiento y restauración atómica
│   │   ├── oui_service.py          # Identificador de fabricante a partir de MAC OUI
│   │   └── alias_service.py        # Persistencia local de nombres y apodos en JSON
│   ├── ui/                         # CustomTkinter GUI, tema y componentes
│   │   ├── app.py                  # Ventana principal, layout maestro y despachador
│   │   ├── theme.py                # Paleta de colores WCAG (Dark/Light mode)
│   │   └── components/             # Widgets modulares reutilizables
│   │       ├── header_bar.py       # Indicadores de interfaz, Gateway, IP y botón Manual
│   │       ├── device_table.py     # Tabla interactiva con búsqueda en vivo y badges
│   │       ├── control_panel.py    # Botones Escanear, Aislar, Restaurar y Renombrar
│   │       ├── log_console.py      # Consola de auditoría con marcas de tiempo
│   │       ├── status_bar.py       # Métricas de red y selector dinámico de tema
│   │       ├── manual_modal.py     # Manual de usuario interactivo desplegable (08-popups)
│   │       ├── footer.py           # Pie de página estándar con créditos ECUADOR-IT (02d-el-footer)
│   │       └── tray_manager.py     # Integración System Tray y notificaciones nativas Windows
│   └── utils/                      # Utilidades transversales
│       └── logger.py               # Logger thread-safe conectado a Queue de la UI
├── tests/                          # Batería de 25 pruebas unitarias
│   ├── test_device_model.py        # Pruebas de máquina de estados y nombres amigables
│   ├── test_footer.py              # Pruebas del componente AppFooter
│   ├── test_manual_modal.py        # Pruebas de secciones del manual desplegable
│   ├── test_network_engine.py      # Pruebas de forjado de tramas ARP
│   ├── test_oui_service.py         # Pruebas de resolución OUI de fabricantes
│   ├── test_permissions.py         # Pruebas de detección de permisos del sistema
│   ├── test_sentinel_service.py    # Pruebas de escucha pasiva e intercepción de intrusos
│   └── test_tray_manager.py        # Pruebas del gestor de bandeja y renderizado de icono
├── device_aliases.json             # Almacenamiento local persistente de nombres de dispositivos
├── Iniciar.bat                     # Lanzador 1-clic silencioso con auto-elevación UAC
├── compilar_exe.bat                # Script de empaquetado standalone con PyInstaller
├── Branding.md                     # Guía de diseño visual y accesibilidad WCAG
├── Project.md                      # Plano arquitectónico del sistema
├── TODO.md                         # Registro y seguimiento de tareas del proyecto
├── features.csv                    # Matriz de paridad de funcionalidades
├── tokens.json                     # Tokens de diseño semánticos validados con contrast.py
└── requirements.txt                # Dependencias fijadas para producción
```

---

## ⚖️ Licencia y Uso Ético

Distribuido bajo la **Licencia MIT**.  
Esta herramienta fue diseñada con fines **educativos, defensivos y de administración de redes locales**. Su uso está estrictamente restringido a entornos autorizados y de propiedad del usuario.

<br>
<p align="center">
  <a href="./Project.md"><img src="https://img.shields.io/badge/Visitar-Arquitectura-blue?style=for-the-badge"></a>
</p>

---
<br>
<p align="center">
  <small>All rights reserved © 2026 | <a href="https://github.com/dwn10">Darwin Paz</a></small>
</p>

