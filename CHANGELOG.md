# Member 3 - Healthcare backend changelog

Stack unchanged: Python, FastAPI, SQLite, existing `database.py` / `main.py` / `ai/`.

## 1. Files created
- `backend/healthcare/common.py` - error type, transaction helper (`BEGIN IMMEDIATE`), validation, ID and link helpers
- `backend/healthcare/schema.py` - idempotent table/column setup
- `backend/healthcare/schemas.py` - Pydantic request models
- `backend/healthcare/clinics.py` - clinic logic
- `backend/healthcare/doctors.py` - doctor, slot and availability logic (includes the AI feed)
- `backend/healthcare/appointments.py` - slot booking / cancellation on the existing appointments table
- `backend/healthcare/medicines.py` - medicine detail updates on the existing medicines table
- `backend/healthcare/routes.py` - FastAPI router
- `CHANGELOG.md`
- (`backend/healthcare/__init__.py` already existed, still empty)

## 2. Files modified (minimal)
- `backend/database.py` - `initialize_database()` now also calls `ensure_healthcare_schema(conn)` (3 lines)
- `backend/main.py` - imports the healthcare router and calls `app.include_router(...)` (2 lines)

## 3. Database changes
New tables (`CREATE TABLE IF NOT EXISTS`):
- `clinics` (id, name, address, contact, services, available, opening_hours, created_at)
- `doctors` (id, name, qualification, specialization, clinic_id, hospital_id, consultation_modes, available, created_at)
- `doctor_slots` (id, doctor_id, date, start_time, end_time, consultation_mode, status, created_at)
  with `UNIQUE (doctor_id, date, start_time)` and `CHECK (end_time > start_time)`

Columns added to EXISTING tables (only if missing):
- `appointments`: `doctor_id`, `slot_id`, `consultation_mode`, `cancellation_reason`
- `medicines`: `dosage`, `frequency`, `start_date`, `end_date`, `follow_up_date`

Indexes: `idx_doctor_slots_lookup`, and partial unique index `ux_appointments_active_slot`
on `appointments(slot_id)` for non-cancelled appointments (database-level double-booking guard).

## 4. APIs added
Clinics: `POST /clinics`, `GET /clinics`, `GET /clinics/{id}`, `PATCH /clinics/{id}`
Doctors: `POST /doctors`, `GET /doctors`, `GET /doctors/{id}`, `PATCH /doctors/{id}`
Slots: `POST /doctors/{id}/slots`, `GET /doctors/{id}/slots`, `DELETE /doctors/{id}/slots/{slot_id}`
Availability: `GET /doctors/{id}/availability`
AI feed: `GET /doctors/availability` (filters: specialization, consultation_mode, clinic_id,
hospital_id, from_date, to_date, include_without_slots, limit). Python callers can use
`healthcare.doctors.get_availability_data(...)` directly.
Appointments: `POST /appointments/book`, `GET /appointments`, `GET /appointments/{id}`,
`POST /appointments/{id}/cancel`
Medicines: `GET /medicines/{id}`, `PATCH /medicines/{id}/details`, `GET /patients/{patient_id}/medicines`

Behaviour notes:
- Consultation modes: `in_person` or `online`. Online bookings get a stored placeholder link
  `<base>/<random token>`; base defaults to `http://localhost:5173/consult`, override with env
  `AAROGYA_CONSULT_BASE_URL`.
- Booking claims the slot with a conditional UPDATE inside `BEGIN IMMEDIATE`; cancelling sets the
  appointment to `cancelled` and the slot back to `available` in one transaction.
- Slots for the same doctor may not overlap (not only exact duplicates). Slots cannot be created in the past.
- A doctor marked `available: false` cannot be booked and is left out of the AI feed.

## 5. Existing functionality intentionally preserved
- All existing routes and handlers in `main.py` are untouched (SOS/emergency flow, `/match`,
  `/appointments` POST, `/medicines` POST and PATCH, `/patients/{id}/followups`, donors, hospitals).
- `ai/` modules untouched; `check_continuity` works on the extended appointment/medicine rows.
- Existing tables, rows and column definitions are not altered or dropped; legacy appointments
  (with only `doctor_name`) and medicines keep working.
- No new dependencies. Stale `__pycache__` folders were left out of the ZIP.
