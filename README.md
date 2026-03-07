# 🤘 Setlist.fm Manager Pro

Ein leistungsstarkes Python-Tool für Konzertliebhaber, um das eigene Konzertarchiv aus Excel mit der **Setlist.fm API** zu synchronisieren, Song-Statistiken zu generieren und ein persönliches Dashboard zu führen.

---

## ✨ Features

* **🔄 Excel-Synchronisation:** Gleicht deine Excel-Liste automatisch mit Setlist.fm ab. 
* **🧠 Intelligenter Sync:** Merkt sich die Anzahl der Zeilen und prüft beim Start nur auf neue Einträge.
* **📊 Interaktives Dashboard:** Übersicht über die Gesamtzahl deiner Konzerte, besuchten Bands, Locations und gehörten Songs.
* **🎵 Song-Analyse:** Wähle eine Band aus einem Dropdown-Menü und sieh sofort, welche Songs du wie oft live gehört hast.
* **📂 Smart CSV Export:** Speichert jede Setlist als saubere CSV-Datei inklusive Artist- und Venue-IDs für spätere Auswertungen.

---

## 🛠 Installation

1.  **Repository klonen oder herunterladen.**
2.  **Abhängigkeiten installieren:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Programm starten:**
    ```bash
    python main.py
    ```

---

## 🚀 Nutzung

1.  **API Key:** Besorge dir einen kostenlosen API-Key auf [Setlist.fm](https://www.setlist.fm/settings/api).
2.  **Konfiguration:** Gib beim ersten Start deinen API-Key an und wähle deine Excel-Datei sowie den Zielordner für die CSVs aus.
3.  **Sync:** Starte die Synchronisation. Das Programm erstellt für jedes Konzert eine detaillierte CSV-Datei.
4.  **Analyse:** Nutze den Tab "Band- & Song-Analyse", um tief in deine Konzert-Historie einzutauchen.

---

## 📁 Dateistruktur

* `main.py`: Die grafische Benutzeroberfläche (Tkinter).
* `logic.py`: Das Herzstück für API-Abfragen und Datenverarbeitung.
* `config_manager.py`: Verwaltung deiner Pfade und Einstellungen.
* `config.ini`: (Lokal) Speichert deine privaten Pfade (wird nicht hochgeladen).

---

## 📝 Voraussetzungen für die Excel-Datei

Deine Excel-Tabelle sollte mindestens folgende Spalten enthalten:
* **Band** (oder Artist/Künstler)
* **Datum** (im Format TT.MM.JJJJ oder ähnlich)

---

**Entwickelt für Musik-Fans, die ihre Live-Erlebnisse digital archivieren wollen.** 🎸