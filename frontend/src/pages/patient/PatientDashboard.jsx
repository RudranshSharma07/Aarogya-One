
import React, { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  CalendarDays,
  ChevronRight,
  Droplets,
  HeartPulse,
  Pill,
  ShieldAlert,
  Stethoscope,
  Video,
  Clock3
} from "lucide-react";

import StatCard from "../../components/common/StatCard";
import PageHeader from "../../components/common/PageHeader";
import { appointmentApi } from "../../services/api";

const PATIENT_ID = "PAT-DEMO-001";

function suggestSpecialty(symptoms) {
  const text = symptoms.toLowerCase();

  if (!text.trim()) return "";

  if (/rash|skin|acne|itch|daag/.test(text)) {
    return "Dermatologist";
  }

  if (/tooth|teeth|dental/.test(text)) {
    return "Dentist";
  }

  if (/eye|vision/.test(text)) {
    return "Ophthalmologist";
  }

  if (/joint|bone|knee/.test(text)) {
    return "Orthopedist";
  }

  if (/fever|cough|cold|headache/.test(text)) {
    return "General Physician";
  }

  return "";
}

function formatDate(date) {
  if (!date) return "Date unavailable";

  return new Date(`${date}T00:00:00`).toLocaleDateString(
    "en-IN",
    {
      day: "numeric",
      month: "short",
      year: "numeric"
    }
  );
}

function formatTime(time) {
  if (!time) return "";

  const [hours, minutes] = time.split(":").map(Number);

  if (!Number.isFinite(hours) || !Number.isFinite(minutes)) {
    return time;
  }

  const period = hours >= 12 ? "PM" : "AM";
  const hour = hours % 12 || 12;

  return `${hour}:${String(minutes).padStart(2, "0")} ${period}`;
}

