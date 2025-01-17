import sqlite3
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from shapely.wkt import loads
import osmnx as ox
import os
import create_tables as ct
import osmnx as ox
import geopandas as gpd

def is_leap_year(year):
    if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
        return True
    return False

def open_excel_file(excel_file_path, sheetname = None):
    # Load the data from Excel
    if os.path.exists(excel_file_path):
        df = pd.read_excel(excel_file_path, sheet_name = sheetname)
    else:
        print(f"Die Datei'{excel_file_path} wurde nicht gefunden.")
    return df    

def open_csv_file(csv_file):
    if os.path.exists(csv_file):
        df = pd.read_csv(csv_file)
    else:
        print(f"Die Datei'{csv_file} wurde nicht gefunden.")
    return df    

def check_table_content(cur, table_name):
    cur.execute(f"select * from {table_name}").fetchall()

def fetch_data_df(table_name, conn):
    return pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
   

def preload_lookup_tables():
    conn = ct.create_or_open_database()
    cur = conn.cursor()
    cur.execute("SELECT date, DateID FROM Date_dim")
    date_lookup = dict(cur.fetchall())
    conn.close()
    return date_lookup

def fetch_data_bezirk(table_name, conn):
    cursor = conn.cursor()
    cursor.execute(f"SELECT bezirk FROM {table_name}")
    results = cursor.fetchall()
    # Convert the result to a list
    bezirk_list = [row[0] for row in results]  # Extract the first element from each tuple
    return bezirk_list


#if required!!
def generate_csv():
    pass
    #so for all the table in the database: generate all the csv Datei 
    
def fetch_data(table_name, database_name):
    with sqlite3.connect(database_name) as conn:
        return pd.read_sql_query(f"select * from {table_name}", conn)

#TODO:split this code between create geojson Datei and read from geojson Datei if available
def get_geo():

    # Get data for Berlin Bezirke
    gdf = ox.features_from_place(
        "Berlin, Germany",
        tags={"boundary": "administrative", "admin_level": "6"}
    )

    # Filter only relevant columns
    gdf = gdf[['name', 'geometry']]

    # Save the GeoDataFrame as a GeoJSON file
    gdf.to_file("../data/processed/berlin_bezirke.geojson", driver="GeoJSON")

    # List of desired Berlin Bezirke
    berlin_bezirke = [
        "Charlottenburg-Wilmersdorf", "Friedrichshain-Kreuzberg", "Lichtenberg",
        "Marzahn-Hellersdorf", "Mitte", "Neukölln", "Pankow", "Reinickendorf",
        "Spandau", "Steglitz-Zehlendorf", "Tempelhof-Schöneberg", "Treptow-Köpenick"
    ]

    # Load and process GeoJSON file
    gdf_bezirke = gpd.read_file("../data/processed/berlin_bezirke.geojson")
    gdf_bezirke = gdf_bezirke[gdf_bezirke['name'].isin(berlin_bezirke)]  # Filter Bezirke
    gdf_bezirke = gdf_bezirke.dissolve(by="name")  # Dissolve by name

    # Convert to a projected CRS for accurate centroid calculations
    gdf_bezirke = gdf_bezirke.to_crs("EPSG:3857")  # Web Mercator (meters)

    # Calculate centroids in the projected CRS
    gdf_bezirke['centroid_x'] = gdf_bezirke.geometry.centroid.x
    gdf_bezirke['centroid_y'] = gdf_bezirke.geometry.centroid.y

    # Reproject back to WGS84 for final output
    gdf_bezirke = gdf_bezirke.to_crs("EPSG:4326")
    gdf_bezirke['Breitengrad'] = gdf_bezirke['centroid_y']
    gdf_bezirke['Längengrad'] = gdf_bezirke['centroid_x']

    # Drop temporary centroid columns
    gdf_bezirke = gdf_bezirke.drop(columns=['centroid_x', 'centroid_y'])

    return gdf_bezirke

def fetch_data_df_chunk(conn, table_name):
    chunks = pd.read_sql_query(f"SELECT * FROM {table_name}", conn, chunksize=10000)
    return chunks

def drop_table(table_name , cur):
    cur.execute(f"DROP TABLE IF EXISTS {table_name}") 

#TE539 für den könnte den Bezirk nicht gefunden werden 
#I would set it to Friedrichshain-Kreuzberg
# Update this code to be useful for every point coordinates given
from geopy.geocoders import Nominatim
def check_point_bezirk():
    geolocator = Nominatim(user_agent="bezirk_locator")
    location = geolocator.reverse((13.51683, 52.39825), language="de")
    if location:
        print("Gefundene Adresse:", location.address)
    else:
        print("Bezirk konnte nicht gefunden werden.")