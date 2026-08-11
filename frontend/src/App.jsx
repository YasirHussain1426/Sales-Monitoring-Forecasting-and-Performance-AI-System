import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import AdminRoute from "./components/AdminRoute";
import ProtectedRoute from "./components/ProtectedRoute";
import AlertsPage from "./pages/AlertsPage";
import DashboardPage from "./pages/DashboardPage";
import DataEntryPage from "./pages/DataEntryPage";
import ForecastActualPage from "./pages/ForecastActualPage";
import ForecastComparisonPage from "./pages/ForecastComparisonPage";
import LoginPage from "./pages/LoginPage";
import SignupPage from "./pages/SignupPage";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/signup" element={<SignupPage />} />
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <DashboardPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/data-entry"
          element={
            <ProtectedRoute>
              <AdminRoute>
                <DataEntryPage />
              </AdminRoute>
            </ProtectedRoute>
          }
        />
        <Route
          path="/forecast-comparison"
          element={
            <ProtectedRoute>
              <AdminRoute>
                <ForecastComparisonPage />
              </AdminRoute>
            </ProtectedRoute>
          }
        />
        <Route
          path="/forecast-actual"
          element={
            <ProtectedRoute>
              <AdminRoute>
                <ForecastActualPage />
              </AdminRoute>
            </ProtectedRoute>
          }
        />
        <Route
          path="/alerts"
          element={
            <ProtectedRoute>
              <AdminRoute>
                <AlertsPage />
              </AdminRoute>
            </ProtectedRoute>
          }
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;