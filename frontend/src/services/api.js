import axios from "axios";

const baseURL =
  (typeof window !== "undefined" && window.__ACCOTECH_API__) ||
  import.meta.env.VITE_API_URL ||
  "http://localhost:8000";

const api = axios.create({ baseURL, timeout: 120000 });

export async function health() {
  const { data } = await api.get("/api/health");
  return data;
}

export async function tallyPing() {
  const { data } = await api.get("/api/tally/ping");
  return data;
}

export async function uploadFile(file) {
  const form = new FormData();
  form.append("file", file);
  const { data } = await api.post("/api/upload", form, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}

export async function previewFile(fileId) {
  const { data } = await api.get(`/api/preview/${fileId}`);
  return data;
}

export async function processFile(fileId, push = false, bankLedger = null) {
  const form = new FormData();
  form.append("file_id", fileId);
  form.append("push", push ? "true" : "false");
  if (bankLedger) form.append("bank_ledger", bankLedger);
  const { data } = await api.post("/api/process", form);
  return data;
}

export async function pushRun(runId) {
  const { data } = await api.post(`/api/push/${runId}`);
  return data;
}

export async function getRunXml(runId) {
  const { data } = await api.get(`/api/runs/${runId}/xml`, {
    responseType: "text",
  });
  return data;
}

export async function getLearningState() {
  const { data } = await api.get("/api/learning");
  return data;
}

export async function saveLearning(corrections) {
  const { data } = await api.post("/api/learning/correct", corrections);
  return data;
}

export async function forgetRule(budgetLine) {
  const { data } = await api.delete(
    `/api/learning/${encodeURIComponent(budgetLine)}`
  );
  return data;
}

export default api;
