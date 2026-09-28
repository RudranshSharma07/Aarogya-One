import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { CheckCircle2, Clock3, Hospital, ShieldAlert, UserRound } from "lucide-react";
import PageHeader from "../../components/common/PageHeader";
import Badge from "../../components/common/Badge";
import { sosApi } from "../../services/api";

const stages=[["submitted","Request submitted",ShieldAlert],["plan","AI rescue plan generated",Clock3],["contacted","Donor/resource contacted",UserRound],["accepted","Donor accepted",CheckCircle2],["confirmed","Hospital confirmed",Hospital],["completed","Emergency completed",CheckCircle2]];

export default function SOSTrack(){const {id}=useParams();const [data,setData]=useState(null);const [error,setError]=useState("");useEffect(()=>{sosApi.get(id).then(r=>setData(r.data)).catch(()=>setError("Unable to load the live SOS status. The backend may be offline or the request ID may not exist."));},[id]);const raw=data?.status||data?.state||"submitted";return <><PageHeader title="Emergency Tracking" subtitle={`Request ID: ${id}`}/>{error&&<div className="error-box">{error}</div>}<div className="card"><div className="status-head"><div><h3>Emergency coordination</h3><p>Only backend-confirmed statuses are displayed.</p></div><Badge tone="orange">{data?.status || "Loading"}</Badge></div><div className="timeline">{stages.map(([key,title,Icon],i)=>{const active=key===raw || (i===0 && !data);return <div className={`timeline-item ${active?"active":""}`} key={key}><div className="timeline-icon"><Icon size={18}/></div><div><b>{title}</b><p>{active?"Current status":"Waiting for backend confirmation"}</p></div></div>})}</div></div></> }