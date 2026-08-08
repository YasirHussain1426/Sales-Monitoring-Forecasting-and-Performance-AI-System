import { useEffect, useMemo, useState } from "react";
import { fetchForecastVsTarget } from "../api/forecasting";
import { getProducts, getRegions, getSalesPeople } from "../api/sales";
import ForecastVsTargetChart from "../components/dashboard/ForecastVsTargetChart";

function MetricCard({ label, value }) {
  return (
    <div className="glass-card card-3d kpi-card">
      <p className="kpi-label">{label}</p>
      <h3 className="kpi-value">{value}</h3>
    </div>
  );
}

function getRiskBadgeStyle(riskStatus) {
  const styles = {
    likely_miss: { backgroundColor: "rgba(239, 68, 68, 0.16)", color: "#fecaca" },
    at_risk: { backgroundColor: "rgba(245, 158, 11, 0.16)", color: "#fde68a" },
    on_track: { backgroundColor: "rgba(59, 130, 246, 0.16)", color: "#bfdbfe" },
    ahead: { backgroundColor: "rgba(34, 197, 94, 0.16)", color: "#bbf7d0" },
  };

  return styles[riskStatus] || { backgroundColor: "rgba(255,255,255,0.08)", color: "#e5eefb" };
}

function buildScopeParams(scopeType, selectedRegion, selectedProduct, selectedSalesperson) {
  return {
    scope_type: scopeType,
    region_id: scopeType === "region" ? selectedRegion || undefined : undefined,
    product_id: scopeType === "product" ? selectedProduct || undefined : undefined,
    salesperson_id:
      scopeType === "salesperson" ? selectedSalesperson || undefined : undefined,
  };
}

