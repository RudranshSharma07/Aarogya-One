
from .rescue_chain import build_rescue_chain


def recalculate_rescue_chain(
    request,
    donors,
    hospitals,
    declined_donor_ids=None,
    unavailable_hospital_ids=None
):
    declined_donor_ids = set(declined_donor_ids or [])
    unavailable_hospital_ids = set(
        unavailable_hospital_ids or []
    )

    # Exclude donors who declined this specific request.
    updated_donors = [
        donor for donor in donors
        if donor["id"] not in declined_donor_ids
    ]

    # Exclude hospitals reported unavailable for this request.
    updated_hospitals = [
        hospital for hospital in hospitals
        if hospital["id"] not in unavailable_hospital_ids
    ]

    # Recalculate using your existing Rescue Chain Engine.
    result = build_rescue_chain(
        request,
        updated_donors,
        updated_hospitals
    )

    result["excluded_resources"] = {
        "declined_donors": sorted(declined_donor_ids),
        "unavailable_hospitals": sorted(
            unavailable_hospital_ids
        )
    }

    result["recalculated"] = True

    return result