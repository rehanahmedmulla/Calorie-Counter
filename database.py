import sqlite3

conn = sqlite3.connect("calories.db")

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS food_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    food TEXT,
    quantity INTEGER,
    calories INTEGER
)
""")

conn.commit()
conn.close()

print("Database Created Successfully!")