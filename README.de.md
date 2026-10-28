# RedLocalBlock 🛡️

**Modernes Werkzeug zur Erkennung, Prüfung und Zugriffskontrolle im lokalen Netzwerk auf Schicht 2 (ARP).**  
Entwickelt in Python mit **CustomTkinter** und **Scapy** unter einer strikten Clean-Room-Softwarearchitektur.

<p align="center">
  <strong>Language:</strong>
  <a href="README.md">Español</a> |
  <a href="README.en.md">English</a> |
  <a href="README.de.md">Deutsch</a>
</p>

<p align="center">
  <a href="./Project.md"><img src="https://img.shields.io/badge/Architektur-Besuchen-blue?style=for-the-badge"></a>
</p>

---

## 🚀 Hauptmerkmale

* **Moderne Benutzeroberfläche (CustomTkinter):**
  * Moderner Dark Mode (Cyberpunk / Terminal) und barrierefreier Light Mode nach WCAG 2.1 AA/AAA Kontraststandards.
  * Dynamischer Theme-Umschalter für alle Karten, Tabellen und Protokolle.
  * Automatische Skalierung für HiDPI- und 4K-Bildschirme.
* **Aktive Subnetz-Erkennung (/24) & Intelligente Hardware-Identifikation:**
  * Asynchrone ARP-Subnetz-Scans ohne Einfrieren der Benutzeroberfläche.
  * Lokale Herstellerauflösung über MAC-OUI-Präfixe (Apple, Samsung, Intel, TP-Link, Espressif, Nintendo, Sony, ARRIS usw.).
  * Benutzerfreundliche Gerätenamen mit Unterstützung für dauerhafte Spitznamen ("✏️ Gerät umbenennen"), die lokal in `device_aliases.json` gespeichert werden.
* **🛡️ Sentinel-Modus (Passives Sniffing) & System-Tray-Integration:**
  * Passives Abhören auf Schicht 2 (0 Netzwerk-Overhead / 0 übertragene Bytes), das in Echtzeit erkennt, wenn sich ein neues oder unbekanntes Gerät verbindet und ARP Announcements / Probes (RFC 5227) sendet.
  * Native Windows Toast- / Ballon-Benachrichtigungen mit IP, MAC-Adresse und erkanntem Hersteller.
  * Geräuschloser Hintergrundbetrieb neben der Systemuhr mit Kontextmenü (`Anzeigen`, `Sentinel-Modus`, `Jetzt scannen`, `Alles wiederherstellen`, `Beenden`).
* **Kontrollierte Schicht-2-Isolation:**
  * Selektive Trennung nicht autorisierter Geräte durch gezielte ARP-Antworten (`op=2`).
  * Schutz vor Selbstsperrung: Gateway und lokaler Host sind strikt gegen Isolierung geschützt.
* **Garantierte Atomare Wiederherstellung (Reconciliation):**
  * Sofortige Wiederherstellung der legitimen ARP-Routing-Tabellen beim Klick auf "Wiederherstellen" (Burst von 5 legitimen Paketen).
  * Notfall-Hooks bei Prozessbeendigung (`atexit`) und beim Schließen des Fensters (`WM_DELETE_WINDOW`).
* **Interaktives Aufklappbares Benutzerhandbuch (Akkordeon-Modal):**
  * Direkt über die Schaltfläche `📖 Handbuch` erreichbarer Dialog mit aufklappbaren Anleitungen.
