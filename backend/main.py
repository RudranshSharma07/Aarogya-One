from datetime import date
from uuid import uuid4
from typing import Literal
from ai.continuity import check_continuity
from fastapi import HTTPException
from database import get_connection, initialize_database
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import sqlite3
from uuid import uuid4
from typing import Literal
from emergency_service import generate_plan, load_emergency

from ai.rescue_chain import build_rescue_chain
from healthcare.routes import router as healthcare_router

app = FastAPI(title="Aarogya One API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class EmergencyRequest(BaseModel):
    request_id: str
    resource_type: str = "blood"
    blood_group: str
    patient_id: str
    units: int = Field(default=1, ge=1)


# Fictional demo data
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
        "name": "Demo Hospital A",
        "available": True,
        "services": ["blood", "emergency"],
        "distance_km": 4
    }
]


@app.get("/")
def home():
    return {"message": "Aarogya One backend is running"}


@app.post("/match")
def match_emergency(request: EmergencyRequest):
    result = build_rescue_chain(
        request.model_dump(),
        load_donors,
        load_hospitals
    )
    return result

class SOSRequest(BaseModel):
    patient_id: str
    hospital_id: str
    resource_type: str = "blood"
    blood_group: str | None = None
    units: int = Field(default=1, ge=1)
    location: str


initialize_database()
app.include_router(healthcare_router)


@app.post("/sos", status_code=201)
def create_sos(request: SOSRequest):
    if request.resource_type == "blood" and not request.blood_group:
        raise HTTPException(
            status_code=422,
            detail="Blood group is required for blood requests"
        )

    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO emergencies (
                patient_id,
                hospital_id,
                resource_type,
                blood_group,
                units,
                location
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                request.patient_id,
                request.hospital_id,
                request.resource_type,
                request.blood_group,
                request.units,
                request.location
            )
        )

        conn.commit()
        request_id = cursor.lastrowid

    return {
        "request_id": f"SOS{request_id:04d}",
        "status": "submitted",
        "message": "Emergency request saved"
    }


@app.get("/sos/{request_id}")
def get_sos(request_id: str):
    # Accept IDs such as SOS0001.
    if not request_id.startswith("SOS"):
        raise HTTPException(400, "Invalid request ID")

    try:
        numeric_id = int(request_id[3:])
    except ValueError:
        raise HTTPException(400, "Invalid request ID")

    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM emergencies WHERE id = ?",
            (numeric_id,)
        ).fetchone()

    if row is None:
        raise HTTPException(404, "SOS request not found")

    result = dict(row)
    result["request_id"] = f"SOS{result.pop('id'):04d}"

    return result

class ResourceResponse(BaseModel):
    resource_type: Literal["donor", "hospital"]
    resource_id: str
    response: Literal["declined", "unavailable"]


