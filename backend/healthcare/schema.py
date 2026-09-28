import sqlite3


def _existing_columns(conn, table: str) -> set[str]:
    return {row[1] for row in conn.execute(f"PRAGMA table_info({table})")}


def _add_missing_columns(conn, table: str, columns: dict[str, str]):
    """Add only the columns the table does not have yet."""
    existing = _existing_columns(conn, table)
    for name, definition in columns.items():
        if name in existing:
            continue
        try:
            conn.execute(
                f"ALTER TABLE {table} ADD COLUMN {name} {definition}"
            )
        except sqlite3.OperationalError as error:
            # Another process may have added it between the check and
            # the ALTER; that is fine.
            if "duplicate column" not in str(error).lower():
                raise


def ensure_healthcare_schema(conn):
    """
    Idempotent Member 3 schema setup.

    Creates the new healthcare tables and extends the EXISTING
    appointments and medicines tables with missing columns only.
    Called from database.initialize_database().
    """
    conn.execute("""
        CREATE TABLE IF NOT EXISTS clinics (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            address TEXT NOT NULL,
            contact TEXT NOT NULL,
            services TEXT NOT NULL,
            available INTEGER NOT NULL DEFAULT 1,
            opening_hours TEXT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS doctors (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            qualification TEXT NOT NULL,
            specialization TEXT NOT NULL,
            clinic_id TEXT REFERENCES clinics(id),
            hospital_id TEXT REFERENCES hospitals(id),
            consultation_modes TEXT NOT NULL,
            available INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS doctor_slots (
            id TEXT PRIMARY KEY,
            doctor_id TEXT NOT NULL REFERENCES doctors(id),
            date TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            consultation_mode TEXT NOT NULL
                CHECK (consultation_mode IN ('in_person', 'online')),
            status TEXT NOT NULL DEFAULT 'available'
                CHECK (status IN ('available', 'booked')),
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            UNIQUE (doctor_id, date, start_time),
            CHECK (end_time > start_time)
        )
    """)

    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_doctor_slots_lookup
        ON doctor_slots (doctor_id, date, status)
    """)

    # Extend the EXISTING appointments table.
    _add_missing_columns(conn, "appointments", {
        "doctor_id": "TEXT",
        "slot_id": "TEXT",
        "consultation_mode": "TEXT",
        "cancellation_reason": "TEXT",
    })

    # Database-level double-booking guard: at most one non-cancelled
    # appointment per slot.
    conn.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS ux_appointments_active_slot
        ON appointments (slot_id)
        WHERE slot_id IS NOT NULL AND status <> 'cancelled'
    """)

    # Extend the EXISTING medicines table.
    _add_missing_columns(conn, "medicines", {
        "dosage": "TEXT",
        "frequency": "TEXT",
        "start_date": "TEXT",
        "end_date": "TEXT",
        "follow_up_date": "TEXT",
    })
