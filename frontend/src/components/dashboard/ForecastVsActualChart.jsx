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

function ForecastVsActualChart({ series }) {
  if (!series || series.length === 0) {
    return (
      <section style={{ marginBottom: "2rem" }}>
        <h2>Forecast vs Actual</h2>
        <p>No comparison data available.</p>
      </section>
    );
  }

  return (
    <section style={{ marginBottom: "2rem" }}>
      <h2>Forecast vs Actual</h2>
      <div style={{ width: "100%", height: 320 }}>
        <ResponsiveContainer>
          <LineChart data={series}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line
              type="monotone"
              dataKey="predicted_value"
              stroke="#7c3aed"
              strokeWidth={3}
              name="Predicted"
            />
            <Line
              type="monotone"
              dataKey="actual_value"
              stroke="#2563eb"
              strokeWidth={3}
              name="Actual"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}

export default ForecastVsActualChart;