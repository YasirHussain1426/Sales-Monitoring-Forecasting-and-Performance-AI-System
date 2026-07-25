function DashboardHeader({ currentUser, onLogout }) {
  return (
    <div
      style={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        marginBottom: "1.5rem",
        gap: "1rem",
        flexWrap: "wrap",
      }}
    >
      <div>
        <h1 style={{ margin: 0 }}>Sales AI System</h1>
        <p style={{ margin: "0.5rem 0", color: "#555" }}>
          Resume project: Django + DRF + React + PostgreSQL
        </p>

        {currentUser && (
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "0.5rem",
              flexWrap: "wrap",
            }}
          >
            <span style={{ color: "#555" }}>
              Signed in as <strong>{currentUser.username}</strong>
            </span>

            <span
              style={{
                padding: "4px 10px",
                borderRadius: "999px",
                fontSize: "12px",
                fontWeight: "bold",
                backgroundColor: currentUser.is_superuser ? "#fee2e2" : "#dbeafe",
                color: currentUser.is_superuser ? "#991b1b" : "#1d4ed8",
              }}
            >
              {currentUser.is_superuser ? "Admin" : "User"}
            </span>
          </div>
        )}
      </div>

      <button onClick={onLogout}>Logout</button>
    </div>
  );
}

export default DashboardHeader;