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

#if required!!
def generate_csv():
    pass
    #so for all the table in the database: generate all the csv Datei 
    
def fetch_data(table_name, database_name):
    with sqlite3.connect(database_name) as conn:
        return pd.read_sql_query(f"select * from {table_name}", conn)

def get_geo():
    gdf = ox.features_from_place(
        "Berlin, Germany",
        tags={"boundary": "administrative", "admin_level": "6"}
    )

    # Filter only relevant columns
    gdf = gdf[['name', 'geometry']]

    # Save the GeoDataFrame as a GeoJSON file
    gdf.to_file("berlin_bezirke.geojson", driver="GeoJSON")

    # List of desired Berlin Bezirke
    berlin_bezirke = [
        "Charlottenburg-Wilmersdorf", "Friedrichshain-Kreuzberg", "Lichtenberg",
        "Marzahn-Hellersdorf", "Mitte", "Neukölln", "Pankow", "Reinickendorf",
        "Spandau", "Steglitz-Zehlendorf", "Tempelhof-Schöneberg", "Treptow-Köpenick"
    ]

    # Load and process GeoJSON file
    gdf_bezirke = gpd.read_file("berlin_bezirke.geojson")
    gdf_bezirke = gdf_bezirke[gdf_bezirke['name'].isin(berlin_bezirke)]  # Filter Bezirke
    gdf_bezirke = gdf_bezirke.dissolve(by="name")  # Dissolve by name
    gdf_bezirke = gdf_bezirke.to_crs("EPSG:4326")  # Ensure CRS is WGS84
    gdf_bezirke['Breitengrad'] = gdf_bezirke.geometry.centroid.y
    gdf_bezirke['Längengrad'] = gdf_bezirke.geometry.centroid.x
    gdf_bezirke.drop(['element','id'], axis =1, inplace=True)
    
    return gdf_bezirke

def fetch_data_df_chunk(conn):
    chunks = pd.read_sql_query("SELECT * FROM Messdaten_auto", conn, chunksize=10000)
    return chunks