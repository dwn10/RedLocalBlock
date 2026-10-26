# Reporte de Ingeniería Inversa: RedLocalBlock (Basado en PinguExit)

**Rol:** Especialista Senior en Ingeniería Inversa & Arquitectura Clean-Room  
**Fecha de Análisis:** 2026-10-26  
**Documento de Entrada:** `resumen.md` y evidencias de repositorio base (`script.py`, capturas de pantalla)  
**Licencia de Referencia:** MIT (Darwin Paz)

---

## 1. Resumen Ejecutivo y Alcance

* **Objetivo Analizado:** Aplicación de escritorio `PinguExit` (`script.py`, ~115 LOC, Python + Tkinter + Scapy).
* **Core Loop Identificado:**
  1. Descubrimiento de parámetros locales (IP, Gateway, MAC).
  2. Resolución ARP de la dirección MAC física del objetivo.
  3. Bucle de forjado y transmisión periódica de paquetes ARP de respuesta (`op=2`) para aislar al cliente de la puerta de enlace (Capa 2).
  4. Detención del aislamiento y restauración de las tablas ARP mediante paquetes legítimos.
* **Inventario de Pantallas / Vistas Observadas:**
  * **Vista Única (Monolítica):** Ventana principal de Tkinter con:
    * Campo de entrada de texto manual para IP de destino (`Entry`).
    * Botón de inicio de bucle (`Iniciar ARP Spoofing`).
    * Botón de interrupción (`Cancelar ARP Spoofing`).
    * Área de texto de desplazamiento (`ScrolledText`) con registros crudos secuenciales.

---

## 2. Hallazgos y Flujos de Usuario (Workflows)

### A. Flujo Principal (Happy Path) - Secuencia de Aislamiento y Restauración

```mermaid
sequenceDiagram
    autonumber
    actor Operador as Usuario / Administrador
    participant GUI as Interfaz Gráfica (Tkinter/GUI)
    participant Core as Motor de Red (Scapy Worker)
    participant Target as Dispositivo Objetivo (Víctima)
    participant Router as Gateway (Router Local)

    Operador->>GUI: Inicia la app y suministra IP Objetivo
    GUI->>Core: Inicia hilo de trabajo en segundo plano (daemon)
    Core->>Target: Envío de ARP Request Broadcast (¿Quién tiene la IP?)
    Target-->>Core: Respuesta ARP con MAC física (hwsrc)
    
    rect rgb(30, 40, 60)
        Note over Core,Router: Bucle Periódico de Aislamiento (Cada 2 segundos)
        Core->>Target: ARP Reply falsificado (Gateway IP está en MAC atacante)
        Core->>Router: ARP Reply falsificado (Target IP está en MAC atacante)
        Target--xRouter: Tráfico bloqueado en Capa 2 (Sin enrutamiento a Internet)
        Core-->>GUI: Emite evento de log "Enviando ARP spoofing..."
    end

    Operador->>GUI: Pulsa "Cancelar / Detener"
    GUI->>Core: Cambia bandera a False y ejecuta restauración
    Core->>Target: Ráfaga ARP legítima (Gateway IP en Router MAC, count=5)
    Core->>Router: Ráfaga ARP legítima (Target IP en Target MAC, count=5)
    Note over Target,Router: Tablas ARP reestablecidas; conectividad restaurada
    Core-->>GUI: Log "Conexión restaurada con éxito"
```

### B. Flujos Secundarios y Casos Borde

1. **Fallo en Resolución de MAC del Objetivo:**
   * Si el dispositivo objetivo está apagado, fuera de la subred o protegido contra ARP broadcast, `srp(paquete, timeout=2)` no devuelve respuestas.
   * *Comportamiento Original:* El script emite `"No se pudo obtener la dirección MAC..."` y aborta la ejecución del hilo de trabajo.
2. **Interrupción Forzada o Excepción durante el Envío:**
   * Si ocurre un socket error o excepción de permisos en el bucle `while ataque_en_curso`, el bloque `except` captura el error y llama a `restaurar_conexion(ip_objetivo)`.
3. **Cierre de Ventana con Bucle Activo (Bug de fuga de estado):**
   * Al cerrar la ventana mediante la cruz (`X`), el hilo `daemon=True` se destruye inmediatamente sin emitir paquetes de restauración, dejando la caché ARP de la víctima contaminada.

---

## 3. Modelos de Datos y Contratos de Integración

### A. Estructuras de Datos de Red (Scapy Packet Contracts)

#### 1. Consulta ARP para Descubrimiento de MAC
```python
Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=ip_objetivo)
```
* **Protocolo:** Ethernet II + ARP (RFC 826)
* **Hardware Type:** `1` (Ethernet)
* **Protocol Type:** `0x0800` (IPv4)
* **Hardware Size:** `6` bytes
* **Protocol Size:** `4` bytes
* **Opcode:** `1` (`who-has` / ARP Request)