def get_exclusions(request_id):
    emergency = load_emergency(request_id)
    numeric_id = int(emergency["request_id"][3:])

    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT resource_type, resource_id, response
            FROM resource_responses
            WHERE emergency_id = ?
            """,
            (numeric_id,)
        ).fetchall()

    declined_donors = [
        row["resource_id"]
        for row in rows
        if row["resource_type"] == "donor"
        and row["response"] == "declined"
    ]

    unavailable_hospitals = [
        row["resource_id"]
        for row in rows
        if row["resource_type"] == "hospital"
        and row["response"] == "unavailable"
    ]

    return declined_donors, unavailable_hospitals



@app.get("/sos/{request_id}/plan")
def get_rescue_plan(request_id: str):
    declined, unavailable = get_exclusions(request_id)

    return generate_plan(
        request_id,
        load_donors(),
        load_hospitals(),
        declined_donor_ids=declined,
        unavailable_hospital_ids=unavailable
    )


@app.post("/sos/{request_id}/response")
def record_resource_response(
    request_id: str,
    response: ResourceResponse
):
    emergency = load_emergency(request_id)
    numeric_id = int(emergency["request_id"][3:])

    # 1. Prevent changes to completed or cancelled requests
    if emergency["status"] in ("completed", "cancelled"):
        raise HTTPException(
            status_code=409,
            detail="Cannot modify a closed emergency"
        )

    # 2. Validate response type
    if (
        response.resource_type == "donor"
        and response.response != "declined"
    ) or (
        response.resource_type == "hospital"
        and response.response != "unavailable"
    ):
        raise HTTPException(
            status_code=422,
            detail="Invalid resource response"
        )

    # 3. Check that the resource exists
    resources = (
        load_donors
        if response.resource_type == "donor"
        else hospitals
    )

    if not any(
        resource["id"] == response.resource_id
        for resource in resources
    ):
        raise HTTPException(
            status_code=404,
            detail="Resource not found"
        )

    # 4. Save the decline or unavailability
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO resource_responses (
                emergency_id,
                resource_type,
                resource_id,
                response
            )
            VALUES (?, ?, ?, ?)
            ON CONFLICT (
                emergency_id,
                resource_type,
                resource_id
            )
            DO UPDATE SET response = excluded.response
            """,
            (
                numeric_id,
                response.resource_type,
                response.resource_id,
                response.response
            )
        )

        # 5. Invalidate previous acceptance and confirmation
        conn.execute(
            """
            UPDATE resource_responses
            SET response = 'invalidated'
            WHERE emergency_id = ?
              AND response IN ('accepted', 'confirmed')
            """,
            (numeric_id,)
        )

        # 6. Return the emergency to matching
        conn.execute(
            """
            UPDATE emergencies
            SET status = 'matching'
            WHERE id = ?
            """,
            (numeric_id,)
        )

        conn.commit()

    # 7. Recalculate the rescue plan
    return {
        "message": "Response recorded and rescue plan recalculated",
        "status": "matching",
        "updated_plan": get_rescue_plan(request_id)
    }

@app.post("/sos/{request_id}/accept/{donor_id}")
def accept_donor_request(request_id: str, donor_id: str):
    emergency = load_emergency(request_id)
    emergency_id = int(emergency["request_id"][3:])

    if emergency["status"] in ("completed", "cancelled"):
        raise HTTPException(409, "Request is already closed")

    
    if not any(
        d["id"] == donor_id and d["available"]
        for d in load_donors()
    ):
        raise HTTPException(
            404, "Available donor not found"
        )

    declined, unavailable = get_exclusions(request_id)

    if donor_id in declined:
        raise HTTPException(
            409, "Donor previously declined this request"
        )

    plan = get_rescue_plan(request_id)

    possible_ids = [
        p["donor_id"]
        for p in (
            [plan["recommended_plan"]]
            + plan["backup_plans"]
        )
        if p is not None
    ]

    if donor_id not in possible_ids:
        raise HTTPException(
            409, "Donor is not in the current rescue plans"
        )

    with get_connection() as conn:
        conn.execute("""
            INSERT INTO resource_responses
                (emergency_id, resource_type,
                 resource_id, response)
            VALUES (?, 'donor', ?, 'accepted')
            ON CONFLICT (
                emergency_id, resource_type, resource_id
            )
            DO UPDATE SET response = 'accepted'
        """, (emergency_id, donor_id))

        conn.execute("""
            UPDATE emergencies
            SET status = 'donor_accepted'
            WHERE id = ?
        """, (emergency_id,))

        conn.commit()

    return {
        "request_id": request_id,
        "donor_id": donor_id,
        "status": "donor_accepted",
        "message": "Donor response recorded"
    }

