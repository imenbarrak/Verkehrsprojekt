import os
import sqlite3
import pandas as pd
from multiprocessing import Process, Queue, current_process

def get_connection():
    """Establish SQLite connection."""
    return sqlite3.connect("my_database_project.db")

def write_to_db(queue):
    """Write data to the database from a shared queue."""
    conn = get_connection()
    cur = conn.cursor()
    while True:
        data = queue.get()
        if data is None:  # Stop signal
            break
        if data:
            try:
                cur.executemany(
                "INSERT INTO Messdaten_auto (MQ_KURZNAME, DateID, TimeID, q_pkw_mq_hr) VALUES (?,?,?,?)",data
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
        
        # Map DateID and Mq_id
        chunk['DateID'] = chunk['tag'].map(date_lookup)
        chunk['mq_name'] = chunk['mq_name'].astype(str)
        #check the mq_name ending with n
        ends_with_n = chunk['mq_name'].str.endswith('n')
    
        mean_values = chunk.loc[ends_with_n].groupby(['mq_name','DateID','stunde'])['q_pkw_mq_hr'].mean()
        
        for mq_name, mean_val in mean_values.items():
            chunk.loc[(chunk['mq_name'] == mq_name) & ends_with_n, 'q_pkw_mq_hr'] = mean_val

        # Prepare data for database insertion
        data_chunk = [
            (mq_name, date_id, hour_id, wert)
            for mq_name, date_id, hour_id, wert  in zip(
                chunk['mq_name'], chunk['DateID'], chunk['stunde'], chunk['q_pkw_mq_hr']
            )
        ]
        # Send data to queue
        queue.put(data_chunk)
    
    print(f"[{current_process().name}] Finished file: {file_path}")

def preload_lookup_tables():
    """Preload lookup tables for dates and mq_names."""
    conn = get_connection()
    print()
    cur = conn.cursor()

    # Preload date lookup
    cur.execute("SELECT date, DateID FROM Date_dim")
    date_lookup = dict(cur.fetchall())
    
    conn.close()
    return date_lookup#, mq_lookup

def main():
    # File paths for all files to process
    file_infos = []
    for year in range(2018, 2024):
        for month in range(1, 13):
            str_month = f"{month:02d}"  # Ensure two-digit month format
            file_path = f"Auto_{year}/mq_hr_{year}_{str_month}.csv.gz"
            if os.path.exists(file_path):
                file_infos.append((year, month, file_path))
            else:
                print(f"File not found: {file_path}")

    print(f"Found {len(file_infos)} files to process.")
    print('files are got')
    # Preload lookup tables
  
    date_lookup = preload_lookup_tables()
    # Setup multiprocessing
    queue = Queue(maxsize=100)
    

    # Start writer process
    writer_process = Process(target=write_to_db, args=(queue,))
    writer_process.start()

    # Start file processors
    processes = []
    for file_info in file_infos:
        p = Process(target=process_file, args=(file_info, date_lookup, queue))
        processes.append(p)
        p.start()

    # Wait for all file processors to finish
    for p in processes:
        p.join()

    # Signal writer process to stop
    queue.put(None)
    print("All files processed.")

if __name__ == "__main__":
    main()
