import sqlite3

conn = sqlite3.connect("hospital.db")
cursor = conn.cursor()

# Patients
cursor.execute("""
CREATE TABLE IF NOT EXISTS patients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT
)
""")

# Doctors
cursor.execute("""
CREATE TABLE IF NOT EXISTS doctors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    specialization TEXT,
    slots TEXT
)
""")

# Appointments
cursor.execute("""
CREATE TABLE IF NOT EXISTS appointments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient TEXT,
    doctor TEXT,
    date TEXT,
    time TEXT,
    status TEXT
)
""")

conn.commit()
conn.close()

print("✅ Database initialized")
