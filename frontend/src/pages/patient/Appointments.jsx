import { CalendarDays, Clock3, Video, MapPin } from "lucide-react";
import PageHeader from "../../components/common/PageHeader";
import Badge from "../../components/common/Badge";

const items=[["Dr. Ananya Sharma","General Physician","Today, 4:30 PM","Online","Confirmed"],["Dr. Rohan Mehta","Internal Medicine","30 Sep, 10:00 AM","Offline","Pending"]];

export default function Appointments(){return <><PageHeader title="Appointments" subtitle="Upcoming visits and appointment history." action={<button className="btn primary"><CalendarDays size={17}/> Book appointment</button>}/><div className="card table-card"><div className="table-head"><h3>Upcoming appointments</h3><span>2 appointments</span></div>{items.map(x=><div className="appointment-row" key={x[0]}><div className="doctor-avatar small">{x[0].split(" ")[1]?.[0]}</div><div className="grow"><b>{x[0]}</b><p>{x[1]}</p></div><span><Clock3 size={14}/> {x[2]}</span><span><Video size={14}/> {x[3]}</span><Badge tone={x[4]==="Confirmed"?"green":"orange"}>{x[4]}</Badge><button className="text-btn">Details</button></div>)}</div></> }