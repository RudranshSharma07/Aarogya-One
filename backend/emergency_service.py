
from fastapi import HTTPException

from database import get_connection
from ai.dynamic_fallback import recalculate_rescue_chain


def load_emergency(request_id: str):
    if not request_id.startswith("SOS"):
        raise HTTPException(400, "Invalid SOS ID")

    try:
        numeric_id = int(request_id[3:])
    except ValueError:
        raise HTTPException(400, "Invalid SOS ID")

    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM emergencies WHERE id = ?",
            (numeric_id,)
        ).fetchone()

    if row is None:
        raise HTTPException(404, "SOS request not found")

    request = dict(row)
    request["request_id"] = (
        f"SOS{request.pop('id'):04d}"
    )

    return request


def generate_plan(
    request_id,
    donors,
    hospitals,
    declined_donor_ids=None,
    unavailable_hospital_ids=None
):
    request = load_emergency(request_id)

    if request["resource_type"] != "blood":
        raise HTTPException(
            422,
            "This demo engine currently supports blood requests"
        )

    return recalculate_rescue_chain(
        request,
        donors,
        hospitals,
        declined_donor_ids=declined_donor_ids,
        unavailable_hospital_ids=unavailable_hospital_ids
    )