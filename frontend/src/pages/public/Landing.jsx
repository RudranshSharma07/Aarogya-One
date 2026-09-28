import { Link } from "react-router-dom";
import { ArrowRight, CalendarCheck, HeartPulse, MapPin, ShieldAlert, Stethoscope, Users, Activity, Droplets } from "lucide-react";

const features = [
  { icon: Stethoscope, title: "Find the right doctor", text: "Explore healthcare professionals and consultation options from one place." },
  { icon: CalendarCheck, title: "Easy appointments", text: "Manage bookings, upcoming visits and consultation details." },
  { icon: ShieldAlert, title: "Emergency coordination", text: "Create an SOS request and follow the emergency coordination journey." },
  { icon: Droplets, title: "Blood donor network", text: "Connect emergency resource requests with registered donors." }
];

export default function Landing() {
  return (
    <div className="landing">
      <header className="landing-nav">
        <Link className="landing-brand" to="/"><span className="brand-mark"><HeartPulse size={22}/></span><span><b>Aarogya One</b><small>Healthcare connected</small></span></Link>
        <nav><a href="#features">Features</a><a href="#how">How it works</a><Link to="/login">Login</Link><Link className="nav-register" to="/register">Get started</Link></nav>
      </header>

      <section className="hero">
        <div className="hero-copy">
          <div className="eyebrow"><Activity size={16}/> Integrated healthcare & emergency coordination</div>
          <h1>Healthcare that stays <span>connected</span> when it matters.</h1>
          <p>Aarogya One brings doctor discovery, appointments, follow-ups, blood donor matching and emergency hospital coordination into one simple platform.</p>
          <div className="hero-actions">
            <Link className="btn primary" to="/patient/doctors">Find a Doctor <ArrowRight size={18}/></Link>
            <Link className="btn outline" to="/patient/sos"><ShieldAlert size={18}/> Emergency SOS</Link>
          </div>
          <div className="trust-row"><span><Users size={17}/> Patients</span><span><Stethoscope size={17}/> Providers</span><span><Droplets size={17}/> Donors</span></div>
        </div>

        <div className="hero-card">
          <div className="hero-card-head"><span>Emergency Center</span><span className="live-dot">● Live</span></div>
          <div className="sos-card"><ShieldAlert size={30}/><div><b>Need emergency help?</b><p>Create an SOS request and coordinate available resources.</p></div></div>
          <Link to="/patient/sos" className="sos-btn">CREATE EMERGENCY SOS</Link>
          <div className="mini-stats"><div><b>24/7</b><span>Coordination</span></div><div><b>4</b><span>User roles</span></div><div><b>1</b><span>Connected platform</span></div></div>
        </div>
      </section>

      <section id="features" className="section">
        <div className="section-heading"><span className="eyebrow">ONE PLATFORM</span><h2>Everything connected around your care</h2><p>Designed to make everyday healthcare and urgent coordination easier to navigate.</p></div>
        <div className="feature-grid">{features.map(({icon: Icon, title, text}) => <div className="feature-card" key={title}><div className="feature-icon"><Icon size={23}/></div><h3>{title}</h3><p>{text}</p><ArrowRight size={17}/></div>)}</div>
      </section>

      <section id="how" className="how section">
        <div className="section-heading"><span className="eyebrow">HOW IT WORKS</span><h2>From care discovery to emergency coordination</h2></div>
        <div className="steps"><div><b>01</b><h3>Create your profile</h3><p>Register as a patient, donor or healthcare provider.</p></div><div><b>02</b><h3>Connect with care</h3><p>Find doctors, manage appointments and follow-ups.</p></div><div><b>03</b><h3>Coordinate emergencies</h3><p>Raise SOS requests and track confirmed responses.</p></div></div>
      </section>

      <footer><div className="landing-brand"><span className="brand-mark"><HeartPulse size={21}/></span><b>Aarogya One</b></div><p>Connected healthcare for everyday needs and critical moments.</p><span>© 2026 Aarogya One</span></footer>
    </div>
  );
}