@app.post("/sos/{request_id}/confirm/{hospital_id}")
def confirm_hospital(request_id: str, hospital_id: str):
    emergency = load_emergency(request_id)
    emergency_id = int(emergency["request_id"][3:])

    if emergency["status"] != "donor_accepted":
        raise HTTPException(
            409, "Donor acceptance is required first"
        )

    declined, unavailable = get_exclusions(request_id)

    if hospital_id in unavailable:
        raise HTTPException(
            409, "Hospital is marked unavailable"
        )

    if not any(
        h["id"] == hospital_id and h["available"]
        for h in load_hospitals
    ):
        raise HTTPException(
            404, "Available hospital not found"
        )

    with get_connection() as conn:
        accepted = conn.execute("""
            SELECT resource_id
            FROM resource_responses
            WHERE emergency_id = ?
              AND resource_type = 'donor'
              AND response = 'accepted'
            LIMIT 1
        """, (emergency_id,)).fetchone()

        if accepted is None:
            raise HTTPException(
                409, "No accepted donor found"
            )

        conn.execute("""
            INSERT INTO resource_responses
                (emergency_id, resource_type,
                 resource_id, response)
            VALUES (?, 'hospital', ?, 'confirmed')
            ON CONFLICT (
                emergency_id, resource_type, resource_id
            )
            DO UPDATE SET response = 'confirmed'
        """, (emergency_id, hospital_id))

        conn.execute("""
            UPDATE emergencies
            SET status = 'hospital_confirmed'
            WHERE id = ?
        """, (emergency_id,))

        conn.commit()

    return {
        "request_id": request_id,
        "donor_id": accepted["resource_id"],
        "hospital_id": hospital_id,
        "status": "hospital_confirmed",
        "message": "Coordinator confirmation recorded"
    }

@app.post("/sos/{request_id}/complete")
def complete_emergency(request_id: str):
    emergency = load_emergency(request_id)

    if emergency["status"] != "hospital_confirmed":
        raise HTTPException(
            409,
            "Hospital confirmation is required first"
        )

    emergency_id = int(emergency["request_id"][3:])

    with get_connection() as conn:
        conn.execute("""
            UPDATE emergencies
            SET status = 'completed'
            WHERE id = ?
        """, (emergency_id,))
        conn.commit()

    return {
        "request_id": request_id,
        "status": "completed",
        "message": "Demo emergency marked complete"
    }

# -------- APPOINTMENTS --------

class AppointmentRequest(BaseModel):
    patient_id: str
    date: date
    doctor_name: str
    consultation_link: str | None = None


@app.post("/appointments", status_code=201)
def create_appointment(request: AppointmentRequest):
    appointment_id = f"APT-{uuid4().hex[:8].upper()}"

    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO appointments
                (id, patient_id, date, status,
                 doctor_name, consultation_link)
            VALUES (?, ?, ?, 'scheduled', ?, ?)
            """,
            (
                appointment_id,
                request.patient_id,
                request.date.isoformat(),
                request.doctor_name,
                request.consultation_link
            )
        )
        conn.commit()

    return {
        "appointment_id": appointment_id,
        "status": "scheduled"
    }


# -------- MEDICINE REMINDERS --------

class MedicineRequest(BaseModel):
    patient_id: str
    name: str


@app.post("/medicines", status_code=201)
def add_medicine(request: MedicineRequest):
    medicine_id = f"MED-{uuid4().hex[:8].upper()}"

    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO medicines
                (id, patient_id, name,
                 active, reminder_status)
            VALUES (?, ?, ?, 1, 'pending')
            """,
            (
                medicine_id,
                request.patient_id,
                request.name
            )
        )
        conn.commit()

    return {
        "medicine_id": medicine_id,
        "reminder_status": "pending"
    }


# -------- UPDATE REMINDER STATUS --------

class ReminderUpdate(BaseModel):
    reminder_status: Literal["pending", "missed", "done"]


@app.patch("/medicines/{medicine_id}")
def update_medicine(
    medicine_id: str,
    request: ReminderUpdate
):
    with get_connection() as conn:
        cursor = conn.execute(
            """
            UPDATE medicines
            SET reminder_status = ?
            WHERE id = ?
            """,
            (request.reminder_status, medicine_id)
        )
        conn.commit()

    if cursor.rowcount == 0:
        raise HTTPException(404, "Medicine not found")

    return {
        "medicine_id": medicine_id,
        "reminder_status": request.reminder_status
    }


# -------- CONTINUITY AI --------

