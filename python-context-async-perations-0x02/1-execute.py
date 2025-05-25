import sqlite3

class ExecuteQuery:
    """Context manager to execute an SQL query and manage connection."""
    def __init__(self, query, params=None, db_name='users.db'):
        self.query = query
        self.params = params if params is not None else ()
        self.db_name = db_name
        self.conn = None
        self.results = None

    def __enter__(self):
        try:
            self.conn = sqlite3.connect(self.db_name)
            cursor = self.conn.cursor()
            cursor.execute(self.query, self.params)
            self.results = cursor.fetchall()
            return self.results
        except Exception as e:
            print(f"Error executing query: {e}")
            self.results = []
            raise
        
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
            email TEXT UNIQUE NOT NULL,
            age INTEGER
        )
    ''')
    try:
        cursor.execute("INSERT INTO users (name, email, age) VALUES ('Alice', 'alice@example.com', 30)")
        cursor.execute("INSERT INTO users (name, email, age) VALUES ('Bob', 'bob@example.com', 22)")
        cursor.execute("INSERT INTO users (name, email, age) VALUES ('Charlie', 'charlie@example.com', 45)")
        cursor.execute("INSERT INTO users (name, email, age) VALUES ('David', 'david@example.com', 28)")
        cursor.execute("INSERT INTO users (name, email, age) VALUES ('Eve', 'eve@example.com', 20)")
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    finally:
        conn.close()

if __name__ == "__main__":
    db_file_name = 'users.db'
    setup_database(db_file_name)

    print("--- Fetching users older than 25 ---")
    query_str = "SELECT * FROM users WHERE age > ?"
    param_val = 25

    try:
        with ExecuteQuery(query_str, (param_val,)) as results:
            print(f"Query: '{query_str}' with param: {param_val}")
            print("Results:")
            if results:
                for row in results:
                    print(row)
            else:
                print("No results found.")
    except Exception as e:
        print(f"An error occurred during query execution: {e}")

    print("\n--- Fetching all users ---")
    try:
        with ExecuteQuery("SELECT * FROM users") as all_users:
            print("Query: 'SELECT * FROM users'")
            print("Results:")
            for user_row in all_users:
                print(user_row)
    except Exception as e:
        print(f"An error occurred during query execution: {e}")

    print("\n--- Testing with a bad query ---")
    try:
        with ExecuteQuery("SELECT * FROM non_existent_table") as bad_results:
            print("Results from bad query (should not be printed):", bad_results)
    except sqlite3.OperationalError as e:
        print(f"Caught expected error: {e}")
    except Exception as e:
        print(f"Caught unexpected error: {e}")