export default function PatientDashboard() {
  const navigate = useNavigate();

  const [symptoms, setSymptoms] = useState("");
  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [appointmentsError, setAppointmentsError] = useState("");

  const specialty = suggestSpecialty(symptoms);

  useEffect(() => {
    let active = true;

    async function loadAppointments() {
      try {
        const response = await appointmentApi.list(PATIENT_ID);

        if (!active) return;

        setAppointments(
          Array.isArray(response.data) ? response.data : []
        );

        setAppointmentsError("");
      } catch (err) {
        console.error("Dashboard appointments error:", err);

        if (active) {
          setAppointmentsError(
            "Unable to load appointments. Check your backend."
          );
        }
      } finally {
        if (active) setLoading(false);
      }
    }

    loadAppointments();

    return () => {
      active = false;
    };
  }, []);

  const now = new Date();

  const upcomingAppointments = appointments
    .filter((appointment) => {
      if (appointment.status !== "scheduled") {
        return false;
      }

      const dateTime = new Date(
        `${appointment.date}T${appointment.start_time || "00:00"}:00`
      );

      return !Number.isNaN(dateTime.getTime()) &&
        dateTime >= now;
    })
    .sort((a, b) => {
      const first = `${a.date}T${a.start_time}`;
      const second = `${b.date}T${b.start_time}`;

      return first.localeCompare(second);
    });

  function findDoctors() {
    const searchTerm = specialty || symptoms.trim();

    if (searchTerm) {
      navigate(
        `/patient/doctors?search=${encodeURIComponent(searchTerm)}`
      );
    } else {
      navigate("/patient/doctors");
    }
  }

  return (
    <>
      <PageHeader
        title="Welcome to Aarogya One 👋"
        subtitle="Manage your care and explore available services."
        action={
          <Link className="btn danger" to="/patient/sos">
            <ShieldAlert size={17} />
            Emergency SOS
          </Link>
        }
      />

      <div className="stats-grid">
        <StatCard
          icon={CalendarDays}
          label="Upcoming appointments"
          value={
            loading
              ? "..."
              : appointmentsError
                ? "—"
                : upcomingAppointments.length
          }
          note={
            appointmentsError
              ? "Unable to load"
              : "Scheduled upcoming bookings"
          }
        />

        <StatCard
          icon={Pill}
          label="Medicine reminders"
          value="—"
          note="Pending medicines API integration"
        />

        <StatCard
          icon={HeartPulse}
          label="Follow-ups"
          value="—"
          note="Pending follow-up integration"
        />

        <StatCard
          icon={Droplets}
          label="Donor status"
          value="—"
          note="Pending donor integration"
        />
      </div>

      <div className="dashboard-grid">
        {/* Find doctors */}
        <section className="card large">
          <div className="card-title">
            <div>
              <h3>Find the right doctor</h3>
              <p>
                Enter symptoms to explore a relevant specialty.
              </p>
            </div>

            <Stethoscope size={22} />
          </div>

          <div className="symptom-box">
            <input
              type="text"
              value={symptoms}
              onChange={(e) => setSymptoms(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") findDoctors();
              }}
              placeholder="e.g. fever, cough, headache..."
              aria-label="Enter symptoms"
            />

            <button
              type="button"
              className="btn primary"
              onClick={findDoctors}
            >
              Find doctors
            </button>
          </div>

          {symptoms.trim() && (
            <div className="suggestion">
              <span className="success-dot" />

              <div>
                <b>Demo specialty suggestion</b>

                <p>
                  {specialty
                    ? `Explore ${specialty} profiles for the symptoms entered.`
                    : "No specific specialty matched. You can browse the doctor directory."}
                  {" "}
                  This is not a diagnosis.
                </p>
              </div>
            </div>
          )}
        </section>

        {/* Live appointments */}
        <section className="card">
          <div className="card-title">
            <div>
              <h3>Upcoming appointments</h3>
              <p>Your scheduled care events</p>
            </div>

            <CalendarDays size={22} />
          </div>

          {loading ? (
            <p>Loading appointments...</p>
          ) : appointmentsError ? (
            <p role="alert">{appointmentsError}</p>
          ) : upcomingAppointments.length === 0 ? (
            <p>
              No upcoming appointments. Find a doctor to
              book your next consultation.
            </p>
          ) : (
            <div className="appointment-list">
              {upcomingAppointments.slice(0, 3).map(
                (appointment) => (
                  <div
                    className="appointment-item"
                    key={appointment.appointment_id}
                    style={{
                      padding: "12px 0",
                      borderBottom:
                        "1px solid rgba(128,128,128,0.2)"
                    }}
                  >
                    <h4 style={{ margin: "0 0 8px" }}>
                      {appointment.doctor_name}
                    </h4>

                    <p style={{ margin: "4px 0" }}>
                      <CalendarDays
                        size={15}
                        style={{ verticalAlign: "middle" }}
                      />
                      {" "}
                      {formatDate(appointment.date)}
                    </p>

                    <p style={{ margin: "4px 0" }}>
                      <Clock3
                        size={15}
                        style={{ verticalAlign: "middle" }}
                      />
                      {" "}
                      {formatTime(appointment.start_time)}
                      {" – "}
                      {formatTime(appointment.end_time)}
                    </p>

                    <p style={{ margin: "4px 0" }}>
                      <Video
                        size={15}
                        style={{ verticalAlign: "middle" }}
                      />
                      {" "}
                      {appointment.consultation_mode === "online"
                        ? "Online consultation"
                        : "In-person consultation"}
                    </p>

                    {appointment.consultation_link && (
                      <a
                        className="text-link"
                        href={appointment.consultation_link}
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        Join consultation
                        <ChevronRight size={15} />
                      </a>
                    )}
                  </div>
                )
              )}
            </div>
          )}

          <Link
            className="text-link"
            to="/patient/appointments"
          >
            View all appointments
            <ChevronRight size={15} />
          </Link>
        </section>

        {/* Medicines */}
        <section className="card">
          <div className="card-title">
            <div>
              <h3>Medicine reminders</h3>
              <p>Your medicine schedule</p>
            </div>

            <Pill size={22} />
          </div>

          <p>
            Open your medicines page to manage reminders.
          </p>

          <Link
            className="text-link"
            to="/patient/medicines"
          >
            View medicines
            <ChevronRight size={15} />
          </Link>
        </section>

        {/* Emergency SOS */}
        <section className="card emergency-card">
          <div className="emergency-icon">
            <ShieldAlert size={25} />
          </div>

          <div>
            <h3>Emergency SOS</h3>

            <p>
              Need urgent coordination?
              Create an SOS request.
            </p>

            <Link
              className="btn danger"
              to="/patient/sos"
            >
              Open Emergency Center
            </Link>
          </div>
        </section>
      </div>
    </>
  );
}