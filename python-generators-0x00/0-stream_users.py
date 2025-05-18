
# Generator function to stream rows from user_data table one by one

import sqlite3

def stream_users():
    # Connect to the database
    conn = sqlite3.connect('user_data.db')
    conn.row_factory = sqlite3.Row  # Enable dictionary-like row access
    cursor = conn.cursor()
    
    # Execute query to fetch all rows from user_data
    cursor.execute("SELECT * FROM user_data")
    
    # Yield each row one by one
    for row in cursor:
        yield dict(row)
    
    # Close connection
    cursor.close()
    conn.close()