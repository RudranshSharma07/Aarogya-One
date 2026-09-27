
def match_resources(request, donors, hospitals):
    """
    Generate a provisional resource plan.
    All inputs are fictional demo data.
    """

    # 1. Find potential donors who match the search criteria.
    potential_donors = []

    for donor in donors:
        if not donor["available"]:
            continue

        # Demo search filter only; not clinical compatibility.
        if donor["blood_group"] != request["blood_group"]:
            continue

        potential_donors.append({
            "donor_id": donor["id"],
            "name": donor["name"],
            "distance_km": donor["distance_km"],
            "verification": "pending",
            "reason": "Matches reported search criteria"
        })

    # 2. Sort potential donors by distance.
    potential_donors.sort(
        key=lambda donor: donor["distance_km"]
    )

    # 3. Find hospitals reporting the required service.
    potential_hospitals = []

    for hospital in hospitals:
        if (
            hospital["available"]
            and request["resource_type"] in hospital["services"]
        ):
            potential_hospitals.append({
                "hospital_id": hospital["id"],
                "name": hospital["name"],
                "distance_km": hospital["distance_km"],
                "verification": "pending"
            })

    potential_hospitals.sort(
        key=lambda hospital: hospital["distance_km"]
    )

    # 4. Identify resource gaps.
    missing_resources = []

    if not potential_donors:
        missing_resources.append("potential_donor")

    if not potential_hospitals:
        missing_resources.append("hospital_service")

    # 5. Return an explainable provisional plan.
    return {
        "request_id": request["request_id"],
        "potential_donors": potential_donors,
        "potential_hospitals": potential_hospitals,
        "missing_resources": missing_resources,
        "plan_status": "provisional",
        "requires_human_confirmation": True
    }