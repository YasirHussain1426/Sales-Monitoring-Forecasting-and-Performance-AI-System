import apiClient from "./client";

const buildParams = (startDate, endDate) => ({
  start_date: startDate || undefined,
  end_date: endDate || undefined,
});

export const getRegions = async () => {
  const response = await apiClient.get("sales/regions/");
  return response.data;
};

export const getProducts = async () => {
  const response = await apiClient.get("sales/products/");
  return response.data;
};

export const getDashboardSummary = async (startDate, endDate) => {
  const response = await apiClient.get("sales/dashboard/summary/", {
    params: buildParams(startDate, endDate),
  });
  return response.data;
};

export const getDashboardTrends = async (startDate, endDate) => {
  const response = await apiClient.get("sales/dashboard/trends/", {
    params: buildParams(startDate, endDate),
  });
  return response.data;
};

export const getSalesByRegion = async (startDate, endDate) => {
  const response = await apiClient.get("sales/dashboard/by-region/", {
    params: buildParams(startDate, endDate),
  });
  return response.data;
};

export const getTopProducts = async (startDate, endDate) => {
  const response = await apiClient.get("sales/dashboard/top-products/", {
    params: buildParams(startDate, endDate),
  });
  return response.data;
};

export const getTransactions = async ({
  startDate,
  endDate,
  region,
  product,
  salesperson,
  page = 1,
}) => {
  const response = await apiClient.get("sales/transactions/", {
    params: {
      start_date: startDate || undefined,
      end_date: endDate || undefined,
      region: region || undefined,
      product: product || undefined,
      salesperson: salesperson || undefined,
      page,
    },
  });

  return response.data;
};

export const getDailyForecast = async (days = 7) => {
  const response = await apiClient.get("forecasting/daily/", {
    params: { days },
  });
  return response.data;
};

export const getSalesPeople = async () => {
  const response = await apiClient.get("sales/salespeople/");
  return response.data;
};

export const getCustomers = async () => {
  const response = await apiClient.get("sales/customers/");
  return response.data;
};

export const getSalespeople = async () => {
  const response = await apiClient.get("sales/salespeople/");
  return response.data;
};

export const createTransaction = async (data) => {
  const response = await apiClient.post("sales/transactions/", data);
  return response.data;
};

export const uploadTransactionsCSV = async (file) => {
  const formData = new FormData();
  formData.append("file", file);
  
  const response = await apiClient.post("sales/transactions/upload_csv/", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });
  return response.data;
};