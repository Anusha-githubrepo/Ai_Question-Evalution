import axios from "axios";

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://localhost:8000",
  timeout: 30000,
});

export const evaluateAnswer = async (payload) => {
  const { data } = await api.post("/evaluate", payload);
  return data;
};

export const fetchHistory = async () => {
  const { data } = await api.get("/history");
  return data;
};

export const fetchEvaluation = async (id) => {
  const { data } = await api.get(`/evaluation/${id}`);
  return data;
};

export const deleteEvaluation = async (id) => {
  await api.delete(`/history/${id}`);
};
