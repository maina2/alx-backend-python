import sqlite3
import functools
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def log_queries(func):
    """Decorator to log SQL queries."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        query = None
        if args:
            query = args[0] 
        if 'query' in kwargs:
            query = kwargs['query']
        
        if query:
            logging.info(f"Executing SQL Query: {query}")
        else:
            logging.warning("No 'query' argument found for logging.")
            
        return func(*args, **kwargs)
    return wrapper

@log_queries
def fetch_all_users(query):
    """Fetches all users from 'users.db'."""
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results

# --- Setup for testing ---
def setup_database():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL
        )
    ''')
    try:
        cursor.execute("INSERT INTO users (name, email) VALUES ('Alice', 'alice@example.com')")
        cursor.execute("INSERT INTO users (name, email) VALUES ('Bob', 'bob@example.com')")
        conn.commit()
    except sqlite3.IntegrityError:
        pass # Data already exists
    conn.close()

if __name__ == "__main__":
    setup_database()

    print("\n--- Fetching all users ---")
    users = fetch_all_users(query="SELECT * FROM users")
    print("Fetched Users:", users)

    print("\n--- Fetching a specific user ---")
    specific_user = fetch_all_users(query="SELECT name FROM users WHERE id = 1")
    print("Fetched Specific User:", specific_user)