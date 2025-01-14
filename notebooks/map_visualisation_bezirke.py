import matplotlib.pyplot as plt
import sys
import os
import folium
from folium.plugins import MarkerCluster


sys.path.append(os.path.abspath("../database_scripts"))
import db_utils as du
import create_tables as ct

#conn = ct.create_or_open_database()
#gdf_zaehlstellen = du.fetch_data_df('Standorten_Zählstelle',conn)
#gdf_bezirke= du.fetch_data_df('Bezirke',conn)
#merged_gdf = gdf_bezirke.merge(gdf_zaehlstellen, on='Bezirk', how='left')
import folium
import geopandas as gpd

# Load Berlin Bezirke GeoDataFrame
gdf_bezirke = gpd.read_file("../data/processed/berlin_bezirke.geojson")  # Ensure this file exists

# Reproject to a projected CRS (e.g., EPSG:3857)
gdf_projected = gdf_bezirke.to_crs("EPSG:3857")

# Calculate centroids in the projected CRS
gdf_projected['centroid'] = gdf_projected.geometry.centroid

# Convert centroids back to geographic CRS for mapping
gdf_projected = gdf_projected.to_crs("EPSG:4326")
gdf_projected['Längengrad'] = gdf_projected['centroid'].x
gdf_projected['Breitengrad'] = gdf_projected['centroid'].y

# Initialize the map centered on Berlin
berlin_map = folium.Map(location=[52.5200, 13.4050], zoom_start=11)

# Add each Bezirk as a GeoJson layer
for _, row in gdf_projected.iterrows():
    folium.GeoJson(
        row['geometry'],  # Polygon of the Bezirk
        name=row['name'],  # Name of the Bezirk
        tooltip=f"Bezirk: {row['name']}<br>Längengrad: {row['Längengrad']:.5f}<br>Breitengrad: {row['Breitengrad']:.5f}"
    ).add_to(berlin_map)

# Add markers for the centroids of each Bezirk
for _, row in gdf_projected.iterrows():
    folium.Marker(
        location=[row['Breitengrad'], row['Längengrad']],
        popup=f"Bezirk: {row['name']}",
        icon=folium.Icon(color="blue", icon="info-sign")
    ).add_to(berlin_map)

# Save and display the map
berlin_map.save("../output/berlin_interactive_map.html")
berlin_map
import webbrowser
webbrowser.open("berlin_interactive_map.html")
