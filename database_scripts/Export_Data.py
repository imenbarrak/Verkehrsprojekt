import sys
import os

# Add the path to `database_scripts` folder
sys.path.append(os.path.abspath("../database_scripts"))
import  db_utils as du
import create_tables as ct
conn = ct.create_or_open_database()
df_bezirke= du.fetch_data_df('Bezirke',conn)
def export_auto_Daten():

    try:
        df_autos_Zähler = du.fetch_data_df('Messquerschnitt',conn)
        df_mess_Autos= du.fetch_data_df('Messdaten_auto',conn)
        df_time = du.fetch_data_df('time_dim',conn)
        #df_merged = df_bezirke.merge(df_autos_Zähler, on='Bezirk', how='left')
        df_merged = df_autos_Zähler.merge(df_mess_Autos, on='MQ_KURZNAME', how='left')    
        df_merged = df_merged.merge(df_time, left_on='Time', right_on='TimeID', how='left')
        df_merged.drop(['TimeID'], axis = 1, inplace= True)
        df_merged.to_csv('../data/processed/MessDatenAuto.csv',index=False)
        print('CSV PKWMessdaten is well generated') 
    except Exception as e:
        print(f'Problem bei export to csv  {e}')
        
def  export_Wetter_Daten():
    du.fetch_data_df('Wetter',conn).to_csv('../data/processed/WetterData.csv', index = False)
    print('CSV WetterDaten is well generated')
    
def export_Fahrrad_Daten():
    try:
        df_fahrrad_Zähler = du.fetch_data_df('Standorten_Zählstelle',conn)
        df_mess_Fahrrad= du.fetch_data_df('Messdaten_Fahrrad',conn)
        df_time = du.fetch_data_df('Time_dim',conn)
        #df_merged = df_fahrrad_Zähler.merge(df_bezirke, on='Bezirk', how='left')
        df_merged = df_fahrrad_Zähler.merge(df_mess_Fahrrad, on='Zählstelle', how='left')
        df_merged = df_merged.rename(columns={'DateID': 'Date', 'TimeID':'Time'})
        df_merged = df_merged.merge(df_time, left_on='Time', right_on='TimeID', how='left')
        df_merged.drop(['TimeID'], axis = 1, inplace= True)
        df_merged.to_csv('../data/processed/MessDatenFahrrad.csv', index=False)
        print('CSV FahrradMessdaten is well generated')
    except Exception as e:
        print(f'Problem bei export to csv  {e}')

if __name__ == "__main__":
    export_auto_Daten()
    export_Wetter_Daten()
    export_Fahrrad_Daten()
    conn.close()