import sqlite3

conn = sqlite3.connect("calories.db")

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS food_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    food TEXT,
    quantity INTEGER,
    calories INTEGER,
    date TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS foods (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    food_name TEXT,
    food_category TEXT,
    serving_type TEXT,
    serving_weight INTEGER,
    calories REAL,
    protein REAL,
    carbs REAL,
    fat REAL,
    fiber REAL
)
""")
foods = [

    ("Rice", "Grains", "100 g", 100, 130, 2.7, 28.0, 0.3, 0.4),

    ("Egg", "Protein", "1 Egg", 50, 70, 6.0, 0.6, 5.0, 0.0),

    ("Chicken Breast", "Protein", "100 g", 100, 165, 31.0, 0.0, 3.6, 0.0),

    ("Banana", "Fruits", "1 Banana", 118, 105, 1.3, 27.0, 0.4, 3.1),

    ("Milk", "Dairy", "250 ml", 250, 150, 8.0, 12.0, 8.0, 0.0),

    ("Apple", "Fruits", "1 Apple", 182, 95, 0.5, 25.0, 0.3, 4.4),

    ("Paneer", "Dairy", "100 g", 100, 265, 18.0, 1.2, 20.0, 0.0),

    ("Roti", "Grains", "1 Roti", 40, 120, 3.0, 22.0, 2.0, 3.0)

]
cursor.executemany("""
 INSERT INTO foods(
    food_name,
    food_category,
    serving_type,
    serving_weight,
    calories,
    protein,
    carbs,
    fat,
    fiber
)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
""", foods)

conn.commit()
conn.close()

print("Database Created Successfully!")