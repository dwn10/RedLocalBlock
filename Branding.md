# Guía de Identidad Visual y Branding: RedLocalBlock

**Rol:** Diseñador UI / Design Engineering & Accesibilidad  
**Estándar de Accesibilidad:** WCAG 2.1 Nivel AA / AAA Certificado (`0 failing AA`)  
**Filosofía:** Design Engineering (Emil Kowalski + Apple HIG) & Seguridad Defensiva  

---

## 1. 🎨 Paleta de Colores Semántica y Accesibilidad (WCAG 2.1)

Los colores han sido seleccionados rigurosamente bajo criterios de alto contraste y estética moderna de herramientas de ciberseguridad (Cyber Dark Mode), validados matemáticamente con `contrast.py`:

```
+--------------------------------------------------------------------------+
|  Color Token       HEX         Rol Semántico                   Contraste |
+--------------------------------------------------------------------------+
|  bg                #0f141c     Fondo principal de la app       -         |
|  surface           #18202c     Tarjetas, contenedores, tablas  -         |
|  surface-hover     #222c3d     Estado hover en filas y paneles -         |
|  border            #293548     Líneas divisorias y contornos   -         |
|  border-input      #64748b     Bordes de campos interactivos   3.88:1 UI |
|  text              #f1f5f9     Texto principal (Slate 100)     16.86:1 AAA|
|  text-muted        #94a3b8     Subtítulos, metadatos, timestamps 7.20:1 AAA|
|  accent            #2563eb     Botón principal (Escanear Red)  5.17:1 AA |
|  on-accent         #ffffff     Texto sobre color accent        -         |
|  danger            #dc2626     Aislamiento / Desasociación     4.83:1 AA |
|  on-danger         #ffffff     Texto sobre botón de peligro    -         |
|  success           #047857     Estado Conectado / Normal       5.48:1 AA |
|  on-success        #ffffff     Texto sobre badge success       -         |
|  warning           #b45309     Badge Gateway / Host Protegido  5.02:1 AA |
|  on-warning        #ffffff     Texto sobre badge warning       -         |
+--------------------------------------------------------------------------+
```

### Resultados de la Auditoría `contrast.py`:
* **9 pares evaluados**, **0 fallos**.
* Textos primarios sobre fondo alcanzan **16.86:1** (superando con holgura el umbral AAA de 7.0:1).
* Textos secundarios alcanzan **7.20:1** (AAA).
* Botones de acción (`accent`, `danger`, `success`, `warning`) cumplen holgadamente el umbral AA (>4.5:1).

---

## 2. 🔤 Tipografía y Cumplimiento de Privacidad (DSGVO / TDDDG)

En cumplimiento estricto con las regulaciones de protección de datos:
* **Cero conexiones externas:** No se realizan peticiones HTTP para descargar fuentes en tiempo de ejecución (prohibido Google Fonts / CDNs).
* **Fuentes Nativas del Sistema:**
  * **Interfaz General (Sans-serif):** `Segoe UI` (Windows), `Inter` / `SF Pro Display` (macOS), `Ubuntu` / `DejaVu Sans` (Linux), con fallback universal a `system-ui`.
  * **Datos Técnicos y Direcciones IP/MAC (Monospace):** `Consolas` (Windows), `Cascadia Code`, `SFMono-Regular`, `Menlo`, con fallback a `monospace`.

### Escala Tipográfica:
* **Display / Título App:** 20px - Bold (`lg`)
* **Cabecera de Secciones:** 16px - SemiBold (`md`)
* **Texto Base / Tablas:** 14px - Regular (`base`)
* **Metadatos y Badges:** 12px - Medium (`sm`)
* **Consola de Logs:** 11px - Regular Monospace (`xs`)

---

## 3. 📐 Sistema de Espaciado y Radios (Grid 8px)

* **Escala de Espaciado:**
  * `xs`: 4px (micro-separaciones)
  * `sm`: 8px (padding interno de celdas)
  * `md`: 12px (separación entre inputs y botones)
  * `lg`: 16px (márgenes de contenedores)
  * `xl`: 24px (espaciado entre secciones)
* **Radios de Borde (`border-radius`):**
  * `sm`: 6px (Badges de estado y tags)
  * `md`: 10px (Campos de entrada, botones de acción)
  * `lg`: 14px (Tarjetas contenedoras principales)
  * `pill`: 999px (Indicadores circulares de conectividad)

---

## 4. ⚡ Principios de Design Engineering & Microinteracciones

1. **Retroalimentación Instantánea (Feedback First):**
   * Al hacer clic en un botón, la respuesta visual debe ser inmediata (cambio de tonalidad activo/presionado sin retrasos).
2. **Jerarquía Visual Clara:**
   * La acción primaria (**Escanear Red**) destaca en azul cobalto (`#2563eb`).
   * La acción destructiva / de aislamiento (**Aislar**) se presenta en rojo crimson (`#dc2626`).
   * La acción pacificadora (**Restaurar Todo**) utiliza tonos neutrales de superficie con borde claro.
3. **Badges de Estado Vivos:**
   * **Conectado / Normal:** Verde esmeralda (`#047857`) con punto de pulso sutil.
   * **Aislado:** Rojo carmesí (`#dc2626`) indicando bloqueo activo en capa 2.
   * **Protegido (Router / Local):** Ámbar dorado (`#b45309`) comunicando que la acción de bloqueo está deshabilitada intencionalmente.
4. **Consola de Auditoría Interactiva:**
   * Fondo diferenciado más oscuro (`#0b0e14`).
   * Colores diferenciados por nivel de evento:
     * `[INFO]` en azul suave (`#60a5fa`).
     * `[ALERT]` en rojo claro (`#f87171`).
     * `[SUCCESS]` en verde menta (`#34d399`).
     * `[WARN]` en amarillo ámbar (`#fbbf24`).
