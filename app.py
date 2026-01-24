import os
import sqlite3
import firebase_admin
from firebase_admin import auth, credentials, firestore
from flask import Flask, request, jsonify, session, redirect
from dotenv import load_dotenv
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

# --------------------------------------------------
# LOAD ENV
# --------------------------------------------------
load_dotenv()

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
FROM_EMAIL = os.getenv("FROM_EMAIL")
SECRET_KEY = os.getenv("SECRET_KEY", "hospital-management-secret-key")

DB = "hospital.db"

# --------------------------------------------------
# FLASK APP
# --------------------------------------------------
app = Flask(__name__, static_folder="static", static_url_path="")
app.secret_key = SECRET_KEY

# --------------------------------------------------
# FIREBASE INIT (SAFE, ONCE)
# --------------------------------------------------
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase-key.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

# --------------------------------------------------
# SQLITE INIT (APPOINTMENTS ONLY)
# --------------------------------------------------
def init_db():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient TEXT NOT NULL,
            doctor TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            status TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()

# --------------------------------------------------
# EMAIL (SENDGRID)
# --------------------------------------------------
def send_notification_email(to, subject, html):
    if not SENDGRID_API_KEY or not FROM_EMAIL:
        print("⚠️ Email not configured")
        return

    try:
        message = Mail(
            from_email=FROM_EMAIL,
            to_emails=to,
            subject=subject,
            html_content=html
        )
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        sg.send(message)
    except Exception as e:
        print("❌ Email error:", e)

# --------------------------------------------------
# AUTH HELPERS
# --------------------------------------------------
def is_logged_in():
    return session.get("logged_in") is True

# --------------------------------------------------
# ROUTES
# --------------------------------------------------
@app.route("/")
def login_page():
    return app.send_static_file("login.html")

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    if data.get("email") == ADMIN_EMAIL and data.get("password") == ADMIN_PASSWORD:
        session["logged_in"] = True
        return jsonify({"success": True})
    return jsonify({"success": False}), 401

@app.route("/signup", methods=["POST"])
def signup():
    data = request.json

    email = data.get("email")
    password = data.get("password")
    role = data.get("role")

    if not email or not password or not role:
        return jsonify({"error": "Missing fields"}), 400

    try:
        user = auth.create_user(email=email, password=password)

        db.collection("users").document(user.uid).set({
            "email": email,
            "role": role,
            "created_at": firestore.SERVER_TIMESTAMP
        })

        return jsonify({"success": True})

    except Exception as e:
        print("❌ SIGNUP ERROR:", e)
        return jsonify({"error": str(e)}), 500

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/home")
def home():
    if not is_logged_in():
        return redirect("/")
    return app.send_static_file("index.html")

# --------------------------------------------------
# PATIENTS (FIREBASE)
# --------------------------------------------------
@app.route("/create_patient", methods=["POST"])
def create_patient():
    if not is_logged_in():
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    name = data.get("name")
    email = data.get("email")

    if not name or not email:
        return jsonify({"error": "Missing fields"}), 400

    db.collection("patients").add({
        "name": name,
        "email": email,
        "created_at": firestore.SERVER_TIMESTAMP
    })

    return jsonify({"message": "Patient registered successfully"})

# --------------------------------------------------
# DOCTORS (FIREBASE) — FIXED UNDEFINED ISSUE
# --------------------------------------------------
@app.route("/doctor")
def get_doctors():
    if not is_logged_in():
        return jsonify([]), 401

    doctors = []
    docs = db.collection("doctors").stream()

    for doc in docs:
        d = doc.to_dict()

        # 🔥 FIX: guarantee specialization always exists
        doctors.append({
            "name": d.get("name", "Unknown"),
            "specialization": d.get("specialization", "General")
        })

    return jsonify(doctors)

# --------------------------------------------------
# CREATE APPOINTMENT
# --------------------------------------------------
@app.route("/create_appointment", methods=["POST"])
def create_appointment():
    if not is_logged_in():
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    patient = data.get("patient")
    doctor = data.get("doctor")
    date = data.get("date")
    time = data.get("time")

    if not all([patient, doctor, date, time]):
        return jsonify({"error": "Missing fields"}), 400

    # 🔥 Get patient email from Firebase
    patient_docs = db.collection("patients").where("name", "==", patient).stream()
    patient_email = None

    for doc in patient_docs:
        patient_email = doc.to_dict().get("email")
        break

    if not patient_email:
        return jsonify({"error": "Patient not found"}), 404

    # ✅ Save appointment (SQLite)
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO appointments (patient, doctor, date, time, status)
        VALUES (?, ?, ?, ?, ?)
    """, (patient, doctor, date, time, "Booked"))
    conn.commit()
    conn.close()

    # 📧 Email
    send_notification_email(
        patient_email,
        "Appointment Confirmation",
        f"""
        <h3>Appointment Confirmed</h3>
        <p><b>Patient:</b> {patient}</p>
        <p><b>Doctor:</b> {doctor}</p>
        <p><b>Date:</b> {date}</p>
        <p><b>Time:</b> {time}</p>
        """
    )

    return jsonify({"message": "Appointment booked successfully"})

# --------------------------------------------------
# APPOINTMENT HISTORY
# --------------------------------------------------
@app.route("/appointments")
def get_appointments():
    if not is_logged_in():
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

    return jsonify([
        {
            "id": r[0],
            "patient": r[1],
            "doctor": r[2],
            "date": r[3],
            "time": r[4],
            "status": r[5]
        } for r in rows
    ])

# --------------------------------------------------
# DELETE APPOINTMENT
# --------------------------------------------------
@app.route("/delete_appointment", methods=["POST"])
def delete_appointment():
    if not is_logged_in():
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("DELETE FROM appointments WHERE id = ?", (data["id"],))
    conn.commit()
    conn.close()

    return jsonify({"message": "Appointment deleted"})

# --------------------------------------------------
# RUN
# --------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)
