import sqlite3

class DatabaseConnection:
    """A class-based context manager for SQLite database connections."""
    def __init__(self, db_name='users.db'):
        self.db_name = db_name
        self.conn = None

    def __enter__(self):
        self.conn = sqlite3.connect(self.db_name)
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            self.conn.close()
        return False

# --- Setup for testing ---
def setup_database(db_name='users.db'):
    conn = sqlite3.connect(db_name)
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
        cursor.execute("INSERT INTO users (name, email) VALUES ('Charlie', 'charlie@example.com')")
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    finally:
        conn.close()

if __name__ == "__main__":
    db_file_name = 'users.db'
    setup_database(db_file_name)

    print(f"--- Fetching all users from {db_file_name} ---")
    
    try:
        with DatabaseConnection(db_file_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users")
            results = cursor.fetchall()
            print("Query Results:")
            for row in results:
                print(row)
    except Exception as e:
        print(f"An error occurred: {e}")

    print("\n--- Testing error handling ---")
    try:
        with DatabaseConnection(db_file_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM non_existent_table")
            results = cursor.fetchall()
            print("Results (should not appear if error occurs):", results)
    except sqlite3.OperationalError as e:
        print(f"Caught expected error: {e}")
    except Exception as e:
        print(f"Caught unexpected error: {e}")

    print("\n--- Demonstrating connection is closed ---")
    try:
        conn_outside_with = None
        with DatabaseConnection(db_file_name) as temp_conn:
            conn_outside_with = temp_conn
            # Check connection status if specific methods exist (e.g., in_transaction for SQLite)
            # print(f"Inside 'with' block: Connection status: {conn_outside_with.in_transaction}") 
        
        if conn_outside_with:
            try:
                conn_outside_with.cursor() 
            except sqlite3.ProgrammingError as e:
                print(f"Outside 'with' block: Caught expected error when trying to use closed connection: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during connection test: {e}")