import create_tables as ct
import store_data as st
import db_utils as dbu
import storing_mess_data_auto  as stm

# Fetch administrative boundaries for Berlin Bezirke

def main():
    try:
        conn = ct.create_or_open_database()
        cur = conn.cursor()
        
        gdf_bezirke = dbu.get_geo()
        #TODO. More separation of concerns if possible 
        #avoid opening the database many times 
        
        #Table creation
        #ct.create_table_date(cur)
        ct.create_table_time(cur)
        ct.create_table_Bezirke(cur)
        #ct.create_table_zählstelle(cur)
        #ct.create_table_Messquerschnitt(cur)
        #ct.create_table_Messdaten_auto(cur)
        ct.create_table_Messdaten_auto_with_date(cur)
        ct.create_table_messdaten_Fahrrad(cur)
        #ct.create_indexes(cur)
        
        #storing data
        #st.store_date(cur)
        st.store_time(cur)
        st.store_bezirke(conn, gdf_bezirke)
        st.store_weather_data_Pro_Bezirk(conn)
        st.store_zählstelle(conn, gdf_bezirke)
        st.store_mess_data_fahrrad(conn)
        st.store_messquerschnitt(conn, gdf_bezirke)
        #st.store_mess_data_auto()
        ####st.store_mess_data_auto_with_Date()

        #stm.store_mess_data_auto_with_Date()
        conn.commit()
        print("All tasks completed successfully!")
        
    finally:
            ct.close_database(conn, cur)


# Main function to orchestrate the workflow

if __name__ == "__main__":
    main()