#### 2. Trama de Desasociación / Aislamiento (Poisoned Reply)
* **Hacia la Víctima:**
  * `op`: `2` (`is-at` / ARP Reply)
  * `pdst`: `ip_objetivo`
  * `hwdst`: `mac_objetivo`
  * `psrc`: `ip_puerta_enlace` (Router)
  * `hwsrc`: `mac_local` (Host del Administrador)
* **Hacia el Router:**
  * `op`: `2` (`is-at` / ARP Reply)
  * `pdst`: `ip_puerta_enlace`
  * `hwdst`: `ff:ff:ff:ff:ff:ff` (o `mac_puerta_enlace`)
  * `psrc`: `ip_objetivo`
  * `hwsrc`: `mac_local`

#### 3. Trama de Reconciliación / Restauración (Clean Reply)
* **Hacia la Víctima:** `psrc=ip_puerta_enlace`, `hwsrc=mac_puerta_enlace_legitima`
* **Hacia el Router:** `psrc=ip_objetivo`, `hwsrc=mac_objetivo_legitima`
* **Multiplicador de Transmisión:** `count=5` para garantizar la sobreescritura de la tabla ARP del switch y clientes.

### B. Modelo de Datos para Dispositivos (`DeviceModel`) en RedLocalBlock

A diferencia del original (que manejaba cadenas sueltas), la versión moderna implementará el siguiente contrato de datos:

```typescript
export interface DispositivoRed {
  ip: string;              // IPv4 (ej. "192.168.1.45")
  mac: string;             // Formato EUI-48 (ej. "00:1A:2B:3C:4D:5E")
  vendor: string;          // Fabricante deducido vía OUI database
  hostname?: string;       // Nombre de host obtenido por mDNS o NetBIOS
  esGateway: boolean;      // Verdadero si coincide con la puerta de enlace
  esHostLocal: boolean;    // Verdadero si es la máquina que corre la app
  estado: 'Normal' | 'Aislado' | 'En Restauración';
  ultimoVisto: Date;       // Timestamp del último paquete observado
}
```

---

## 4. Entrega a `01-El Arquitecto` (Directrices Clean-Room)

### A. Features Must-Have para el Core Loop (Matriz MoSCoW)
* [x] **Detección Automática de Red Multiplataforma:** Detección de Gateway e IP local sin depender de binarios de Linux (`ip route`), compatible nativamente con Windows (`conf.route.route("0.0.0.0")`) y Linux.
* [x] **Validación de Privilegios Elevados:** Verificación de ejecución como Administrador (Windows) o root (Linux) antes de abrir sockets de bajo nivel.
* [x] **Ciclo de Aislamiento y Restauración Garantizada:**
  * Invocación obligatoria de `restaurar_conexion()` al hacer clic en "Detener".
  * Interceptación del evento de cierre de ventana `protocol("WM_DELETE_WINDOW")` para restaurar tablas antes de liberar memoria.
* [x] **Arquitectura Thread-Safe:** Desacople entre el worker de Scapy y la GUI mediante `queue.Queue` y llamadas `root.after()` periódicas.

### B. Propuesta de Stack Moderno para RedLocalBlock

1. **Frontend / GUI:** **`CustomTkinter`**
   * Mantiene la ligereza de Python y Tkinter sin dependencias pesadas de Qt/C++.
   * Proporciona temas modernos (Modo Oscuro/Claro automático), bordes redondeados, tipografías nítidas y componentes interactivos premium.
2. **Motor de Red:** **`Scapy` nativo**
   * Modularizado en una capa de servicio independiente `NetworkService`.
   * Módulo auxiliar para búsqueda de proveedores OUI (`manuf` o diccionario embebido ligero para fabricantes como Apple, Samsung, Intel, etc.).
3. **Módulo de Descubrimiento:**
   * Escaneo rápido de la subred (`/24`) mediante `srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst="192.168.1.0/24"))` en hilo dedicado con barra de progreso.

### C. Puntos Débiles Detectados en el Original a Erradicar

1. **Comando de Shell Hardcodeado:** Eliminar completamente `os.popen("ip route | ...")`.
2. **Falta de Detección de Red:** Reemplazar el campo de texto manual de IP por una tabla interactiva con selección con un clic.
3. **Violación de Concurrencia:** Eliminar el acceso directo a los widgets desde hilos de trabajo.
4. **Dependencias Fantasma:** Remover `uuid` de `requirements.txt`.
5. **Falta de Lista Blanca:** Prohibir explícitamente en la lógica de negocio el aislamiento de la propia IP y del Gateway para prevenir DoS local inadvertido.
