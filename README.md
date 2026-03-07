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

## 🛠 Installation & Start

Es gibt zwei Möglichkeiten, das Programm zu nutzen:

### Option A: Für Anwender (Empfohlen)
1. Lade die neueste `SetlistManagerPro.exe` aus den **[Releases](../../releases)** herunter.
2. Starte die Datei per Doppelklick.
3. **Hinweis zu Windows:** Da die App nicht digital signiert ist, erscheint beim ersten Start evtl. der blaue Warnbildschirm ("Der Computer wurde durch Windows geschützt").
   * Klicke auf **"Weitere Informationen"**.
   * Klicke auf den Button **"Trotzdem ausführen"**.

### Option B: Für Entwickler (Python benötigt)
1. Repository klonen: `git clone https://github.com/DEIN_NAME/Setlist-Manager-Pro.git`
2. Abhängigkeiten installieren: `pip install -r requirements.txt`
3. Starten: `python main.py`

---

## ❓ Problembehandlung (FAQ)

**Frage: Warum erkennt Windows die App als Gefahr an?**
Antwort: Windows SmartScreen blockiert standardmäßig alle ausführbaren Dateien, die keinen registrierten (und kostenpflichtigen) Herausgeber-Stempel haben. Da dies ein Open-Source-Projekt ist, wurde auf ein solches Zertifikat verzichtet. Der Quellcode ist hier auf GitHub jederzeit für jeden einsehbar.

**Frage: Die App startet nicht oder stürzt beim Excel-Lesen ab?**
Antwort: Stelle sicher, dass die Excel-Datei während des Sync-Vorgangs nicht in einem anderen Programm (z.B. Excel selbst) geöffnet ist.

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
