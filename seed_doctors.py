import sqlite3

doctors = [
    ("Dr. Anita Rao", "Gynecologist", "10:00,11:00,14:00"),
    ("Dr. Rajesh Kumar", "Cardiologist", "09:00,13:00,16:00"),
    ("Dr. Meera Nair", "Dermatologist", "11:00,15:00"),
    ("Dr. Arun Menon", "Orthopedic", "10:30,12:30"),
    ("Dr. Priya Shah", "Pediatrician", "09:30,14:30"),
    ("Dr. Sanjay Verma", "Neurologist", "10:00,16:00"),
    ("Dr. Kavya Iyer", "ENT", "11:00,13:00"),
    ("Dr. Mohit Jain", "General Physician", "09:00,11:00,17:00"),
    ("Dr. Sneha Paul", "Psychiatrist", "12:00,15:00"),
    ("Dr. Ramesh Pillai", "Urologist", "10:00,14:00")
]

conn = sqlite3.connect("hospital.db")
cur = conn.cursor()

cur.executemany(
    "INSERT INTO doctors (name, specialization, slots) VALUES (?, ?, ?)",
    doctors
)

conn.commit()
conn.close()

print("✅ 10 Doctors seeded")
