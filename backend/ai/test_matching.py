
from matching import match_resources
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
        "name": "Rohit",
        "blood_group": "B+",
        "available": False,
        "distance_km": 2
    },
    {
        "id": "D003",
        "name": "Karan",
        "blood_group": "B+",
        "available": True,
        "distance_km": 8
    }
]

hospitals = [
    {
        "id": "H001",
        "name": "Demo Hospital A",
        "available": True,
        "services": ["blood", "emergency"],
        "distance_km": 4
    },
    {
        "id": "H002",
        "name": "Demo Hospital B",
        "available": False,
        "services": ["blood"],
        "distance_km": 2
    }
]

result = match_resources(
    request,
    donors,
    hospitals
)

pprint(result)

# Basic automated checks
assert len(result["potential_donors"]) == 2
assert result["potential_donors"][0]["donor_id"] == "D001"
assert len(result["potential_hospitals"]) == 1
assert result["missing_resources"] == []
assert result["plan_status"] == "provisional"

print("All initial tests passed.")