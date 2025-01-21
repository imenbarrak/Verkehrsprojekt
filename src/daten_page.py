import streamlit as st
import pandas as pd
import os
import sys
import time
import holidays
import numpy as np


sys.path.append(os.path.abspath("../database_scripts"))
import db_utils as du
import create_tables as ct

def convert_time_of_the_day(time):
    time_of_the_day = 0
    if time >= 4 and time < 10 :
        time_of_the_day = 1 #(1,'morgens')
    elif time >= 10 and time < 12:
        time_of_the_day = 2  #(2,'vormittags')
    elif time == 12 :
        time_of_the_day = 3 #(3,'mittags')
    elif time > 12 and time < 17:
        time_of_the_day = 4 #(4,'nachmittags')
    elif time > 17 and time <= 22:
        time_of_the_day = 5 #(5,'abends')      
    else:
        time_of_the_day = 6 #(6,'nachts')
    
    return time_of_the_day

# @st.cache_data
# def load_large_dataframe(filename):
#     return pd.read_csv(filename)

# Hauptfunktion der Streamlit App
def app():
    
    st.header('Datenüberblick')
    st.markdown("""
    Wir haben genau drei Datensätze analysiert: den Fahrradzähler in Berlin, den Messquerschnitt für Autos in Berlin sowie Wetterdaten in Berlin. Die betrachtete Periode erstreckt sich stundenweise von 2018 bis 2023.
    """)
    st.subheader('Messdaten PKWs')
    st.write("Lade Daten... Bitte warten.")

    #df_mess_auto = pd.read_csv('../data/processed/MessDatenAuto.csv')
    df_mess_auto = pd.read_csv('../data/processed/MessDatenAuto.csv')
    progress_bar = st.progress(0)  # Initialize the progress bar
    status_text = st.empty()  # Placeholder for status text

    
    # Simulate the loading process
    for i in range(101):  # Simulate 100 steps
        time.sleep(0.05)  # Simulate loading delay
        progress_bar.progress(i)  # Update progress
        status_text.text(f"Daten geladen: {i}%")

    # Show success message when loading is complete
    st.success("Daten erfolgreich geladen!")
    df_mess_auto.rename(columns={'BREITE_WGS84': 'Breitengrad','LÄNGE_WGS84': 'Längengrad','q_pkw_mq_hr':'Anzahl'},inplace= True)
    df_mess_auto.reset_index(drop=True, inplace=True)
    st.dataframe(df_mess_auto.head())
    st.write(f"Die ursprüngliche Anzahl von PKWs Daten {df_mess_auto.shape}")
    
    st.subheader('Messdaten Fahrräder')
    
    #df_mess_fahrrad = pd.read_csv('../data/processed/MessDatenFahrrad.csv')
    df_mess_fahrrad = pd.read_csv('../data/processed/MessDatenFahrrad.csv')
    df_mess_fahrrad.rename(columns={'Breitengrad_left': 'Breitengrad','Längengrad_left': 'Längengrad','Wert':'Anzahl'}, inplace= True)
    df_mess_fahrrad.reset_index(drop=True, inplace=True)
    st.dataframe(df_mess_fahrrad.head())
    st.write(f"Die ursprüngliche Anzahl von Fahrräder Daten {df_mess_fahrrad.shape}")
    
    
    st.subheader('Wetter Daten')
    df_wetter = pd.read_csv('../data/processed/WetterData.csv')
    df_wetter.rename(columns={'TimeID': 'Time'}, inplace= True)
    st.dataframe(df_wetter.head())
    st.write(f"Die ursprüngliche Anzahl von Wetter Daten {df_wetter.shape}")
    

    st.subheader('Zusammenführung von die daten  basierend auf die Datum, Uhrzeit und den Bezirk')
    df_merged_pkws = df_mess_auto.merge(df_wetter, left_on=['Date','Time','Bezirk'], right_on =['Date','Time','Bezirk'],how='left')
    df_mess_auto.drop(['INBETRIEBNAHME'], axis= 1, inplace = True)
    #st.dataframe(df_merged_pkws.head())
    #st.write(f"Die ursprüngliche Anzahl von Zusammenführuung Daten {df_merged_pkws.shape}")
    
    df_merged_fahrräder = df_mess_fahrrad.merge(df_wetter, left_on=['Date','Time','Bezirk'], right_on =['Date','Time','Bezirk'],how='left')
    #df_merged_fahrräder.drop(['TimeID','time'], axis= 1, inplace = True)
    #st.dataframe(df_merged_fahrräder.head())
    #st.write(f"Die ursprüngliche Anzahl von Zusammenführuung Daten {df_merged_pkws.shape}")
    
    st.write("Da die Datenmenge sehr groß ist, haben wir die Daten aggregiert und die Mittelwerte berechnet, um einen besseren Überblick über ganz Berlin zu erhalten. Nach der Bereinigung und dem Feature Engineering haben wir mit diesen aggregierten Daten weitergearbeitet.")
    
    columns_to_aggregate = [
    'temperature_2m (°C)', 
    'relative_humidity_2m (%)', 
    'rain (mm)', 
    'snowfall (cm)', 
    'cloud_cover (%)'
    ]
    
    #aggregated_df_wetter = pd.read_csv('../data/raw/Bezirke Wetter/Bezirke_Durchschnitt.csv',encoding='ISO-8859-1')
    #aggregated_df_wetter[aggregated_df_wetter.columns[0]] = pd.to_datetime(aggregated_df_wetter.iloc[:, 0], errors='coerce')
    #aggregated_df_wetter['Date'] = aggregated_df_wetter.iloc[:,0].dt.strftime('%d.%m.%Y')  # Extract the date part
    #aggregated_df_wetter['Time'] = aggregated_df_wetter.iloc[:,0].dt.hour  # Extract the time part
    #aggregated_df_wetter.drop(['time'], axis = 1, inplace = True )
    
    
    #ohne Bezirk!!!!
    aggregated_df_pkw = df_merged_pkws.groupby(['Date', 'Time']).agg({
    **{col: 'mean' for col in columns_to_aggregate},  # Mean for weather columns
    'Anzahl': lambda x: np.floor(x.mean())   # mean for 'Anzahl'
    }).reset_index()
    #st.write(aggregated_df_pkw.head())
    #st.write(aggregated_df_pkw.shape)
    #aggregated_df_pkw = df_merged_pkws.groupby(['Bezirk', 'Date', 'Time'])[columns_to_aggregate+['Anzahl']].mean().reset_index() #
    #aggregated_df_fahrrad = df_merged_fahrräder.groupby(['Bezirk', 'Date', 'Time'])[columns_to_aggregate+['Anzahl']].mean().reset_index()#'Bezirk', 
    
    aggregated_df_fahrrad = df_merged_fahrräder.groupby(['Date', 'Time']).agg({
    **{col: 'mean' for col in columns_to_aggregate},  # Mean for weather columns
    'Anzahl': lambda x: np.floor(x.mean())   # mean for 'Anzahl'
    }).reset_index()
    #st.write(aggregated_df_fahrrad.head())
    #st.write(aggregated_df_fahrrad.shape)
    # bezirk_map =  {
    #  "Mitte":1, "Friedrichshain-Kreuzberg" :2, "Pankow":3, "Charlottenburg-Wilmersdorf":4, "Spandau": 5 , "Steglitz-Zehlendorf":6, "Tempelhof-Schöneberg":7, "Neukölln":8,
    #             "Treptow-Köpenick":9, "Marzahn-Hellersdorf":10, "Lichtenberg":11,  "Reinickendorf":12
    #             }    
    ##################Für PKWs
    #aggregated_df_pkw['Bezirk'] = aggregated_df_pkw['Bezirk'].map(bezirk_map) !!!!!!!  
    
    aggregated_df_pkw['time_of_the_day_'] = aggregated_df_pkw['Time'].apply(convert_time_of_the_day)
    
    # Assuming 'aggregated_df' is your DataFrame
    aggregated_df_pkw['Date'] = pd.to_datetime(aggregated_df_pkw['Date'], format='%d.%m.%Y', errors='coerce')

    # Generate Berlin holidays for the years in the 'Date' column
    berlin_holidays = holidays.Germany(years=aggregated_df_pkw['Date'].dt.year.unique(), subdiv='BE')

    # Convert holidays to a datetime format
    berlin_holidays = pd.to_datetime(list(berlin_holidays.keys()))

    # Add the 'day_of_the_week' column (0=Monday, 6=Sunday)
    aggregated_df_pkw['day_of_the_week'] = aggregated_df_pkw['Date'].dt.weekday

    # Check if each date is a holiday using .isin()
    aggregated_df_pkw['is_holiday'] = aggregated_df_pkw['Date'].isin(berlin_holidays)
    
    #st.dataframe(aggregated_df_pkw.shape)
    
    #st.write(f'Nach der Bearbeitung hat unser Datensatz nun die Form {aggregated_df_pkw.shape}')
    
    ################Für Fahrräder
    #aggregated_df_fahrrad['Bezirk'] = aggregated_df_fahrrad['Bezirk'].map(bezirk_map)!!!!!!!!   
    aggregated_df_fahrrad['time_of_the_day'] = aggregated_df_fahrrad['Time'].apply(convert_time_of_the_day)
    
    # Assuming 'aggregated_df' is your DataFrame
    aggregated_df_fahrrad['Date'] = pd.to_datetime(aggregated_df_fahrrad['Date'], format='%d.%m.%Y', errors='coerce')

    # Generate Berlin holidays for the years in the 'Date' column
    berlin_holidays = holidays.Germany(years=aggregated_df_fahrrad['Date'].dt.year.unique(), subdiv='BE')

    # Add the 'day_of_the_week' column (0=Monday, 6=Sunday)
    aggregated_df_fahrrad['day_of_the_week'] = aggregated_df_fahrrad['Date'].dt.weekday

    # Check if each date is a holiday using .isin()
    aggregated_df_fahrrad['is_holiday'] = aggregated_df_fahrrad['Date'].isin(berlin_holidays)
    
    ###st.dataframe(aggregated_df_fahrrad.head())
    
    #st.write(f'Nach der Bearbeitung hat unser Datensatz nun die Form {aggregated_df_fahrrad.shape}')
    #print(df_merged_fahrräder.head())

    st.session_state.df_pkws = aggregated_df_pkw
    st.session_state.df_Fahrräder = aggregated_df_fahrrad
    #st.session_state.bezirk_map = bezirk_map
