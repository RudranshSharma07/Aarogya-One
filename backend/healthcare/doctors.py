import sqlite3

from healthcare.common import (
    HealthcareError,
    check_mode,
    clean_modes,
    clean_text,
    from_json_list,
    new_id,
    parse_date,
    parse_time,
    read_connection,
    to_json_list,
    today_iso,
    transaction,
)
from healthcare.clinics import clinic_from_row


# -------- serialisation --------

def slot_from_row(row) -> dict:
    return {
        "slot_id": row["id"],
        "doctor_id": row["doctor_id"],
        "date": row["date"],
        "start_time": row["start_time"],
        "end_time": row["end_time"],
        "consultation_mode": row["consultation_mode"],
        "status": row["status"],
    }


def _doctor_dict(conn, row) -> dict:
    clinic = None
    if row["clinic_id"]:
        clinic_row = conn.execute(
            "SELECT * FROM clinics WHERE id = ?",
            (row["clinic_id"],)
        ).fetchone()
        clinic = clinic_from_row(clinic_row) if clinic_row else None

    hospital = None
    if row["hospital_id"]:
        hospital_row = conn.execute(
            "SELECT id, name FROM hospitals WHERE id = ?",
            (row["hospital_id"],)
        ).fetchone()
        if hospital_row:
            hospital = {
                "hospital_id": hospital_row["id"],
                "name": hospital_row["name"]
            }

    return {
        "doctor_id": row["id"],
        "name": row["name"],
        "qualification": row["qualification"],
        "specialization": row["specialization"],
        "consultation_modes": from_json_list(row["consultation_modes"]),
        "available": bool(row["available"]),
        "clinic": clinic,
        "hospital": hospital,
        "created_at": row["created_at"],
    }


def _require_doctor_row(conn, doctor_id: str):
    row = conn.execute(
        "SELECT * FROM doctors WHERE id = ?",
        (doctor_id,)
    ).fetchone()

    if row is None:
        raise HealthcareError(404, "Doctor not found")

    return row


def _check_references(conn, clinic_id, hospital_id):
    if clinic_id is not None and conn.execute(
        "SELECT 1 FROM clinics WHERE id = ?", (clinic_id,)
    ).fetchone() is None:
        raise HealthcareError(422, "clinic_id does not exist")

    if hospital_id is not None and conn.execute(
        "SELECT 1 FROM hospitals WHERE id = ?", (hospital_id,)
    ).fetchone() is None:
        raise HealthcareError(422, "hospital_id does not exist")


# -------- doctors --------

