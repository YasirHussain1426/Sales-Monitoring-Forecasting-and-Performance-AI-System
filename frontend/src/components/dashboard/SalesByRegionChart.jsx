import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

function SalesByRegionChart({ salesByRegion }) {
  return (
    <section style={{ marginBottom: "2rem" }}>
      <h2>Sales by Region</h2>
      {salesByRegion.length === 0 ? (
        <p>No regional sales data found.</p>
      ) : (
        <div style={{ width: "100%", height: 300 }}>
          <ResponsiveContainer>
            <BarChart data={salesByRegion}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="region" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="total_sales" fill="#16a34a" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </section>
  );
}

export default SalesByRegionChart;