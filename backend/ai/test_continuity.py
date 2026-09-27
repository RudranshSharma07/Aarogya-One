
from datetime import date
from continuity import check_continuity

appointments = [
    {
        "id": "A001",
        "patient_id": "P001",
        "date": "2026-09-25",
        "status": "scheduled"
    },
    {
        "id": "A002",
        "patient_id": "P001",
        "date": "2026-09-27",
        "status": "scheduled"
    },
    {
        "id": "A003",
        "patient_id": "P001",
        "date": "2026-09-24",
        "status": "completed"
    }
]

medicines = [
    {
        "id": "M001",
        "patient_id": "P001",
        "active": True,
        "reminder_status": "missed"
    },
    {
        "id": "M002",
        "patient_id": "P001",
        "active": True,
        "reminder_status": "pending"
    }
]

result = check_continuity(
    patient_id="P001",
    appointments=appointments,
    medicines=medicines,
    today=date(2026, 9, 27)
)

for alert in result["alerts"]:
    print(alert["type"], "-", alert["message"])

assert result["total_alerts"] == 4
assert result["attention_required"] is True

alert_types = {
    alert["type"] for alert in result["alerts"]
}

assert "missed_appointment" in alert_types
assert "appointment_today" in alert_types
assert "missed_medicine_reminder" in alert_types
assert "medicine_reminder" in alert_types

# A different patient should not receive Rahul's alerts.
other_patient = check_continuity(
    patient_id="P002",
    appointments=appointments,
    medicines=medicines,
    today=date(2026, 9, 27)
)

assert other_patient["total_alerts"] == 0

print("ALL CONTINUITY TESTS PASSED")