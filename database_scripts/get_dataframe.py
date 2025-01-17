
import  db_utils as du
import create_tables as ct

def time_of_the_day_as_number(time_of_the_day):
        if time_of_the_day == 'nachts': 
            return 0
        if time_of_the_day == 'morgens':
            return 1
        if time_of_the_day == 'vormittags':
            return 2
        if time_of_the_day == 'mittags':
            return 3
        if time_of_the_day == 'nachmittags':
            return 4
        else:
            return 5
        
def merge_dataframe():
        
    conn = ct.create_or_open_database()
    df_fahrrad_Zähler = du.fetch_data_df('Standorten_Zählstelle',conn)
    df_mess_Fahrrad= du.fetch_data_df('Messdaten_Fahrrad',conn)
    df_bezirke= du.fetch_data_df('Bezirke',conn)
    df_date = du.fetch_data_df('Date_dim',conn)
    df_time = du.fetch_data_df('Time_dim',conn)
    df_wetter = du.fetch_data_df('Wetter',conn)
    #type conversion inside the dataframe
    df_time['TimeID'] = df_time['TimeID'].astype('int')
    df_date['DateID'] = df_date['DateID'].astype('int')
    df_wetter['TimeID'] = df_wetter['TimeID'].astype('int')
    df_wetter['DateID'] = df_wetter['DateID'].astype('int32')
    df_date['year'] = df_date['year'].astype('int')
    df_date['month'] = df_date['month'].astype('int')
    df_date['day'] = df_date['day'].astype('int')
    df_date['is_holiday'] = df_date['is_holiday'].astype('bool')
    df_date['quarter'] = df_date['quarter'].astype('int')
    df_mess_Fahrrad['TimeID'] = df_mess_Fahrrad['TimeID'].astype('int')
    df_mess_Fahrrad['DateID'] = df_mess_Fahrrad['DateID'].astype('int')
    #df_mess_Fahrrad['Wert'] = df_mess_Fahrrad['Wert'].astype('int32')

    df_wetter['temperature_2m (°C)'] = df_wetter['temperature_2m (°C)'].astype('float32')
    df_wetter['relative_humidity_2m (%)'] = df_wetter['relative_humidity_2m (%)'].astype('float32')
    df_wetter['rain (mm)'] = df_wetter['rain (mm)'].astype('float32')
    df_wetter['snowfall (cm)'] = df_wetter['snowfall (cm)'].astype('float32')
    df_wetter['cloud_cover (%)'] = df_wetter['cloud_cover (%)'].astype('float32')
   
    #df_fahrrad_Zähler['Zählstelle_ID'] = range(0, df_fahrrad_Zähler.shape[0])
    #df_fahrrad_Zähler['Zählstelle_ID'] = df_fahrrad_Zähler['Zählstelle_ID'].astype('int')
    #df_bezirke['Bezirk_ID'] =  range(0, df_bezirke.shape[0])
    #df_bezirke['Bezirk_ID'] = df_bezirke['Bezirk_ID'].astype('int')

   
    df_time['timeoftheday']=df_time['time_of_the_day'].apply(time_of_the_day_as_number)
    df_time['timeoftheday'] = df_time['timeoftheday'].astype('int')
    df_merged = df_bezirke.merge(df_fahrrad_Zähler, on='Bezirk', how='left')
    df_merged = df_merged.merge(df_mess_Fahrrad, on='Zählstelle', how='left')
    df_merged = df_merged.merge(df_wetter, on=['DateID','TimeID', 'Bezirk'], how='left')
    df_merged = df_merged.merge(df_date, on='DateID', how='left')
    df_merged = df_merged.merge(df_time, on='TimeID', how='left')
    #print(df_merged.info())
    #df_merged.drop(['time_of_the_day','Breitengrad', 'Längengrad', 'Geometry','Bezirk','Date','Beschreibung','Installationsdatum','Zählstelle'], axis = 1, inplace= True)
    #df_merged.dropna(inplace=True, axis= 0)  # the Bezirk Reinickendorf   wurde gelöscht  id= 7
    
    return df_merged

def merge_dataframe_autos():
        
    conn = ct.create_or_open_database()
    df_autos_Zähler = du.fetch_data_df('Messquerschnitt',conn)
    df_mess_Autos= du.fetch_data_df('Messdaten_auto',conn)
    df_time = du.fetch_data_df('Time_dim',conn)
    df_wetter = du.fetch_data_df('Wetter',conn)
    #df_merged = df_bezirke.merge(df_autos_Zähler, on='Bezirk', how='left')
    df_merged = df_mess_Autos.merge(df_autos_Zähler, on='MQ_KURZNAME', how='left')
    df_merged = df_merged.merge(df_time, left_on='Time', right_on='TimeID', how='left')
    df_merged = df_merged.merge(df_wetter, on=['Date','TimeID','Bezirk'],how='left')
    
    return df_merged