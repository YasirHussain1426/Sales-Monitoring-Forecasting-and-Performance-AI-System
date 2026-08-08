import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

function getRiskColor(riskStatus) {
  switch (riskStatus) {
    case "likely_miss":
      return "#dc2626";
    case "at_risk":
      return "#f59e0b";
    case "on_track":
      return "#2563eb";
    case "ahead":
      return "#16a34a";
    default:
      return "#6b7280";
  }
}

function ForecastVsTargetChart({ data }) {
  if (!data) {
    return null;
  }

  const comparisonData = [
    {
      name: "Comparison",
      projected_total: data.projected_total,
      target_amount: data.target_amount,
    },
  ];

  const contributionData = [
    {
      name: "Sales Mix",
      actual_to_date: data.actual_to_date,
      forecast_remaining: data.forecast_remaining,
    },
  ];

  return (
    <section style={{ marginBottom: "2rem" }}>
      <h2>Forecast vs Target</h2>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))",
          gap: "1rem",
        }}
      >
        <div
          style={{
            border: "1px solid #e5e7eb",
            borderRadius: "12px",
            padding: "1rem",
            backgroundColor: "#fff",
          }}
        >
          <h3 style={{ marginTop: 0 }}>Projected vs Target</h3>
          <div style={{ width: "100%", height: 280 }}>
            <ResponsiveContainer>
              <BarChart data={comparisonData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar
                  dataKey="projected_total"
                  fill={getRiskColor(data.risk_status)}
                  name="Projected Total"
                />
                <Bar
                  dataKey="target_amount"
                  fill="#2563eb"
                  name="Target Amount"
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div
          style={{
            border: "1px solid #e5e7eb",
            borderRadius: "12px",
            padding: "1rem",
            backgroundColor: "#fff",
          }}
        >
          <h3 style={{ marginTop: 0 }}>Actual vs Forecast Remaining</h3>
          <div style={{ width: "100%", height: 280 }}>
            <ResponsiveContainer>
              <BarChart data={contributionData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar
                  dataKey="actual_to_date"
                  stackId="sales"
                  fill="#2563eb"
                  name="Actual To Date"
                />
                <Bar
                  dataKey="forecast_remaining"
                  stackId="sales"
                  fill="#7c3aed"
                  name="Forecast Remaining"
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </section>
  );
}

export default ForecastVsTargetChart;