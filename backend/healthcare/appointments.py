import sqlite3

from healthcare.common import (
    HealthcareError,
    build_consultation_link,
    check_mode,
    clean_text,
    new_id,
    read_connection,
    today_iso,
    transaction,
)

_SELECT_APPOINTMENT = """
    SELECT a.*, s.start_time AS slot_start_time,
           s.end_time AS slot_end_time
    FROM appointments a
    LEFT JOIN doctor_slots s ON s.id = a.slot_id
"""


def appointment_from_row(row) -> dict:
    return {
        "appointment_id": row["id"],
        "patient_id": row["patient_id"],
        "doctor_id": row["doctor_id"],
        "doctor_name": row["doctor_name"],
        "slot_id": row["slot_id"],
        "date": row["date"],
        "start_time": row["slot_start_time"],
        "end_time": row["slot_end_time"],
        "status": row["status"],
        "consultation_mode": row["consultation_mode"],
        "consultation_link": row["consultation_link"],
        "cancellation_reason": row["cancellation_reason"],
    }


def _fetch(conn, appointment_id: str):
    return conn.execute(
        _SELECT_APPOINTMENT + " WHERE a.id = ?",
        (appointment_id,)
    ).fetchone()


def book_appointment(
    patient_id,
    slot_id,
    consultation_mode=None
) -> dict:
    """
    Book a doctor slot in the EXISTING appointments table.

    The slot is claimed with a conditional UPDATE inside a
    BEGIN IMMEDIATE transaction, so only one caller can win it.
    A partial unique index on appointments(slot_id) is a second,
    database-level guard.
    """
    patient = clean_text(patient_id, "patient_id")

    if consultation_mode is not None:
        check_mode(consultation_mode)

    appointment_id = new_id("APT")

    with transaction() as conn:
        slot = conn.execute(
            """
            SELECT s.*, d.name AS doctor_name,
                   d.available AS doctor_available
            FROM doctor_slots s
            JOIN doctors d ON d.id = s.doctor_id
            WHERE s.id = ?
            """,
            (slot_id,)
        ).fetchone()

        if slot is None:
            raise HealthcareError(404, "Slot not found")

        if not slot["doctor_available"]:
            raise HealthcareError(409, "Doctor is currently unavailable")

        if slot["date"] < today_iso():
            raise HealthcareError(409, "Slot date has already passed")

        if (
            consultation_mode is not None
            and consultation_mode != slot["consultation_mode"]
        ):
            raise HealthcareError(
                422,
                "Slot is for "
                f"{slot['consultation_mode']} consultations"
            )

        claimed = conn.execute(
            """
            UPDATE doctor_slots
            SET status = 'booked'
            WHERE id = ? AND status = 'available'
            """,
            (slot_id,)
        )

        if claimed.rowcount != 1:
            raise HealthcareError(409, "Slot is already booked")

        mode = slot["consultation_mode"]
        link = build_consultation_link() if mode == "online" else None

        try:
            conn.execute(
                """
                INSERT INTO appointments
                    (id, patient_id, date, status, doctor_name,
                     consultation_link, doctor_id, slot_id,
                     consultation_mode)
                VALUES (?, ?, ?, 'scheduled', ?, ?, ?, ?, ?)
                """,
                (
                    appointment_id,
                    patient,
                    slot["date"],
                    slot["doctor_name"],
                    link,
                    slot["doctor_id"],
                    slot_id,
                    mode
                )
            )
        except sqlite3.IntegrityError:
            raise HealthcareError(409, "Slot is already booked")

        return appointment_from_row(_fetch(conn, appointment_id))


def cancel_appointment(appointment_id: str, reason=None) -> dict:
    """Cancel an appointment and free its slot in one transaction."""
    cleaned_reason = (reason or "").strip() or None

    with transaction() as conn:
        row = _fetch(conn, appointment_id)

        if row is None:
            raise HealthcareError(404, "Appointment not found")

        if row["status"] == "cancelled":
            raise HealthcareError(409, "Appointment is already cancelled")

        if row["status"] == "completed":
            raise HealthcareError(
                409, "A completed appointment cannot be cancelled"
            )

        conn.execute(
            """
            UPDATE appointments
            SET status = 'cancelled', cancellation_reason = ?
            WHERE id = ?
            """,
            (cleaned_reason, appointment_id)
        )

        if row["slot_id"]:
            conn.execute(
                "UPDATE doctor_slots SET status = 'available' "
                "WHERE id = ?",
                (row["slot_id"],)
            )

        return appointment_from_row(_fetch(conn, appointment_id))


def get_appointment(appointment_id: str) -> dict:
    with read_connection() as conn:
        row = _fetch(conn, appointment_id)

    if row is None:
        raise HealthcareError(404, "Appointment not found")

    return appointment_from_row(row)


def list_appointments(
    patient_id=None,
    doctor_id=None,
    status=None
) -> list[dict]:
    query = _SELECT_APPOINTMENT + " WHERE 1 = 1"
    params = []

    if patient_id:
        query += " AND a.patient_id = ?"
        params.append(patient_id)

    if doctor_id:
        query += " AND a.doctor_id = ?"
        params.append(doctor_id)

    if status:
        query += " AND a.status = ?"
        params.append(status)

    query += " ORDER BY a.date, s.start_time, a.id"

    with read_connection() as conn:
        rows = conn.execute(query, params).fetchall()

    return [appointment_from_row(row) for row in rows]
