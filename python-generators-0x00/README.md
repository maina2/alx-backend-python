Project Overview
This project demonstrates the use of Python generators to stream rows from a MySQL database one by one, optimizing memory usage. The script seed.py sets up a MySQL database (ALX_prodev), creates a table (user_data), populates it with data from a CSV file (user_data.csv), and provides a generator function to stream the table's rows. The project is designed to work with the provided 0-main.py script for testing.
Objectives
Create a MySQL database (ALX_prodev) and a table (user_data) with fields:
user_id (UUID, Primary Key, Indexed)

name (VARCHAR, NOT NULL)

email (VARCHAR, NOT NULL)

age (DECIMAL, NOT NULL)

Populate the table with data from user_data.csv.

Implement a generator (stream_db_rows) to stream rows from the user_data table one by one.

Prerequisites
Python 3.6+

MySQL Server (running locally or accessible)

Python Libraries:
mysql-connector-python (pip install mysql-connector-python)

CSV File:
A user_data.csv file with columns: user_id, name, email, age.

