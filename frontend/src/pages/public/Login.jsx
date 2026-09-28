import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { HeartPulse, LockKeyhole, Mail, Eye, EyeOff, ShieldCheck } from "lucide-react";

export default function Login() {
  const navigate = useNavigate();
  const [show, setShow] = useState(false);
  const [role, setRole] = useState("patient");
  const submit = (e) => { e.preventDefault(); navigate(`/${role}/dashboard`); };

  return <div className="auth-page">
    <div className="auth-visual"><Link to="/" className="landing-brand"><span className="brand-mark"><HeartPulse size={22}/></span><span><b>Aarogya One</b><small>Healthcare connected</small></span></Link><div><div className="eyebrow"><ShieldCheck size={16}/> Secure demo access</div><h1>Welcome back to connected care.</h1><p>Access your healthcare dashboard and keep your care journey organized.</p></div><small>Demo authentication — backend authentication is not implemented yet.</small></div>
    <div className="auth-form-wrap"><form className="auth-form" onSubmit={submit}><div className="form-heading"><span className="mobile-logo"><HeartPulse/></span><h2>Sign in</h2><p>Continue to your Aarogya One dashboard.</p></div>
      <label>Email address<div className="input-wrap"><Mail size={18}/><input type="email" placeholder="you@example.com" required/></div></label>
      <label>Password<div className="input-wrap"><LockKeyhole size={18}/><input type={show ? "text" : "password"} placeholder="••••••••" required/><button type="button" onClick={() => setShow(!show)}>{show ? <EyeOff size={17}/> : <Eye size={17}/>}</button></div></label>
      <div className="form-row"><label className="checkbox"><input type="checkbox"/> Remember me</label><a href="#forgot">Forgot password?</a></div>
      <label>Demo role<select value={role} onChange={e => setRole(e.target.value)}><option value="patient">Patient</option><option value="donor">Donor</option><option value="provider">Healthcare Provider</option><option value="admin">Admin</option></select></label>
      <button className="btn primary full" type="submit">Sign in</button>
      <p className="switch-auth">Don't have an account? <Link to="/register">Create one</Link></p>
    </form></div>
  </div>
}