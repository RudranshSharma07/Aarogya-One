export default function StatCard({ icon: Icon, label, value, note, tone = "teal" }) {
  return (
    <div className="stat-card">
      <div className={`stat-icon ${tone}`}><Icon size={20} /></div>
      <div>
        <p className="muted">{label}</p>
        <h3>{value}</h3>
        {note && <small>{note}</small>}
      </div>
    </div>
  );
}