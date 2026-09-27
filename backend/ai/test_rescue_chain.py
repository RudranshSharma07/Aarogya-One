
from rescue_chain import build_rescue_chain
from pprint import pprint

request = {
    "request_id": "SOS001",
    "resource_type": "blood",
    "blood_group": "B+"
}

donors = [
    {
        "id": "D001",
        "name": "Aman",
        "blood_group": "B+",
        "available": True,
        "distance_km": 5
    },
    {
        "id": "D002",
        "name": "Karan",
        "blood_group": "B+",
        "available": True,
        "distance_km": 8
    }
]

hospitals = [
    {
        "id": "H001",
        "name": "Hospital A",
        "available": True,
        "services": ["blood", "emergency"],
        "distance_km": 4
    },
    {
        "id": "H002",
        "name": "Hospital B",
        "available": False,
        "services": ["blood"],
        "distance_km": 2
    }
]

result = build_rescue_chain(
    request,
    donors,
    hospitals
)

pprint(result)

assert result["recommended_plan"] is not None
assert result["recommended_plan"]["donor_id"] == "D001"
assert result["recommended_plan"]["hospital_id"] == "H001"
assert len(result["backup_plans"]) == 1

# Test the missing-hospital situation
unavailable_hospitals = [
    {**hospital, "available": False}
    for hospital in hospitals
]

failed_result = build_rescue_chain(
    request,
    donors,
    unavailable_hospitals
)

assert failed_result["recommended_plan"] is None
assert "hospital_service" in failed_result["missing_resources"]

print("All rescue chain tests passed.")