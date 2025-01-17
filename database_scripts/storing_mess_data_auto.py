import os
import sqlite3
import pandas as pd
import numpy as np
from multiprocessing import Process, Queue, current_process
import create_tables as ct

def store_mess_data_auto_with_Date():
    
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
    
    # Setup multiprocessing
    queue = Queue(maxsize=100)
    
    # Start writer process
    writer_process = Process(target = write_to_db_with_date, args=(queue,))
    writer_process.start()
    #print('started...')
    # Start file processors
    processes = []
    for file_info in file_infos:
        p = Process(target = process_file_with_Date, args=(file_info, queue))
        processes.append(p)
        p.start()

    # Wait for all file processors to finish
    for p in processes:
        p.join()

    # Signal writer process to stop
    queue.put(None)
    print("All files processed.")

def write_to_db_with_date(queue):
    
    """Write data to the database from a shared queue."""
    #print(f"[{current_process().name}] Writer process started.")
    conn = ct.create_or_open_database()
    cur = conn.cursor()
    while True:
        data = queue.get()
        if data is None:  # Stop signal
            break
        if data:
            try:
                
                #print(data)
                cur.executemany(
                "INSERT INTO Messdaten_auto (MQ_KURZNAME, Date, Time, q_pkw_mq_hr) VALUES (?, ?, ?, ?)",data
                )
                conn.commit()
            except sqlite3.Error as e:
                print(f"Database error in writer: {e}")
    conn.close()     

def process_file_with_Date(file_info, queue):
    
    """Process a single file."""
    year, month, file_path = file_info
    #print(f"[{current_process().name}] Starting file: {file_path}")
    
    chunk_iter = pd.read_csv(file_path, delimiter=';', compression='gzip', chunksize=10000)
    for chunk in chunk_iter:
        # Drop unnecessary columns
        chunk.drop(
            ['v_pkw_mq_hr', 'q_lkw_mq_hr', 'v_lkw_mq_hr', 'qualitaet', 'q_kfz_mq_hr', 'v_kfz_mq_hr'],
            axis=1,
            inplace=True,
        )
        #print(chunk)
        chunk['mq_name'] = chunk['mq_name'].astype(str)
        # Create base names by removing 'n' suffix
        chunk['base_mq_name'] = chunk['mq_name'].str.rstrip('n')
        chunk.rename(columns={'tag': 'Date'}, inplace=True)
        # Calculate the mean for each base_mq_name, DateID, and stunde
        mean_values = (
            chunk.groupby(['base_mq_name', 'Date', 'stunde'])['q_pkw_mq_hr']
            .mean()
            .reset_index()
            .rename(columns={'q_pkw_mq_hr': 'mean_q_pkw_mq_hr'})
        )
        mean_values['mean_q_pkw_mq_hr'] = np.floor(mean_values['mean_q_pkw_mq_hr']).astype(int)

        # Merge mean values back into the chunk
        chunk = chunk.merge(
            mean_values,
            on=['base_mq_name', 'Date', 'stunde'],
            how='left'
        )

        # Update q_pkw_mq_hr for rows with prefixed mq_name
        ends_with_n = chunk['mq_name'].str.endswith('n')
        chunk.loc[ends_with_n, 'q_pkw_mq_hr'] = chunk.loc[ends_with_n, 'mean_q_pkw_mq_hr']

        # Drop helper column if not needed
        chunk.drop(columns=['base_mq_name', 'mean_q_pkw_mq_hr'], inplace=True)

        # Prepare data for database insertion
        data_chunk = [
            (mq_name, date, hour_id, wert)
            for mq_name, date, hour_id, wert in zip(
                chunk['mq_name'], chunk['Date'], chunk['stunde'], chunk['q_pkw_mq_hr']
            )
        ]
 
        # Send data to queue
        queue.put(data_chunk)
        
    print(f"[{current_process().name}] Finished file: {file_path}")


if __name__ == "__main__":
    store_mess_data_auto_with_Date()