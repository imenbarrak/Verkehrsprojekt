
import streamlit as st

def app():
    # Setze einen Titel für die App
    st.title("Vergleich von PKW- und Fahrradnutzung in Berlin  -  Welchen Einfluss haben Zeit- und Wetterfaktoren?")

    # Zeige eine Information mit zusätzlichen Hinweisen zur Bedienung der App
    st.info("""Das Projekt analysiert die Fahrrad- und Autonutzung in Berlin, untersucht Einflussfaktoren wie Wetter und Tageszeit und entwickelt Vorhersagemodelle für zukünftige Mobilitätstrends. Ziel ist es, datenbasierte Einblicke für eine nachhaltige Verkehrsplanung zu liefern.""")
    st.info("Wir haben die Daten aus verschiedenen Quellen exportiert:")

    # Links zu den Datenquellen
    st.markdown("[Fahrrad-Daten](https://daten.berlin.de/datensaetze/radzahldaten-in-berlin)")
    st.markdown("[PKW-Daten](https://api.viz.berlin.de/daten/verkehrsdetektion)")
    st.markdown("[Wetter-Daten](https://open-meteo.com/)")
    
    