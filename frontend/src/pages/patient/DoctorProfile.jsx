
import React, { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import {
  ArrowLeft,
  CalendarDays,
  CheckCircle2,
  Clock3,
  Hospital,
  MapPin,
  Video
} from "lucide-react";

import PageHeader from "../../components/common/PageHeader";
import {
  doctorsApi,
  doctorSlotsApi,
  bookingApi
} from "../../services/api";

const PATIENT_ID = "PAT-DEMO-001";

export default function DoctorProfile() {
  const { id } = useParams();

  const [doctor, setDoctor] = useState(null);
  const [slots, setSlots] = useState([]);
  const [selectedSlot, setSelectedSlot] = useState(null);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [slotsError, setSlotsError] = useState("");

  const [booking, setBooking] = useState(false);
  const [bookingError, setBookingError] = useState("");
  const [confirmation, setConfirmation] = useState(null);

  // Load doctor and appointment slots.
  useEffect(() => {
    let active = true;

    async function loadProfile() {
      setLoading(true);
      setError("");
      setSlotsError("");
      setSelectedSlot(null);
      setConfirmation(null);

      try {
        const response = await doctorsApi.list();

        const doctors = Array.isArray(response.data)
          ? response.data
          : [];

        const found = doctors.find(
          (item) => item.doctor_id === id
        );

        if (!found) {
          throw new Error("Doctor not found.");
        }

        if (!active) return;

        setDoctor(found);

        try {
          const response = await doctorSlotsApi.list(id);

          if (!active) return;

          const data = response.data;

          setSlots(
            Array.isArray(data)
              ? data
              : Array.isArray(data?.slots)
                ? data.slots
                : []
          );
        } catch (err) {
          console.error("Slot loading error:", err);

          if (active) {
            setSlotsError(
              "Unable to load appointment slots."
            );
          }
        }
      } catch (err) {
        console.error("Doctor loading error:", err);

        if (active) {
          setError(
            err.message || "Unable to load doctor."
          );
        }
      } finally {
        if (active) setLoading(false);
      }
    }

    loadProfile();

    return () => {
      active = false;
    };
  }, [id]);

  // Book the selected available slot.
  async function handleBooking() {
    if (
      !selectedSlot ||
      selectedSlot.status !== "available" ||
      booking
    ) {
      return;
    }

    setBooking(true);
    setBookingError("");
    setConfirmation(null);

    try {
      const response = await bookingApi.create({
        patient_id: PATIENT_ID,
        slot_id: selectedSlot.slot_id,
        consultation_mode:
          selectedSlot.consultation_mode
      });

      setConfirmation(response.data);
      setSelectedSlot(null);

      // Booking succeeded. Refresh slots separately,
      // so a refresh failure cannot look like a
      // booking failure.
      try {
        const refreshed = await doctorSlotsApi.list(id);

        const data = refreshed.data;

        setSlots(
          Array.isArray(data)
            ? data
            : Array.isArray(data?.slots)
              ? data.slots
              : []
        );

        setSlotsError("");
      } catch (err) {
        console.error("Slot refresh error:", err);

        setSlotsError(
          "Appointment booked, but slots could not be refreshed."
        );
      }
    } catch (err) {
      console.error("Booking error:", err);

      const detail = err.response?.data?.detail;

      setBookingError(
        typeof detail === "string"
          ? detail
          : "Booking failed. Please try again."
      );
    } finally {
      setBooking(false);
    }
  }

  if (loading) {
    return <p>Loading doctor profile...</p>;
  }

  if (error || !doctor) {
    return (
      <>
        <Link
          to="/patient/doctors"
          className="back-link"
        >
          <ArrowLeft size={16} />
          Back to doctors
        </Link>

        <p role="alert">
          {error || "Doctor not found."}
        </p>
      </>
    );
  }

  const modes = (
    doctor.consultation_modes || []
  )
    .map((mode) =>
      mode === "in_person"
        ? "In-person"
        : "Online"
    )
    .join(" & ");

  const location =
    doctor.clinic?.name ||
    doctor.hospital?.name ||
    "Location not specified";

  const initials = doctor.name
    .replace(/^Dr\.\s*/i, "")
    .split(" ")
    .slice(0, 2)
    .map((part) => part[0])
    .join("")
    .toUpperCase();

  return (
    <>
      <Link
        to="/patient/doctors"
        className="back-link"
      >
        <ArrowLeft size={16} />
        Back to doctors
      </Link>

      <PageHeader
        title={doctor.name}
        subtitle={`${doctor.specialization} · Registered doctor`}
      />

      <div className="profile-grid">
        {/* Doctor information */}
        <section className="card doctor-profile">
          <div className="profile-avatar">
            {initials}
          </div>

          <h2>{doctor.name}</h2>

          <b>
            {doctor.qualification} ·{" "}
            {doctor.specialization}
          </b>

          <p>
            <Hospital size={15} />
            {" "}{location}
          </p>

          <p>
            <MapPin size={15} />
            {" "}{location}
          </p>

          <div className="info-chips">
            <span>
              <Video size={15} />
              {" "}{modes || "Mode not specified"}
            </span>

            <span>
              <CheckCircle2 size={15} />
              {" "}
              {doctor.available
                ? "Available"
                : "Currently unavailable"}
            </span>
          </div>
        </section>

        {/* Appointment booking */}
        <section className="card">
          <div className="card-title">
            <div>
              <h3>Book an appointment</h3>
              <p>Select an available slot.</p>
            </div>

            <CalendarDays size={22} />
          </div>

          {slotsError && (
            <p role="alert">{slotsError}</p>
          )}

          {!slotsError && slots.length === 0 && (
            <p>No appointment slots available.</p>
          )}

          <div className="slots">
            {slots.map((slot) => {
              const available =
                slot.status === "available";

              const selected =
                selectedSlot?.slot_id ===
                slot.slot_id;

              return (
                <button
                  key={slot.slot_id}
                  type="button"
                  className={
                    selected ? "selected" : ""
                  }
                  disabled={
                    !available || booking
                  }
                  onClick={() => {
                    setSelectedSlot(slot);
                    setBookingError("");
                  }}
                >
                  <Clock3 size={14} />

                  {slot.date} ·{" "}
                  {slot.start_time}–
                  {slot.end_time}

                  {!available && " (Booked)"}
                </button>
              );
            })}
          </div>

          {selectedSlot && (
            <p>
              Selected: {selectedSlot.date},
              {" "}{selectedSlot.start_time}–
              {selectedSlot.end_time}
              {" "}({selectedSlot.consultation_mode})
            </p>
          )}

          <button
            type="button"
            className="btn primary full"
            disabled={
              !selectedSlot ||
              !doctor.available ||
              booking
            }
            onClick={handleBooking}
          >
            {booking
              ? "Booking..."
              : "Book Appointment"}
          </button>

          {bookingError && (
            <p role="alert">
              {bookingError}
            </p>
          )}

          {confirmation && (
            <div
              className="suggestion"
              role="status"
            >
              <h3>
                <CheckCircle2 size={20} />
                {" "}Appointment booked!
              </h3>

              <p>
                <b>Appointment ID:</b>{" "}
                {confirmation.appointment_id}
              </p>

              <p>
                <b>Doctor:</b>{" "}
                {confirmation.doctor_name}
              </p>

              <p>
                <b>Date:</b>{" "}
                {confirmation.date}
              </p>

              <p>
                <b>Time:</b>{" "}
                {confirmation.start_time}–
                {confirmation.end_time}
              </p>

              <p>
                <b>Status:</b>{" "}
                {confirmation.status}
              </p>

              {confirmation.consultation_link && (
                <a
                  href={
                    confirmation.consultation_link
                  }
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  Consultation link
                </a>
              )}
            </div>
          )}
        </section>
      </div>
    </>
  );
}