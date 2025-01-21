import streamlit as st
import daten_page
import data_analyse_page
import verwendete_ML_page
import bewertung_ML_page
import Map_Daten
import Home_page  # If you define Home as a separate module or function
import data_distribution

def main():
    pages = {
        "1. Einführung": Home_page.app,  # Assuming you have 'app' function in Home_p.py
        "2. Dateneinblicke": daten_page.app,  # Same assumption for other pages
        "3. Geografische Verteilung": data_distribution.app,  # Same assumption for other pages
        "4. Datenanalyse": data_analyse_page.app#,
        #"5. Verwendete ML": Map_Daten.app
        #"6. Bewertungen ML": bewertung_ML_page.app,
        #"7. Fazit": fazit_page.app
    }

    st.sidebar.title("Navigation")
    if "enable_month" not in st.session_state:
        st.session_state.enable_month = False
    # Set default page to "1. Home"
    page = st.sidebar.radio("Seiten auswählen", list(pages.keys()), index=0)
    if page == "4. Datenanalyse":
        dropdown_options_year =  [None] + list(range(2018,2024))
        dropdown_options_month =  [None] + list(range(1,13))
        #if 'bezirk_map' in st.session_state:
                #bezirk_map = st.session_state.bezirk_map
                #dropdown_options_bezirk = [None] + list(bezirk_map.keys())
                #bezirk = st.sidebar.selectbox("Bezirke:", dropdown_options_bezirk, format_func=lambda x: x if x is not None else "Ein Bezirk auswählen" , index = 0, key #='bezirk')
                #if bezirk is not None and bezirk != st.session_state.bezirk:
                    #st.session_state.bezirk = bezirk
                #st.sidebar.write(f"Ausgewählt Bezirk: {bezirk}")
                
        if dropdown_options_year:
            #year = st.sidebar.selectbox("Jahr:", dropdown_options_year, placeholder="Ein Jahr Auswählen", index = 0)
            year = st.sidebar.selectbox("Jahr:", dropdown_options_year, format_func=lambda x: x if x is not None else "Ein Jahr auswählen" , index = 0, key='year')
            if year is not None and year != st.session_state.year and 'year' in st.session_state:
                #st.write("Bitte wählen Sie das Jahr")
            #else:
                st.session_state.year = year
            st.sidebar.write(f"Ausgewählt Jahr: {year}")
            if year is None:  # If "Ein Jahr auswählen" is selected
                st.session_state.enable_month = False
            else:
                st.session_state.enable_month = True
            
        if dropdown_options_month:
            #month = st.sidebar.selectbox("Monat:", dropdown_options_month, placeholder="Ein Monat Auswählen", index = 0)
            month = st.sidebar.selectbox("Monat:", dropdown_options_month, format_func=lambda x: x if x is not None else "Ein Monat auswählen",index = 0 ,key='month',disabled=not st.session_state.enable_month)
            if month is not None and month != st.session_state.month and 'month' in st.session_state:
                st.session_state.month = month
            st.sidebar.write(f"Ausgewählt Monat: {month}")
       

    # Call the page function for the selected page
    pages[page]()  # Call the appropriate page function

if __name__ == "__main__":
    main()
