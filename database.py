import sqlite3

conn = sqlite3.connect("students.db")

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS students(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    studentid TEXT,
    studentname TEXT,
    gender TEXT,
    department TEXT,
    attendance REAL,
    studyhours REAL,
    internalmarks REAL,
    assignmentmarks REAL,
    finalexammarks REAL,
    prediction TEXT,
    confidence REAL,
    grade TEXT
)
""")

conn.commit()
conn.close()

print("Database created successfully!")