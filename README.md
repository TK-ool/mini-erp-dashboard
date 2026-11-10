# Mini-ERP und Inventory Management Dashboard

Ein kompakter **Enterprise-Resource-Planning (ERP)** und **Warehouse Management System (WMS)** Prototyp für einen imaginären Getränke-Großhandel.

Dieses Projekt demonstriert das Zusammenspiel aus einer relationalen Datenbankarchitektur, Backend-Logik und einer modernen und interaktiven Web-Benutzeroberfläche.

---
## Features

* **Echtzeit-Inventur:** Der aktuelle Stand der Datenbank kann jederzeit agnezeigt werden, um einen genauen Überblick über den Warenbestand zu erhalten.
* **Wareneinkauf und -verkauf:** Waren können über einen Knpfdruck eingekauft und ausgebucht werden.
* **Historischer Bestandsverlauf:** Bei bestehender Lagerhistorie kann der Verlau eines jedes Produkts eingesehen werden.

---
## Datenmodell (ER-Diagramm)

Das relationale Datenmodell basiert auf der Krähenfuß-Notation. Es wurde über das Tool [databasediagram.com](https://databasediagram.com/app) entwickelt:

![ER-Diagramm](res/database_diagram.png)

---
## Genutzte Technologien

* **Backend & Logik:** Python 3 (inkl. 'sqlite3', 'os')
* **Datenverarbeitung & Anaytics:** Pandas  
* **Datenbank:** SQLite (dateibasierte relationale DB)
* **Frontend / UI:** Streamlit (Interaktives Web-Framework)
* **Grafiken:** databasediagram.com

---
## Installation und Lokaler Start

```bash
py -m streamlit run app.py
```

*Nach wenigen Sekunden öffnet sich das Dashboard automatisch in Ihrem Standard-Browser unter 'http://localhost:8501'*

---
## Datenbank-Architektur im Detail

Um Datenredundanzen und Inkonsistenzen im ERP-System vollständig zu vermeiden, steuert das System die Bestände über zwei zentrale Prinzipien:

1. **Atomare Speicherung:** Der einzige physisch veränderbare Zähler in der Tabelle `produkte` ist `gesamt_flaschen` (die kleinstmögliche logistische Einheit). Einzelflaschenbruch oder Teilmengen führen somit nie zu Rundungsfehlern.
2.  **Transaktions-Logging:** Bestandsveränderungen werden nicht flüchtig überschrieben, sondern zeitscharf in der Tabelle `lager_historie` mitgeschrieben. Der zeitliche Verlauf im Frontend wird performant über die kumulierte Summe (`cumsum()`) des transaktionalen Deltas errechnet.

---
## Roadmap & zukünftige Features

Ich plane dieses Projekt zukünftig stetig weiterzuentwickeln. Die folgenden Ideen möchte ich noch umsetzen:

- [ ] **Login-System nach Rollen:** Absicherung des Dashboards durch ein Login-Menü, welches zwischen Administrator, Logistik-Mitarbeiter und Gast unterscheidet
- [ ] **Erweiterte visuelle Analytics:** Mehr Möglichkeiten sich den Warenbestand im Dashboard anzeigen zu lassen und Trends zu erkennen
- [ ] **Automatisierte Daten-Generierung:** Zu Demo zwecken soll per Knopfdruck eine Lagerhistorie generiert werden können
- [ ] **Cloud Deployment:** Unabhängig von Standort aufrufbar
- [ ] **Interaktives User-Tutorial:** Zu Demo zwecken soll es eine kurze Einleitung in das Dashboard geben
