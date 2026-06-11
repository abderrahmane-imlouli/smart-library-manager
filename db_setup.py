import sqlite3

conn = sqlite3.connect("library.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS books(
    code TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    copies INTEGER NOT NULL,
    borrowed INTEGER DEFAULT 0
)
""")

conn.commit()
conn.close()

print(" Database created successfully!")
