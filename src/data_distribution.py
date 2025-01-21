from shapely import Point
import streamlit as st
import folium
import sys
import os
import geopandas as gpd
import matplotlib.pyplot as plt
from folium.plugins import MarkerCluster
import pandas as pd
from streamlit_folium import folium_static


def app():

    df = pd.read_excel("../data/processed/Tableau Standort PKW.xlsx")
    df_Zählstationen = pd.read_excel("../data/processed/Tableau Excel Fahrrad.xlsx")
    
    #with st.expander("Map"):
    # Create the map centered around the average latitude and longitude
    m = folium.Map(location=[df['BREITENGRAD'].mean(), df['LÄNGENGRAD'].mean()], zoom_start=13)

    # Add markers with popup
    marker_cluster = MarkerCluster(name="Messstationen PKWs").add_to(m)
    for index, row in df.iterrows():
        popup_html =f""" 
                <b>Messstation:<b>{row['MQ_KURZNAME']}</p>
                <b>Zählungen:<b>{row['Anzahl Zählungen']} PKWs</p>
            """
        folium.Marker(
            location=[row['BREITENGRAD'], row['LÄNGENGRAD']],
            popup=folium.Popup(popup_html, max_width=300),
            icon=folium.Icon(color="blue", icon="info-sign") 
            #popup=f"{row['MQ_KURZNAME']} - {row['Anzahl Zählungen']} Zählungen"
        ).add_to(marker_cluster)

    marker_cluster_new = MarkerCluster(name="Zählerstelle Fahrräder").add_to(m)
    for index, row in df_Zählstationen.iterrows():
        popup_html = f"""
        <b>Zählstelle:</b> {row['Zählstelle']}<br>
        <b>Zählungen:</b> {row['Anzahl Messungen']}<br>
        """
        folium.Marker(
            location=[row['Breitengrad'], row['Längengrad']],
            popup=folium.Popup(popup_html, max_width=300),
            icon=folium.Icon(color="green", icon="info-sign")  # Use green for new stations
        ).add_to(marker_cluster_new)
    folium.LayerControl().add_to(m)
    
    st.title("Geografische PKWs Messstationen und Farrad Zählstelle auf der Karte")
    st.write("Diese Karte zeigt die Messstationen/Zählstelle mit ihren jeweiligen Zählwerten")
    folium_static(m, width = 1200, height = 600)


    #with st.expander("Global"):
    sys.path.append(os.path.abspath("../database_scripts"))
    import  db_utils as du
    gdf_bezirke = du.get_geo()
    print(gdf_bezirke)
    col1, col2 = st.columns(2)
    with col1:
        # Create GeoDataFrame for Zählstellen
        geometry = [Point(xy) for xy in zip(df_Zählstationen["Längengrad"], df_Zählstationen["Breitengrad"])]
        gdf_zaehlstellen = gpd.GeoDataFrame(df_Zählstationen, geometry=geometry, crs="EPSG:4326")

        # Spatial join: Match Zählstellen with Bezirke
        gdf_zaehlstellen = gpd.sjoin(gdf_zaehlstellen, gdf_bezirke, how="left", predicate="within")
    
        fig, ax = plt.subplots(figsize=(10, 10))
        gdf_bezirke.plot(ax=ax, color="lightblue", edgecolor="black", alpha=0.7)
        gdf_zaehlstellen.plot(ax=ax, color="red", markersize=20, label="Zählstellen")

        # Add labels, legend, and title
        plt.title("Zählstellen und Bezirke", fontsize=16)
        plt.xlabel("Longitude", fontsize=12)
        plt.ylabel("Latitude", fontsize=12)
        plt.legend()

        # Display the plot in Streamlit
        st.pyplot(fig)
        
    with col2:
        geometry_mq = [Point(xy) for xy in zip(df["LÄNGENGRAD"], df["BREITENGRAD"])]
        gdf_mq = gpd.GeoDataFrame(df, geometry=geometry_mq, crs="EPSG:4326")

        # Spatial join: Match Zählstellen with Bezirke
        gdf_mq = gpd.sjoin(gdf_mq, gdf_bezirke, how="left", predicate="within")
        
        fig, ax = plt.subplots(figsize=(10, 10))
        gdf_bezirke.plot(ax=ax, color="lightblue", edgecolor="black", alpha=0.7)
        gdf_mq.plot(ax=ax, color="blue", markersize=20, label="Zählstellen")

        # Add labels, legend, and title
        plt.title("Messquerschnitt und Bezirke", fontsize=16)
        plt.xlabel("Longitude", fontsize=12)
        plt.ylabel("Latitude", fontsize=12)
        plt.legend()

        # Display the plot in Streamlit
        st.pyplot(fig)