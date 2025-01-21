import streamlit as st
import daten_page
import data_analyse_page
import verwendete_ML_page
import bewertung_ML_page
import fazit_page

def main():
    pages = {
        "1. Home" : app,
        "2. Data Überblick" : daten_page,
        "3. Datenanalyse" : data_analyse_page,
        "4. Verwendete ML" : verwendete_ML_page,
        "5. Bewertungen ML" : bewertung_ML_page,
        "6. Fazit" : fazit_page
    }
    
    st.sidebar.title("Navigation")
    
    # Set default page to "1. Home"
    page = st.sidebar.radio("Seiten auswählen", list(pages.keys()), index=0)
    
    # Inhaltsanzeige basierend auf der Auswahl
    if page == "1. Home":
        app()
    elif page == "2. Data Überblick":
        show_data()
    elif page == "3. Datenanalyse":
        show_data_analysis()
    elif page == "4. Verwendete ML":
        show_used_ML()
    elif page == "5. Bewertung ML":
        show_evaluation_ML()
    elif page == "6. Fazit":
        show_fazit()
    
    pages[page].app()

# Inhalt der Home-Seite
def app():
    st.title("Verkehrsdynamik in Berlin: Fahrrad- und Autonutzung im Wandel der Zeit")
    st.info("""Das Projekt analysiert die Fahrrad- und Autonutzung in Berlin, untersucht Einflussfaktoren wie Wetter und Tageszeit und entwickelt Vorhersagemodelle für zukünftige Mobilitätstrends. Ziel ist es, datenbasierte Einblicke für eine nachhaltige Verkehrsplanung zu liefern.""")

def show_data():
    st.title("Dateüberblick")

def show_data_analysis():
    st.title("Datenanalyse")

def show_used_ML():
    st.title("Verwendete ML")
    st.write("Vorhersage-Modell wird geladen...")

def show_evaluation_ML():
    st.title("Bewertung ML")
    st.write("Vorhersage-Modell wird geladen...")

def show_fazit():
    st.title("Fazit")
    st.write("Vorhersage-Modell wird geladen...")

if __name__ == "__main__":
    main()
