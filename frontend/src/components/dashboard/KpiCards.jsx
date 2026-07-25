function KpiCards({ summary }) {
  const cards = [
    { label: "Total Revenue", value: `₹${summary?.total_revenue ?? 0}` },
    { label: "Total Transactions", value: summary?.total_transactions ?? 0 },
    { label: "Total Quantity Sold", value: summary?.total_quantity ?? 0 },
    { label: "Average Order Value", value: `₹${summary?.average_order_value ?? 0}` },
  ];

  return (
    <section style={{ marginBottom: "2rem" }}>
      <h2>Dashboard Summary</h2>
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
          gap: "1rem",
        }}
      >
        {cards.map((card) => (
          <div
            key={card.label}
            style={{
              border: "1px solid #ddd",
              borderRadius: "12px",
              padding: "1rem",
              backgroundColor: "#fff",
              boxShadow: "0 1px 3px rgba(0,0,0,0.08)",
            }}
          >
            <p style={{ margin: 0, color: "#666", fontSize: "14px" }}>{card.label}</p>
            <h3 style={{ margin: "0.5rem 0 0 0" }}>{card.value}</h3>
          </div>
        ))}
      </div>
    </section>
  );
}

export default KpiCards;