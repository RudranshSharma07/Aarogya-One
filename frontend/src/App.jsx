import { Routes, Route, Navigate } from "react-router-dom";
import Landing from "./pages/public/Landing";
import Login from "./pages/public/Login";
import Register from "./pages/public/Register";
import DashboardLayout from "./components/layout/DashboardLayout";
import PatientDashboard from "./pages/patient/PatientDashboard";
import Doctors from "./pages/patient/Doctors";
import DoctorProfile from "./pages/patient/DoctorProfile";
import Appointments from "./pages/patient/Appointments";
import Medicines from "./pages/patient/Medicines";
import SOS from "./pages/patient/SOS";
import SOSTrack from "./pages/patient/SOSTrack";
import DonorDashboard from "./pages/donor/DonorDashboard";
import DonorRequests from "./pages/donor/DonorRequests";
import DonorProfile from "./pages/donor/DonorProfile";
import ProviderDashboard from "./pages/provider/ProviderDashboard";
import ProviderDoctors from "./pages/provider/ProviderDoctors";
import ProviderAppointments from "./pages/provider/ProviderAppointments";
import ProviderEmergencies from "./pages/provider/ProviderEmergencies";
import AdminDashboard from "./pages/admin/AdminDashboard";
import AdminProviders from "./pages/admin/AdminProviders";
import AdminUsers from "./pages/admin/AdminUsers";
import AdminEmergencies from "./pages/admin/AdminEmergencies";

const page = (content) => <DashboardLayout>{content}</DashboardLayout>;

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />

      <Route path="/patient/dashboard" element={page(<PatientDashboard />)} />
      <Route path="/patient/doctors" element={page(<Doctors />)} />
      <Route path="/patient/doctors/:id" element={page(<DoctorProfile />)} />
      <Route path="/patient/appointments" element={page(<Appointments />)} />
      <Route path="/patient/medicines" element={page(<Medicines />)} />
      <Route path="/patient/sos" element={page(<SOS />)} />
      <Route path="/patient/sos/:id" element={page(<SOSTrack />)} />

      <Route path="/donor/dashboard" element={page(<DonorDashboard />)} />
      <Route path="/donor/requests" element={page(<DonorRequests />)} />
      <Route path="/donor/profile" element={page(<DonorProfile />)} />

      <Route path="/provider/dashboard" element={page(<ProviderDashboard />)} />
      <Route path="/provider/doctors" element={page(<ProviderDoctors />)} />
      <Route path="/provider/appointments" element={page(<ProviderAppointments />)} />
      <Route path="/provider/emergencies" element={page(<ProviderEmergencies />)} />

      <Route path="/admin/dashboard" element={page(<AdminDashboard />)} />
      <Route path="/admin/providers" element={page(<AdminProviders />)} />
      <Route path="/admin/users" element={page(<AdminUsers />)} />
      <Route path="/admin/emergencies" element={page(<AdminEmergencies />)} />

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}