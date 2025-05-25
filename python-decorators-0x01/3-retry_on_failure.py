import time
import sqlite3
import functools


def with_db_connection(func):
    """
    Decorator that opens a database connection, passes it to the decorated function,
    and closes it afterwards. Assumes the database file is 'users.db'.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn = None
        try:
            conn = sqlite3.connect('users.db')
            result = func(conn, *args, **kwargs)
            return result
        except Exception as e:
            print(f"Database operation failed: {e}")
            raise
        finally:
            if conn:
                conn.close()
    return wrapper

# --- New decorator
def retry_on_failure(retries=3, delay=1):

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            while attempts < retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempts += 1
                    print(f"Attempt {attempts}/{retries} failed: {e}")
                    if attempts < retries:
                        print(f"Retrying in {delay} second(s)...")
                        time.sleep(delay)
                    else:
                        print(f"Max retries ({retries}) exceeded. Raising exception.")
                        raise 
        return wrapper
    return decorator 

@with_db_connection
@retry_on_failure(retries=3, delay=1)
def fetch_users_with_retry(conn):
    """
    Fetches all users from the database.
    Includes a simulated transient error for testing retry logic.
    """
    cursor = conn.cursor()
    

    global CALL_COUNT # Use a global counter for simulation
    if not hasattr(fetch_users_with_retry, 'call_count'):
        fetch_users_with_retry.call_count = 0
    
    fetch_users_with_retry.call_count += 1
    
    if fetch_users_with_retry.call_count < 3: # Fail on first 2 calls
        raise sqlite3.OperationalError("Database is temporarily unavailable (simulated error).")
    
    cursor.execute("SELECT * FROM users")
    return cursor.fetchall()

# --- Setup for testing 
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
        pass
    conn.close()

if __name__ == "__main__":
    setup_database()

    print("--- Attempting to fetch users with automatic retry on failure ---")
    try:
        users = fetch_users_with_retry()
        print("\nSuccessfully fetched users:")
        print(users)
    except Exception as e:
        print(f"\nFailed to fetch users after all retries: {e}")

    print("\n--- Testing a function that should succeed on the first try ---")
    # Reset call count for a new test
    if hasattr(fetch_users_with_retry, 'call_count'):
        del fetch_users_with_retry.call_count
    
    @with_db_connection
    @retry_on_failure(retries=1, delay=0.1)
    def simple_fetch(conn):
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM users WHERE id = 1")
        return cursor.fetchone()

    try:
        user_name = simple_fetch()
        print("Successfully fetched single user:", user_name)
    except Exception as e:
        print(f"Failed simple fetch: {e}")