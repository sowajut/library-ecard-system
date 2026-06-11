import sqlite3

connection = sqlite3.connect("library.db")

cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    surname TEXT NOT NULL,
    other_names TEXT NOT NULL,
    faculty TEXT NOT NULL,
    department TEXT NOT NULL,
    year_of_entry TEXT NOT NULL,
    matric_no TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    card_status TEXT DEFAULT 'Pending',
    passport_photo TEXT,
    card_number TEXT,
    qr_code TEXT
)
""")

connection.commit()
connection.close()

print("Database created successfully!")