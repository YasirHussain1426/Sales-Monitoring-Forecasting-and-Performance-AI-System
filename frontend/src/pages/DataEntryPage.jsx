import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getCurrentUser, logoutUser } from "../api/auth";
import {
  createTransaction,
  getCustomers,
  getProducts,
  getRegions,
  getSalespeople,
} from "../api/sales";
import DashboardHeader from "../components/dashboard/DashboardHeader";

const todayIso = () => new Date().toISOString().slice(0, 10);

const formatCurrency = (value) => {
  const numberValue = Number.parseFloat(value);
  if (Number.isNaN(numberValue)) return "0.00";
  return numberValue.toFixed(2);
};

const calculateTotal = (quantity, unitPrice, discountAmount) => {
  const qty = Number.parseFloat(quantity || 0);
  const price = Number.parseFloat(unitPrice || 0);
  const discount = Number.parseFloat(discountAmount || 0);
  return Math.max(0, qty * price - discount).toFixed(2);
};

const parseCsvLine = (line) => {
  const fields = [];
  let current = "";
  let insideQuotes = false;

  for (let index = 0; index < line.length; index += 1) {
    const character = line[index];

    if (character === '"') {
      if (insideQuotes && line[index + 1] === '"') {
        current += '"';
        index += 1;
      } else {
        insideQuotes = !insideQuotes;
      }
      continue;
    }

    if (character === "," && !insideQuotes) {
      fields.push(current.trim());
      current = "";
      continue;
    }

    current += character;
  }

  fields.push(current.trim());
  return fields;
};

const parseCsvText = (text) => {
  const lines = text
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean);

  if (lines.length === 0) {
    return [];
  }

  const headers = parseCsvLine(lines[0]).map((header) =>
    header.toLowerCase().trim()
  );

  return lines.slice(1).map((line) => {
    const values = parseCsvLine(line);
    const row = {};

    headers.forEach((header, index) => {
      row[header] = (values[index] || "").trim();
    });

    return row;
  });
};

