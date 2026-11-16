import streamlit as lit
import altair as alt
import sqlite3
import os
import pandas as pd
import random
import time
from datetime import datetime, timedelta

# 1.1 Icon der Webapp
lit.set_page_config(
    page_title="ERP Mini Manager",
    page_icon="res/bottle_image.png",
    layout="wide"
)

# 1.2 Titel der Webapp
lit.title("ERP Mini Retail Manager Dashboard")

# 1.3 Begrüßungsnachricht
lit.write("Willkommen im Logistik- und Stammdaten-Zentrum von Flaschenflug!")

# Ermittelt den absoluten Pfad des aktuellen Ordners, in dem app.py liegt
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "retail_manager.db")

# Flaschen in Kisten
FLASCHEN_PRO_KISTE = 24

# Ab Hier Warnung Fürs Nachbestellen
MINDESTBESTAND_KISTEN = 125 

# Session State initialisieren
if "flaschen" not in lit.session_state:
    lit.session_state.flaschen = 0
if "kisten" not in lit.session_state:
    lit.session_state.kisten = 0

# Hilfsfunktion für Berechnungen Kisten/Flaschen
def update_via_flaschen():
    lit.session_state.kisten = lit.session_state.flaschen/FLASCHEN_PRO_KISTE

def reset_inputs():
    lit.session_state.flaschen = 0
    lit.session_state.kisten = 0

# 2. Hilfsfunktion für Datenbankverbindungen
def run_query(query, params=(), fetch=False):
    #  Verbindung zur vorhandenen SQLite-Datei aufbauen
    # 'with' sorgt dafür, dass die Verbindung am Ende automatisch geschlossen wird
    
    with sqlite3.connect(DB_PATH) as connection:
        cursor = connection.cursor()
    
        #2. SQL-Abfrage ausführen
        cursor.execute(query, params)
    
        #3. Alle Ergebnisse abrufen
        if fetch:
            return cursor.fetchall()
        connection.commit()

# --- BEREICH 1: WARENBESTAND ANZEIGEN ---
lit.header("1. Aktueller Lagerbestand")

# Daten aus der DB holen
produkte = run_query("SELECT produkt_id, name, sku, preis, gesamt_flaschen, flaschen_pro_kiste FROM produkte", fetch=True)

if not produkte:
    lit.info("Keine Produkte in der Datenbank vorhanden.")
else:
    h1, h2, h3, h4, h5 = lit.columns(5)
    h1.markdown("**Produktname**")
    h2.markdown("**Artikelnummer**")
    h3.markdown("**Gebinde (VPE)**")
    h4.markdown("**Bestand (Volle Kisten)**")
    h5.markdown("**Bestand (Anbruch Einzelflaschen)**")
    lit.divider()

    for produkt_id, name, sku, preis, gesamt_flaschen, vpe in produkte:
        volle_kisten = gesamt_flaschen // vpe
        rest_flaschen = gesamt_flaschen % vpe
        
        col1, col2, col3, col4, col5 = lit.columns(5)
        col1.text(name)
        col2.text(sku)
        col3.text(f"{vpe}er Kiste ({preis:.2f} €)")

        # Feedback für volle Kisten
        if volle_kisten < MINDESTBESTAND_KISTEN:
            col4.error(f"{volle_kisten} Kisten (Niedrig!)")
        else:
            col4.success(f"{volle_kisten} Kisten")

        # Angebrochene Kisten
        if rest_flaschen > 0:
            col5.warning(f"{rest_flaschen} Einzelflaschen")
        else:
            col5.text("0 Flaschen Anbruch")
        
lit.divider()


# --- BEREICH 2: INTERAKTIVE LOGIK ---
lit.header("2. ERP-Aktion: Waren bestellen")

# Dropdown-Auswahl aller Produkte generieren
produkt_namen = [p[1] for p in produkte]
ausgewaehltes_produkt = lit.selectbox("Produkt auswaehlen:", produkt_namen, key="produkt_auswahl")

current_vpe = 24
for produkt_id, name, sku, preis, gesamt_flaschen, vpe in produkte:
    if name == ausgewaehltes_produkt:
        current_vpe = vpe
        break


lit.info(f" INFO: {ausgewaehltes_produkt} wird nur in **{current_vpe}er Kisten** verkauft")

neue_kisten = lit.number_input(
    "Anzahl Kisten:",
    min_value = 0,
    value = 0,
    step = 1,
    key="kisten_input"
)

