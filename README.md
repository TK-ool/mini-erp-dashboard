# \# Mini-ERP und Inventory Management Dashboard



Ein kompakter \*\*Enterprise-Resource-Planning (ERP)\*\* und \*\*Warehouse Management System (WMS)\*\* Prototyp für einen imaginären Getränke-Großhandel.

Dieses Projekt demonstriert das Zusammenspiel aus einer relationalen Datenbankarchitektur, Backend-Logik und einer modernen und interaktiven Web-Benutzeroberfläche.



\---



\## Features



* \*\*Echtzeit-Inventur:\*\*
* \*\*Logistisches Gebindemanagement:\*\*
* \*\*Wareneinkauf\*\*
* \*\*Historischer Bestandsverlauf\*\*



\---



\## Datenmodell (ER-Diagramm)



Das relationale Datenmodell basiert auf der Krähenfuß-Notation:



!\[ER-Diagramm](res/database\_diagram.png)



\---



\## Genutzte Technologien



* \*\*Backend \& Logik:\*\* Python 3 (inkl. 'sqlite3', 'os')
* \*\*Datenverarbeitung \& Anaytics:\*\* Pandas  
* \*\*Datenbank:\*\* SQLite (dateibasierte relationale DB)
* \*\*Frontend / UI:\*\* Streamlit (Interaktives Web-Framework)



\---



\## Installation und Lokaler Start



```bash

py -m streamlit run app.py

```



\*Nach wenigen Sekunden öffnet sich das Dashboard automatisch in Ihrem Standard-Browser unter 'http://localhost:8501'.\*



\---



\## Datenbank-Architektur im Detail



Um Datenredundanzen und Inkonsistenzen im ERP-System vollständig zu vermeiden, steuert das System die Bestände über zwei zentrale Prinzipien:

1\.  \*\*Atomare Speicherung:\*\* Der einzige physisch veränderbare Zähler in der Tabelle `produkte` ist `gesamt\_flaschen` (die kleinstmögliche logistische Einheit). Einzelflaschenbruch oder Teilmengen führen somit nie zu Rundungsfehlern.

2\.  \*\*Transaktions-Logging:\*\* Bestandsveränderungen werden nicht flüchtig überschrieben, sondern zeitscharf in der Tabelle `lager\_historie` mitgeschrieben. Der zeitliche Verlauf im Frontend wird performant über die kumulierte Summe (`cumsum()`) des transaktionalen Deltas errechnet.

