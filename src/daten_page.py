import streamlit as st
import pandas as pd
import os
import time
import numpy as np

@st.cache_data
def load_dataset(file_path):
    return pd.read_csv(file_path)

@st.cache_data
def aggregate_data(df, columns_to_aggregate):
    return df.groupby(['Date', 'Time']).agg({
        **{col: 'mean' for col in columns_to_aggregate},
        'Anzahl': lambda x: np.floor(x.mean())
    }).reset_index()

def app():
    st.header('Datenüberblick')
    st.markdown("""
    Wir haben genau drei Datensätze analysiert: den Fahrradzähler in Berlin, den Messquerschnitt für Autos in Berlin sowie Wetterdaten in Berlin. Die betrachtete Periode erstreckt sich stundenweise von 2018 bis 2023.
    """)

    datasets = [
        ("Lade Messdaten PKWs...", '../data/processed/MessDatenAuto.csv', 'PKWs'),
        ("Lade Messdaten Fahrräder...", '../data/processed/MessDatenFahrrad.csv', 'Fahrräder'),
        ("Lade Wetterdaten...", '../data/processed/WetterData.csv', 'Wetter'),
    ]

    loaded_data = {}
    progress_bar = st.progress(0)
    total_steps = len(datasets)

    for i, (message, file_path, data_key) in enumerate(datasets):
        st.write(message)
        df = load_dataset(file_path)
        loaded_data[f"df_{data_key}"] = df
        progress_bar.progress((i + 1) / total_steps)

    st.success("Alle Daten wurden erfolgreich geladen!")

    df_mess_auto = loaded_data['df_PKWs']
    df_mess_fahrrad = loaded_data['df_Fahrräder']
    df_wetter = loaded_data['df_Wetter']

    st.subheader('Messdaten PKWs')
    df_mess_auto.rename(columns={'BREITE_WGS84': 'Breitengrad', 'LÄNGE_WGS84': 'Längengrad', 'q_pkw_mq_hr': 'Anzahl'}, inplace=True)
    df_mess_auto.reset_index(drop=True, inplace=True)
    st.dataframe(df_mess_auto.head())
    st.write(f"Die ursprüngliche Anzahl von PKWs Daten {df_mess_auto.shape}")

    st.subheader('Messdaten Fahrräder')
    df_mess_fahrrad.rename(columns={'Breitengrad_left': 'Breitengrad', 'Längengrad_left': 'Längengrad', 'Wert': 'Anzahl'}, inplace=True)
    df_mess_fahrrad.reset_index(drop=True, inplace=True)
    st.dataframe(df_mess_fahrrad.head())
    st.write(f"Die ursprüngliche Anzahl von Fahrräder Daten {df_mess_fahrrad.shape}")

    st.subheader('Wetter Daten')
    df_wetter.rename(columns={'TimeID': 'Time'}, inplace=True)
    st.dataframe(df_wetter.head())
    st.write(f"Die ursprüngliche Anzahl von Wetter Daten {df_wetter.shape}")

    st.subheader('Zusammenführung von die Daten basierend auf die Datum, Uhrzeit und den Bezirk')
    st.write("Da die Datenmenge sehr groß ist, haben wir die Daten aggregiert und die Mittelwerte berechnet, um einen besseren Überblick über ganz Berlin zu erhalten. Nach der Bereinigung und dem Feature Engineering haben wir mit diesen aggregierten Daten weitergearbeitet.")
    st.write("Aggregiere Daten, bitte warten...")

    with st.spinner('Aggregiere Daten, bitte warten...'):
        progress_bar = st.progress(0)
        total_steps = 2

        df_merged_pkws = df_mess_auto.merge(df_wetter, on=['Date', 'Time', 'Bezirk'], how='left')
        df_mess_auto.drop(['INBETRIEBNAHME'], axis=1, inplace=True)

        df_merged_fahrräder = df_mess_fahrrad.merge(df_wetter, on=['Date', 'Time', 'Bezirk'], how='left')

        columns_to_aggregate = [
            'temperature_2m (°C)',
            'relative_humidity_2m (%)',
            'rain (mm)',
            'snowfall (cm)',
            'cloud_cover (%)'
        ]

        aggregated_df_pkw = aggregate_data(df_merged_pkws, columns_to_aggregate)
        progress_bar.progress(1 / total_steps)

        aggregated_df_fahrrad = aggregate_data(df_merged_fahrräder, columns_to_aggregate)
        progress_bar.progress(2 / total_steps)

        st.session_state.df_pkws = aggregated_df_pkw
        st.session_state.df_Fahrräder = aggregated_df_fahrrad

        st.success("Daten erfolgreich aggregiert!")
