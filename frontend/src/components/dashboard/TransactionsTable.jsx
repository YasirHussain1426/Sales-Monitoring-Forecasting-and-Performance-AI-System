const tableHeaderStyle = {
  border: "1px solid #ddd",
  padding: "10px",
  backgroundColor: "#f5f5f5",
  textAlign: "left",
};

const tableCellStyle = {
  border: "1px solid #ddd",
  padding: "10px",
};

function TransactionsTable({
  transactions,
  transactionCount,
  currentPage,
  hasNextPage,
  hasPreviousPage,
  onNextPage,
  onPreviousPage,
}) {
  const totalPages = Math.max(1, Math.ceil(transactionCount / 10));

  return (
    <section style={{ marginBottom: "2rem" }}>
      <h2>Sales Transactions</h2>
      <p>
        Total Records: {transactionCount} | Page {currentPage} of {totalPages}
      </p>

      {transactions.length === 0 ? (
        <p>No transactions found.</p>
      ) : (
        <>
          <div style={{ overflowX: "auto" }}>
            <table
              style={{
                width: "100%",
                borderCollapse: "collapse",
                marginTop: "1rem",
              }}
            >
              <thead>
                <tr>
                  <th style={tableHeaderStyle}>Date</th>
                  <th style={tableHeaderStyle}>Customer</th>
                  <th style={tableHeaderStyle}>Product</th>
                  <th style={tableHeaderStyle}>Region</th>
                  <th style={tableHeaderStyle}>Salesperson</th>
                  <th style={tableHeaderStyle}>Quantity</th>
                  <th style={tableHeaderStyle}>Total Amount</th>
                </tr>
              </thead>
              <tbody>
                {transactions.map((transaction) => (
                  <tr key={transaction.id}>
                    <td style={tableCellStyle}>{transaction.transaction_date}</td>
                    <td style={tableCellStyle}>{transaction.customer_name}</td>
                    <td style={tableCellStyle}>{transaction.product_name}</td>
                    <td style={tableCellStyle}>{transaction.region_name}</td>
                    <td style={tableCellStyle}>{transaction.salesperson_code}</td>
                    <td style={tableCellStyle}>{transaction.quantity}</td>
                    <td style={tableCellStyle}>₹{transaction.total_amount}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              marginTop: "1rem",
              gap: "1rem",
            }}
          >
            <button onClick={onPreviousPage} disabled={!hasPreviousPage}>
              Previous
            </button>
            <button onClick={onNextPage} disabled={!hasNextPage}>
              Next
            </button>
          </div>
        </>
      )}
    </section>
  );
}

export default TransactionsTable;