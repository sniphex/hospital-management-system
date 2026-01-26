<!-- Improved compatibility of back to top link -->
<a id="readme-top"></a>

<br />
<div align="center">
  <h3 align="center">HOSPITAL DATABASE MANAGEMENT SYSTEM</h3>

  <p align="center">
    A full-stack hospital workflow management system built with Flask, Firebase, and SQLite.
    <br />
    <br />
    <a href="https://github.com/sniphex/hospital-management-system">View Repository</a>
    ·
    <a href="https://github.com/sniphex/hospital-management-system/issues">Report Bug</a>
    ·
    <a href="https://github.com/sniphex/hospital-management-system/issues">Request Feature</a>
  </p>
</div>

---

## 📑 Table of Contents
<details>
  <summary>Expand</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#architecture">Architecture</a></li>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contact">Contact</a></li>
  </ol>
</details>

---

## About The Project

The **Hospital Management System** is a backend-focused full-stack application designed to manage hospital workflows such as patient registration, doctor management, and appointment scheduling.

The project focuses on **real-world backend concerns**:
- authentication
- session handling
- database separation
- cloud deployment
- production debugging

This is not a demo UI project — it is an **engineering-driven system**.

### Key Capabilities
- Firebase Authentication for user accounts
- Role-based access control
- Patient and doctor management
- Appointment booking and history
- Email notifications via SendGrid
- Cloud deployment on Render

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

## Architecture

The system follows a clean client-server architecture with clear separation of responsibilities.
Browser (HTML / JS)
|
| HTTP Requests (JSON)
v
Flask Backend (Render)
|
|-- Firebase Authentication
|-- Firestore (Users, Patients, Doctors)
|-- SQLite (Appointments)
|
|-- SendGrid (Email Notifications)


### Design Rationale
- **Firebase** handles authentication and scalable user data
- **SQLite** stores transactional appointment records
- **Flask** acts as the orchestration layer
- **SendGrid** handles asynchronous email delivery

This separation keeps the system maintainable and production-ready.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

## Built With

* **Backend**: Python, Flask  
* **Authentication**: Firebase Authentication  
* **Databases**: Firestore, SQLite  
* **Email Service**: SendGrid  
* **Deployment**: Render  
* **Version Control**: Git, GitHub  

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

## Getting Started

### Prerequisites

- Python 3.9+
- Git
- Firebase project with Admin SDK credentials
- SendGrid API key

### Installation

1. Clone the repository
   ```sh
   git clone https://github.com/sniphex/hospital-management-system.git
2. Create and activate virtual environment

python -m venv venv
source venv/bin/activate


3. Install dependencies

pip install -r requirements.txt


4. Set environment variables (Render or local .env)

SECRET_KEY=your_secret_key
SENDGRID_API_KEY=your_sendgrid_key
FROM_EMAIL=your_email
FIREBASE_CREDENTIALS=<firebase_json_string>


5. Run the app

python app.py

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Usage

Admin can log in and manage doctors

Receptionist can register patients

Appointments can be booked and tracked

Patients receive email confirmations

Appointment history is maintained securely

This system mirrors real hospital front-desk workflows.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Roadmap

 Firebase Authentication
        ||
 Appointment booking
        ||
 Email notifications
        ||
 Cloud deployment
        ||
 Improved role-based dashboards
        ||
 Audit logs
        ||
 Analytics and reporting

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Contact

Abhirami Suresh
📧 Email: aamisuresh03@gmail.com
🔗 LinkedIn: www.linkedin.com/in/abhirami-suresh-22b594250

## Project Link:
https://github.com/sniphex/hospital-management-system

<p align="right">(<a href="#readme-top">back to top</a>)</p>

