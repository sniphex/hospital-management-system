import os
import sqlite3
from flask import Flask, request, jsonify, session, redirect
from dotenv import load_dotenv
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

load_dotenv()

app = Flask(__name__, static_folder="static", static_url_path="")
app.secret_key = os.getenv("SECRET_KEY", "hospital-management-secret-key-2024")

DB = "hospital.db"

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
FROM_EMAIL = os.getenv("FROM_EMAIL")

def init_db():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("""CREATE TABLE IF NOT EXISTS patients(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL
    )""")

    cur.execute("""CREATE TABLE IF NOT EXISTS doctors(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        specialization TEXT NOT NULL
    )""")

    cur.execute("""CREATE TABLE IF NOT EXISTS appointments(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient TEXT NOT NULL,
        doctor TEXT NOT NULL,
        date TEXT NOT NULL,
        time TEXT NOT NULL,
        status TEXT NOT NULL
    )""")

    cur.execute("SELECT COUNT(*) FROM doctors")
    if cur.fetchone()[0] == 0:
        doctors = [
            ("Dr. Rajesh Kumar", "Cardiologist"),
            ("Dr. Anita Rao", "Gynecologist"),
            ("Dr. Sunil Mehta", "Orthopedic"),
            ("Dr. Neha Sharma", "Dermatologist"),
            ("Dr. Arjun Pillai", "Neurologist"),
        ]
        cur.executemany("INSERT INTO doctors (name, specialization) VALUES (?,?)", doctors)

    conn.commit()
    conn.close()

init_db()

def send_notification_email(recipient, subject, content):
    if not SENDGRID_API_KEY or not FROM_EMAIL:
        return False
    
    try:
        message = Mail(
            from_email=FROM_EMAIL,
            to_emails=recipient,
            subject=subject,
            html_content=content
        )
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        return response.status_code in [200, 202]
    except Exception as e:
        print(f"Email notification error: {e}")
        return False

def check_authentication():
    return session.get("logged_in") == True

@app.route("/")
def index():
    return app.send_static_file("login.html")

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")
    
    if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
        session["logged_in"] = True
        return jsonify({"success": True})
    
    return jsonify({"success": False}), 401

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/home")
def home():
    if not check_authentication():
        return redirect("/")
    return app.send_static_file("index.html")

@app.route("/create_patient", methods=["POST"])
def create_patient():
    if not check_authentication():
        return jsonify({"error": "Unauthorized access"}), 401

    data = request.json
    patient_name = data.get("name")
    patient_email = data.get("email")
    
    if not patient_name or not patient_email:
        return jsonify({"error": "Missing required fields"}), 400
    
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("INSERT INTO patients (name, email) VALUES (?, ?)", 
                (patient_name, patient_email))
    conn.commit()
    conn.close()
    
    return jsonify({"message": "Patient registered successfully"})

@app.route("/doctor")
def get_doctors():
    if not check_authentication():
        return jsonify([]), 401
    
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT name, specialization FROM doctors")
    rows = cur.fetchall()
    conn.close()
    
    doctors_list = []
    for row in rows:
        doctors_list.append({
            "name": row[0],
            "specialization": row[1]
        })
    
    return jsonify(doctors_list)

@app.route("/create_appointment", methods=["POST"])
def create_appointment():
    print("DEBUG: create_appointment route HIT")
    if not check_authentication():
        return jsonify({"error": "Unauthorized access"}), 401

    data = request.json

    patient_name = data.get("patient")
    doctor_name = data.get("doctor")
    appointment_date = data.get("date")
    appointment_time = data.get("time")

    if not all([patient_name, doctor_name, appointment_date, appointment_time]):
        return jsonify({"error": "All fields are required"}), 400

    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    # Fetch patient email
    cur.execute("SELECT email FROM patients WHERE name = ?", (patient_name,))
    row = cur.fetchone()

    if not row:
        conn.close()
        return jsonify({"error": "Patient not found"}), 404

    patient_email = row[0]

    # Insert appointment
    cur.execute("""
        INSERT INTO appointments (patient, doctor, date, time, status)
        VALUES (?, ?, ?, ?, ?)
    """, (
        patient_name,
        doctor_name,
        appointment_date,
        appointment_time,
        "Booked"
    ))

    conn.commit()
    conn.close()

    # Send email (DO NOT BLOCK BOOKING)
    try:
        send_notification_email(
            patient_email,
            "Appointment Confirmation",
            f"""
            <h3>Appointment Confirmed</h3>
            <p>Patient: {patient_name}</p>
            <p>Doctor: {doctor_name}</p>
            <p>Date: {appointment_date}</p>
            <p>Time: {appointment_time}</p>
            """
        )
    except Exception as e:
        print("Email failed but appointment saved:", e)

    return jsonify({
        "success": True,
        "message": "Appointment booked successfully"
    })


@app.route("/appointments")
def get_appointments():
    if not check_authentication():
        return jsonify([]), 401
    
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("""
        SELECT id, patient, doctor, date, time, status 
        FROM appointments 
        ORDER BY id DESC
    """)
    rows = cur.fetchall()
    conn.close()
    
    appointments_list = []
    for row in rows:
        appointments_list.append({
            "id": row[0],
            "patient": row[1],
            "doctor": row[2],
            "date": row[3],
            "time": row[4],
            "status": row[5]
        })
    
    return jsonify(appointments_list)

@app.route("/delete_appointment", methods=["POST"])
def delete_appointment():
    if not check_authentication():
        return jsonify({"error": "Unauthorized access"}), 401

    data = request.json
    appointment_id = data.get("id")
    
    if not appointment_id:
        return jsonify({"error": "Appointment ID required"}), 400
    
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("DELETE FROM appointments WHERE id = ?", (appointment_id,))
    conn.commit()
    conn.close()
    
    return jsonify({"message": "Appointment deleted successfully"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)