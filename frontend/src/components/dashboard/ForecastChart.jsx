import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

function ForecastChart({ forecastData }) {
  if (!forecastData) {
    return null;
  }

  const history = forecastData.history || [];
  const forecast = forecastData.forecast || [];

  const combinedData = [
    ...history.map((item) => ({
      date: item.date,
      actual_sales: item.sales,
      predicted_sales: null,
    })),
    ...forecast.map((item) => ({
      date: item.date,
      actual_sales: null,
      predicted_sales: item.predicted_sales,
    })),
  ];

  return (
    <section style={{ marginBottom: "2rem" }}>
      <h2>Sales Forecast (Next 7 Days)</h2>

      {combinedData.length === 0 ? (
        <p>No forecast data available.</p>
      ) : (
        <div style={{ width: "100%", height: 320 }}>
          <ResponsiveContainer>
            <LineChart data={combinedData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line
                type="monotone"
                dataKey="actual_sales"
                stroke="#2563eb"
                strokeWidth={3}
                name="Actual Sales"
              />
              <Line
                type="monotone"
                dataKey="predicted_sales"
                stroke="#dc2626"
                strokeWidth={3}
                strokeDasharray="6 6"
                name="Forecast Sales"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
    </section>
  );
}

export default ForecastChart;