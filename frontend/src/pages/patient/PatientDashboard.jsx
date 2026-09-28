import { Link } from "react-router-dom";
import { CalendarDays, ChevronRight, Clock3, Droplets, HeartPulse, Pill, ShieldAlert, Stethoscope } from "lucide-react";
import StatCard from "../../components/common/StatCard";
import Badge from "../../components/common/Badge";
import PageHeader from "../../components/common/PageHeader";

export default function PatientDashboard() {
  return <><PageHeader title="Good morning, Yashika 👋" subtitle="Here’s what’s happening with your care today." action={<Link className="btn danger" to="/patient/sos"><ShieldAlert size={17}/> Emergency SOS</Link>}/>
    <div className="stats-grid"><StatCard icon={CalendarDays} label="Upcoming appointments" value="2" note="Next: Today, 4:30 PM"/><StatCard icon={Pill} label="Medicine reminders" value="3" note="1 due in the next hour"/><StatCard icon={HeartPulse} label="Follow-ups" value="1" note="Due this week"/><StatCard icon={Droplets} label="Donor status" value="Active" note="Available for requests" tone="green"/></div>
    <div className="dashboard-grid">
      <section className="card large"><div className="card-title"><div><h3>Find the right doctor</h3><p>Enter symptoms to explore an appropriate specialty.</p></div><Stethoscope size={22}/></div><div className="symptom-box"><input placeholder="e.g. fever, cough, headache..."/><button className="btn primary" onClick={() => location.href="/patient/doctors"}>Find doctors</button></div><div className="suggestion"><span className="success-dot"></span><div><b>Demo suggestion</b><p>For fever symptoms, General Physician profiles can be explored. This is not a diagnosis.</p></div></div></section>
      <section className="card"><div className="card-title"><div><h3>Upcoming</h3><p>Your next care events</p></div><CalendarDays size={22}/></div><div className="appointment-mini"><div className="date-box"><b>28</b><span>SEP</span></div><div><b>Dr. Ananya Sharma</b><p>General Physician</p><small><Clock3 size={13}/> 4:30 PM · Online</small></div></div><Link className="text-link" to="/patient/appointments">View all appointments <ChevronRight size={15}/></Link></section>
      <section className="card"><div className="card-title"><div><h3>Medicine reminders</h3><p>Today's status</p></div><Pill size={22}/></div>{["Vitamin D","Paracetamol","Daily supplement"].map((x,i)=><div className="list-row" key={x}><span className={`check ${i===1?"done":""}`}>{i===1?"✓":""}</span><span><b>{x}</b><small>{i===0?"1:00 PM":i===1?"Completed":"9:00 PM"}</small></span><Badge tone={i===1?"green":"orange"}>{i===1?"Done":"Pending"}</Badge></div>)}</section>
      <section className="card emergency-card"><div className="emergency-icon"><ShieldAlert size={25}/></div><div><h3>Emergency SOS</h3><p>Need urgent coordination? Create an SOS request.</p><Link className="btn danger" to="/patient/sos">Open Emergency Center</Link></div></section>
    </div>
  </>;
}