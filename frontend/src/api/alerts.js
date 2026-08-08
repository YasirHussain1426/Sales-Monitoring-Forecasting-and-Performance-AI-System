import apiClient from "./client";

export async function fetchAlerts(params = {}) {
  const response = await apiClient.get("/alerts/", { params });
  return response.data;
}

export async function runAlertRules(payload = {}) {
  const response = await apiClient.post("/alerts/rules/run/", payload);
  return response.data;
}

export async function resolveAlert(alertId) {
  const response = await apiClient.post(`/alerts/${alertId}/resolve/`);
  return response.data;
}