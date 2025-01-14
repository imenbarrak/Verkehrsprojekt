import sqlite3
import holidays
from shapely import Point
import db_utils
from datetime import date
import geopandas as gpd
import pandas as pd 
import os
from multiprocessing import Process, Queue, current_process
import create_tables as ct
import db_utils as dbu
import numpy as np

#TODO optimize the time needed to store in the dabase and check if it is normal 

def store_date(cur):
    
    dates = []
    for year in range(2018, 2024):
        berlin_holidays = holidays.Germany(years =year,subdiv='BE')
        for month in range(1, 13):
            for day in range(1, 32):
                if month == 2 and db_utils.is_leap_year(year) and day == 30:
                    break
                elif month == 2 and not db_utils.is_leap_year(year) and day == 29:
                    break
                elif month in (4,6,9,11)  and day == 31:
                    break
                elif month in (1,3,5,7,8,10,12) and day == 32:
                    break
                
                d = date(year, month, day)  # Year, Month, Day
                formatted_date = d.strftime("%d.%m.%Y")
                is_holiday = d in berlin_holidays

                #day_of_week = d.weekday()
                quarter = (month - 1) // 3 + 1
                d_to_save= (formatted_date, year ,month , day, d.weekday(), is_holiday,quarter)
                dates.append(d_to_save)

    cur.executemany("INSERT INTO Date_dim(date, year, month, day,day_of_the_week, is_holiday,quarter) VALUES (?,?,?,?,?,?,?)" , dates)
    print("Date data saved successfully!")
    
def store_time(cur):
    
    time_of_the_day = ''
    for i in range (0, 24):
        if i >= 4 and i < 10 :
            time_of_the_day ='morgens'
        if i >= 10 and i < 12:
            time_of_the_day ='vormittags'
        if i == 12 :
            time_of_the_day ='mittags'
        if i > 12 and i < 17:
            time_of_the_day ='nachmittags'
        if i > 17 and i <= 22:
            time_of_the_day ='abends'      
        if i > 22 or i < 4:
            time_of_the_day ='nachts'
 
        cur.execute("INSERT INTO time_dim(timeID, time_of_the_day) VALUES  (?, ?)", (i,time_of_the_day))
        
    print("Time data saved successfully!")

def store_messquerschnitt(conn, df_bezirke):
    
    #TODO: better way to define path_files
    #df_Messquerschnitt = db_utils.open_excel_file('..#\\data\\raw\\Stammdaten_Verkehrsdetektion_2022_07_20.xlsx')
    df_Messquerschnitt = pd.read_excel('..\\data\\raw\\Stammdaten_Verkehrsdetektion_2022_07_20.xlsx')
    df_Messquerschnitt.drop(['MQ_ID15','DET_NAME_ALT','DET_NAME_NEU', 'DET_ID15','ABBAUDATUM','RICHTUNG', 'DEINSTALLIERT', 'KOMMENTAR','annotation','SPUR'], axis = 1,inplace = True)
    #wir behalten nur die notwendige Informationen
    df_Messquerschnitt.columns = ['MQ_KURZNAME','STRASSE','POSITION','POS_DETAIL','BREITE_WGS84','LÄNGE_WGS84',
        'INBETRIEBNAHME']

    df_Messquerschnitt = df_Messquerschnitt.drop_duplicates()
    df_Messquerschnitt = df_Messquerschnitt.rename(columns={'BREITE_WGS84': 'Breitengrad','LÄNGE_WGS84':'Längengrad' })
    # Create GeoDataFrame for MQ
    geometry = [Point(xy) for xy in zip(df_Messquerschnitt["Breitengrad"], df_Messquerschnitt["Längengrad"])]
   
    gdf_Messquerschnitt = gpd.GeoDataFrame(df_Messquerschnitt, geometry = geometry, crs="EPSG:4326")
    #match MQ with Bezirk
    gdf_Messquerschnitt = gpd.sjoin(gdf_Messquerschnitt, df_bezirke, how = "left", predicate = "within")
    result = gdf_Messquerschnitt[['MQ_KURZNAME','name','STRASSE','POSITION','POS_DETAIL','INBETRIEBNAHME']]
    result = result.rename(columns={'name': 'Bezirk'})
    result.to_sql('Messquerschnitt', conn, if_exists = 'append', index = False)
    print("Messquerschnitt data saved successfully!")

