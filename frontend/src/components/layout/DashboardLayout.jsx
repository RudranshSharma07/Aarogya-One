import { NavLink, useNavigate } from "react-router-dom";
import { useState } from "react";
import {
  Activity, CalendarDays, ChevronLeft, ChevronRight, ClipboardList,
  Droplets, HeartPulse, Hospital, LayoutDashboard, LogOut, Menu,
  Pill, Search, Settings, ShieldAlert, Stethoscope, Users, X
} from "lucide-react";

const sections = {
  patient: [
    ["/patient/dashboard", "Dashboard", LayoutDashboard],
    ["/patient/doctors", "Find Doctors", Search],
    ["/patient/appointments", "Appointments", CalendarDays],
    ["/patient/medicines", "Medicines", Pill],
    ["/patient/sos", "Emergency SOS", ShieldAlert]
  ],
  donor: [
    ["/donor/dashboard", "Dashboard", LayoutDashboard],
    ["/donor/requests", "Emergency Requests", ShieldAlert],
    ["/donor/profile", "Donor Profile", Droplets]
  ],
  provider: [
    ["/provider/dashboard", "Dashboard", LayoutDashboard],
    ["/provider/doctors", "Doctors", Stethoscope],
    ["/provider/appointments", "Appointments", CalendarDays],
    ["/provider/emergencies", "Emergencies", ShieldAlert]
  ],
  admin: [
    ["/admin/dashboard", "Overview", LayoutDashboard],
    ["/admin/providers", "Providers", Hospital],
    ["/admin/users", "Users", Users],
    ["/admin/emergencies", "Emergencies", ShieldAlert]
  ]
};

function roleFromPath() {
  const p = location.pathname;
  if (p.startsWith("/donor")) return "donor";
  if (p.startsWith("/provider")) return "provider";
  if (p.startsWith("/admin")) return "admin";
  return "patient";
}

export default function DashboardLayout({ children }) {
  const navigate = useNavigate();
  const [collapsed, setCollapsed] = useState(false);
  const [mobile, setMobile] = useState(false);
  const role = roleFromPath();
  const nav = sections[role];

  const roleName = role === "provider" ? "Healthcare Provider" : role[0].toUpperCase() + role.slice(1);

  return (
    <div className={`app-shell ${collapsed ? "collapsed" : ""}`}>
      <aside className={`sidebar ${mobile ? "mobile-open" : ""}`}>
        <div className="brand">
          <div className="brand-mark"><HeartPulse size={23} /></div>
          {!collapsed && <div><strong>Aarogya One</strong><span>Healthcare connected</span></div>}
          <button className="mobile-close" onClick={() => setMobile(false)}><X size={20}/></button>
        </div>

        <div className="role-pill">{roleName}</div>
        <nav>
          {nav.map(([to, label, Icon]) => (
            <NavLink key={to} to={to} onClick={() => setMobile(false)} className={({isActive}) => isActive ? "active" : ""}>
              <Icon size={19}/><span>{label}</span>
            </NavLink>
          ))}
        </nav>

        <div className="sidebar-bottom">
          <NavLink to="/"><Activity size={19}/><span>Home</span></NavLink>
          <button onClick={() => navigate("/login")}><LogOut size={19}/><span>Logout</span></button>
        </div>

        <button className="collapse-btn" onClick={() => setCollapsed(!collapsed)}>
          {collapsed ? <ChevronRight size={18}/> : <ChevronLeft size={18}/>}
        </button>
      </aside>

      <main className="main-area">
        <header className="topbar">
          <button className="mobile-menu" onClick={() => setMobile(true)}><Menu size={22}/></button>
          <div className="topbar-search"><Search size={17}/><input placeholder="Search Aarogya One..." /></div>
          <div className="top-actions">
            <button className="icon-btn"><Settings size={19}/></button>
            <div className="avatar">AG</div>
          </div>
        </header>
        <div className="content">{children}</div>
      </main>
    </div>
  );
}