import { Link } from "react-router-dom";

function DashboardHeader({ currentUser, onLogout }) {
  return (
    <div
      className="glass-card section-card fade-up"
      style={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        gap: "1rem",
        flexWrap: "wrap",
      }}
    >
      <div>
        <h1 className="page-title">Sales AI System</h1>
        <p className="page-subtitle">
          Sales monitoring, forecasting, and alert intelligence
        </p>

        {currentUser && (
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "0.5rem",
              flexWrap: "wrap",
              marginTop: "0.75rem",
            }}
          >
            <span style={{ color: "var(--muted)" }}>
              Signed in as <strong style={{ color: "var(--text)" }}>{currentUser.username}</strong>
            </span>

            <span
              className="badge"
              style={{
                backgroundColor: currentUser.is_superuser
                  ? "rgba(239, 68, 68, 0.18)"
                  : "rgba(59, 130, 246, 0.18)",
                color: currentUser.is_superuser ? "#fecaca" : "#bfdbfe",
              }}
            >
              {currentUser.is_superuser ? "Admin" : "User"}
            </span>
          </div>
        )}
      </div>

      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: "0.75rem",
          flexWrap: "wrap",
        }}
      >
        <Link
          to="/data-entry"
          style={{
            textDecoration: "none",
            padding: "8px 12px",
            borderRadius: "8px",
            backgroundColor: "#16a34a", 
            color: "#fff",
            fontWeight: 500,
          }}
        >
          Data Entry
        </Link>
        <Link to="/forecast-comparison" className="action-link action-blue">
          Forecast Comparison
        </Link>
        <Link to="/forecast-actual" className="action-link action-violet">
          Forecast vs Actual
        </Link>
        <Link to="/alerts" className="action-link action-red">
          Alerts
        </Link>

        <button onClick={onLogout}>Logout</button>
      </div>
    </div>
  );
}

export default DashboardHeader;