import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { HeartPulse, UserRound, Droplets, Hospital, Stethoscope, ArrowRight } from "lucide-react";

const roles = [
  ["patient","Patient","Find care and manage appointments",UserRound],
  ["donor","Donor","Help during emergency requests",Droplets],
  ["hospital","Hospital","Manage services and emergencies",Hospital],
  ["clinic","Clinic","Manage doctors and appointments",Hospital],
  ["doctor","Independent Doctor","Manage profile and availability",Stethoscope]
];

export default function Register() {
  const [role, setRole] = useState("patient");
  const navigate = useNavigate();
  return <div className="auth-page register-page"><div className="register-box">
    <Link to="/" className="landing-brand"><span className="brand-mark"><HeartPulse size={22}/></span><span><b>Aarogya One</b><small>Healthcare connected</small></span></Link>
    <div className="form-heading"><h2>Create your account</h2><p>Choose the profile that matches how you use Aarogya One.</p></div>
    <div className="role-grid">{roles.map(([id,title,desc,Icon]) => <button key={id} className={`role-option ${role===id ? "selected":""}`} onClick={() => setRole(id)}><Icon size={22}/><span><b>{title}</b><small>{desc}</small></span></button>)}</div>
    <div className="two-col"><label>Full name<input placeholder="Enter your name"/></label><label>Phone number<input placeholder="+91 XXXXX XXXXX"/></label></div>
    <div className="two-col"><label>Email address<input type="email" placeholder="you@example.com"/></label><label>Password<input type="password" placeholder="Create a password"/></label></div>
    <button className="btn primary full" onClick={() => navigate(role === "doctor" || role === "hospital" || role === "clinic" ? "/provider/dashboard" : `/${role}/dashboard`)}>Create demo account <ArrowRight size={18}/></button>
    <p className="demo-note">Demo registration UI. Real authentication and role authorization will be enforced by the backend when available.</p>
    <p className="switch-auth">Already registered? <Link to="/login">Sign in</Link></p>
  </div></div>
}