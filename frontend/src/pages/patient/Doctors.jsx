
import React, { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import {
  Search,
  MapPin,
  Video,
  Hospital,
  SlidersHorizontal,
  Star
} from "lucide-react";

import PageHeader from "../../components/common/PageHeader";
import { doctorsApi } from "../../services/api";

export default function Doctors() {
  const [searchParams] = useSearchParams();

  const [doctors, setDoctors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [search, setSearch] = useState(
    () => searchParams.get("search") || ""
  );

  const [specialty, setSpecialty] = useState("");
  const [mode, setMode] = useState("");

  useEffect(() => {
    setSearch(searchParams.get("search") || "");
  }, [searchParams]);

  useEffect(() => {
    let active = true;

    async function loadDoctors() {
      try {
        const response = await doctorsApi.list();

        if (active) {
          setDoctors(
            Array.isArray(response.data) ? response.data : []
          );
          setError("");
        }
      } catch (err) {
        console.error("Doctors API error:", err);

        if (active) {
          setError(
            "Unable to load doctors. Check that FastAPI is running."
          );
        }
      } finally {
        if (active) setLoading(false);
      }
    }

    loadDoctors();

    return () => {
      active = false;
    };
  }, []);

  const specialties = [
    ...new Set(
      doctors.map((d) => d.specialization).filter(Boolean)
    )
  ];

  const filteredDoctors = doctors.filter((doctor) => {
    const query = search.trim().toLowerCase();

    const matchesSearch =
      !query ||
      (doctor.name || "").toLowerCase().includes(query) ||
      (doctor.specialization || "").toLowerCase().includes(query);

    const matchesSpecialty =
      !specialty ||
      doctor.specialization === specialty;

    const matchesMode =
      !mode ||
      (doctor.consultation_modes || []).includes(mode);

    return matchesSearch && matchesSpecialty && matchesMode;
  });

  function resetFilters() {
    setSearch("");
    setSpecialty("");
    setMode("");
  }

  return (
    <>
      <PageHeader
        title="Find a Doctor"
        subtitle="Explore doctors registered on Aarogya One."
      />

      <div className="search-panel">
        <div className="input-wrap">
          <Search size={18} />

          <input
            type="text"
            placeholder="Search doctor or specialty"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>

        <select
          value={specialty}
          onChange={(e) => setSpecialty(e.target.value)}
        >
          <option value="">All specialties</option>

          {specialties.map((item) => (
            <option key={item} value={item}>
              {item}
            </option>
          ))}
        </select>

        <select
          value={mode}
          onChange={(e) => setMode(e.target.value)}
        >
          <option value="">All modes</option>
          <option value="online">Online</option>
          <option value="in_person">In-person</option>
        </select>

        <button
          type="button"
          className="btn outline"
          onClick={resetFilters}
        >
          <SlidersHorizontal size={17} />
          Reset filters
        </button>
      </div>

      <div className="recommendation-banner">
        <Star size={20} />

        <div>
          <b>Symptom-based recommendation</b>
          <p>
            The dashboard provides basic demo specialty
            suggestions. These are not medical diagnoses.
          </p>
        </div>
      </div>

      {loading && <p>Loading doctors...</p>}

      {error && (
        <p role="alert">{error}</p>
      )}

      {!loading && !error && filteredDoctors.length === 0 && (
        <p>No doctors found for the selected filters.</p>
      )}

      {!loading && !error && (
        <div className="doctor-list">
          {filteredDoctors.map((doctor) => {
            const location =
              doctor.clinic?.name ||
              doctor.hospital?.name ||
              "Location not specified";

            const modes = (
              doctor.consultation_modes || []
            )
              .map((item) =>
                item === "in_person"
                  ? "In-person"
                  : item === "online"
                    ? "Online"
                    : item
              )
              .join(" & ");

            const initial =
              doctor.name
                ?.replace(/^Dr\.\s*/i, "")
                .charAt(0)
                .toUpperCase() || "D";

            return (
              <div
                className="doctor-card card"
                key={doctor.doctor_id}
              >
                <div className="doctor-avatar">
                  {initial}
                </div>

                <div className="doctor-info">
                  <h3>{doctor.name}</h3>

                  <b>{doctor.specialization}</b>

                  <p>
                    {doctor.qualification ||
                      "Qualification not specified"}
                  </p>

                  <p>
                    <Hospital size={14} />
                    {" "}{location}
                  </p>

                  <div className="doctor-tags">
                    <span>
                      <MapPin size={13} />
                      {" "}View profile for appointment slots
                    </span>

                    <span>
                      <Video size={13} />
                      {" "}{modes || "Mode not specified"}
                    </span>
                  </div>
                </div>

                <div className="doctor-action">
                  <span
                    className={
                      doctor.available
                        ? "available"
                        : "unavailable"
                    }
                  >
                    {doctor.available
                      ? "● Available"
                      : "● Unavailable"}
                  </span>

                  <Link
                    className="btn primary"
                    to={`/patient/doctors/${encodeURIComponent(
                      doctor.doctor_id
                    )}`}
                  >
                    View profile
                  </Link>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </>
  );
}