
import sqlite3

def create_or_open_database():
    print("""Establish SQLite connection.""")
    return sqlite3.connect("..\\data\\processed\\my_database_project.db")


def close_database(conn, cur):
    cur.close()
    conn.close()
    print("connection and cursor closed")
        
def create_table_date (cur):

    cur.execute("""
        CREATE TABLE IF NOT EXISTS Date_dim (
        DateID INTEGER PRIMARY KEY AUTOINCREMENT,
        Date TEXT NOT NULL,
        year INTEGER NOT NULL,
        month INTEGER NOT NULL,
        day INTEGER NOT NULL,
        day_of_the_week TEXT NOT NULL,
        is_holiday BOOLEAN DEFAULT 0,
        quarter INTEGER NOT NULL
    )
    """)
    print("Table Date_dim is created")

def create_table_time(cur):
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS time_dim (
        TimeID INTEGER PRIMARY KEY,
        time_of_the_day TEXT NOT NULL 
        )
    """)
    print("table time_dim is created")

def create_table_Bezirke(cur):
    
    cur.execute('''
        CREATE TABLE IF NOT EXISTS Bezirke (
        Bezirk TEXT PRIMARY KEY ,
        Breitengrad REAL,
        Längengrad REAL,
        geometry TEXT
    )
    ''')
    print("table Bezirke is created")

def create_table_zählstelle(cur):
    
    cur.execute('''
    CREATE TABLE IF NOT EXISTS Standorten_Zählstelle (
        Zählstelle TEXT PRIMARY KEY,
        Bezirk TEXT,
        Beschreibung TEXT,
        Installationsdatum DATE
    )
    ''')
    print("Table Standorten_Zählstelle is created")
    
    
def create_table_Messquerschnitt(cur):
    cur.execute('''
        CREATE TABLE IF NOT EXISTS Messquerschnitt (
        MQ_KURZNAME TEXT PRIMARY KEY,
        Bezirk TEXT,
        STRASSE TEXT,
        POSITION TEXT,
        POS_DETAIL TEXT,
        INBETRIEBNAHME TEXT
    )
    ''')
    print("Table Messquerschnitt is created")
    
def create_table_Messdaten_auto(cur):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS Messdaten_auto(
        MQ_KURZNAME TEXT NOT NULL,
        DateId DATETIME NOT NULL,
        TimeId INTEGER,
        q_pkw_mq_hr INTEGER,
        FOREIGN KEY (MQ_KURZNAME) REFERENCES Messquerschnitt(MQ_KURZNAME),
        FOREIGN KEY (DateId) REFERENCES Date_dim(DateID),
        FOREIGN KEY (TimeId) REFERENCES Time_dim(timeID),
        UNIQUE(MQ_KURZNAME, DateId, TimeId)
        )
    """)
    print("Table MessdatenAuto is created")
    
def create_table_messdaten_Fahrrad (cur):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS Messdaten_Fahrrad (
        Zählstelle TEXT NOT NULL,
        DateID DATETIME NOT NULL,
        TimeID INTEGER NOT NULL,
        Wert INTEGER,
        FOREIGN KEY (Zählstelle) REFERENCES Standorten_Zählstelle(Zählstelle),
        FOREIGN KEY (DateID) REFERENCES Date_dim(DateID),
        FOREIGN KEY (TimeID) REFERENCES Time_dim(TimeID),
        UNIQUE(Zählstelle, DateID, TimeID)
        )
    """)
    
    print("Table MessdatenFahrrad is created")
    

def create_indexes(cur):
    #add index for primary key + index for date
    cur.execute('CREATE INDEX IF NOT EXISTS idx_mq_name ON Messdaten_auto(MQ_KURZNAME);')
    cur.execute('CREATE INDEX IF NOT EXISTS idx_mq_name ON Messdaten_Fahrrad(MQ_KURZNAME);')
    
def add_index(cur, table_name, column_name):
    index_name = f"{table_name}_{column_name}_idx"  # Naming the index
    
    try:
        # SQL command to create an index
        cur.execute(f"CREATE INDEX IF NOT EXISTS {index_name} ON {table_name} ({column_name})")
        print(f"Index {index_name} created successfully on {column_name} in {table_name}.")
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")