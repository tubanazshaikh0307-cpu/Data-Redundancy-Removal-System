import sqlite3

conn = sqlite3.connect('database.db')

cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT UNIQUE
)
''')

conn.commit()
conn.close()

print("Database created successfully!")