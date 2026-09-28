import { Link } from "react-router-dom";
import { Search, MapPin, Video, Hospital, SlidersHorizontal, Star } from "lucide-react";
import PageHeader from "../../components/common/PageHeader";

const doctors = [
  {id:1,name:"Dr. Ananya Sharma",spec:"General Physician",qual:"MBBS, MD",place:"Aarogya Care Hospital",mode:"Online & Offline",slot:"Today · 4:30 PM"},
  {id:2,name:"Dr. Rohan Mehta",spec:"Internal Medicine",qual:"MBBS, MD",place:"Mediconnect Clinic",mode:"Offline",slot:"Tomorrow · 10:00 AM"},
  {id:3,name:"Dr. Priya Kapoor",spec:"Dermatologist",qual:"MBBS, MD (Dermatology)",place:"City Health Clinic",mode:"Online",slot:"Tomorrow · 2:00 PM"}
];

export default function Doctors() {
  return <><PageHeader title="Find a Doctor" subtitle="Explore demo doctor profiles. Real doctor directory APIs are not connected yet."/>
    <div className="search-panel"><div className="input-wrap"><Search size={18}/><input placeholder="Search symptoms, specialty or doctor"/></div><select><option>All specialties</option><option>General Physician</option><option>Dermatologist</option><option>Internal Medicine</option></select><select><option>All modes</option><option>Online</option><option>Offline</option></select><button className="btn outline"><SlidersHorizontal size={17}/> Filters</button></div>
    <div className="recommendation-banner"><Star size={20}/><div><b>Symptom-based recommendation</b><p>Enter your symptoms to get a specialty suggestion. This helps find care and does not diagnose disease.</p></div></div>
    <div className="doctor-list">{doctors.map(d=><div className="doctor-card card" key={d.id}><div className="doctor-avatar">{d.name.split(" ").slice(1,2)[0]?.[0] || "D"}</div><div className="doctor-info"><h3>{d.name}</h3><b>{d.spec}</b><p>{d.qual}</p><p><Hospital size={14}/> {d.place}</p><div className="doctor-tags"><span><MapPin size={13}/> Available slot: {d.slot}</span><span><Video size={13}/> {d.mode}</span></div></div><div className="doctor-action"><span className="available">● Available</span><Link to={`/patient/doctors/${d.id}`} className="btn primary">View profile</Link></div></div>)}</div>
  </>;
}