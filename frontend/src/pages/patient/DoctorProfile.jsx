import { Link, useParams } from "react-router-dom";
import { ArrowLeft, CalendarDays, CheckCircle2, Clock3, Hospital, MapPin, Video } from "lucide-react";
import PageHeader from "../../components/common/PageHeader";

export default function DoctorProfile() {
  const {id} = useParams();
  return <><Link to="/patient/doctors" className="back-link"><ArrowLeft size={16}/> Back to doctors</Link><PageHeader title="Dr. Ananya Sharma" subtitle="General Physician · Demo profile"/>
    <div className="profile-grid"><section className="card doctor-profile"><div className="profile-avatar">AS</div><h2>Dr. Ananya Sharma</h2><b>MBBS, MD · General Physician</b><p><Hospital size={15}/> Aarogya Care Hospital</p><p><MapPin size={15}/> Roorkee · Demo location</p><div className="info-chips"><span><Video size={15}/> Online & Offline</span><span><CheckCircle2 size={15}/> Registered demo profile</span></div></section>
    <section className="card"><div className="card-title"><div><h3>Book an appointment</h3><p>Select a demo availability slot.</p></div><CalendarDays size={22}/></div><div className="date-strip"><button className="selected"><b>28</b><small>SEP</small></button><button><b>29</b><small>SEP</small></button><button><b>30</b><small>SEP</small></button></div><div className="slots">{["10:00 AM","11:30 AM","4:30 PM","6:00 PM"].map((x,i)=><button key={x} className={i===2?"selected":""}><Clock3 size={14}/>{x}</button>)}</div><button className="btn primary full">Book Appointment</button><small className="demo-note">Booking UI is demo-only until doctor slot APIs are available.</small></section></div>
  </>;
}