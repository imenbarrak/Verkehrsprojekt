from shapely.geometry import Point
import streamlit as st
import folium
import geopandas as gpd
import pandas as pd
from streamlit_folium import folium_static
from folium.plugins import MarkerCluster, Fullscreen
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.cm as cm
import sys
import os

# Cache the loading of geographic data
@st.cache_data
def load_geodata():
    """Load and cache geographic data."""
    sys.path.append(os.path.abspath("../database_scripts"))
    import db_utils as du
    return du.get_geo()

@st.cache_data
def load_data():
    """Load and cache measurement data."""
    df_pkws = pd.read_excel("../data/processed/Tableau Standort PKW.xlsx")
    df_bikes = pd.read_excel("../data/processed/Tableau Excel Fahrrad.xlsx")
    return df_pkws, df_bikes

@st.cache_data
def preprocess_geometries(df_pkws, df_bikes, _gdf_bezirke):
    """Preprocess geometries and perform spatial joins."""
    # Create GeoDataFrame for bicycles
    gdf_bikes = gpd.GeoDataFrame(
        df_bikes,
        geometry=[Point(xy) for xy in zip(df_bikes["Längengrad"], df_bikes["Breitengrad"])],
        crs="EPSG:4326",
    )
    gdf_bikes = gpd.sjoin(gdf_bikes, _gdf_bezirke, how="left", predicate="within")

    # Create GeoDataFrame for PKWs
    gdf_pkws = gpd.GeoDataFrame(
        df_pkws,
        geometry=[Point(xy) for xy in zip(df_pkws["LÄNGENGRAD"], df_pkws["BREITENGRAD"])],
        crs="EPSG:4326",
    )
    gdf_pkws = gpd.sjoin(gdf_pkws, _gdf_bezirke, how="left", predicate="within")

    return gdf_bikes, gdf_pkws

def app():
    st.title("Geografische Visualisierung")

    # Load data and geodata
    df_pkws, df_bikes = load_data()
    gdf_bezirke = load_geodata()

    # Preprocess geometries
    gdf_bikes, gdf_pkws = preprocess_geometries(df_pkws, df_bikes, gdf_bezirke)

    # Create map
    st.header("Verteilung Messstationen")
    map_view = folium.Map(
        location=[df_pkws['BREITENGRAD'].mean(), df_pkws['LÄNGENGRAD'].mean()],
        zoom_start=13
    )
    Fullscreen(position="topright").add_to(map_view)

    # Add PKW markers
    marker_cluster_pkws = MarkerCluster(name="Messstationen PKWs").add_to(map_view)
    for _, row in df_pkws.iterrows():
        popup_html = f"""<b>Messstation:</b> {row['MQ_KURZNAME']}<br>
        <b>Zählungen:</b> {row['Anzahl Zählungen']} PKWs"""
        folium.Marker(
            location=[row['BREITENGRAD'], row['LÄNGENGRAD']],
            popup=folium.Popup(popup_html, max_width=300),
            icon=folium.Icon(color="blue", icon="info-sign")
        ).add_to(marker_cluster_pkws)

    # Add Bike markers
    marker_cluster_bikes = MarkerCluster(name="Zählstellen Fahrräder").add_to(map_view)
    for _, row in df_bikes.iterrows():
        popup_html = f"""<b>Zählstelle:</b> {row['Zählstelle']}<br>
        <b>Zählungen:</b> {row['Anzahl Messungen']} Fahrräder"""
        folium.Marker(
            location=[row['Breitengrad'], row['Längengrad']],
            popup=folium.Popup(popup_html, max_width=300),
            icon=folium.Icon(color="green", icon="info-sign")
        ).add_to(marker_cluster_bikes)

    folium.LayerControl().add_to(map_view)
    folium_static(map_view, width=700, height=500)

    # Plot data with GeoPandas
    st.subheader("Zählstellen und Bezirke")
    col1, col2 = st.columns(2)
    
    with col1:
        #st.subheader("Zählstellen und Bezirke (Fahrräder)")
        norm_bikes = colors.Normalize(
            vmin=gdf_bikes['Anzahl Messungen'].min(),
            vmax=gdf_bikes['Anzahl Messungen'].max()
        )
        cmap_bikes = cm.get_cmap('Reds')

        fig, ax = plt.subplots(figsize=(10, 8))
        gdf_bezirke.plot(ax=ax, color="lightblue", edgecolor="black")
        gdf_bikes.plot(
            ax=ax,
            color=[cmap_bikes(norm_bikes(value)) for value in gdf_bikes['Anzahl Messungen']],
            markersize=60,
            label="Zählstellen Fahrräder"
        )
        sm = plt.cm.ScalarMappable(cmap=cmap_bikes, norm=norm_bikes)
        sm.set_array([])
        cbar = fig.colorbar(sm, ax=ax, fraction=0.03, pad=0.04)
        cbar.set_label("Anzahl Messungen", fontsize=12)
        plt.legend()
        plt.title("Fahrradzählstellen")
        st.pyplot(fig)

    with col2:
        #st.subheader("Messstationen und Bezirke (PKWs)")
        norm_pkws = colors.Normalize(
            vmin=gdf_pkws['Anzahl Zählungen'].min(),
            vmax=gdf_pkws['Anzahl Zählungen'].max()
        )
        cmap_pkws = cm.get_cmap('Blues')

        fig, ax = plt.subplots(figsize=(10, 8))
        gdf_bezirke.plot(ax=ax, color="lightblue", edgecolor="black")
        gdf_pkws.plot(
            ax=ax,
            color=[cmap_pkws(norm_pkws(value)) for value in gdf_pkws['Anzahl Zählungen']],
            markersize=60,
            label="Messstationen PKWs"
        )
        sm = plt.cm.ScalarMappable(cmap=cmap_pkws, norm=norm_pkws)
        sm.set_array([])
        cbar = fig.colorbar(sm, ax=ax, fraction=0.03, pad=0.04)
        cbar.set_label("Anzahl Zählungen", fontsize=12)
        plt.legend()
        plt.title("PKW-Messstationen")
        st.pyplot(fig)