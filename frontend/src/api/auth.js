import apiClient from "./client";

export const loginUser = async (username, password) => {
  const response = await apiClient.post("auth/login/", { username, password });
  return response.data;
};

export const getCurrentUser = async () => {
  const response = await apiClient.get("auth/me/");
  return response.data;
};

export const logoutUser = () => {
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
};