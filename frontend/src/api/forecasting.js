import apiClient from "./client";

export async function fetchForecastVsTarget(params = {}) {
  const response = await apiClient.get("/forecasting/forecast-vs-target/", {
    params,
  });
  return response.data;
}

export async function fetchForecastVsActual(params = {}) {
  const response = await apiClient.get("/forecasting/forecast-vs-actual/", {
    params,
  });
  return response.data;
}

export async function fetchDailyForecast(params = {}) {
  const response = await apiClient.get("/forecasting/daily/", {
    params,
  });
  return response.data;
}