export default function DataEntryPage() {
  const navigate = useNavigate();

  const [currentUser, setCurrentUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [csvUploading, setCsvUploading] = useState(false);

  const [customers, setCustomers] = useState([]);
  const [products, setProducts] = useState([]);
  const [salespeople, setSalespeople] = useState([]);
  const [regions, setRegions] = useState([]);

  const [csvFile, setCsvFile] = useState(null);
  const [csvSummary, setCsvSummary] = useState(null);

  const [message, setMessage] = useState("");
  const [messageType, setMessageType] = useState("info");

  const [formData, setFormData] = useState({
    transaction_date: todayIso(),
    customer: "",
    product: "",
    salesperson: "",
    quantity: 1,
    discount_amount: "0.00",
    notes: "",
  });

  useEffect(() => {
    let active = true;

    const init = async () => {
      try {
        const user = await getCurrentUser();
        const [productData, customerData, salespersonData, regionData] =
          await Promise.all([
            getProducts(),
            getCustomers(),
            getSalespeople(),
            getRegions(),
          ]);

        if (!active) return;

        setCurrentUser(user);
        setProducts(productData.results || productData);
        setCustomers(customerData.results || customerData);
        setSalespeople(salespersonData.results || salespersonData);
        setRegions(regionData.results || regionData);
      } catch (error) {
        console.error(error);
        logoutUser();
        navigate("/login", { replace: true });
      } finally {
        if (active) setLoading(false);
      }
    };

    init();

    return () => {
      active = false;
    };
  }, [navigate]);

  const selectedProduct = useMemo(
    () => products.find((item) => String(item.id) === String(formData.product)),
    [formData.product, products]
  );

  const calculatedTotal = calculateTotal(
    formData.quantity,
    selectedProduct?.unit_price || 0,
    formData.discount_amount
  );

  const handleChange = (event) => {
    const { name, value } = event.target;
    setFormData((previous) => ({
      ...previous,
      [name]: value,
    }));
  };

  const handleManualSubmit = async (event) => {
    event.preventDefault();
    setMessage("");
    setCsvSummary(null);

    if (!formData.customer || !formData.product || !formData.salesperson) {
      setMessageType("error");
      setMessage("Select customer, product, and salesperson first.");
      return;
    }

    if (!selectedProduct) {
      setMessageType("error");
      setMessage("Select a valid product.");
      return;
    }

    setSaving(true);

    try {
      await createTransaction({
        transaction_date: formData.transaction_date,
        customer: Number(formData.customer),
        product: Number(formData.product),
        salesperson: Number(formData.salesperson),
        quantity: Number(formData.quantity),
        unit_price: formatCurrency(selectedProduct.unit_price),
        discount_amount: formatCurrency(formData.discount_amount),
        total_amount: calculatedTotal,
        notes: formData.notes,
      });

      setMessageType("success");
      setMessage("Transaction recorded successfully!");
      setFormData((previous) => ({
        ...previous,
        quantity: 1,
        discount_amount: "0.00",
        notes: "",
      }));
    } catch (error) {
      console.error(error);
      setMessageType("error");
      setMessage(
        error.response?.data
          ? JSON.stringify(error.response.data)
          : "Failed to record transaction."
      );
    } finally {
      setSaving(false);
    }
  };

  const handleCSVSubmit = async (event) => {
    event.preventDefault();
    setMessage("");
    setCsvSummary(null);

    if (!csvFile) {
      setMessageType("error");
      setMessage("Please select a file first.");
      return;
    }

    setCsvUploading(true);

    try {
      const text = await csvFile.text();
      const rows = parseCsvText(text);

      if (rows.length === 0) {
        setMessageType("error");
        setMessage("CSV file is empty.");
        return;
      }

      let successCount = 0;
      const errors = [];

      for (let index = 0; index < rows.length; index += 1) {
        const row = rows[index];
        const normalized = Object.fromEntries(
          Object.entries(row).map(([key, value]) => [key.toLowerCase(), value])
        );

        const payload = {
          transaction_date:
            normalized.transaction_date || normalized.date || todayIso(),
          customer: Number(
            normalized.customer_id || normalized.customer || normalized.customerid
          ),
          product: Number(
            normalized.product_id || normalized.product || normalized.productid
          ),
          salesperson: Number(
            normalized.salesperson_id ||
              normalized.salesperson ||
              normalized.salespersonid
          ),
          quantity: Number(normalized.quantity || 1),
          unit_price: formatCurrency(normalized.unit_price || 0),
          discount_amount: formatCurrency(normalized.discount_amount || 0),
          total_amount: calculateTotal(
            normalized.quantity || 1,
            normalized.unit_price || 0,
            normalized.discount_amount || 0
          ),
          notes: normalized.notes || "",
        };

        if (
          !payload.customer ||
          !payload.product ||
          !payload.salesperson ||
          !payload.quantity
        ) {
          errors.push(`Row ${index + 2}: missing required values.`);
          continue;
        }

        try {
          await createTransaction(payload);
          successCount += 1;
        } catch (error) {
          const detail = error.response?.data
            ? JSON.stringify(error.response.data)
            : error.message;
          errors.push(`Row ${index + 2}: ${detail}`);
        }
      }

      setCsvSummary({
        successCount,
        totalCount: rows.length,
        errors,
      });

      if (successCount > 0 && errors.length === 0) {
        setMessageType("success");
        setMessage("CSV uploaded successfully!");
        setCsvFile(null);
      } else if (successCount > 0) {
        setMessageType("error");
        setMessage("CSV uploaded with some row errors.");
      } else {
        setMessageType("error");
        setMessage("CSV upload failed.");
      }
    } catch (error) {
      console.error(error);
      setMessageType("error");
      setMessage("Error processing file. Ensure headers and data types are correct.");
    } finally {
      setCsvUploading(false);
    }
  };

  const handleLogout = () => {
    logoutUser();
    navigate("/login", { replace: true });
  };

  if (loading) {
    return (
      <div className="page-shell">
        <div className="glass-card loading-card">Loading data entry...</div>
      </div>
    );
  }

  // Consistent inline style block to enforce column rendering for labels
  const labelStyle = {
    display: "flex",
    flexDirection: "column",
    gap: "0.4rem",
    flex: "1 1 200px" // Allows fields to grow and shrink responsively
  };

  return (
    <div className="page-shell">
      <DashboardHeader
        currentUser={currentUser}
        onLogout={handleLogout}
        activePage="data-entry"
      />

      <section className="page-intro" style={{ marginBottom: "1.5rem" }}>
        <h2 className="section-heading">Data Entry Center</h2>
      </section>

      {message && (
        <div
          className={`status-banner status-${messageType}`}
          style={{
            marginBottom: "1.5rem",
            padding: "1rem",
            borderRadius: "6px",
            borderLeft: `4px solid ${messageType === "error" ? "red" : "green"}`
          }}
        >
          {message}
        </div>
      )}

      <section
        className="split-grid"
        style={{ display: "flex", flexDirection: "column", gap: "2rem" }}
      >
        <div className="glass-card panel" style={{ padding: "1.5rem" }}>
          <h3 className="panel-title" style={{ marginBottom: "1.5rem" }}>
            Record Single Sale
          </h3>

          <form
            className="form-stack"
            onSubmit={handleManualSubmit}
            style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}
          >
            {/* Form Row 1 */}
            <div style={{ display: "flex", flexWrap: "wrap", gap: "1rem" }}>
              <label className="field" style={labelStyle}>
                <span className="field-label" style={{ fontWeight: "600" }}>Date</span>
                <input
                  className="text-input"
                  style={{ padding: "0.6rem", borderRadius: "4px" }}
                  type="date"
                  name="transaction_date"
                  value={formData.transaction_date}
                  onChange={handleChange}
                  required
                />
              </label>

              <label className="field" style={labelStyle}>
                <span className="field-label" style={{ fontWeight: "600" }}>Customer</span>
                <select
                  className="text-input"
                  style={{ padding: "0.6rem", borderRadius: "4px" }}
                  name="customer"
                  value={formData.customer}
                  onChange={handleChange}
                  required
                >
                  <option value="">Select Customer...</option>
                  {customers.map((customer) => (
                    <option key={customer.id} value={customer.id}>
                      {customer.name}
                    </option>
                  ))}
                </select>
              </label>
            </div>

            {/* Form Row 2 */}
            <div style={{ display: "flex", flexWrap: "wrap", gap: "1rem" }}>
              <label className="field" style={labelStyle}>
                <span className="field-label" style={{ fontWeight: "600" }}>Salesperson</span>
                <select
                  className="text-input"
                  style={{ padding: "0.6rem", borderRadius: "4px" }}
                  name="salesperson"
                  value={formData.salesperson}
                  onChange={handleChange}
                  required
                >
                  <option value="">Select Sales Rep...</option>
                  {salespeople.map((salesperson) => (
                    <option key={salesperson.id} value={salesperson.id}>
                      {salesperson.employee_code}
                    </option>
                  ))}
                </select>
              </label>

              <label className="field" style={labelStyle}>
                <span className="field-label" style={{ fontWeight: "600" }}>Product</span>
                <select
                  className="text-input"
                  style={{ padding: "0.6rem", borderRadius: "4px" }}
                  name="product"
                  value={formData.product}
                  onChange={handleChange}
                  required
                >
                  <option value="">Select Product...</option>
                  {products.map((product) => (
                    <option key={product.id} value={product.id}>
                      {product.name} ({product.sku})
                    </option>
                  ))}
                </select>
              </label>
            </div>

            {/* Form Row 3 */}
            <div className="field-row" style={{ display: "flex", flexWrap: "wrap", gap: "1rem" }}>
              <label className="field" style={labelStyle}>
                <span className="field-label" style={{ fontWeight: "600" }}>Quantity</span>
                <input
                  className="text-input"
                  style={{ padding: "0.6rem", borderRadius: "4px" }}
                  type="number"
                  min="1"
                  name="quantity"
                  value={formData.quantity}
                  onChange={handleChange}
                  required
                />
              </label>

              <label className="field" style={labelStyle}>
                <span className="field-label" style={{ fontWeight: "600" }}>Discount (₹)</span>
                <input
                  className="text-input"
                  style={{ padding: "0.6rem", borderRadius: "4px" }}
                  type="number"
                  min="0"
                  step="0.01"
                  name="discount_amount"
                  value={formData.discount_amount}
                  onChange={handleChange}
                />
              </label>
            </div>

            <div
              className="total-line"
              style={{ padding: "0.75rem 0", fontSize: "1.1rem", borderTop: "1px solid rgba(255,255,255,0.1)" }}
            >
              Calculated Total: <strong style={{ marginLeft: "0.5rem" }}>₹{calculatedTotal}</strong>
            </div>

            <label className="field" style={{ ...labelStyle, flex: "1 1 100%" }}>
              <span className="field-label" style={{ fontWeight: "600" }}>Notes</span>
              <textarea
                className="text-area"
                style={{ padding: "0.6rem", borderRadius: "4px", minHeight: "80px" }}
                name="notes"
                rows="4"
                value={formData.notes}
                onChange={handleChange}
              />
            </label>

            <button
              className="button button-primary"
              type="submit"
              disabled={saving}
              style={{
                alignSelf: "flex-start",
                padding: "0.75rem 1.5rem",
                borderRadius: "4px",
                cursor: saving ? "not-allowed" : "pointer"
              }}
            >
              {saving ? "Saving..." : "Save Transaction"}
            </button>
          </form>
        </div>

        <div className="glass-card panel" style={{ padding: "1.5rem" }}>
          <h3 className="panel-title" style={{ marginBottom: "1rem" }}>
            Bulk CSV Upload
          </h3>
          <p className="helper-text" style={{ marginBottom: "0.75rem", opacity: 0.9 }}>
            Upload a CSV file containing your weekly or monthly sales data. The CSV
            must contain these headers:
          </p>
          <code
            className="csv-code"
            style={{
              display: "block",
              marginBottom: "1.5rem",
              padding: "0.75rem",
              backgroundColor: "rgba(0,0,0,0.3)",
              borderRadius: "4px",
              fontFamily: "monospace"
            }}
          >
            transaction_date, customer_id, product_id, salesperson_id, quantity,
            unit_price, discount_amount, notes
          </code>

          <form
            className="form-stack"
            onSubmit={handleCSVSubmit}
            style={{ display: "flex", alignItems: "center", gap: "1rem", flexWrap: "wrap", marginBottom: "2rem" }}
          >
            <label
              className="file-input button button-secondary"
              style={{
                display: "inline-flex",
                alignItems: "center",
                padding: "0.6rem 1rem",
                cursor: "pointer",
                border: "1px solid rgba(255,255,255,0.2)",
                borderRadius: "4px"
              }}
            >
              {/* Native input completely hidden; triggering exclusively via label */}
              <input
                type="file"
                accept=".csv,text/csv"
                style={{ display: "none" }}
                onChange={(event) => setCsvFile(event.target.files?.[0] || null)}
              />
              <span>{csvFile ? csvFile.name : "Choose File..."}</span>
            </label>

            <button
              className="button button-primary"
              type="submit"
              disabled={csvUploading}
              style={{ padding: "0.6rem 1rem", borderRadius: "4px" }}
            >
              {csvUploading ? "Uploading..." : "Upload CSV"}
            </button>
          </form>

          {csvSummary && (
            <div
              className="csv-summary"
              style={{
                marginBottom: "1.5rem",
                padding: "1rem",
                backgroundColor: "rgba(255,255,255,0.05)",
                borderRadius: "4px"
              }}
            >
              <p>
                Imported <strong>{csvSummary.successCount}</strong> of{" "}
                <strong>{csvSummary.totalCount}</strong> rows.
              </p>

              {csvSummary.errors.length > 0 && (
                <ul className="error-list" style={{ marginTop: "0.75rem", color: "#ff6b6b" }}>
                  {csvSummary.errors.map((item, index) => (
                    <li key={index} style={{ marginBottom: "0.25rem" }}>{item}</li>
                  ))}
                </ul>
              )}
            </div>
          )}

          <div
            className="lookup-summary"
            style={{
              display: "flex",
              gap: "2rem",
              flexWrap: "wrap",
              paddingTop: "1.5rem",
              borderTop: "1px solid rgba(255,255,255,0.1)"
            }}
          >
            <div style={{ display: "flex", flexDirection: "column", gap: "0.25rem" }}>
              <span className="muted-label" style={{ fontSize: "0.85rem", opacity: 0.7 }}>Customers loaded</span>
              <strong style={{ fontSize: "1.1rem" }}>{customers.length}</strong>
            </div>
            <div style={{ display: "flex", flexDirection: "column", gap: "0.25rem" }}>
              <span className="muted-label" style={{ fontSize: "0.85rem", opacity: 0.7 }}>Products loaded</span>
              <strong style={{ fontSize: "1.1rem" }}>{products.length}</strong>
            </div>
            <div style={{ display: "flex", flexDirection: "column", gap: "0.25rem" }}>
              <span className="muted-label" style={{ fontSize: "0.85rem", opacity: 0.7 }}>Salespeople loaded</span>
              <strong style={{ fontSize: "1.1rem" }}>{salespeople.length}</strong>
            </div>
            <div style={{ display: "flex", flexDirection: "column", gap: "0.25rem" }}>
              <span className="muted-label" style={{ fontSize: "0.85rem", opacity: 0.7 }}>Regions loaded</span>
              <strong style={{ fontSize: "1.1rem" }}>{regions.length}</strong>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}