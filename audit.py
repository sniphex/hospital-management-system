import sqlite3

DB_NAME = "database.db"

def log_action(action):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO audit_logs (action) VALUES (?)",
        (action,)
    )

    conn.commit()
    conn.close()
