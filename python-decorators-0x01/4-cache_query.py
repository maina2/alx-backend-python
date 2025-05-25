import time
import sqlite3
import functools

# Global cache for storing query results
query_cache = {}

# --- Decorator from previous task: with_db_connection ---
def with_db_connection(func):
    """Decorator to open and close database connections."""
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

# --- New decorator: cache_query ---
def cache_query(func):
    """
    Decorator that caches query results based on the SQL query string.
    """
    @functools.wraps(func)
    def wrapper(conn, query, *args, **kwargs):
        if query in query_cache:
            print(f"DEBUG: Returning cached result for query: {query}")
            return query_cache[query]
        
        print(f"DEBUG: Executing query and caching result: {query}")
        result = func(conn, query, *args, **kwargs)
        query_cache[query] = result
        return result
    return wrapper

@with_db_connection
@cache_query
def fetch_users_with_cache(conn, query):
    """
    Fetches users from the database using the provided query.
    Simulates a delay to observe caching effect.
    """
    cursor = conn.cursor()
    cursor.execute(query)
    time.sleep(0.5) 
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

    print("--- First call: Fetching users (should hit DB and cache) ---")
    start_time = time.time()
    users = fetch_users_with_cache(query="SELECT * FROM users")
    end_time = time.time()
    print(f"Users (first call): {users}")
    print(f"Time taken: {end_time - start_time:.4f} seconds")
    print(f"Cache content: {query_cache.keys()}")

    print("\n--- Second call: Fetching users (should use cache) ---")
    start_time = time.time()
    users_again = fetch_users_with_cache(query="SELECT * FROM users")
    end_time = time.time()
    print(f"Users (second call): {users_again}")
    print(f"Time taken: {end_time - start_time:.4f} seconds (should be much faster)")
    print(f"Cache content: {query_cache.keys()}")

    print("\n--- Third call: Fetching different data (should hit DB and cache new query) ---")
    start_time = time.time()
    specific_user_query = "SELECT name, email FROM users WHERE id = 1"
    specific_user = fetch_users_with_cache(query=specific_user_query)
    end_time = time.time()
    print(f"Specific User: {specific_user}")
    print(f"Time taken: {end_time - start_time:.4f} seconds")
    print(f"Cache content: {query_cache.keys()}")

    print("\n--- Fourth call: Fetching different data again (should use cache) ---")
    start_time = time.time()
    specific_user_again = fetch_users_with_cache(query=specific_user_query)
    end_time = time.time()
    print(f"Specific User (again): {specific_user_again}")
    print(f"Time taken: {end_time - start_time:.4f} seconds (should be much faster)")
    print(f"Cache content: {query_cache.keys()}")