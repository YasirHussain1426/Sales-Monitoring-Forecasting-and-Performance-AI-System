function KpiCards({ summary }) {
  const cards = [
    { label: "Total Revenue", value: `₹${summary?.total_revenue ?? 0}` },
    { label: "Total Transactions", value: summary?.total_transactions ?? 0 },
    { label: "Total Quantity Sold", value: summary?.total_quantity ?? 0 },
    { label: "Average Order Value", value: `₹${summary?.average_order_value ?? 0}` },
  ];

  return (
    <section className="fade-up stagger-1" style={{ marginBottom: "2rem" }}>
      <h2 className="section-title">Dashboard Summary</h2>
      <div className="kpi-grid">
        {cards.map((card) => (
          <div
            key={card.label}
            className="glass-card card-3d kpi-card"
          >
            <p className="kpi-label">{card.label}</p>
            <h3 className="kpi-value">{card.value}</h3>
          </div>
        ))}
      </div>
    </section>
  );
}

export default KpiCards;