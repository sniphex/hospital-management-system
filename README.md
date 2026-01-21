🏥 Hospital Management System (HMS)

A full-stack Hospital Management System built with Flask that enables secure patient registration, appointment booking, role-based authentication, email notifications, and appointment tracking through a clean, hospital-style dashboard.

🔗 Live Demo:
👉 https://hospital-management-system.onrender.com

📌 Overview

This project simulates a real hospital workflow, where an administrator can:

Register patients

Manage doctor availability

Book appointments

Track appointment history

Send confirmation emails automatically

The system is designed to be practical, production-oriented, and deployment-ready.

✨ Core Features
🔐 Authentication

Secure login using environment variables

Session-based authentication

Logout support

Protected routes

👤 Patient Management

Register patients with name & email

Validates patient existence before booking

Stores data securely in SQLite

🩺 Doctor Management

Pre-seeded doctor database

Doctors listed with specializations

Dynamic doctor selection during booking

📅 Appointment Booking

Book appointments with:

Patient

Doctor

Date (calendar picker)

Time

Prevents incomplete bookings

Appointment status tracking

📜 Appointment History

View all appointments in a structured table

Search by patient or doctor name

Filter by appointment status

📧 Email Notifications

Automatic confirmation email sent to patients

SMTP-based integration

Booking remains successful even if email fails (fail-safe)

🎨 User Interface

Clean, hospital-style admin dashboard

Responsive layout

Professional color scheme and spacing

🛠 Technology Stack
Layer	Technology
Backend	Python, Flask
Frontend	HTML, CSS, JavaScript
Database	SQLite
Authentication	Flask Sessions
Email	SMTP (smtplib)
Deployment	Render
📂 Project Structure
hospital-management-system/
│
├── app.py                  # Main Flask application
├── database.py             # Database utilities
├── init_db.py              # Database initialization
├── seed_doctors.py         # Doctor seed data
├── mailer.py               # Email service
├── requirements.txt
├── README.md
│
├── static/
│   ├── login.html          # Login page
│   ├── index.html          # Admin dashboard
│   ├── patient.html
│   ├── appointments.html
│
├── hospital.db             # SQLite database (ignored)
├── .env                    # Environment variables (ignored)
└── .gitignore

⚙️ Local Setup
1️⃣ Clone the Repository
git clone https://github.com/<your-username>/hospital-management-system.git
cd hospital-management-system

2️⃣ Create Virtual Environment
python -m venv venv
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate      # Windows

3️⃣ Install Dependencies
pip install -r requirements.txt

4️⃣ Configure Environment Variables

Create a .env file:

ADMIN_EMAIL=admin@hms.local
ADMIN_PASSWORD=admin123

EMAIL_USER=your_email@gmail.com
EMAIL_PASS=your_app_password


⚠️ Use Gmail App Password, not your real email password.

5️⃣ Initialize Database
python init_db.py
python seed_doctors.py

6️⃣ Run the Application
python app.py


Access the app at:

http://127.0.0.1:5000

🔑 Default Credentials
Role	Email	Password
Administrator	admin@hms.local
	admin123
🚀 Deployment

The application is deployed on Render, using:

Production-ready WSGI server

Secure environment variables

Centralized logging

🔮 Planned Enhancements

Doctor login & dashboards

Appointment status updates (Completed / Cancelled)

Analytics & reports

PDF appointment summaries

SMS notifications

⭐ Why This Project Matters

Models a real-world hospital workflow

Demonstrates backend + frontend integration

Includes authentication & sessions

Implements email automation

Fully deployed & production-ready

This project goes beyond CRUD and reflects practical system design.

👩‍💻 Author

Abhirami Suresh
Final-year Computer Science Engineering student
Focused on Backend Development, Cloud Computing & Full-Stack Systems
