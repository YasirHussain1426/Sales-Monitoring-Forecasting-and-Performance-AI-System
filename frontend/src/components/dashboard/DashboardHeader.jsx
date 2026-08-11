import { Link } from "react-router-dom";

function DashboardHeader({ currentUser, onLogout }) {
  const isAdmin = Boolean(currentUser?.is_staff || currentUser?.is_superuser);

  return (
    <header className="glass-card dashboard-header">
      <div>
        <h1 className="page-title">Sales AI System</h1>
        <p className="page-subtitle">Sales monitoring, forecasting, and alert intelligence</p>
        <div className="header-userline">
          <span>Signed in as <strong>{currentUser?.username || "User"}</strong></span>
          <span className="badge">{isAdmin ? "Admin" : "User"}</span>
        </div>
      </div>

      <div className="header-actions">
        {isAdmin && <Link className="action-link action-green" to="/data-entry">Data Entry</Link>}
        {isAdmin && <Link className="action-link action-blue" to="/forecast-comparison">Forecast Comparison</Link>}
        {isAdmin && <Link className="action-link action-violet" to="/forecast-actual">Forecast vs Actual</Link>}
        {isAdmin && <Link className="action-link action-red" to="/alerts">Alerts</Link>}
        <button className="action-link action-ghost" onClick={onLogout}>Logout</button>
      </div>
    </header>
  );
}

export default DashboardHeader;