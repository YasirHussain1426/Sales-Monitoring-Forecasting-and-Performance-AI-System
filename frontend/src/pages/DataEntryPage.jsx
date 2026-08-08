import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  getProducts,
  getCustomers,
  getSalespeople,
  createTransaction,
  uploadTransactionsCSV,
} from "../api/sales";
import DashboardHeader from "../components/dashboard/DashboardHeader";
import { getCurrentUser, logoutUser } from "../api/auth";

export default function DataEntryPage() {
  const navigate = useNavigate();
  const [currentUser, setCurrentUser] = useState(null);

  const [products, setProducts] = useState([]);
  const [customers, setCustomers] = useState([]);
  const [salespeople, setSalespeople] = useState([]);

  const [formData, setFormData] = useState({
    transaction_date: new Date().toISOString().split("T")[0],
    customer: "",
    product: "",
    salesperson: "",
    quantity: 1,
    unit_price: 0,
    discount_amount: 0,
    total_amount: 0,
  });

  const [csvFile, setCsvFile] = useState(null);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    async function init() {
      try {
        const user = await getCurrentUser();
        setCurrentUser(user);

        const [prodData, custData, repData] = await Promise.all([
          getProducts(),
          getCustomers(),
          getSalespeople(),
        ]);

        setProducts(prodData.results || prodData);
        setCustomers(custData.results || custData);
        setSalespeople(repData.results || repData);
      } catch (err) {
        navigate("/login");
      }
    }
    init();
  }, [navigate]);

  useEffect(() => {
    const selectedProduct = products.find((p) => p.id === parseInt(formData.product));
    const price = selectedProduct ? selectedProduct.unit_price : formData.unit_price;
    const total = formData.quantity * price - formData.discount_amount;

    setFormData((prev) => ({
      ...prev,
      unit_price: price,
      total_amount: total > 0 ? total : 0,
    }));
  }, [formData.product, formData.quantity, formData.discount_amount, products]);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleManualSubmit = async (e) => {
    e.preventDefault();
    try {
      setMessage("");
      setError("");
      await createTransaction(formData);
      setMessage("Transaction recorded successfully!");
      setFormData({ ...formData, quantity: 1, discount_amount: 0 });
    } catch (err) {
      setError(err.response?.data ? JSON.stringify(err.response.data) : "Failed to record transaction.");
    }
  };

  const handleCSVSubmit = async (e) => {
    e.preventDefault();
    if (!csvFile) return setError("Please select a file first.");

    try {
      setMessage("");
      setError("");
      const res = await uploadTransactionsCSV(csvFile);
      setMessage(res.detail || "CSV uploaded successfully!");
      setCsvFile(null);
    } catch (err) {
      setError(err.response?.data?.detail || "CSV Upload failed.");
    }
  };

  return (
    <div className="p-8 font-sans text-white">
      <DashboardHeader currentUser={currentUser} onLogout={() => { logoutUser(); navigate("/login"); }} />

      <h1 className="text-2xl font-bold mb-6">Data Entry Center</h1>

      {message && (
        <div className="p-4 mb-4 rounded-lg bg-green-100 text-green-800">
          {message}
        </div>
      )}
      {error && (
        <div className="p-4 mb-4 rounded-lg bg-red-100 text-red-800">
          {error}
        </div>
      )}

      <div className="grid gap-8 md:grid-cols-2">
        {/* MANUAL ENTRY */}
        <section className="glass-card section-card bg-white text-black rounded-xl p-6">
          <h2 className="text-lg font-semibold mb-4">Record Single Sale</h2>
          <form onSubmit={handleManualSubmit} className="flex flex-col gap-4">
            <div>
              <label className="block font-semibold mb-1">Date</label>
              <input
                type="date"
                name="transaction_date"
                value={formData.transaction_date}
                onChange={handleChange}
                required
                className="w-full p-2 rounded border border-gray-300"
              />
            </div>
            <div>
              <label className="block font-semibold mb-1">Customer</label>
              <select
                name="customer"
                value={formData.customer}
                onChange={handleChange}
                required
                className="w-full p-2 rounded border border-gray-300"
              >
                <option value="">Select Customer...</option>
                {customers.map((c) => (
                  <option key={c.id} value={c.id}>{c.name}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block font-semibold mb-1">Salesperson</label>
              <select
                name="salesperson"
                value={formData.salesperson}
                onChange={handleChange}
                required
                className="w-full p-2 rounded border border-gray-300"
              >
                <option value="">Select Sales Rep...</option>
                {salespeople.map((s) => (
                  <option key={s.id} value={s.id}>{s.employee_code}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block font-semibold mb-1">Product</label>
              <select
                name="product"
                value={formData.product}
                onChange={handleChange}
                required
                className="w-full p-2 rounded border border-gray-300"
              >
                <option value="">Select Product...</option>
                {products.map((p) => (
                  <option key={p.id} value={p.id}>{p.name} (₹{p.unit_price})</option>
                ))}
              </select>
            </div>
            <div className="flex gap-4">
              <div className="flex-1">
                <label className="block font-semibold mb-1">Quantity</label>
                <input
                  type="number"
                  min="1"
                  name="quantity"
                  value={formData.quantity}
                  onChange={handleChange}
                  required
                  className="w-full p-2 rounded border border-gray-300"
                />
              </div>
              <div className="flex-1">
                <label className="block font-semibold mb-1">Discount (₹)</label>
                <input
                  type="number"
                  min="0"
                  step="0.01"
                  name="discount_amount"
                  value={formData.discount_amount}
                  onChange={handleChange}
                  className="w-full p-2 rounded border border-gray-300"
                />
              </div>
            </div>
            <div>
              <strong>Calculated Total: ₹{formData.total_amount}</strong>
            </div>
            <button
              type="submit"
              className="p-3 bg-blue-600 text-white rounded font-bold hover:bg-blue-700"
            >
              Save Transaction
            </button>
          </form>
        </section>

        {/* BULK CSV */}
        <section className="glass-card section-card bg-white text-black rounded-xl p-6">
          <h2 className="text-lg font-semibold mb-4">Bulk CSV Upload</h2>
          <p className="text-gray-600 text-sm mb-4">
            Upload a CSV file containing your weekly or monthly sales data. The CSV must contain the following headers:
            <br /><br />
            <code>transaction_date, customer_id, product_id, salesperson_id, quantity, unit_price, discount_amount, notes</code>
          </p>
          <form onSubmit={handleCSVSubmit} className="flex flex-col gap-4">
            <input
              type="file"
              accept=".csv"
              onChange={(e) => setCsvFile(e.target.files[0])}
              className="border border-dashed border-gray-400 p-4 rounded"
            />
            <button
              type="submit"
              className="p-3 bg-green-600 text-white rounded font-bold hover:bg-green-700"
            >
              Upload CSV
            </button>
          </form>
        </section>
      </div>
    </div>
  );
}
