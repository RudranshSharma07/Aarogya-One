from typing import Literal

from fastapi import APIRouter, HTTPException, Query

from healthcare import appointments, clinics, doctors, medicines
from healthcare.common import HealthcareError
from healthcare.schemas import (
    AppointmentBooking,
    AppointmentCancellation,
    ClinicCreate,
    ClinicUpdate,
    ConsultationMode,
    DoctorCreate,
    DoctorUpdate,
    MedicineDetails,
    SlotCreate,
)

router = APIRouter()

SlotStatus = Literal["available", "booked"]


def _call(func, *args, **kwargs):
    """Run a service function and map domain errors to HTTP errors."""
    try:
        return func(*args, **kwargs)
    except HealthcareError as error:
        raise HTTPException(
            status_code=error.status_code,
            detail=error.detail
        )


# -------- CLINICS --------

@router.post("/clinics", status_code=201)
def register_clinic(request: ClinicCreate):
    return _call(
        clinics.create_clinic,
        name=request.name,
        address=request.address,
        contact=request.contact,
        services=request.services,
        available=request.available,
        opening_hours=request.opening_hours
    )


@router.get("/clinics")
def list_clinics(available: bool | None = None):
    return _call(clinics.list_clinics, available=available)


@router.get("/clinics/{clinic_id}")
def get_clinic(clinic_id: str):
    return _call(clinics.get_clinic, clinic_id)


@router.patch("/clinics/{clinic_id}")
def update_clinic(clinic_id: str, request: ClinicUpdate):
    return _call(
        clinics.update_clinic,
        clinic_id,
        request.model_dump(exclude_unset=True)
    )


# -------- DOCTORS --------

@router.post("/doctors", status_code=201)
def register_doctor(request: DoctorCreate):
    return _call(
        doctors.create_doctor,
        name=request.name,
        qualification=request.qualification,
        specialization=request.specialization,
        consultation_modes=request.consultation_modes,
        clinic_id=request.clinic_id,
        hospital_id=request.hospital_id,
        available=request.available
    )


@router.get("/doctors")
def list_doctors(
    specialization: str | None = None,
    clinic_id: str | None = None,
    hospital_id: str | None = None,
    consultation_mode: ConsultationMode | None = None,
    available: bool | None = None
):
    return _call(
        doctors.list_doctors,
        specialization=specialization,
        clinic_id=clinic_id,
        hospital_id=hospital_id,
        consultation_mode=consultation_mode,
        available=available
    )


# Declared before /doctors/{doctor_id} so "availability" is not
# treated as a doctor id.
@router.get("/doctors/availability")
def doctor_availability_feed(
    specialization: str | None = None,
    consultation_mode: ConsultationMode | None = None,
    clinic_id: str | None = None,
    hospital_id: str | None = None,
    from_date: str | None = None,
    to_date: str | None = None,
    include_without_slots: bool = False,
    limit: int = Query(default=50, ge=1, le=200)
):
    """Structured doctor + open-slot data for the AI/recommendation side."""
    return _call(
        doctors.get_availability_data,
        specialization=specialization,
        consultation_mode=consultation_mode,
        clinic_id=clinic_id,
        hospital_id=hospital_id,
        from_date=from_date,
        to_date=to_date,
        include_without_slots=include_without_slots,
        limit=limit
    )


@router.get("/doctors/{doctor_id}")
def get_doctor(doctor_id: str):
    return _call(doctors.get_doctor, doctor_id)


@router.patch("/doctors/{doctor_id}")
def update_doctor(doctor_id: str, request: DoctorUpdate):
    return _call(
        doctors.update_doctor,
        doctor_id,
        request.model_dump(exclude_unset=True)
    )


@router.get("/doctors/{doctor_id}/availability")
def get_doctor_availability(
    doctor_id: str,
    from_date: str | None = None,
    to_date: str | None = None,
    consultation_mode: ConsultationMode | None = None
):
    return _call(
        doctors.get_doctor_availability,
        doctor_id,
        from_date=from_date,
        to_date=to_date,
        consultation_mode=consultation_mode
    )


# -------- DOCTOR SLOTS --------

@router.post("/doctors/{doctor_id}/slots", status_code=201)
def create_doctor_slot(doctor_id: str, request: SlotCreate):
    return _call(
        doctors.create_slot,
        doctor_id,
        date=request.date,
        start_time=request.start_time,
        end_time=request.end_time,
        consultation_mode=request.consultation_mode
    )


@router.get("/doctors/{doctor_id}/slots")
def list_doctor_slots(
    doctor_id: str,
    status: SlotStatus | None = None,
    from_date: str | None = None,
    to_date: str | None = None,
    consultation_mode: ConsultationMode | None = None
):
    return _call(
        doctors.list_slots,
        doctor_id,
        status=status,
        from_date=from_date,
        to_date=to_date,
        consultation_mode=consultation_mode
    )


@router.delete("/doctors/{doctor_id}/slots/{slot_id}")
def delete_doctor_slot(doctor_id: str, slot_id: str):
    return _call(doctors.delete_slot, doctor_id, slot_id)


# -------- APPOINTMENTS (extends the existing appointments table) --------

@router.post("/appointments/book", status_code=201)
def book_appointment(request: AppointmentBooking):
    return _call(
        appointments.book_appointment,
        patient_id=request.patient_id,
        slot_id=request.slot_id,
        consultation_mode=request.consultation_mode
    )


@router.get("/appointments")
def list_appointments(
    patient_id: str | None = None,
    doctor_id: str | None = None,
    status: str | None = None
):
    return _call(
        appointments.list_appointments,
        patient_id=patient_id,
        doctor_id=doctor_id,
        status=status
    )


@router.get("/appointments/{appointment_id}")
def get_appointment(appointment_id: str):
    return _call(appointments.get_appointment, appointment_id)


@router.post("/appointments/{appointment_id}/cancel")
def cancel_appointment(
    appointment_id: str,
    request: AppointmentCancellation | None = None
):
    reason = request.reason if request else None
    return _call(
        appointments.cancel_appointment,
        appointment_id,
        reason
    )


# -------- MEDICINES (extends the existing medicines table) --------

@router.get("/medicines/{medicine_id}")
def get_medicine(medicine_id: str):
    return _call(medicines.get_medicine, medicine_id)


@router.patch("/medicines/{medicine_id}/details")
def update_medicine_details(medicine_id: str, request: MedicineDetails):
    return _call(
        medicines.update_medicine_details,
        medicine_id,
        request.model_dump(exclude_unset=True)
    )


@router.get("/patients/{patient_id}/medicines")
def list_patient_medicines(patient_id: str):
    return _call(medicines.list_patient_medicines, patient_id)