export default function ForecastComparisonPage() {
  const [data, setData] = useState(null);
  const [method, setMethod] = useState("weighted");
  const [scopeType, setScopeType] = useState("overall");

  const [regions, setRegions] = useState([]);
  const [products, setProducts] = useState([]);
  const [salespeople, setSalespeople] = useState([]);

  const [selectedRegion, setSelectedRegion] = useState("");
  const [selectedProduct, setSelectedProduct] = useState("");
  const [selectedSalesperson, setSelectedSalesperson] = useState("");

  const [loading, setLoading] = useState(true);
  const [optionsLoading, setOptionsLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadOptions() {
      try {
        setOptionsLoading(true);
        const [regionsData, productsData, salespeopleData] = await Promise.all([
          getRegions(),
          getProducts(),
          getSalesPeople(),
        ]);

        setRegions(regionsData.results || regionsData);
        setProducts(productsData.results || productsData);
        setSalespeople(salespeopleData.results || salespeopleData);
      } catch (err) {
        setError(err.response?.data?.detail || "Failed to load filter options.");
      } finally {
        setOptionsLoading(false);
      }
    }

    loadOptions();
  }, []);

  useEffect(() => {
    setSelectedRegion("");
    setSelectedProduct("");
    setSelectedSalesperson("");
  }, [scopeType]);

  const scopeParams = useMemo(
    () =>
      buildScopeParams(
        scopeType,
        selectedRegion,
        selectedProduct,
        selectedSalesperson
      ),
    [scopeType, selectedRegion, selectedProduct, selectedSalesperson]
  );

  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true);
        setError("");
        const result = await fetchForecastVsTarget({
          method,
          window: 7,
          ...scopeParams,
        });
        setData(result);
      } catch (err) {
        setError(err.response?.data?.detail || "Failed to load forecast comparison.");
      } finally {
        setLoading(false);
      }
    }

    if (
      (scopeType === "region" && !selectedRegion) ||
      (scopeType === "product" && !selectedProduct) ||
      (scopeType === "salesperson" && !selectedSalesperson)
    ) {
      setData(null);
      setLoading(false);
      return;
    }

    if (!optionsLoading) {
      loadData();
    }
  }, [
    method,
    scopeType,
    selectedRegion,
    selectedProduct,
    selectedSalesperson,
    scopeParams,
    optionsLoading,
  ]);

  if (optionsLoading || loading) {
    return <div className="page-shell">Loading forecast comparison...</div>;
  }

  return (
    <div className="page-shell">
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
          <h1 className="page-title">Forecast vs Target</h1>
          <p className="page-subtitle">
            Scope-aware forecast comparison against stored targets.
          </p>
        </div>

        <select
          value={method}
          onChange={(event) => setMethod(event.target.value)}
        >
          <option value="weighted">Weighted Moving Average</option>
          <option value="moving_average">Moving Average</option>
        </select>
      </div>

      <section className="glass-card section-card fade-up stagger-1">
        <h2 className="section-title">Scope Filters</h2>

        <div
          style={{
            display: "flex",
            gap: "1rem",
            alignItems: "end",
            flexWrap: "wrap",
          }}
        >
          <div>
            <label htmlFor="scope-type">Scope Type</label>
            <br />
            <select
              id="scope-type"
              value={scopeType}
              onChange={(event) => setScopeType(event.target.value)}
            >
              <option value="overall">Overall</option>
              <option value="region">Region</option>
              <option value="product">Product</option>
              <option value="salesperson">Salesperson</option>
            </select>
          </div>

          {scopeType === "region" && (
            <div>
              <label htmlFor="region-select">Region</label>
              <br />
              <select
                id="region-select"
                value={selectedRegion}
                onChange={(event) => setSelectedRegion(event.target.value)}
              >
                <option value="">Select Region</option>
                {regions.map((region) => (
                  <option key={region.id} value={region.id}>
                    {region.name}
                  </option>
                ))}
              </select>
            </div>
          )}

          {scopeType === "product" && (
            <div>
              <label htmlFor="product-select">Product</label>
              <br />
              <select
                id="product-select"
                value={selectedProduct}
                onChange={(event) => setSelectedProduct(event.target.value)}
              >
                <option value="">Select Product</option>
                {products.map((product) => (
                  <option key={product.id} value={product.id}>
                    {product.name}
                  </option>
                ))}
              </select>
            </div>
          )}

          {scopeType === "salesperson" && (
            <div>
              <label htmlFor="salesperson-select">Salesperson</label>
              <br />
              <select
                id="salesperson-select"
                value={selectedSalesperson}
                onChange={(event) => setSelectedSalesperson(event.target.value)}
              >
                <option value="">Select Salesperson</option>
                {salespeople.map((salesperson) => (
                  <option key={salesperson.id} value={salesperson.id}>
                    {salesperson.employee_code}
                  </option>
                ))}
              </select>
            </div>
          )}
        </div>
      </section>

      {error && (
        <div className="glass-card section-card" style={{ color: "#fecaca", marginTop: "1rem" }}>
          {error}
        </div>
      )}

      {!data ? (
        <div className="glass-card section-card fade-up stagger-2" style={{ marginTop: "1rem" }}>
          Select a valid scope to load forecast comparison.
        </div>
      ) : (
        <>
          <div className="kpi-grid fade-up stagger-2" style={{ marginTop: "1.5rem" }}>
            <MetricCard label="Actual To Date" value={data.actual_to_date} />
            <MetricCard label="Forecast Remaining" value={data.forecast_remaining} />
            <MetricCard label="Projected Total" value={data.projected_total} />
            <MetricCard label="Target Amount" value={data.target_amount} />
            <MetricCard label="Variance" value={data.variance_amount} />
            <MetricCard label="Attainment %" value={data.attainment_pct} />
          </div>

          <div className="glass-card section-card fade-up stagger-2">
            <ForecastVsTargetChart data={data} />
          </div>

          <section className="glass-card section-card fade-up stagger-3">
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                gap: "1rem",
                flexWrap: "wrap",
              }}
            >
              <h2 className="section-title" style={{ marginBottom: 0 }}>Risk Summary</h2>
              <span
                className="badge"
                style={getRiskBadgeStyle(data.risk_status)}
              >
                {data.risk_status}
              </span>
            </div>

            <div style={{ marginTop: "1rem", color: "var(--muted)" }}>
              <p><strong style={{ color: "var(--text)" }}>Forecast method:</strong> {data.forecast_method}</p>
              <p><strong style={{ color: "var(--text)" }}>Remaining days:</strong> {data.remaining_days}</p>
              <p><strong style={{ color: "var(--text)" }}>Target type:</strong> {data.target_type}</p>
              <p><strong style={{ color: "var(--text)" }}>Scope type:</strong> {data.scope_type}</p>
            </div>
          </section>
        </>
      )}
    </div>
  );
}