@app.get("/patients/{patient_id}/followups")
def get_patient_followups(patient_id: str):
    with get_connection() as conn:
        appointments = [
            dict(row)
            for row in conn.execute(
                """
                SELECT * FROM appointments
                WHERE patient_id = ?
                """,
                (patient_id,)
            ).fetchall()
        ]

        medicines = [
            dict(row)
            for row in conn.execute(
                """
                SELECT * FROM medicines
                WHERE patient_id = ?
                """,
                (patient_id,)
            ).fetchall()
        ]

    return check_continuity(
        patient_id,
        appointments,
        medicines
    )

# -------- MEDICONNECT: DONORS --------

class DonorRegistration(BaseModel):
    name: str
    blood_group: str
    available: bool = True
    distance_km: float = Field(ge=0)


class DonorAvailability(BaseModel):
    available: bool


@app.post("/donors", status_code=201)
def register_donor(request: DonorRegistration):
    donor_id = f"D-{uuid4().hex[:8].upper()}"

    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO donors
                (id, name, blood_group,
                 available, distance_km)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                donor_id,
                request.name,
                request.blood_group,
                int(request.available),
                request.distance_km
            )
        )
        conn.commit()

    return {
        "donor_id": donor_id,
        "message": "Demo donor registered"
    }


@app.get("/donors")
def list_donors():
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM donors"
        ).fetchall()

    return [
        {
            **dict(row),
            "available": bool(row["available"])
        }
        for row in rows
    ]


@app.patch("/donors/{donor_id}")
def update_donor(
    donor_id: str,
    request: DonorAvailability
):
    with get_connection() as conn:
        cursor = conn.execute(
            """
            UPDATE donors
            SET available = ?
            WHERE id = ?
            """,
            (int(request.available), donor_id)
        )
        conn.commit()

    if cursor.rowcount == 0:
        raise HTTPException(
            404, "Donor not found"
        )

    return {
        "donor_id": donor_id,
        "available": request.available
    }

# -------- MEDICONNECT: HOSPITALS --------
import json
class HospitalRegistration(BaseModel):
    name: str
    available: bool = True
    services: list[str]
    distance_km: float = Field(ge=0)


class HospitalUpdate(BaseModel):
    available: bool
    services: list[str]


@app.post("/hospitals", status_code=201)
def register_hospital(request: HospitalRegistration):
    hospital_id = f"H-{uuid4().hex[:8].upper()}"

    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO hospitals
                (id, name, available,
                 services, distance_km)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                hospital_id,
                request.name,
                int(request.available),
                json.dumps(request.services),
                request.distance_km
            )
        )
        conn.commit()

    return {"hospital_id": hospital_id}


@app.get("/hospitals")
def list_hospitals():
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM hospitals"
        ).fetchall()

    return [
        {
            **dict(row),
            "available": bool(row["available"]),
            "services": json.loads(row["services"])
        }
        for row in rows
    ]


@app.patch("/hospitals/{hospital_id}")
def update_hospital(
    hospital_id: str,
    request: HospitalUpdate
):
    with get_connection() as conn:
        cursor = conn.execute(
            """
            UPDATE hospitals
            SET available = ?, services = ?
            WHERE id = ?
            """,
            (
                int(request.available),
                json.dumps(request.services),
                hospital_id
            )
        )
        conn.commit()

    if cursor.rowcount == 0:
        raise HTTPException(
            404, "Hospital not found"
        )

    return {
        "hospital_id": hospital_id,
        "available": request.available,
        "services": request.services
    }

def load_donors():
    with get_connection() as conn:
        return [
            {
                **dict(row),
                "available": bool(row["available"])
            }
            for row in conn.execute(
                "SELECT * FROM donors"
            ).fetchall()
        ]


def load_hospitals():
    with get_connection() as conn:
        return [
            {
                **dict(row),
                "available": bool(row["available"]),
                "services": json.loads(row["services"])
            }
            for row in conn.execute(
                "SELECT * FROM hospitals"
            ).fetchall()
        ]