def store_mess_data_fahrrad(cur):
    
    excel_file_path = '..\\data\\raw\\Fahrrad\\gesamtdatei-stundenwerte.xlsx'
    excel_file = pd.ExcelFile(excel_file_path)
    sheet_names = excel_file.sheet_names

    data = [] 
    for item in sheet_names[3:]:
        print(item)
        df = pd.read_excel(excel_file_path, sheet_name = item,index_col = 0)
        df_reset = df.reset_index()

        df_reset.iloc[:,0]= pd.to_datetime(df_reset.iloc[:,0])
        df_reset['Date'] = df_reset.iloc[:,0].dt.strftime('%d.%m.%Y')  # Extract the date part
        df_reset['Time'] = df_reset.iloc[:,0].dt.hour  # Extract the time part

        df_reset.drop('Zählstelle        Inbetriebnahme', axis = 1, inplace = True)
        columns = ['Date', 'Time'] + [col for col in df.columns if col not in ['Date', 'Time']]

        # Reorder the DataFrame
        df_reset = df_reset[columns]
        #TODO: which code can I also put out of this method
        date_ids = [
            cur.execute("SELECT DateID FROM Date_dim WHERE date = ?", (date,)).fetchone()[0]
            for date in df_reset['Date'].tolist()
        ]
        hour_ids = df_reset['Time'].tolist()
        try:
            for column in df_reset.columns[2:]:
                zaehler = column.split()[0]
                zaehler_ids = [zaehler for _ in range(len(date_ids))]
                data.extend([(zaehler_id, date_id, hour_id,  wert) for zaehler_id, date_id, hour_id,  wert in zip(zaehler_ids,date_ids, hour_ids,  df_reset[column])])

            cur.executemany("INSERT INTO Messdaten_Fahrrad (Zählstelle, DateID, TimeID, Wert) VALUES (?,?,?,?)" , data)        
            
        except Exception as e:
            print(f"Es gibt ein Problem {e}")
            
def store_mess_data_auto():
    
    file_infos = []
    for year in range(2018, 2024):
    #year = 2018
        for month in range(1, 13):
    #month = 1
            str_month = f"{month:02d}"  # Ensure two-digit month format
            file_path = f"../data/raw/Auto_{year}/mq_hr_{year}_{str_month}.csv.gz"
            if os.path.exists(file_path):
                file_infos.append((year, month, file_path))
            else:
                print(f"File not found: {file_path}")

    print(f"Found {len(file_infos)} files to process.")
    print('files are got')
    # Preload lookup tables
  
    date_lookup = db_utils.preload_lookup_tables()
    # Setup multiprocessing
    queue = Queue(maxsize=100)
    
    # Start writer process
    writer_process = Process(target = write_to_db, args=(queue,))
    writer_process.start()

    # Start file processors
    processes = []
    for file_info in file_infos:
        p = Process(target = process_file, args=(file_info, date_lookup, queue))
        processes.append(p)
        p.start()

    # Wait for all file processors to finish
    for p in processes:
        p.join()

    # Signal writer process to stop
    queue.put(None)
    print("All files processed.")

def write_to_db(queue):
    
    """Write data to the database from a shared queue."""
    conn = ct.create_or_open_database()
    cur = conn.cursor()
    while True:
        data = queue.get()
        if data is None:  # Stop signal
            break
        if data:
            try:
                cur.executemany(
                "INSERT INTO Messdaten_auto (MQ_KURZNAME, DateID, TimeID, q_pkw_mq_hr) VALUES (?, ?, ?, ?)",data
                )
                conn.commit()
            except sqlite3.Error as e:
                print(f"Database error in writer: {e}")
    conn.close()     

def process_file(file_info, date_lookup, queue):
    
    """Process a single file."""
    year, month, file_path = file_info
    print(f"[{current_process().name}] Starting file: {file_path}")
    
    chunk_iter = pd.read_csv(file_path, delimiter=';', compression='gzip', chunksize=10000)
    for chunk in chunk_iter:
        # Drop unnecessary columns
        chunk.drop(
            ['v_pkw_mq_hr', 'q_lkw_mq_hr', 'v_lkw_mq_hr', 'qualitaet', 'q_kfz_mq_hr', 'v_kfz_mq_hr'],
            axis=1,
            inplace=True,
        )
        
        # Map DateID
        chunk['DateID'] = chunk['tag'].map(date_lookup)
        chunk['mq_name'] = chunk['mq_name'].astype(str)
        # Create base names by removing 'n' suffix
        chunk['base_mq_name'] = chunk['mq_name'].str.rstrip('n')

        # Calculate the mean for each base_mq_name, DateID, and stunde
        mean_values = (
            chunk.groupby(['base_mq_name', 'DateID', 'stunde'])['q_pkw_mq_hr']
            .mean()
            .reset_index()
            .rename(columns={'q_pkw_mq_hr': 'mean_q_pkw_mq_hr'})
        )
        mean_values['mean_q_pkw_mq_hr'] = np.floor(mean_values['mean_q_pkw_mq_hr']).astype(int)

        # Merge mean values back into the chunk
        chunk = chunk.merge(
            mean_values,
            on=['base_mq_name', 'DateID', 'stunde'],
            how='left'
        )

        # Update q_pkw_mq_hr for rows with prefixed mq_name
        ends_with_n = chunk['mq_name'].str.endswith('n')
        chunk.loc[ends_with_n, 'q_pkw_mq_hr'] = chunk.loc[ends_with_n, 'mean_q_pkw_mq_hr']

        # Drop helper column if not needed
        chunk.drop(columns=['base_mq_name', 'mean_q_pkw_mq_hr'], inplace=True)

        # Prepare data for database insertion
        data_chunk = [
            (mq_name, date_id, hour_id, wert)
            for mq_name, date_id, hour_id, wert in zip(
                chunk['mq_name'], chunk['DateID'], chunk['stunde'], chunk['q_pkw_mq_hr']
            )
        ]
 
        # Send data to queue
        queue.put(data_chunk)
        
    print(f"[{current_process().name}] Finished file: {file_path}")

