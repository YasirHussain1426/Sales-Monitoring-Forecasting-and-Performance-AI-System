import { useEffect, useMemo, useState } from "react";
import { fetchForecastVsActual } from "../api/forecasting";
import { getProducts, getRegions, getSalesPeople } from "../api/sales";
import ForecastVsActualChart from "../components/dashboard/ForecastVsActualChart";

function SummaryCard({ label, value }) {
  return (
    <div className="glass-card card-3d kpi-card">
      <p className="kpi-label">{label}</p>
      <h3 className="kpi-value">{value}</h3>
    </div>
  );
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

export default function ForecastActualPage() {
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
        const result = await fetchForecastVsActual({
          compare_days: 30,
          window: 7,
          method,
          ...scopeParams,
        });
        setData(result);
      } catch (err) {
        setError(err.response?.data?.detail || "Failed to load forecast vs actual.");
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
    return <div className="page-shell">Loading forecast vs actual...</div>;
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
          <h1 className="page-title">Forecast vs Actual</h1>
          <p className="page-subtitle">
            Compare predicted sales with actual historical sales by scope.
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
          Select a valid scope to load forecast vs actual.
        </div>
      ) : (
        <>
          <div className="kpi-grid fade-up stagger-2" style={{ marginTop: "1.5rem" }}>
            <SummaryCard label="WAPE" value={data.summary?.wape} />
            <SummaryCard label="Bias" value={data.summary?.bias} />
            <SummaryCard label="Compared Points" value={data.summary?.compared_points} />
          </div>

          <div className="glass-card section-card fade-up stagger-2">
            <ForecastVsActualChart series={data.series} />
          </div>

          <section className="glass-card section-card fade-up stagger-3">
            <h2 className="section-title">Recent Comparison Table</h2>

            <div className="table-shell">
              <table style={{ width: "100%", borderCollapse: "collapse" }}>
                <thead>
                  <tr>
                    <th style={{ borderBottom: "1px solid rgba(255,255,255,0.12)", padding: "0.75rem", textAlign: "left" }}>Date</th>
                    <th style={{ borderBottom: "1px solid rgba(255,255,255,0.12)", padding: "0.75rem", textAlign: "left" }}>Predicted</th>
                    <th style={{ borderBottom: "1px solid rgba(255,255,255,0.12)", padding: "0.75rem", textAlign: "left" }}>Actual</th>
                    <th style={{ borderBottom: "1px solid rgba(255,255,255,0.12)", padding: "0.75rem", textAlign: "left" }}>Error</th>
                  </tr>
                </thead>
                <tbody>
                  {data.series?.map((item) => (
                    <tr key={item.date}>
                      <td style={{ borderBottom: "1px solid rgba(255,255,255,0.08)", padding: "0.75rem" }}>{item.date}</td>
                      <td style={{ borderBottom: "1px solid rgba(255,255,255,0.08)", padding: "0.75rem" }}>{item.predicted_value}</td>
                      <td style={{ borderBottom: "1px solid rgba(255,255,255,0.08)", padding: "0.75rem" }}>{item.actual_value}</td>
                      <td style={{ borderBottom: "1px solid rgba(255,255,255,0.08)", padding: "0.75rem" }}>{item.error}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        </>
      )}
    </div>
  );
}