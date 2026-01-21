import os
import sqlite3
from flask import Flask, request, jsonify, session, redirect
from dotenv import load_dotenv
import smtplib
from email.message import EmailMessage

load_dotenv()

app = Flask(__name__, static_folder="static", static_url_path="")
app.secret_key = "hospital-secret"

DB = "hospital.db"

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")

# -------------------- DB INIT --------------------
def init_db():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("""CREATE TABLE IF NOT EXISTS patients(
        id INTEGER PRIMARY KEY,
        name TEXT,
        email TEXT
    )""")

    cur.execute("""CREATE TABLE IF NOT EXISTS doctors(
        id INTEGER PRIMARY KEY,
        name TEXT,
        specialization TEXT
    )""")

    cur.execute("""CREATE TABLE IF NOT EXISTS appointments(
        id INTEGER PRIMARY KEY,
        patient TEXT,
        doctor TEXT,
        date TEXT,
        time TEXT,
        status TEXT
    )""")

    # Seed doctors
    cur.execute("SELECT COUNT(*) FROM doctors")
    if cur.fetchone()[0] == 0:
        doctors = [
            ("Dr. Rajesh Kumar", "Cardiologist"),
            ("Dr. Anita Rao", "Gynecologist"),
            ("Dr. Sunil Mehta", "Orthopedic"),
            ("Dr. Neha Sharma", "Dermatologist"),
            ("Dr. Arjun Pillai", "Neurologist"),
        ]
        cur.executemany("INSERT INTO doctors VALUES (NULL,?,?)", doctors)

    conn.commit()
    conn.close()

init_db()

# -------------------- EMAIL --------------------
def send_email(to, subject, body):
    msg = EmailMessage()
    msg["From"] = EMAIL_USER
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(msg)

# -------------------- AUTH --------------------
@app.route("/")
def login_page():
    return app.send_static_file("login.html")

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    if data["email"] == ADMIN_EMAIL and data["password"] == ADMIN_PASSWORD:
        session["logged"] = True
        return jsonify({"success": True})
    return jsonify({"success": False}), 401

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/home")
def home():
    if not session.get("logged"):
        return redirect("/")
    return app.send_static_file("index.html")

# -------------------- API GUARD --------------------
def guard():
    if not session.get("logged"):
        return False
    return True

# -------------------- PATIENT --------------------
@app.route("/create_patient", methods=["POST"])
def create_patient():
    if not guard(): return jsonify({"error":"unauthorized"}),401

    d = request.json
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("INSERT INTO patients VALUES (NULL,?,?)",(d["name"],d["email"]))
    conn.commit()
    conn.close()
    return jsonify({"message":"Patient registered"})

# -------------------- DOCTORS --------------------
@app.route("/doctor")
def doctors():
    if not guard(): return jsonify([]),401
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT name,specialization FROM doctors")
    rows = cur.fetchall()
    conn.close()
    return jsonify([{"name":r[0],"specialization":r[1]} for r in rows])

# -------------------- APPOINTMENT --------------------
@app.route("/create_appointment", methods=["POST"])
def create_appointment():
    data = request.json

    required = ["patient", "doctor", "date", "time"]
    if not all(k in data and data[k] for k in required):
        return jsonify({"error": "Missing appointment details"}), 400

    conn = sqlite3.connect("hospital.db")
    cur = conn.cursor()

    # get patient email
    cur.execute("SELECT email FROM patients WHERE name = ?", (data["patient"],))
    row = cur.fetchone()

    if not row:
        conn.close()
        return jsonify({"error": "Patient not found"}), 404

    patient_email = row[0]

    # INSERT APPOINTMENT (THIS MUST ALWAYS WORK)
    cur.execute("""
        INSERT INTO appointments (patient, doctor, date, time, status)
        VALUES (?, ?, ?, ?, ?)
    """, (
        data["patient"],
        data["doctor"],
        data["date"],
        data["time"],
        "Booked"
    ))

    conn.commit()
    conn.close()

    # TRY EMAIL — NEVER CRASH
    try:
        send_email(
            to=patient_email,
            subject="Appointment Confirmation",
            body=f"""
Dear {data['patient']},

Your appointment has been booked successfully.

Doctor: {data['doctor']}
Date: {data['date']}
Time: {data['time']}

— Hospital Management System
""",
            user=EMAIL_USER,
            password=EMAIL_PASS
        )
    except Exception as e:
        print("EMAIL FAILED:", e)   # Render logs only

    return jsonify({"message": "Appointment booked successfully"})

# -------------------- HISTORY --------------------
@app.route("/appointments")
def history():
    if not guard(): return jsonify([]),401
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT id,patient,doctor,date,time,status FROM appointments ORDER BY id DESC")
    rows = cur.fetchall()
    conn.close()
    return jsonify([
        {"id":r[0],"patient":r[1],"doctor":r[2],"date":r[3],"time":r[4],"status":r[5]}
        for r in rows
    ])
# -------------------- DELETE APPOINTMENT --------------------
@app.route("/delete_appointment", methods=["POST"])
def delete_appointment():
    if not guard(): return jsonify({"error":"unauthorized"}),401

    d = request.json
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    
    cur.execute("DELETE FROM appointments WHERE id=?", (d["id"],))
    
    conn.commit()
    conn.close()
    
    return jsonify({"message":"Appointment deleted successfully"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
