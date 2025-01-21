import streamlit as st
import pandas as pd
import geopandas as gpd
import pydeck as pdk
import sys
import os
import daten_page as dp
import matplotlib.pyplot as plt
import folium
from streamlit_folium import st_folium

sys.path.append(os.path.abspath("../data/database_scripts"))
import  db_utils as du
import create_tables as ct  

def app():


    # Load Berlin Bezirke data
    conn = ct.create_or_open_database()
    df_bezirk = du.fetch_data_df('Bezirke', conn)

# Create GeoDataFrame
    gdf_bezirke = gpd.GeoDataFrame(
        df_bezirk, 
        geometry=gpd.GeoSeries.from_wkt(df_bezirk['Geometry'])
    )

    # Set the CRS if not already set
    gdf_bezirke.set_crs(epsg=25833, inplace=True)  # Replace 25833 with the correct CRS if needed
    gdf_bezirke = gdf_bezirke.to_crs(epsg=4326)  # Convert to WGS84 (latitude and longitude)

    # Create a clean Folium map
    m = folium.Map(location=[52.5200, 13.4050], zoom_start=11, tiles="CartoDB Positron")  # Simple light background
    df_autos_Zähler = du.fetch_data_df('Messquerschnitt',conn)
    df_autos_Zähler.rename(columns={'BREITE_WGS84': 'latitude', 'LÄNGE_WGS84': 'longitude'}, inplace=True)

    # Add Bezirke polygons to the map
    for _, row in gdf_bezirke.iterrows():
        folium.GeoJson(
            row['geometry'],
            style_function=lambda x: {
                'fillColor': 'lightblue',
                'color': 'black',
                'weight': 1,
                'fillOpacity': 0.7
            }
        ).add_to(m)
    for _, row in df_autos_Zähler.iterrows():
        folium.CircleMarker(
            location=[row['latitude'], row['longitude']],
            radius=5,  # Circle size
            color='red',  # Circle border color
            fill=True,
            fill_color='red',  # Circle fill color
            fill_opacity=0.8,
        ).add_to(m)

    # Display the interactive map in Streamlit
    st.title("Karte der Berliner Bezirke")
    st_folium(m, width=700, height=500)

    """ 
    
    df_autos_Zähler = du.fetch_data_df('Messquerschnitt',conn)
    print(df_autos_Zähler.columns)
    df_fahrräder_Zähler = du.fetch_data_df('Standorten_Zählstelle',conn)
    print(df_fahrräder_Zähler.columns)
    # Beispiel-Datenframe mit Bezirken und Koordinaten
    df_mess_auto = pd.read_csv('../data/processed/MessDatenAuto.csv')
    print(df_mess_auto.columns)
    df_mess_auto = df_mess_auto.groupby('MQ_KURZNAME')['q_pkw_mq_hr'].mean().reset_index()
    print(df_mess_auto)
    # Streamlit-App
    st.title("Interaktive Karte: Bezirke und Messstationen in Berlin")

    # Kartenlayer für Messstationen
    station_layer = pdk.Layer(
        "ScatterplotLayer",
        data=df_mess_auto,
        get_position="[Längengrad, Breitengrad]",
        get_radius=200,  # Radius in Metern
        get_fill_color="[255, 0, 0, 160]",
        pickable=True
    )

    ) """

    # Optionale Informationen in Streamlit anzeigen
    # st.subheader("Daten der Bezirke")
    # st.dataframe(df_bezirk[["Bezirk"]])

    # st.subheader("Daten der Messstationen")
    # st.dataframe(df_mess_auto)
