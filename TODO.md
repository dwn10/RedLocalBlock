# TODO: Lista de Tareas y Estado del Proyecto - RedLocalBlock 🛡️

*Última Actualización: 2026-10-28*

---

## 📊 Estado del Proyecto

**RedLocalBlock** se encuentra en estado **Completado y Listo para Producción**.

El software incluye descubrimiento concurrente de subred `/24`, aislamiento seguro de Capa 2 (ARP) con reconciliación atómica garantizada, sistema inteligente de identificación de dispositivos con soporte para apodos persistentes, manual de uso desplegable (`08-popups`), soporte dinámico integral de Modo Oscuro / Claro y un footer corporativo estándar (`02d-el-footer`) con créditos enlazados a ECUADOR-IT.

---

## ✅ Tareas Ejecutadas

### Fase 0 & 1: Arquitectura
- [x] Plano arquitectónico maestro (`Project.md`) con ERD, flujos Mermaid y mitigación de fallos de red.
- [x] Sistema de diseño y tokens de accesibilidad WCAG 2.1 AA/AAA (`tokens.json` y `Branding.md`).
- [x] Configuración de exclusiones de seguridad e integridad (`.gitignore`, `.env.example`, `requirements.txt`).

### Fase 2: Motor de Red y Capa de Dominio (Core)
- [x] Modelo de dominio estricto `DispositivoRed` con validación IPv4, normalización MAC y máquina de estados.
- [x] Detección de red multiplataforma (`SystemDetector`) para Windows y Linux sin depender de comandos bash.
- [x] Verificación preventiva de elevación UAC en Windows y root en Linux (`Permissions`).
- [x] Motor Scapy de bajo nivel (`NetworkEngine`) con forjado de paquetes ARP `op=1` y `op=2`.
- [x] Ráfagas atómicas de restauración (5 paquetes ARP legítimos) para reconciliación inmediata de tablas.
- [x] Protección anti-autoaislamiento: Gateway y Host local blindados contra bloqueos.

### Fase 3: Servicios de Orquestación y Datos
- [x] Servicio asíncrono de escaneo de subred `/24` sin bloquear el hilo principal (`ScanService`).
- [x] Servicio de aislamiento y restauración atómica con hooks `atexit` y cierre de ventana (`IsolationService`).
- [x] Resolución local de fabricantes por prefijo MAC con más de 40 marcas indexadas (`OUIService`).
- [x] Nombres amigables de dispositivos y persistencia de alias personalizados en JSON (`AliasService` + `device_aliases.json`).

### Fase 4: Interfaz de Usuario y Experiencia (UI/UX)
- [x] Ventana principal responsiva ensamblada en `CustomTkinter` (`app.py`).
- [x] Cabecera interactiva con indicadores de Gateway, IP Local, Interfaz y acceso a Manual (`HeaderBar`).
- [x] Tabla interactiva de dispositivos con búsqueda en vivo y badges de estado (`DeviceTable`).
- [x] Panel de control con botones de Escaneo, Aislamiento, Restauración y botón para Renombrar Dispositivos (`ControlPanel`).
- [x] Consola de auditoría en tiempo real conectada a cola thread-safe (`LogConsole` + `AppLogger`).
- [x] Barra de estado con métricas de red y selector de tema dinámico (`StatusBar`).
- [x] Sistema híbrido completo de Modo Claro y Modo Oscuro con tuplas de color WCAG 2.1 (`src/ui/theme.py`).
- [x] Manual interactivo desplegable con acordeones (Patrón `08-popups` en `ManualModal`).
- [x] Pie de página centrado con año dinámico y atribución enlazada a ECUADOR-IT (Patrón `02d-el-footer` en `AppFooter`).

### Fase 5: Pruebas, Empaquetado y Notificaciones en Segundo Plano
- [x] Batería de 25 pruebas unitarias automatizadas (`tests/` con 100% de aprobación).
- [x] Validación matemática de contraste WCAG con `contrast.py` (0 fallos AA/AAA).
- [x] Verificación en vivo de ejecución de interfaz con Npcap en Windows.
- [x] Script lanzador de doble clic para Windows con auto-elevación UAC sin consola negra (`Iniciar.bat`).
- [x] Script automatizado de compilación a binario portable PyInstaller (`compilar_exe.bat`).
- [x] **Modo Centinela (SentinelService):** Escucha pasiva en Capa 2 (ARP RFC 5227) con 0 sobrecarga de red y detección en tiempo real de nuevos dispositivos.
- [x] **Bandeja del Sistema (TrayManager):** Icono interactivo en la bandeja de Windows con menú contextual, minimizado en segundo plano y notificaciones Toast nativas.

---

## ⏳ Tareas Pendientes (Backlog de Mejoras Futuras)

- [ ] **Exportación de Reportes:** Permitir exportar el inventario de dispositivos y eventos de auditoría a CSV y JSON.
- [ ] **Rango de Subred Personalizado:** Permitir escanear máscaras variables (ej. `/16`, `/23` o rangos CIDR configurables).

---

## 🎯 Siguiente Paso Sugerido (Call to Action)

> **Exportación de Reportes / Auditoría:** Implementar la exportación del inventario de dispositivos y los registros de la consola a archivos CSV y JSON formateados.

