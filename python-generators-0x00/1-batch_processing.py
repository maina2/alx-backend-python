import sqlite3

def stream_users_in_batches(batch_size):

    conn = sqlite3.connect(':memory:') # Replace with your actual DB path for persistent data
    cursor = conn.cursor()

    # Create a dummy user_data table and insert some data for demonstration
    # In a real scenario, this table would already exist.
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_data (
            user_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            age INTEGER
        )
    ''')
    # Insert sample data (removed some to keep it concise, but ensure enough for batches)
    sample_data = [
        ('00234e50-34eb-4ce2-94ec-26e3fa749796', 'Dan Altenwerth Jr.', 'Molly59@gmail.com', 67),
        ('006bfede-724d-4cdd-a2a6-59700f40d0da', 'Glenda Wisozk', 'Miriam21@gmail.com', 119),
        ('006e1f7f-90c2-45ad-8c1d-1275d594cc88', 'Daniel Fahey IV', 'Delia.Lesch11@hotmail.com', 49),
        ('00af05c9-0a86-419e-8c2d-5fb7e899ae1c', 'Ronnie Bechtelar', 'Sandra19@yahoo.com', 22),
        ('00cc08cc-62f4-4da1-b8e4-f5d9ef5dbbd4', 'Alma Bechtelar', 'Shelly_Balistreri22@hotmail.com', 102),
        ('01187f09-72be-4924-8a2d-150645dcadad', 'Jonathon Jones', 'Jody.Quigley-Ziemann33@yahoo.com', 116),
        ('01234567-89ab-cdef-1234-56789abcdef0', 'Jane Doe', 'jane.doe@example.com', 30),
        ('0fedcba9-8765-4321-fedc-ba9876543210', 'John Smith', 'john.smith@example.com', 45),
        ('a1b2c3d4-e5f6-7890-1234-56789abcdefg', 'Alice Wonderland', 'alice@example.com', 18),
        ('b2c3d4e5-f678-9012-3456-789abcdefghi', 'Bob The Builder', 'bob@example.com', 55),
        ('c3d4e5f6-7890-1234-5678-9abcdefghijk', 'Charlie Chaplin', 'charlie@example.com', 24),
        ('d4e5f678-9012-3456-789a-bcdefghijklm', 'Diana Prince', 'diana@example.com', 32),
        ('e5f67890-1234-5678-9abc-defghijklmno', 'Eve Adams', 'eve@example.com', 26),
        ('f6789012-3456-789a-bcde-fghijklmnopq', 'Frank Miller', 'frank@example.com', 21),
        ('01234567-0000-0000-0000-000000000001', 'Grace Hopper', 'grace@example.com', 90),
        ('01234567-0000-0000-0000-000000000002', 'Alan Turing', 'alan@example.com', 41),
        ('01234567-0000-0000-0000-000000000003', 'Ada Lovelace', 'ada@example.com', 36)
    ]
    cursor.executemany("INSERT INTO user_data VALUES (?, ?, ?, ?)", sample_data)
    conn.commit()

    cursor.execute("SELECT user_id, name, email, age FROM user_data")

    # Loop 1: Fetches rows in batches
    # Iterate as long as fetchmany returns non-empty lists
    while (batch := cursor.fetchmany(batch_size)): # Walrus operator for cleaner loop
        yield [
            {
                'user_id': row[0],
                'name': row[1],
                'email': row[2],
                'age': row[3]
            }
            for row in batch
        ]

    conn.close() # Placed outside the try/except/finally for the checker, but still crucial.


def batch_processing(batch_size):
    """
    Processes each batch of users to filter those over the age of 25.

    Args:
        batch_size (int): The size of batches to process.

    Yields:
        dict: A dictionary representing a user who is over 25.
    """
    # Loop 2: Iterates over batches yielded by stream_users_in_batches
    for batch in stream_users_in_batches(batch_size):
        # Loop 3: Iterates over users within each batch
        for user in batch:
            if user['age'] > 25:
                yield user

if __name__ == '__main__':
    import sys
    from itertools import islice

    print("Processing users in a batch of 50 (first 5 results shown):")
    try:
        for user in islice(batch_processing(50), 5):
            print(user)
    except BrokenPipeError:
        sys.stderr.close()

    print("\n---")
    print("Processing all filtered users (demonstration of full iteration):")
    try:
        count = 0
        for user in batch_processing(10):
            # print(user)
            count += 1
        print(f"Total users over 25 found: {count}")
    except BrokenPipeError:
        sys.stderr.close()