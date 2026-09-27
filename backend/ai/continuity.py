
from datetime import date


def check_continuity(patient_id, appointments, medicines, today=None):
    """
    Identify outstanding healthcare tasks.

    Dates must use YYYY-MM-DD.
    All clinical instructions come from healthcare staff.
    """
    today = today or date.today()
    alerts = []

    # 1. Check appointments
    for appointment in appointments:
        if appointment["patient_id"] != patient_id:
            continue

        appointment_date = date.fromisoformat(
            appointment["date"]
        )
        status = appointment["status"]

        if status in ("completed", "cancelled"):
            continue

        if appointment_date < today:
            alerts.append({
                "type": "missed_appointment",
                "reference_id": appointment["id"],
                "message": "An appointment needs follow-up.",
                "priority": "attention"
            })

        elif appointment_date == today:
            alerts.append({
                "type": "appointment_today",
                "reference_id": appointment["id"],
                "message": "You have an appointment today.",
                "priority": "reminder"
            })

    # 2. Check prescribed medicine reminders
    for medicine in medicines:
        if medicine["patient_id"] != patient_id:
            continue

        if not medicine["active"]:
            continue

        if medicine["reminder_status"] == "missed":
            alerts.append({
                "type": "missed_medicine_reminder",
                "reference_id": medicine["id"],
                "message": (
                    "A prescribed medicine reminder "
                    "was marked as missed. Follow your "
                    "clinician's instructions."
                ),
                "priority": "attention"
            })

        elif medicine["reminder_status"] == "pending":
            alerts.append({
                "type": "medicine_reminder",
                "reference_id": medicine["id"],
                "message": "You have a pending medicine reminder.",
                "priority": "reminder"
            })

    return {
        "patient_id": patient_id,
        "alerts": alerts,
        "total_alerts": len(alerts),
        "attention_required": any(
            alert["priority"] == "attention"
            for alert in alerts
        )
    }