import sqlite3

# Set the location of the SQLite database
DB_FILE = "database.db"

# Open a connection to the database
with sqlite3.connect(DB_FILE) as conn:
    # Create a new cursor
    c = conn.cursor()

    # Create a table to store user data
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            batch TEXT NOT NULL
        )
    """)

    # Create a table to store credit card names
    c.execute("""
    CREATE TABLE payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    card_name TEXT NOT NULL
    
     )
     """)





 


    # Save the changes to the database
conn.commit()