# Funktion zum Einbuchen neuer Waren. Liest Produkt Name aus Eingabefeld und übergibt ihn in die SQL-Query
def buchen():
    produkt_name = lit.session_state.produkt_auswahl
    # Werte aus dem Widget-State holen, nicht aus Variablen außerhalb
    kisten = lit.session_state.kisten_input

    ergebnis = run_query(
        "SELECT produkt_id, gesamt_flaschen, flaschen_pro_kiste FROM produkte WHERE name = ?",
        (produkt_name,), fetch=True
    )

    # SQL-Statement zum Erhöhen des Bestandes
    if ergebnis:
        pid, alte_flaschen, vpe = ergebnis[0]
        zubuchende_flaschen = kisten * vpe

        # Einschreiben in Datenbank
        run_query(
            "UPDATE produkte SET gesamt_flaschen = ? WHERE produkt_id = ?",
            (alte_flaschen + zubuchende_flaschen, pid)
        )

        #Lager Historie updaten
        run_query(
            "INSERT INTO lager_historie (produkt_id, aenderung_flaschen) VALUES (?, ?)",
            (pid, zubuchende_flaschen)
        )
        lit.session_state.buchung_erfolgreich = True
        lit.toast("Daten erfolgreich in das ERP-System verbucht!")

# Funktion zum Ausbuchen von Waren. Liest Produkt Name aus Eingabefeld und übergibt ihn in die SQL-Query
def entfernen():
    produkt_name = lit.session_state.produkt_auswahl
    kisten = lit.session_state.kisten_input

    # Aktuellen Bestand aus DB holen
    ergebnis = run_query(
        "SELECT produkt_id, gesamt_flaschen, flaschen_pro_kiste FROM produkte WHERE name = ?",
        (produkt_name,), fetch=True
    )

    # SQL-Statement zum Verringern des Bestandes
    if ergebnis:
        pid, alte_flaschen, vpe = ergebnis[0]
        zuentfernende_flaschen = kisten * vpe

        # Zu wenig Flaschen auf Lager
        if alte_flaschen - zuentfernende_flaschen < 0:
            lit.toast("So viel ist nicht auf Lager. Bitte nachbestellen!")
            lit.session_state.buchung_erfolgreich = False
        else:
            # Update DB mit niedrigerem Bestand
            run_query(
                "UPDATE produkte SET gesamt_flaschen = ? WHERE produkt_id = ?",
                (alte_flaschen - zuentfernende_flaschen, pid)
            )

            # Update Lager Historie Datenbank
            run_query(
                "INSERT INTO lager_historie (produkt_id, aenderung_flaschen) VALUES (?, ?)",
                (pid, (-zuentfernende_flaschen))
            )
            lit.session_state.buchung_erfolgreich = True
            lit.toast("Daten erfolgreich aus dem ERP System entfernt!")

# Button zum Speichern und löschen in der Datenbank
btn_col1, btn_col2, _ = lit.columns([1, 1, 4])

btn_col1.button("Bestand in DB verbuchen", on_click=buchen)
btn_col2.button("Bestand aus DB entfernen", on_click=entfernen)

if lit.session_state.get("buchung_erfolgreich"):
    lit.session_state.buchung_erfolgreich = False
    lit.rerun()


# --- BEREICH 3: Grafiken ---
lit.header("3. Bestandsverlauf")

if produkte:
    plot_produkt = lit.selectbox("Produkt auswählen", produkt_namen, key = "plot_auswahl")

    plot_id = None
    aktueller_bestand = 0
    for pid, name, sku, preis, gesamt, vpe in produkte:
        if name == plot_produkt:
            plot_id = pid
            aktueller_bestand = gesamt
            break

    historie_raw = run_query(
        "SELECT DATE(zeitstempel), aenderung_flaschen FROM lager_historie WHERE produkt_id = ? ORDER BY zeitstempel ASC",
        (plot_id,), fetch = True
    )

    if not historie_raw:
        lit.info("Noch keine historischen Daten für dieses Produkt vorhanden")
    else:
        # Daten in ein Pandas DataFrame konvertieren
        dataframe = pd.DataFrame(historie_raw, columns=["Datum", "Änderung"])
        
        # Mehrere Buchungen am selben Tag zusammenfassen
        dataframe = dataframe.groupby("Datum", as_index=False)["Änderung"].sum()

        dataframe = dataframe.groupby("Datum", as_index=False)["Änderung"].sum()
        dataframe["Datum"] = pd.to_datetime(dataframe["Datum"])
        dataframe = dataframe.set_index("Datum")

        # Alle Kalendertage von der ersten bis zur letzten Buchung, fehlende = 0 Änderung
        alle_tage = pd.date_range(dataframe.index.min(), dataframe.index.max(), freq="D")
        dataframe = dataframe.reindex(alle_tage, fill_value=0)

        dataframe["Lagerbestand (Flaschen)"] = dataframe["Änderung"].cumsum()
        startwert = aktueller_bestand - dataframe["Änderung"].sum()
        dataframe["Lagerbestand (Flaschen)"] += startwert

        # Hier wird geplottet
        df_plot = dataframe.reset_index().rename(columns={"index": "Datum"})
        chart = alt.Chart(df_plot).mark_line(interpolate="step-after", point=True).encode(
            x=alt.X("Datum:T", title="Datum",
                    axis=alt.Axis(format="%d.%m.", labelAngle=-45, tickCount="day")),
            y=alt.Y("Lagerbestand (Flaschen):Q", title="Lagerbestand (Flaschen)"),
            tooltip=[
                alt.Tooltip("Datum:T", title="Datum", format="%d.%m.%Y"),
                alt.Tooltip("Lagerbestand (Flaschen):Q", title="Bestand")
            ]
        ).interactive()
        lit.altair_chart(chart, use_container_width=True)



