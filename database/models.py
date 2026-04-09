def create_tables(conn):
    """Create the required database tables if they do not exist."""
    cur = conn.cursor()
    
    # Create Users table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS Users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            skills TEXT NOT NULL,
            experience INTEGER,
            location TEXT
        )
    ''')
    
    # Create Jobs table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS Jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            company TEXT NOT NULL,
            location TEXT,
            description TEXT,
            url TEXT,
            source TEXT
        )
    ''')
    
    conn.commit()

def insert_job(title, company, location, description, url, source):
    """Insert a job into the Jobs table if it doesn't already exist (based on URL)."""
    from database.db import get_db_connection
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Check if job exists
    cur.execute('SELECT id FROM Jobs WHERE url = ?', (url,))
    if not cur.fetchone():
        cur.execute('''
            INSERT INTO Jobs (title, company, location, description, url, source)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (title, company, location, description, url, source))
        conn.commit()
    conn.close()

def get_all_jobs():
    """Retrieve all jobs from the database."""
    from database.db import get_db_connection
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM Jobs')
    jobs = cur.fetchall()
    conn.close()
    return [dict(ix) for ix in jobs]
