import { Link } from "react-router-dom";

function DashboardHeader({ currentUser, onLogout, activePage = "dashboard" }) {
  const isAdmin = Boolean(currentUser?.is_staff || currentUser?.is_superuser);

  return (
    <header className="glass-card dashboard-header">
      <div className="header-brand">
        <h1 className="brand-title">Sales AI System</h1>
        <p className="brand-subtitle">
          Sales monitoring, forecasting, and alert intelligence
        </p>
        <div className="header-userline">
          <span>
            Signed in as <strong>{currentUser?.username || "User"}</strong>
          </span>
          <span className={`role-badge ${isAdmin ? "role-admin" : "role-user"}`}>
            {isAdmin ? "Admin" : "User"}
          </span>
        </div>
      </div>

      <div className="header-actions">
        <Link className={`action-link action-green ${activePage === "data-entry" ? "is-active" : ""}`} to="/data-entry">
          Data Entry
        </Link>
        <Link className={`action-link action-blue ${activePage === "forecast-comparison" ? "is-active" : ""}`} to="/forecast-comparison">
          Forecast Comparison
        </Link>
        <Link className={`action-link action-violet ${activePage === "forecast-actual" ? "is-active" : ""}`} to="/forecast-actual">
          Forecast vs Actual
        </Link>
        <Link className={`action-link action-red ${activePage === "alerts" ? "is-active" : ""}`} to="/alerts">
          Alerts
        </Link>
        <button className="action-link action-ghost" onClick={onLogout} type="button">
          Logout
        </button>
      </div>
    </header>
  );
}

export default DashboardHeader;