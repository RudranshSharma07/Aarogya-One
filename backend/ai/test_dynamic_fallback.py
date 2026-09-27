
from dynamic_fallback import recalculate_rescue_chain

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
        "services": ["blood"],
        "distance_km": 4
    },
    {
        "id": "H002",
        "name": "Hospital B",
        "available": True,
        "services": ["blood"],
        "distance_km": 7
    }
]

# TEST 1: Normal situation
initial = recalculate_rescue_chain(
    request, donors, hospitals
)

assert initial["recommended_plan"]["donor_id"] == "D001"
assert initial["recommended_plan"]["hospital_id"] == "H001"

print("TEST 1 PASSED: Initial plan generated")


# TEST 2: Aman declines
after_decline = recalculate_rescue_chain(
    request,
    donors,
    hospitals,
    declined_donor_ids=["D001"]
)

assert (
    after_decline["recommended_plan"]["donor_id"]
    == "D002"
)

print("TEST 2 PASSED: Backup donor selected")


# TEST 3: Both hospitals become unavailable
no_hospital = recalculate_rescue_chain(
    request,
    donors,
    hospitals,
    unavailable_hospital_ids=["H001", "H002"]
)

assert no_hospital["recommended_plan"] is None
assert "hospital_service" in no_hospital["missing_resources"]

print("TEST 3 PASSED: Missing hospital detected")
print("ALL DYNAMIC FALLBACK TESTS PASSED")