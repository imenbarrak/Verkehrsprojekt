from shapely import Point
import streamlit as st
import folium
import sys
import os
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
from streamlit_folium import folium_static
from folium.plugins import MarkerCluster, Fullscreen
import matplotlib.colors as colors
import matplotlib.cm as cm


def app():

    df = pd.read_excel("../data/processed/Tableau Standort PKW.xlsx")
    df_Zählstationen = pd.read_excel("../data/processed/Tableau Excel Fahrrad.xlsx")
    
    #with st.expander("Map"):
    # Create the map centered around the average latitude and longitude
   
    with st.container():
       
        m = folium.Map(location=[df['BREITENGRAD'].mean(), df['LÄNGENGRAD'].mean()], zoom_start=13)
        # Add fullscreen control
        Fullscreen(position="topright", title="Toggle Fullscreen", title_cancel="Exit Fullscreen").add_to(m)

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
        folium_static(m, width = 800, height = 600)
        #st.markdown('</div>', unsafe_allow_html=True)
    with st.container():
        st.subheader("Kompakte Übersicht")
    #with st.container():
        
        #with st.expander("Global"):
        sys.path.append(os.path.abspath("../database_scripts"))
        import  db_utils as du
        gdf_bezirke = du.get_geo()
        print(gdf_bezirke)
        col1, col2,col3 = st.columns([5,1,5])  # Equal width; adjust ratios if needed

        with col1:
            #st.subheader("Zählstellen und Bezirke")
            #st.write(" ")
            #st.write(" ")
            # Create GeoDataFrame for Zählstellen
            geometry = [Point(xy) for xy in zip(df_Zählstationen["Längengrad"], df_Zählstationen["Breitengrad"])]
            gdf_zaehlstellen = gpd.GeoDataFrame(df_Zählstationen, geometry=geometry, crs="EPSG:4326")

            # Spatial join: Match Zählstellen with Bezirke
            gdf_zaehlstellen = gpd.sjoin(gdf_zaehlstellen, gdf_bezirke, how="left", predicate="within")

            # Normalize the 'Anzahlen' column for color mapping
            norm = colors.Normalize(vmin=gdf_zaehlstellen['Anzahl Messungen'].min(), vmax=gdf_zaehlstellen['Anzahl Messungen'].max())
            cmap = cm.get_cmap('Reds')

            # Plot the map
            fig, ax = plt.subplots(figsize=(16, 10))
            gdf_bezirke.plot(ax=ax, color="lightblue", edgecolor="black", alpha=0.7)
            gdf_zaehlstellen.plot(
                ax=ax,
                color=[cmap(norm(value)) for value in gdf_zaehlstellen['Anzahl Messungen']],
                markersize=40,
                label="Zählstellen",
            )
            sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
            sm.set_array([])
            cbar = fig.colorbar(sm, ax=ax, fraction=0.03, pad=0.04)
            cbar.set_label("Anzahl Messungen", fontsize=12)

            plt.title("Zählstellen und Bezirke", fontsize=16)
            plt.xlabel("Longitude", fontsize=12)
            plt.ylabel("Latitude", fontsize=12)
            plt.legend()
            st.pyplot(fig)
        with col2:
            st.write("   ")
        with col3:
            #st.subheader("Messquerschnitt und Bezirke")

            # Create GeoDataFrame for Messquerschnitt
            geometry_mq = [Point(xy) for xy in zip(df["LÄNGENGRAD"], df["BREITENGRAD"])]
            gdf_mq = gpd.GeoDataFrame(df, geometry=geometry_mq, crs="EPSG:4326")

            # Spatial join: Match Messquerschnitt with Bezirke
            gdf_mq = gpd.sjoin(gdf_mq, gdf_bezirke, how="left", predicate="within")

            # Normalize the 'Anzahlen' column for color mapping
            norm = colors.Normalize(vmin=gdf_mq['Anzahl Zählungen'].min(), vmax=gdf_mq['Anzahl Zählungen'].max())
            cmap = cm.get_cmap('Blues')

            # Plot the map
            fig, ax = plt.subplots(figsize=(16, 10))
            gdf_bezirke.plot(ax=ax, color="lightblue", edgecolor="black", alpha=0.7)
            gdf_mq.plot(
                ax=ax,
                color=[cmap(norm(value)) for value in gdf_mq['Anzahl Zählungen']],
                markersize=40,
                label="Messstationen",
            )
            sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
            sm.set_array([])
            cbar = fig.colorbar(sm, ax=ax, fraction=0.03, pad=0.04)
            cbar.set_label("Anzahl Zählungen", fontsize=12)

            plt.title("Messquerschnitt und Bezirke", fontsize=16)
            plt.xlabel("Longitude", fontsize=12)
            plt.ylabel("Latitude", fontsize=12)
            plt.legend()
            st.pyplot(fig)