* **Standardisierte Fußzeile:**
  * Footer mit dynamischer Jahresangabe und Verlinkung zur Entwicklungsagentur **[ECUADOR-IT](https://www.ecuador-it.com/)**.
* **Echte Plattformunabhängigkeit (Windows / Linux):**
  * Native Gateway- und IP-Ermittlung ohne Abhängigkeit von Linux-Shell-Befehlen.
  * Vorbeugende Berechtigungsprüfung: Windows UAC-Dialog und Linux Root (`sudo`).
* **Datenschutz und Sicherheit durch Design (DSGVO / TDDDG):**
  * 100% *Local-First*-Betrieb: Keine Telemetrie, keine Cookies, keine Cloud-Abhängigkeiten.
  * Lokale Systemschriftarten ohne externe CDN-Aufrufe.
  * Keine Paketinhalt-Inspektion (kein MitM-Sniffing von Passwörtern oder Nutzdaten).

---

## 📋 Systemanforderungen

* **Python 3.11+**
* **Windows:**
  * Erfordert den **[Npcap 1.90 Installer](https://npcap.com/dist/npcap-1.90.exe)** zur Schicht-2-Paketverarbeitung.
  * *Wichtig bei der Installation:* Die Option **`Install Npcap in WinPcap API-compatible Mode`** aktivieren.
  * Administratorrechte (das Startskript fordert die UAC-Erhöhung automatisch an).
* **Linux:** Erfordert Superuser-Rechte (`sudo`).

---

## 🛠️ Installation

1. **Repository klonen oder herunterladen:**
   ```bash
   git clone https://github.com/dwn10/RedLocalBlock.git
   cd RedLocalBlock
   ```

2. **Virtuelle Umgebung erstellen und aktivieren (empfohlen):**
   ```bash
   python -m venv venv
   # Unter Windows:
   .\venv\Scripts\activate
   # Unter Linux:
   source venv/bin/activate
   ```

3. **Offizielle Abhängigkeiten installieren:**
   ```bash
   pip install -r requirements.txt
   ```

---

## 💻 Verwendung

### Unter Windows (Drei verfügbare Varianten):

#### 🚀 Option 1: 1-Klick-Starter (`Iniciar.bat` - Empfohlen)
* **Doppelklick** auf `Iniciar.bat`.
* **Vorteile:** Sofortiger Start (<0,5s), läuft geräuschlos über `pythonw.exe` ohne schwarze Konsolenfenster und fordert bei Bedarf automatisch Administratorrechte an.

#### 📦 Option 2: Portable Kompilierung und Ausführung (`.exe`)
Um eine eigenständige ausführbare Datei für die Verteilung ohne Python-Installation zu erstellen:
1. Doppelklick auf `compilar_exe.bat` (oder `.\compilar_exe.bat` im Terminal ausführen).
2. Die Binärdatei wird in `dist/RedLocalBlock.exe` mit allen gebündelten Abhängigkeiten (`customtkinter`, `scapy`, `pystray` usw.) erzeugt.
3. **Ausführen:** Doppelklick auf `dist/RedLocalBlock.exe` und den Windows UAC-Administrator-Dialog bestätigen.
> *Hinweis:* Auf dem Zielrechner muss der Treiber **Npcap** installiert sein.

#### 🛠️ Option 3: Terminal- / Entwicklermodus
Konsole als **Administrator** ausführen:
```bash
python -m src.main
```

### Unter Linux:
Mit Superuser-Rechten starten:
```bash
sudo python -m src.main
```

---

## 🧪 Automatisierte Unit-Tests

Zur Validierung der Netzwerk-Engines, Gerätemodelle, OUI-Auflösung, Modale und System-Tray-Überwachung:
```bash
python -m unittest discover tests
```

---

## 📂 Projektstruktur

```
RedLocalBlock/
├── src/
│   ├── main.py                     # Einstiegspunkt und UAC-/Root-Rechteerhöhung
│   ├── core/                       # Scapy-Engine, Netzwerkdetektor und Berechtigungen
│   │   ├── network_engine.py       # Erstellung & Injektion von ARP/Ethernet-Frames
│   │   ├── system_detector.py      # Plattformunabhängige Gateway-, IP- und MAC-Erkennung
│   │   └── permissions.py          # Vorbeugende Administrator-/Root-Prüfungen
│   ├── models/                     # Entitätsmodelle und Lebenszyklus-Zustandsmaschine
│   │   └── device.py               # DispositivoRed-Modell und Gerätenamenauflösung
│   ├── services/                   # Netzwerkdienste, Aliase und OUI-Auflösung
│   │   ├── scan_service.py         # Asynchroner /24 Subnetz-Scan mit Fortschritt
│   │   ├── sentinel_service.py     # Passives Schicht-2-Sniffing & Eindringlingserkennung
│   │   ├── isolation_service.py    # Isolationslebenszyklus und atomare ARP-Wiederherstellung
│   │   ├── oui_service.py          # Herstellererkennung über MAC-OUI-Präfixe
│   │   └── alias_service.py        # Lokale persistente Namensspeicherung in JSON
│   ├── ui/                         # CustomTkinter GUI, Farbsystem und Komponenten
│   │   ├── app.py                  # Hauptfenster-Layout, Dispatcher und Ereignisschleife
│   │   ├── theme.py                # WCAG 2.1 Farbpalette (Dark/Light Mode)
│   │   └── components/             # Modulare Benutzeroberflächen-Komponenten
│   │       ├── header_bar.py       # Schnittstellen-Indikatoren und Handbuch-Schaltfläche
│   │       ├── device_table.py     # Interaktive Tabelle mit Live-Suche und Status-Badges
│   │       ├── control_panel.py    # Aktionsschaltflächen: Scannen, Isolieren, Tray usw.
│   │       ├── log_console.py      # Echtzeit-Überwachungsprotokoll mit Zeitstempeln
│   │       ├── status_bar.py       # Netzwerkmetriken, Theme-Schalter und Sentinel-Status
│   │       ├── manual_modal.py     # Interaktives Akkordeon-Benutzerhandbuch-Popup
│   │       ├── footer.py           # Standard-Fußzeile mit ECUADOR-IT-Credits
│   │       └── tray_manager.py     # System-Tray-Icon und native Windows-Toast-Meldungen
│   └── utils/                      # Übergreifende Hilfsprogramme
│       └── logger.py               # Threadsicherer Logger mit GUI-Queue
├── tests/                          # Suite von 25 automatisierten Unit-Tests
│   ├── test_device_model.py        # Tests für Zustandsmaschine und Gerätenamen
│   ├── test_footer.py              # Tests für die Fußzeilenkomponente
│   ├── test_manual_modal.py        # Tests für die Handbuch-Akkordeons
│   ├── test_network_engine.py      # Tests für die ARP-Paketerstellung
│   ├── test_oui_service.py         # Tests für die Herstellerauflösung
│   ├── test_permissions.py         # Tests für die Berechtigungsprüfung
│   ├── test_sentinel_service.py    # Tests für passives Sniffing und Alarme
│   └── test_tray_manager.py        # Tests für System-Tray und Icon-Generierung
├── device_aliases.json             # Lokale JSON-Speicherung für Gerätespitznamen
├── Iniciar.bat                     # Geräuschloser 1-Klick-Starter mit Auto-UAC
├── compilar_exe.bat                # Skript zur Erstellung der portablen .exe
├── Branding.md                     # Visuelle Identität und WCAG-Richtlinien
├── Project.md                      # Systemarchitektur-Blaupause
├── TODO.md                         # Projekt-Roadmap und Meilensteine
├── tokens.json                     # Semantische Design-Tokens geprüft mit contrast.py
└── requirements.txt                # Festgelegte Produktionsabhängigkeiten
```

---

## ⚖️ Lizenz und Ethische Nutzung

Veröffentlicht unter der **MIT-Lizenz**.  
Dieses Werkzeug wurde ausschließlich für **didaktische, defensive und administrative Zwecke in lokalen Netzwerken** entwickelt. Die Nutzung ist streng auf Netzwerke beschränkt, die sich im Eigentum des Benutzers befinden oder für die eine ausdrückliche Genehmigung vorliegt.

<br>
<p align="center">
  <a href="./Project.md"><img src="https://img.shields.io/badge/Architektur-Besuchen-blue?style=for-the-badge"></a>
</p>

---
<br>
<p align="center">
  <small>All rights reserved © 2026 | <a href="https://github.com/dwn10">Darwin Paz</a></small>
</p>
