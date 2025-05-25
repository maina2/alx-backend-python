import asyncio
import aiosqlite
import sqlite3 
import time 

# --- Synchronous Database Setup (for initial creation and population) ---
def setup_database(db_name='users.db'):
    """Ensures a dummy users.db exists with some data, including age."""
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
        cursor.execute("INSERT INTO users (name, email, age) VALUES ('Eve', 'eve@example.com', 55)")
        cursor.execute("INSERT INTO users (name, email, age) VALUES ('Frank', 'frank@example.com', 38)")
        cursor.execute("INSERT INTO users (name, email, age) VALUES ('Grace', 'grace@example.com', 60)")
        conn.commit()
    except sqlite3.IntegrityError:
        pass 
    finally:
        conn.close()

# --- Asynchronous Database Functions ---
async def async_fetch_users(db_name='users.db'):
    """
    Asynchronously fetches all users from the database.
    Simulates a small delay to highlight concurrency.
    """
    print("Starting async_fetch_users...")
    async with aiosqlite.connect(db_name) as db:
        await asyncio.sleep(0.1) 
        cursor = await db.execute("SELECT * FROM users")
        users = await cursor.fetchall()
        await cursor.close()
    print("Finished async_fetch_users.")
    return users

async def async_fetch_older_users(db_name='users.db'):
    """
    Asynchronously fetches users older than 40 from the database.
    Simulates a small delay to highlight concurrency.
    """
    print("Starting async_fetch_older_users...")
    async with aiosqlite.connect(db_name) as db:
        await asyncio.sleep(0.05) 
        cursor = await db.execute("SELECT * FROM users WHERE age > 40")
        older_users = await cursor.fetchall()
        await cursor.close()
    print("Finished async_fetch_older_users.")
    return older_users

async def fetch_concurrently():
    """
    Executes multiple asynchronous database queries concurrently using asyncio.gather.
    """
    print("Starting concurrent fetches...")
    start_time = time.time()

    all_users, older_users = await asyncio.gather(
        async_fetch_users(),
        async_fetch_older_users()
    )

    end_time = time.time()
    print(f"Finished concurrent fetches in {end_time - start_time:.4f} seconds.")
    
    print("\n--- All Users ---")
    for user in all_users:
        print(user)
    
    print("\n--- Users Older Than 40 ---")
    for user in older_users:
        print(user)

    return all_users, older_users

if __name__ == "__main__":
    db_file_name = 'users.db'
    setup_database(db_file_name) 

    print("Running asynchronous concurrent queries...")
    asyncio.run(fetch_concurrently())
    print("\nConcurrent query execution complete.")