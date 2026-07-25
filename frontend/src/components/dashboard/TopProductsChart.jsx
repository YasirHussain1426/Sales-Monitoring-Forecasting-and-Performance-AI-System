import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

function TopProductsChart({ topProducts }) {
  return (
    <section style={{ marginBottom: "2rem" }}>
      <h2>Top Products</h2>
      {topProducts.length === 0 ? (
        <p>No product sales data found.</p>
      ) : (
        <div style={{ width: "100%", height: 300 }}>
          <ResponsiveContainer>
            <BarChart data={topProducts}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="product_name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="total_sales" fill="#f59e0b" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </section>
  );
}

export default TopProductsChart;