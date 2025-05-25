import sqlite3
import functools

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

def transactional(func):
    """
    Decorator that wraps a database operation in a transaction.
    Commits on success, rolls back on error.
    """
    @functools.wraps(func)
    def wrapper(conn, *args, **kwargs):
        try:
            conn.execute("BEGIN TRANSACTION")
            result = func(conn, *args, **kwargs)
            conn.commit()
            print("Transaction committed successfully.")
            return result
        except Exception as e:
            conn.rollback()
            print(f"Transaction rolled back due to error: {e}")
            raise
    return wrapper

@with_db_connection
@transactional
def update_user_email(conn, user_id, new_email):
    """Updates a user's email in the database."""
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET email = ? WHERE id = ?", (new_email, user_id))
    # Uncomment next line to simulate an error for rollback testing
    # if user_id == 2:
    #     raise ValueError("Simulating an error for rollback!")
    return cursor.rowcount

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
        cursor.execute("INSERT INTO users (name, email) VALUES ('Charlie', 'charlie@example.com')")
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    conn.close()

def get_user_email(user_id):
    """Helper to verify email after update."""
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT email FROM users WHERE id = ?", (user_id,))
    email = cursor.fetchone()
    conn.close()
    return email[0] if email else None


if __name__ == "__main__":
    setup_database()

    print("--- Initial Emails ---")
    print(f"User 1 email: {get_user_email(1)}")
    print(f"User 2 email: {get_user_email(2)}")

    print("\n--- Attempting to update user 1 email (should commit) ---")
    try:
        rows_affected = update_user_email(user_id=1, new_email='alice.new@example.com')
        print(f"Updated {rows_affected} row(s).")
    except Exception as e:
        print(f"Update failed: {e}")
    print(f"User 1 email after attempt: {get_user_email(1)}")

    print("\n--- Attempting to update user 2 email with simulated error (should rollback) ---")
    try:
        rows_affected = update_user_email(user_id=2, new_email='bob.fail@example.com')
        print(f"Updated {rows_affected} row(s).")
    except ValueError as e:
        print(f"Caught expected error: {e}")
    except Exception as e:
        print(f"Update failed unexpectedly: {e}")
    print(f"User 2 email after attempt: {get_user_email(2)}")