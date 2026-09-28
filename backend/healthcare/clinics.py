from healthcare.common import (
    HealthcareError,
    clean_list,
    clean_text,
    from_json_list,
    new_id,
    read_connection,
    to_json_list,
    transaction,
)


def clinic_from_row(row) -> dict:
    return {
        "clinic_id": row["id"],
        "name": row["name"],
        "address": row["address"],
        "contact": row["contact"],
        "services": from_json_list(row["services"]),
        "available": bool(row["available"]),
        "opening_hours": row["opening_hours"],
        "created_at": row["created_at"],
    }


def create_clinic(
    name,
    address,
    contact,
    services,
    available=True,
    opening_hours=None
) -> dict:
    clinic_id = new_id("CLN")
    hours = (opening_hours or "").strip() or None

    with transaction() as conn:
        conn.execute(
            """
            INSERT INTO clinics
                (id, name, address, contact, services,
                 available, opening_hours)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                clinic_id,
                clean_text(name, "name"),
                clean_text(address, "address"),
                clean_text(contact, "contact"),
                to_json_list(clean_list(services, "services")),
                int(available),
                hours
            )
        )

    return get_clinic(clinic_id)


def get_clinic(clinic_id: str) -> dict:
    with read_connection() as conn:
        row = conn.execute(
            "SELECT * FROM clinics WHERE id = ?",
            (clinic_id,)
        ).fetchone()

    if row is None:
        raise HealthcareError(404, "Clinic not found")

    return clinic_from_row(row)


def list_clinics(available: bool | None = None) -> list[dict]:
    query = "SELECT * FROM clinics"
    params = []

    if available is not None:
        query += " WHERE available = ?"
        params.append(int(available))

    query += " ORDER BY name, id"

    with read_connection() as conn:
        rows = conn.execute(query, params).fetchall()

    return [clinic_from_row(row) for row in rows]


def update_clinic(clinic_id: str, changes: dict) -> dict:
    """Update only the fields present in `changes`."""
    assignments = []
    params = []

    for field in ("name", "address", "contact"):
        if field in changes:
            assignments.append(f"{field} = ?")
            params.append(clean_text(changes[field], field))

    if "services" in changes:
        assignments.append("services = ?")
        params.append(
            to_json_list(clean_list(changes["services"], "services"))
        )

    if "available" in changes:
        if changes["available"] is None:
            raise HealthcareError(422, "available must be true or false")
        assignments.append("available = ?")
        params.append(int(changes["available"]))

    if "opening_hours" in changes:
        assignments.append("opening_hours = ?")
        params.append((changes["opening_hours"] or "").strip() or None)

    if not assignments:
        raise HealthcareError(422, "No fields to update")

    with transaction() as conn:
        cursor = conn.execute(
            f"UPDATE clinics SET {', '.join(assignments)} WHERE id = ?",
            (*params, clinic_id)
        )

        if cursor.rowcount == 0:
            raise HealthcareError(404, "Clinic not found")

    return get_clinic(clinic_id)
