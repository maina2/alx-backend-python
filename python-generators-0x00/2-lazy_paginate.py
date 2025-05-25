import sqlite3
import uuid
import random
from faker import Faker

# --- Simulation of external 'seed' module and 'paginate_users' function ---
# This section is for making the script runnable independently for testing.
# In your actual environment, these would be imported from 'seed.py'.

class Seed:
    """Simulates a database connection utility."""
    def connect_to_prodev(self):
        conn = sqlite3.connect(':memory:')
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_data (
                user_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                age INTEGER
            )
        ''')
        
        # Insert sample data for pagination
        sample_data = []
        fake = Faker()
        for _ in range(200):
            sample_data.append((
                str(uuid.uuid4()),
                fake.name(),
                fake.email(),
                random.randint(18, 120)
            ))
        cursor.executemany("INSERT OR IGNORE INTO user_data VALUES (?, ?, ?, ?)", sample_data)
        conn.commit()
        return conn

seed = Seed()

def paginate_users(page_size, offset):
    """Fetches a single page of user data from the database."""
    connection = seed.connect_to_prodev()
    cursor = connection.cursor()
    cursor.execute(f"SELECT user_id, name, email, age FROM user_data LIMIT {page_size} OFFSET {offset}")
    rows = cursor.fetchall()
    connection.close()

    dict_rows = []
    for row in rows:
        dict_rows.append({
            'user_id': row[0],
            'name': row[1],
            'email': row[2],
            'age': row[3]
        })
    return dict_rows

# --- End of simulation ---


def lazy_pagination(page_size):
    """
    Generator function to lazily load paginated data from the users database.
    """
    offset = 0
    while True:
        page_data = paginate_users(page_size, offset)
        if not page_data:
            break
        yield page_data
        offset += page_size


if __name__ == '__main__':
    import sys

    print("Lazy loading paginated data (first 7 users shown):")
    try:
        user_count = 0
        for page in lazy_pagination(50):
            for user in page:
                print(user)
                user_count += 1
                if user_count >= 7:
                    break
            if user_count >= 7:
                break
    except BrokenPipeError:
        sys.stderr.close()

    print("\n---")
    print("Demonstrating full pagination (counting users):")
    try:
        total_users_fetched = 0
        for page in lazy_pagination(25):
            total_users_fetched += len(page)
        print(f"Total users fetched across all pages: {total_users_fetched}")
    except BrokenPipeError:
        sys.stderr.close()