def create_doctor(
    name,
    qualification,
    specialization,
    consultation_modes,
    clinic_id=None,
    hospital_id=None,
    available=True
) -> dict:
    doctor_id = new_id("DOC")

    with transaction() as conn:
        _check_references(conn, clinic_id, hospital_id)

        conn.execute(
            """
            INSERT INTO doctors
                (id, name, qualification, specialization,
                 clinic_id, hospital_id, consultation_modes,
                 available)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                doctor_id,
                clean_text(name, "name"),
                clean_text(qualification, "qualification"),
                clean_text(specialization, "specialization"),
                clinic_id,
                hospital_id,
                to_json_list(clean_modes(consultation_modes)),
                int(available)
            )
        )

    return get_doctor(doctor_id)


def get_doctor(doctor_id: str) -> dict:
    with read_connection() as conn:
        return _doctor_dict(conn, _require_doctor_row(conn, doctor_id))


def _list_doctor_dicts(
    conn,
    specialization=None,
    clinic_id=None,
    hospital_id=None,
    consultation_mode=None,
    available=None
) -> list[dict]:
    query = "SELECT * FROM doctors WHERE 1 = 1"
    params = []

    if specialization:
        query += " AND LOWER(specialization) = LOWER(?)"
        params.append(specialization.strip())

    if clinic_id:
        query += " AND clinic_id = ?"
        params.append(clinic_id)

    if hospital_id:
        query += " AND hospital_id = ?"
        params.append(hospital_id)

    if available is not None:
        query += " AND available = ?"
        params.append(int(available))

    query += " ORDER BY name, id"

    doctors = [
        _doctor_dict(conn, row)
        for row in conn.execute(query, params).fetchall()
    ]

    if consultation_mode:
        check_mode(consultation_mode)
        doctors = [
            d for d in doctors
            if consultation_mode in d["consultation_modes"]
        ]

    return doctors


def list_doctors(
    specialization=None,
    clinic_id=None,
    hospital_id=None,
    consultation_mode=None,
    available=None
) -> list[dict]:
    with read_connection() as conn:
        return _list_doctor_dicts(
            conn,
            specialization=specialization,
            clinic_id=clinic_id,
            hospital_id=hospital_id,
            consultation_mode=consultation_mode,
            available=available
        )


def update_doctor(doctor_id: str, changes: dict) -> dict:
    """Update only the fields present in `changes`."""
    assignments = []
    params = []

    for field in ("name", "qualification", "specialization"):
        if field in changes:
            assignments.append(f"{field} = ?")
            params.append(clean_text(changes[field], field))

    if "consultation_modes" in changes:
        assignments.append("consultation_modes = ?")
        params.append(
            to_json_list(clean_modes(changes["consultation_modes"]))
        )

    if "available" in changes:
        if changes["available"] is None:
            raise HealthcareError(422, "available must be true or false")
        assignments.append("available = ?")
        params.append(int(changes["available"]))

    for field in ("clinic_id", "hospital_id"):
        if field in changes:
            assignments.append(f"{field} = ?")
            params.append(changes[field])

    if not assignments:
        raise HealthcareError(422, "No fields to update")

    with transaction() as conn:
        _require_doctor_row(conn, doctor_id)
        _check_references(
            conn,
            changes.get("clinic_id"),
            changes.get("hospital_id")
        )
        conn.execute(
            f"UPDATE doctors SET {', '.join(assignments)} WHERE id = ?",
            (*params, doctor_id)
        )

    return get_doctor(doctor_id)


# -------- slots --------

def create_slot(
    doctor_id,
    date,
    start_time,
    end_time,
    consultation_mode
) -> dict:
    slot_date = parse_date(date)
    start = parse_time(start_time, "start_time")
    end = parse_time(end_time, "end_time")
    mode = check_mode(consultation_mode)

    if end <= start:
        raise HealthcareError(422, "end_time must be after start_time")

    if slot_date < today_iso():
        raise HealthcareError(422, "Slots cannot be created in the past")

    slot_id = new_id("SLT")

    with transaction() as conn:
        doctor = _require_doctor_row(conn, doctor_id)

        if mode not in from_json_list(doctor["consultation_modes"]):
            raise HealthcareError(
                422,
                f"Doctor does not offer {mode} consultations"
            )

        if conn.execute(
            """
            SELECT 1 FROM doctor_slots
            WHERE doctor_id = ? AND date = ? AND start_time = ?
            """,
            (doctor_id, slot_date, start)
        ).fetchone():
            raise HealthcareError(
                409, "This doctor already has a slot at that date and time"
            )

        if conn.execute(
            """
            SELECT 1 FROM doctor_slots
            WHERE doctor_id = ? AND date = ?
              AND start_time < ? AND end_time > ?
            """,
            (doctor_id, slot_date, end, start)
        ).fetchone():
            raise HealthcareError(
                409, "Slot overlaps an existing slot for this doctor"
            )

        try:
            conn.execute(
                """
                INSERT INTO doctor_slots
                    (id, doctor_id, date, start_time, end_time,
                     consultation_mode, status)
                VALUES (?, ?, ?, ?, ?, ?, 'available')
                """,
                (slot_id, doctor_id, slot_date, start, end, mode)
            )
        except sqlite3.IntegrityError:
            raise HealthcareError(
                409, "This doctor already has a slot at that date and time"
            )

        row = conn.execute(
            "SELECT * FROM doctor_slots WHERE id = ?", (slot_id,)
        ).fetchone()

        return slot_from_row(row)


def list_slots(
    doctor_id,
    status=None,
    from_date=None,
    to_date=None,
    consultation_mode=None
) -> list[dict]:
    if status is not None and status not in ("available", "booked"):
        raise HealthcareError(422, "status must be available or booked")

    query = "SELECT * FROM doctor_slots WHERE doctor_id = ?"
    params = [doctor_id]

    if status:
        query += " AND status = ?"
        params.append(status)

    if from_date:
        query += " AND date >= ?"
        params.append(parse_date(from_date, "from_date"))

    if to_date:
        query += " AND date <= ?"
        params.append(parse_date(to_date, "to_date"))

    if consultation_mode:
        query += " AND consultation_mode = ?"
        params.append(check_mode(consultation_mode))

    query += " ORDER BY date, start_time"

    with read_connection() as conn:
        _require_doctor_row(conn, doctor_id)
        rows = conn.execute(query, params).fetchall()

    return [slot_from_row(row) for row in rows]


def delete_slot(doctor_id: str, slot_id: str) -> dict:
    """Remove an unbooked slot that has never had an appointment."""
    with transaction() as conn:
        row = conn.execute(
            "SELECT * FROM doctor_slots WHERE id = ? AND doctor_id = ?",
            (slot_id, doctor_id)
        ).fetchone()

        if row is None:
            raise HealthcareError(404, "Slot not found")

        if row["status"] == "booked":
            raise HealthcareError(409, "A booked slot cannot be deleted")

        if conn.execute(
            "SELECT 1 FROM appointments WHERE slot_id = ?", (slot_id,)
        ).fetchone():
            raise HealthcareError(
                409, "Slot has appointment history and cannot be deleted"
            )

        conn.execute("DELETE FROM doctor_slots WHERE id = ?", (slot_id,))

    return {"slot_id": slot_id, "deleted": True}


# -------- availability (also the AI / recommendation feed) --------

def _window(from_date, to_date) -> tuple[str, str | None]:
    start = parse_date(from_date, "from_date") if from_date else today_iso()
    end = parse_date(to_date, "to_date") if to_date else None

    if end is not None and end < start:
        raise HealthcareError(422, "to_date must not be before from_date")

    return start, end


def _available_slots_by_doctor(
    conn,
    doctor_ids,
    start,
    end,
    consultation_mode
) -> dict:
    grouped = {doctor_id: [] for doctor_id in doctor_ids}

    if not doctor_ids:
        return grouped

    placeholders = ", ".join("?" for _ in doctor_ids)
    query = (
        "SELECT * FROM doctor_slots "
        f"WHERE doctor_id IN ({placeholders}) "
        "AND status = 'available' AND date >= ?"
    )
    params = [*doctor_ids, start]

    if end:
        query += " AND date <= ?"
        params.append(end)

    if consultation_mode:
        query += " AND consultation_mode = ?"
        params.append(consultation_mode)

    query += " ORDER BY date, start_time"

    for row in conn.execute(query, params).fetchall():
        grouped[row["doctor_id"]].append(slot_from_row(row))

    return grouped


def get_doctor_availability(
    doctor_id,
    from_date=None,
    to_date=None,
    consultation_mode=None
) -> dict:
    start, end = _window(from_date, to_date)

    if consultation_mode:
        check_mode(consultation_mode)

    with read_connection() as conn:
        doctor = _doctor_dict(conn, _require_doctor_row(conn, doctor_id))

        slots = []
        if doctor["available"]:
            slots = _available_slots_by_doctor(
                conn, [doctor_id], start, end, consultation_mode
            )[doctor_id]

    return {
        **doctor,
        "available_slots": slots,
        "next_available_slot": slots[0] if slots else None,
    }


def get_availability_data(
    specialization=None,
    consultation_mode=None,
    clinic_id=None,
    hospital_id=None,
    from_date=None,
    to_date=None,
    include_without_slots=False,
    limit=50
) -> dict:
    """
    Structured feed for the AI / recommendation modules.

    Each entry has doctor, specialization, qualification,
    clinic/hospital, consultation modes and open appointment slots.
    Unavailable doctors are never included.
    """
    start, end = _window(from_date, to_date)

    with read_connection() as conn:
        doctors = _list_doctor_dicts(
            conn,
            specialization=specialization,
            clinic_id=clinic_id,
            hospital_id=hospital_id,
            consultation_mode=consultation_mode,
            available=True
        )

        slots_by_doctor = _available_slots_by_doctor(
            conn,
            [d["doctor_id"] for d in doctors],
            start,
            end,
            consultation_mode
        )

    results = []
    for doctor in doctors:
        slots = slots_by_doctor[doctor["doctor_id"]]

        if not slots and not include_without_slots:
            continue

        results.append({
            **doctor,
            "available_slots": slots,
            "next_available_slot": slots[0] if slots else None,
        })

    results = results[:limit]

    return {
        "filters": {
            "specialization": specialization,
            "consultation_mode": consultation_mode,
            "clinic_id": clinic_id,
            "hospital_id": hospital_id,
            "from_date": start,
            "to_date": end,
        },
        "total_doctors": len(results),
        "doctors": results,
    }
