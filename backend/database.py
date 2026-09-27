
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "aarogya.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS emergencies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id TEXT NOT NULL,
                hospital_id TEXT NOT NULL,
                resource_type TEXT NOT NULL,
                blood_group TEXT,
                units INTEGER NOT NULL,
                location TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'submitted',
                created_at TEXT NOT NULL
                    DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.execute("""
            CREATE TABLE IF NOT EXISTS resource_responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                emergency_id INTEGER NOT NULL,
                resource_type TEXT NOT NULL,
                resource_id TEXT NOT NULL,
                response TEXT NOT NULL,
                UNIQUE (
                emergency_id,
                resource_type,
                resource_id
            ),
            FOREIGN KEY (emergency_id)
            REFERENCES emergencies(id)
            )
        """)
        
        conn.execute("""
    CREATE TABLE IF NOT EXISTS appointments (
        id TEXT PRIMARY KEY,
        patient_id TEXT NOT NULL,
        date TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'scheduled',
        doctor_name TEXT,
        consultation_link TEXT
    )
""")

        conn.execute("""
    CREATE TABLE IF NOT EXISTS medicines (
        id TEXT PRIMARY KEY,
        patient_id TEXT NOT NULL,
        name TEXT NOT NULL,
        active INTEGER NOT NULL DEFAULT 1,
        reminder_status TEXT NOT NULL DEFAULT 'pending'
    )
""")
        
        conn.execute("""
    CREATE TABLE IF NOT EXISTS donors (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        blood_group TEXT NOT NULL,
        available INTEGER NOT NULL DEFAULT 1,
        distance_km REAL NOT NULL DEFAULT 0
    )
""")

        conn.execute("""
    CREATE TABLE IF NOT EXISTS hospitals (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        available INTEGER NOT NULL DEFAULT 1,
        services TEXT NOT NULL,
        distance_km REAL NOT NULL DEFAULT 0
    )
""")
        conn.commit()