def store_weather_data_Pro_Bezirk(conn):
    df_final = pd.DataFrame()
    df_bezirke = dbu.fetch_data_bezirk('Bezirke', conn)
    for name in df_bezirke:
        try:
            df_wetter_bezirk = pd.read_csv('../data/raw/Bezirke Wetter/open-meteo-' + name + '.csv', header = 2)
            df_wetter_bezirk[df_wetter_bezirk.columns[0]] = pd.to_datetime(df_wetter_bezirk.iloc[:, 0], errors='coerce')
            df_wetter_bezirk['Date'] = df_wetter_bezirk.iloc[:,0].dt.strftime('%d.%m.%Y')  # Extract the date part
            df_wetter_bezirk['TimeID'] = df_wetter_bezirk.iloc[:,0].dt.hour  # Extract the time part
            df_wetter_bezirk.reset_index()
            #TODO: check if improving is possible 
            date_dim = pd.read_sql_query("SELECT DateID, Date FROM Date_dim", conn)
            df_wetter_bezirk = pd.merge(df_wetter_bezirk,  date_dim , on = 'Date', how = 'inner')
            
            df_wetter_bezirk.drop(['time','Date'], inplace = True, axis = 1)
            df_final = pd.concat([df_final, df_wetter_bezirk], ignore_index=True)
            
        except Exception as e:
            print(f"Error querying table Bezirke : {e}")
            continue  # Skip this table if there's an error
        
    #'wind_speed_10m (km/h)' is important ??
    new_order = ['DateID', 'TimeID','temperature_2m (°C)', 'relative_humidity_2m (%)', 'rain (mm)', 'snowfall (cm)', 'cloud_cover (%)']  # Specify the new order
    df_final = df_final[new_order]
    df_final.to_sql('Wetter', conn, if_exists = 'append', index = False)
    
    print("Weather Data is well stored")
        
def store_bezirke(conn,gdf_bezirke):
    # Prepare the DataFrame for SQL
    df_bezirke = gdf_bezirke.reset_index()
    df_bezirke['geometry'] = df_bezirke['geometry'].apply(lambda geom: geom.wkt)  # Convert geometry to WKT
    df_bezirke = df_bezirke.rename(columns={'name': 'Bezirk', 'geometry': 'Geometry'})

    # Insert data into the SQLite table using pandas
    df_bezirke[['Bezirk', 'Breitengrad', 'Längengrad', 'Geometry']].to_sql(
        'Bezirke', conn, if_exists='replace', index=False
    )

    print("Bezirke data saved successfully!")

    return gdf_bezirke

def store_zählstelle(conn,gdf_bezirke):
    
    excel_file_path = '../data/raw/Fahrrad/gesamtdatei-stundenwerte.xlsx'

    if os.path.exists(excel_file_path):
        df_zaehlstellen = pd.read_excel(excel_file_path, sheet_name = 'Standortdaten')
    else:
        print(f"Die Datei'{excel_file_path} wurde nicht gefunden.")
          
    df_zaehlstellen.columns = ['Zählstelle', 'Beschreibung', 'Breitengrad', 'Längengrad', 'Installationsdatum']

    # Create GeoDataFrame for Zählstellen
    geometry = [Point(xy) for xy in zip(df_zaehlstellen["Längengrad"], df_zaehlstellen["Breitengrad"])]
    gdf_zaehlstellen = gpd.GeoDataFrame(df_zaehlstellen, geometry=geometry, crs="EPSG:4326")

    # Spatial join: Match Zählstellen with Bezirke
    gdf_zaehlstellen = gpd.sjoin(gdf_zaehlstellen, gdf_bezirke, how="left", predicate="within")

    # Keep only relevant columns
    result = gdf_zaehlstellen[["Zählstelle", "name", 'Beschreibung', 'Installationsdatum']]
    result = result.rename(columns={'name': 'Bezirk'})
    #insert in the database
    result.to_sql('Standorten_Zählstelle', conn, if_exists = 'append', index = False)
    print("Standorten_Zählstelle saved successfully!")