# Funktion welche sämtliche Einträge löscht und neue Zufallsdaten generiert
def reset_mit_zufallsdaten(tage=30):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM lager_historie")

        produkte_db = cur.execute(
            "SELECT produkt_id, flaschen_pro_kiste FROM produkte"
        ).fetchall()

        heute = datetime.now()

        for pid, vpe in produkte_db:
            bestand = 0  # in Flaschen

            for tage_zurueck in range(tage, -1, -1):
                buchungsdatum = heute - timedelta(days=tage_zurueck)

                # Sonntags ruht der Betrieb
                if buchungsdatum.weekday() == 6:
                    continue

                buchungszeit = buchungsdatum.replace(
                    hour=random.randint(7, 17), minute=random.randint(0, 59), second=0
                )
                zeit = buchungszeit.strftime("%Y-%m-%d %H:%M:%S")

                kisten_im_lager = bestand // vpe

                if bestand == 0:
                    # Erstbefüllung (erster Werktag im Zeitraum)
                    aenderung = random.randint(150, 300) * vpe

                elif kisten_im_lager < MINDESTBESTAND_KISTEN:
                    # Meldebestand unterschritten -> nachbestellen
                    aenderung = random.randint(150, 250) * vpe

                elif random.random() < 0.3:
                    continue  # an diesem Tag keine Bewegung

                else:
                    # Normaler Warenausgang
                    kisten_raus = min(random.randint(5, 40), kisten_im_lager)
                    aenderung = -kisten_raus * vpe

                bestand += aenderung
                cur.execute(
                    "INSERT INTO lager_historie (produkt_id, aenderung_flaschen, zeitstempel) VALUES (?, ?, ?)",
                    (pid, aenderung, zeit)
                )

            cur.execute(
                "UPDATE produkte SET gesamt_flaschen = ? WHERE produkt_id = ?",
                (bestand, pid)
            )
        conn.commit()


@lit.dialog("Datenbank zurücksetzen")
def reset_dialog():
    lit.warning(
        "**Alle Einträge der Lagerhistorie werden gelöscht** und durch zufällige "
        "Testdaten ersetzt. Die Lagerbestände werden dabei überschrieben. "
        "Das kann nicht rückgängig gemacht werden!"
    )

    # Countdown beim ersten Öffnen, nicht bei späteren Fragment-Reruns
    if not lit.session_state.get("reset_bereit", False):
        platzhalter = lit.empty()
        for sekunden in range(10, 0, -1):
            platzhalter.button(f"Neuen Bestand Generieren ({sekunden}s)", disabled=True, key=f"wait_{sekunden}")
            time.sleep(1)
        platzhalter.empty()
        lit.session_state.reset_bereit = True

    col_ok, col_abbruch = lit.columns(2)

    if col_abbruch.button("Abbrechen"):
        lit.session_state.reset_bereit = False
        lit.rerun()  # schließt den Dialog

    if col_ok.button("Neuen Bestand Generieren", type="primary"):
        reset_mit_zufallsdaten()
        lit.session_state.reset_bereit = False
        lit.session_state.reset_fertig = True
        lit.rerun()  # schließt den Dialog und lädt alles neu

if lit.button("Datenbank zurücksetzen (Testdaten)"):
    lit.session_state.reset_bereit = False
    reset_dialog()

if lit.session_state.pop("reset_fertig", False):
    lit.toast("Datenbank zurückgesetzt, Testdaten erzeugt!")