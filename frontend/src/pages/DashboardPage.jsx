import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  getDashboardSummary,
  getDashboardTrends,
  getProducts,
  getRegions,
  getSalesByRegion,
  getTopProducts,
  getTransactions,
  getDailyForecast,
} from "../api/sales";
import { getCurrentUser, logoutUser } from "../api/auth";
import DashboardHeader from "../components/dashboard/DashboardHeader";
import FilterBar from "../components/dashboard/FilterBar";
import KpiCards from "../components/dashboard/KpiCards";
import ForecastChart from "../components/dashboard/ForecastChart";
import SalesTrendChart from "../components/dashboard/SalesTrendChart";
import SalesByRegionChart from "../components/dashboard/SalesByRegionChart";
import TopProductsChart from "../components/dashboard/TopProductsChart";
import TransactionsTable from "../components/dashboard/TransactionsTable";

function DashboardPage() {
  const navigate = useNavigate();

  const [currentUser, setCurrentUser] = useState(null);
  const [authLoading, setAuthLoading] = useState(true);

  const [summary, setSummary] = useState(null);
  const [forecastData, setForecastData] = useState(null);
  const [trends, setTrends] = useState([]);
  const [regions, setRegions] = useState([]);
  const [products, setProducts] = useState([]);
  const [salesByRegion, setSalesByRegion] = useState([]);
  const [topProducts, setTopProducts] = useState([]);
  const [transactions, setTransactions] = useState([]);
  const [transactionCount, setTransactionCount] = useState(0);

  const [startDate, setStartDate] = useState("2026-07-01");
  const [endDate, setEndDate] = useState("2026-07-12");
  const [selectedRegion, setSelectedRegion] = useState("");
  const [selectedProduct, setSelectedProduct] = useState("");

  const [currentPage, setCurrentPage] = useState(1);
  const [nextPageUrl, setNextPageUrl] = useState(null);
  const [previousPageUrl, setPreviousPageUrl] = useState(null);

  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  const loadDashboardData = async (
    selectedStartDate,
    selectedEndDate,
    selectedRegionId = selectedRegion,
    selectedProductId = selectedProduct,
    page = currentPage
  ) => {
    try {
      setLoading(true);
      setError("");

      const [
        summaryData,
        trendsData,
        regionsData,
        productsData,
        regionSalesData,
        topProductsData,
        transactionsData,
        forecastResponse,
      ] = await Promise.all([
        getDashboardSummary(selectedStartDate, selectedEndDate),
        getDashboardTrends(selectedStartDate, selectedEndDate),
        getRegions(),
        getProducts(),
        getSalesByRegion(selectedStartDate, selectedEndDate),
        getTopProducts(selectedStartDate, selectedEndDate),
        getTransactions({
          startDate: selectedStartDate,
          endDate: selectedEndDate,
          region: selectedRegionId,
          product: selectedProductId,
          page,
        }),
        getDailyForecast(7),
      ]);

      setSummary(summaryData);
      setForecastData(forecastResponse);
      setTrends(trendsData);
      setRegions(regionsData.results || regionsData);
      setProducts(productsData.results || productsData);
      setSalesByRegion(regionSalesData);
      setTopProducts(topProductsData);
      setTransactions(transactionsData.results || []);
      setTransactionCount(transactionsData.count || 0);
      setNextPageUrl(transactionsData.next || null);
      setPreviousPageUrl(transactionsData.previous || null);
      setCurrentPage(page);
    } catch (err) {
      console.error(err);
      setError(err.response?.data ? JSON.stringify(err.response.data) : err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const initializePage = async () => {
      try {
        const user = await getCurrentUser();
        setCurrentUser(user);
        await loadDashboardData(startDate, endDate);
      } catch (err) {
        console.error(err);
        logoutUser();
        navigate("/login", { replace: true });
      } finally {
        setAuthLoading(false);
      }
    };

    initializePage();
  }, []);

  const handleApplyFilters = () => {
    loadDashboardData(startDate, endDate, selectedRegion, selectedProduct, 1);
  };

  const handleNextPage = () => {
    if (nextPageUrl) {
      loadDashboardData(
        startDate,
        endDate,
        selectedRegion,
        selectedProduct,
        currentPage + 1
      );
    }
  };

  const handlePreviousPage = () => {
    if (previousPageUrl && currentPage > 1) {
      loadDashboardData(
        startDate,
        endDate,
        selectedRegion,
        selectedProduct,
        currentPage - 1
      );
    }
  };

  const handleLogout = () => {
    logoutUser();
    navigate("/login", { replace: true });
  };

  if (authLoading) {
    return <div className="page-shell">Checking session...</div>;
  }

  return (
    <div className="page-shell">
      <DashboardHeader currentUser={currentUser} onLogout={handleLogout} />

      <div className="glass-card section-card fade-up stagger-1">
        <FilterBar
          startDate={startDate}
          endDate={endDate}
          selectedRegion={selectedRegion}
          selectedProduct={selectedProduct}
          regions={regions}
          products={products}
          onStartDateChange={setStartDate}
          onEndDateChange={setEndDate}
          onRegionChange={setSelectedRegion}
          onProductChange={setSelectedProduct}
          onApplyFilters={handleApplyFilters}
        />
      </div>

      {loading && <p>Loading data...</p>}
      {error && <p style={{ color: "#fca5a5" }}>{error}</p>}

      {!loading && !error && (
        <>
          <KpiCards summary={summary} />

          <div className="glass-card section-card fade-up stagger-1">
            <ForecastChart forecastData={forecastData} />
          </div>

          <div className="glass-card section-card fade-up stagger-2">
            <SalesTrendChart trends={trends} />
          </div>

          <div className="glass-card section-card fade-up stagger-2">
            <SalesByRegionChart salesByRegion={salesByRegion} />
          </div>

          <div className="glass-card section-card fade-up stagger-3">
            <TopProductsChart topProducts={topProducts} />
          </div>

          <div className="glass-card section-card fade-up stagger-3">
            <TransactionsTable
              transactions={transactions}
              transactionCount={transactionCount}
              currentPage={currentPage}
              hasNextPage={!!nextPageUrl}
              hasPreviousPage={!!previousPageUrl}
              onNextPage={handleNextPage}
              onPreviousPage={handlePreviousPage}
            />
          </div>
        </>
      )}
    </div>
  );
}

export default DashboardPage;