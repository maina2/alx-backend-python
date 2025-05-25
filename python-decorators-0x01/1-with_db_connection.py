import sqlite3
import functools

def with_db_connection(func):
    """
    Decorator that opens a database connection, passes it to the decorated function,
    and closes it afterwards.
    Assumes the database file is 'users.db'.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn = None # Initialize conn to None
        try:
            conn = sqlite3.connect('users.db') # Open the connection
            
            # Pass the connection object as the first argument
            # or explicitly as 'conn' keyword argument if the decorated function
            # expects it that way. The prompt shows 'conn' as the first positional.
            result = func(conn, *args, **kwargs) 
            return result
        except Exception as e:
            # Handle exceptions, e.g., log them
            print(f"Database operation failed: {e}")
            raise # Re-raise the exception after handling
        finally:
            if conn:
                conn.close() # Ensure the connection is closed
    return wrapper

@with_db_connection
def get_user_by_id(conn, user_id):
    """
    Fetches a user by ID using the provided database connection.
    """
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    return cursor.fetchone()

# --- Setup for testing (create a dummy users.db if it doesn't exist) ---
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
        cursor.execute("INSERT INTO users (name, email) VALUES ('Charlie', 'charlie@example.com')")
        conn.commit()
    except sqlite3.IntegrityError:
        pass # Ignore if data already exists
    conn.close()

if __name__ == "__main__":
    setup_database() # Ensure the database and some data exist

    print("--- Fetching user by ID with automatic connection handling ---")
    user = get_user_by_id(user_id=1)
    print("User with ID 1:", user)

    user = get_user_by_id(user_id=2)
    print("User with ID 2:", user)

    user = get_user_by_id(user_id=99) # Non-existent user
    print("User with ID 99:", user) # Should print None or empty tuple