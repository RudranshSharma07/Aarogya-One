from typing import Literal

from pydantic import BaseModel, Field

ConsultationMode = Literal["in_person", "online"]

DATE_PATTERN = r"^\d{4}-\d{2}-\d{2}$"
TIME_PATTERN = r"^\d{2}:\d{2}$"


# -------- clinics --------

class ClinicCreate(BaseModel):
    name: str = Field(min_length=1)
    address: str = Field(min_length=1)
    contact: str = Field(min_length=1)
    services: list[str] = Field(min_length=1)
    available: bool = True
    opening_hours: str | None = None


class ClinicUpdate(BaseModel):
    name: str | None = None
    address: str | None = None
    contact: str | None = None
    services: list[str] | None = None
    available: bool | None = None
    opening_hours: str | None = None


# -------- doctors --------

class DoctorCreate(BaseModel):
    name: str = Field(min_length=1)
    qualification: str = Field(min_length=1)
    specialization: str = Field(min_length=1)
    consultation_modes: list[ConsultationMode] = Field(min_length=1)
    clinic_id: str | None = None
    hospital_id: str | None = None
    available: bool = True


class DoctorUpdate(BaseModel):
    name: str | None = None
    qualification: str | None = None
    specialization: str | None = None
    consultation_modes: list[ConsultationMode] | None = None
    clinic_id: str | None = None
    hospital_id: str | None = None
    available: bool | None = None


# -------- slots --------

class SlotCreate(BaseModel):
    date: str = Field(pattern=DATE_PATTERN)
    start_time: str = Field(pattern=TIME_PATTERN)
    end_time: str = Field(pattern=TIME_PATTERN)
    consultation_mode: ConsultationMode


# -------- appointments --------

class AppointmentBooking(BaseModel):
    patient_id: str = Field(min_length=1)
    slot_id: str = Field(min_length=1)
    consultation_mode: ConsultationMode | None = None


class AppointmentCancellation(BaseModel):
    reason: str | None = Field(default=None, max_length=500)


# -------- medicines --------

class MedicineDetails(BaseModel):
    dosage: str | None = Field(default=None, max_length=200)
    frequency: str | None = Field(default=None, max_length=200)
    start_date: str | None = Field(default=None, pattern=DATE_PATTERN)
    end_date: str | None = Field(default=None, pattern=DATE_PATTERN)
    follow_up_date: str | None = Field(default=None, pattern=DATE_PATTERN)
