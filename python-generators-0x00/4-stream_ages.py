#!/usr/bin/python3
# 4-stream_ages.py
# Generator to stream user ages and calculate average age memory-efficiently

import sqlite3

def stream_user_ages():
    # Connect to the database
    conn = sqlite3.connect('user_data.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Fetch ages one by one
    cursor.execute("SELECT age FROM user_data")
    
    # Yield each age
    for row in cursor:
        yield row['age']
    
    cursor.close()
    conn.close()

def calculate_average_age():
    total_age = 0
    count = 0
    
    for age in stream_user_ages():
        total_age += age
        count += 1
    
    average_age = total_age / count if count > 0 else 0
    print(f"Average age of users: {average_age}")

# Run the calculation
calculate_average_age()