import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000",
  headers: { "Content-Type": "application/json" }
});

export const donorsApi = {
  list: () => api.get("/donors"),
  create: (data) => api.post("/donors", data),
  update: (id, data) => api.patch(`/donors/${id}`, data)
};

export const hospitalsApi = {
  list: () => api.get("/hospitals"),
  create: (data) => api.post("/hospitals", data),
  update: (id, data) => api.patch(`/hospitals/${id}`, data)
};

export const sosApi = {
  create: (data) => api.post("/sos", data),
  get: (id) => api.get(`/sos/${id}`),
  plan: (id) => api.get(`/sos/${id}/plan`),
  response: (id, data) => api.post(`/sos/${id}/response`, data),
  accept: (id, donorId) => api.post(`/sos/${id}/accept/${donorId}`),
  confirm: (id, hospitalId) => api.post(`/sos/${id}/confirm/${hospitalId}`),
  complete: (id) => api.post(`/sos/${id}/complete`)
};

export const appointmentApi = {
  create: (data) => api.post("/appointments", data)
};

export const medicineApi = {
  create: (data) => api.post("/medicines", data),
  update: (id, data) => api.patch(`/medicines/${id}`, data)
};

export const followupApi = {
  list: (patientId) => api.get(`/patients/${patientId}/followups`)
};

export const matchApi = {
  create: (data) => api.post("/match", data)
};

export default api;