import { useEffect, useState } from "react";
import { fetchAlerts, resolveAlert, runAlertRules } from "../api/alerts";

function getSeverityStyle(severity) {
  switch (severity) {
    case "high":
      return { backgroundColor: "rgba(239, 68, 68, 0.16)", color: "#fecaca" };
    case "medium":
      return { backgroundColor: "rgba(245, 158, 11, 0.16)", color: "#fde68a" };
    default:
      return { backgroundColor: "rgba(59, 130, 246, 0.16)", color: "#bfdbfe" };
  }
}

// ✅ Pretty JSON Viewer
function JsonViewer({ data }) {
  if (typeof data === "object" && data !== null) {
    return (
      <ul style={{ listStyle: "none", paddingLeft: "1rem", margin: 0 }}>
        {Object.entries(data).map(([key, value]) => (
          <li key={key} style={{ marginBottom: "0.5rem" }}>
            <strong style={{ color: "var(--text)" }}>{key}:</strong>{" "}
            {typeof value === "object" ? (
              <JsonViewer data={value} />
            ) : (
              <span style={{ color: "var(--muted)" }}>{String(value)}</span>
            )}
          </li>
        ))}
      </ul>
    );
  }
  return <span style={{ color: "var(--muted)" }}>{String(data)}</span>;
}

export default function AlertsPage() {
  const [alerts, setAlerts] = useState([]);
  const [statusFilter, setStatusFilter] = useState("");
  const [severityFilter, setSeverityFilter] = useState("");
  const [loading, setLoading] = useState(true);
  const [runningRules, setRunningRules] = useState(false);
  const [resolvingId, setResolvingId] = useState(null);
  const [error, setError] = useState("");
  const [runResult, setRunResult] = useState(null);

  const currentFilters = {
    status: statusFilter || undefined,
    severity: severityFilter || undefined,
  };

  const loadAlerts = async (filters = {}) => {
    try {
      setLoading(true);
      setError("");
      const data = await fetchAlerts(filters);
      setAlerts(data);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to load alerts.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAlerts(currentFilters);
  }, [statusFilter, severityFilter]);

  const handleRunRules = async () => {
    try {
      setRunningRules(true);
      setError("");
      const result = await runAlertRules({
        method: "weighted",
        window: 7,
        compare_days: 30,
      });
      setRunResult(result);
      await loadAlerts(currentFilters);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to run alert rules.");
    } finally {
      setRunningRules(false);
    }
  };

  const handleResolveAlert = async (alertId) => {
    try {
      setResolvingId(alertId);
      setError("");
      await resolveAlert(alertId);
      await loadAlerts(currentFilters);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to resolve alert.");
    } finally {
      setResolvingId(null);
    }
  };

  return (
    <div className="page-shell">
      {/* Header */}
      <div
        className="glass-card section-card fade-up"
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
          <h1 className="page-title">Alerts</h1>
          <p className="page-subtitle">
            Forecast target shortfalls and high forecast error alerts.
          </p>
        </div>

        <button onClick={handleRunRules} disabled={runningRules}>
          {runningRules ? "Running..." : "Run Alert Rules"}
        </button>
      </div>

      {/* Filters */}
      <section className="glass-card section-card fade-up stagger-1">
        <h2 className="section-title">Filters</h2>
        <div style={{ display: "flex", gap: "1rem", flexWrap: "wrap" }}>
          <div>
            <label>Status</label>
            <select
              value={statusFilter}
              onChange={(event) => setStatusFilter(event.target.value)}
            >
              <option value="">All</option>
              <option value="open">Open</option>
              <option value="resolved">Resolved</option>
            </select>
          </div>
          <div>
            <label>Severity</label>
            <select
              value={severityFilter}
              onChange={(event) => setSeverityFilter(event.target.value)}
            >
              <option value="">All</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
            </select>
          </div>
        </div>
      </section>

      {/* Rule Run Result */}
      {runResult && (
        <section
          className="glass-card section-card fade-up stagger-2"
          style={{ marginTop: "1.5rem" }}
        >
          <h2 className="section-title">Rule Run Result</h2>
          <JsonViewer data={runResult} />
        </section>
      )}

      {/* Error */}
      {error && (
        <div className="glass-card section-card" style={{ color: "#fecaca", marginTop: "1.5rem" }}>
          {error}
        </div>
      )}

      {/* Alerts List */}
      {loading && <p style={{ marginTop: "1.5rem" }}>Loading alerts...</p>}
      {!loading && !error && (
        <section className="glass-card section-card fade-up stagger-3" style={{ marginTop: "1.5rem" }}>
          <h2 className="section-title">Alert List</h2>
          {alerts.length === 0 ? (
            <p style={{ color: "var(--muted)" }}>No alerts found.</p>
          ) : (
            <div className="table-shell">
              {/* Table same as before */}
            </div>
          )}
        </section>
      )}
    </div>
  );
}
