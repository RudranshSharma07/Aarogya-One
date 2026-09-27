
from .matching import match_resources


def build_rescue_chain(request, donors, hospitals):
    # Reuse your Stage 1 matching algorithm
    matches = match_resources(request, donors, hospitals)

    potential_donors = matches["potential_donors"]
    potential_hospitals = matches["potential_hospitals"]

    rescue_plans = []

    # Combine potential donors and hospitals
    for donor in potential_donors:
        for hospital in potential_hospitals:
            plan = {
                "donor_id": donor["donor_id"],
                "donor_name": donor["name"],
                "hospital_id": hospital["hospital_id"],
                "hospital_name": hospital["name"],

                # Demo-only proximity measure.
                # Not an actual route or arrival-time estimate.
                "combined_distance_km": (
                    donor["distance_km"]
                    + hospital["distance_km"]
                ),

                "pending_confirmations": [
                    "donor_response",
                    "blood_bank_verification",
                    "hospital_confirmation"
                ],

                "status": "provisional"
            }

            rescue_plans.append(plan)

    # Sort by illustrative proximity
    rescue_plans.sort(
        key=lambda plan: plan["combined_distance_km"]
    )

    # Identify missing resources
    missing_resources = matches["missing_resources"]

    if not rescue_plans:
        recommendation = (
            "No complete potential resource combination "
            "found. Expand the search and contact "
            "emergency services."
        )
    else:
        recommendation = (
            "Potential resource combinations found. "
            "Human confirmation is required."
        )

    return {
        "request_id": request["request_id"],
        "recommended_plan": (
            rescue_plans[0] if rescue_plans else None
        ),
        "backup_plans": rescue_plans[1:3],
        "missing_resources": missing_resources,
        "recommendation": recommendation,
        "status": "awaiting_confirmation"
    }