from healthcare.common import (
    HealthcareError,
    parse_date,
    read_connection,
    transaction,
)

DETAIL_FIELDS = ("dosage", "frequency")
DATE_FIELDS = ("start_date", "end_date", "follow_up_date")


def medicine_from_row(row) -> dict:
    return {
        "medicine_id": row["id"],
        "patient_id": row["patient_id"],
        "name": row["name"],
        "active": bool(row["active"]),
        "reminder_status": row["reminder_status"],
        "dosage": row["dosage"],
        "frequency": row["frequency"],
        "start_date": row["start_date"],
        "end_date": row["end_date"],
        "follow_up_date": row["follow_up_date"],
    }


def get_medicine(medicine_id: str) -> dict:
    with read_connection() as conn:
        row = conn.execute(
            "SELECT * FROM medicines WHERE id = ?",
            (medicine_id,)
        ).fetchone()

    if row is None:
        raise HealthcareError(404, "Medicine not found")

    return medicine_from_row(row)


def list_patient_medicines(patient_id: str) -> list[dict]:
    with read_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM medicines WHERE patient_id = ? ORDER BY id",
            (patient_id,)
        ).fetchall()

    return [medicine_from_row(row) for row in rows]


def update_medicine_details(medicine_id: str, changes: dict) -> dict:
    """
    Update prescription details on the EXISTING medicines table.

    Only fields present in `changes` are touched; an explicit None
    clears that field. Reminder status and active flag are untouched.
    """
    allowed = DETAIL_FIELDS + DATE_FIELDS
    unknown = set(changes) - set(allowed)

    if unknown:
        raise HealthcareError(
            422, "Unknown field(s): " + ", ".join(sorted(unknown))
        )

    if not changes:
        raise HealthcareError(422, "No fields to update")

    cleaned = {}

    for field in DETAIL_FIELDS:
        if field in changes:
            cleaned[field] = (changes[field] or "").strip() or None

    for field in DATE_FIELDS:
        if field in changes:
            value = changes[field]
            cleaned[field] = (
                None if value is None else parse_date(value, field)
            )

    with transaction() as conn:
        row = conn.execute(
            "SELECT * FROM medicines WHERE id = ?",
            (medicine_id,)
        ).fetchone()

        if row is None:
            raise HealthcareError(404, "Medicine not found")

        merged = {
            field: cleaned.get(field, row[field]) for field in DATE_FIELDS
        }

        if (
            merged["start_date"]
            and merged["end_date"]
            and merged["end_date"] < merged["start_date"]
        ):
            raise HealthcareError(
                422, "end_date must not be before start_date"
            )

        if (
            merged["start_date"]
            and merged["follow_up_date"]
            and merged["follow_up_date"] < merged["start_date"]
        ):
            raise HealthcareError(
                422, "follow_up_date must not be before start_date"
            )

        assignments = ", ".join(f"{field} = ?" for field in cleaned)
        conn.execute(
            f"UPDATE medicines SET {assignments} WHERE id = ?",
            (*cleaned.values(), medicine_id)
        )

        updated = conn.execute(
            "SELECT * FROM medicines WHERE id = ?",
            (medicine_id,)
        ).fetchone()

        return medicine_from_row(updated)
