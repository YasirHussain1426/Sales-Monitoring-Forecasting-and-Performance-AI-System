import { BrowserRouter, Route, Routes } from "react-router-dom";
import ProtectedRoute from "./components/ProtectedRoute";
import DashboardPage from "./pages/DashboardPage";
import ForecastActualPage from "./pages/ForecastActualPage";
import ForecastComparisonPage from "./pages/ForecastComparisonPage";
import LoginPage from "./pages/LoginPage";
import SignupPage from "./pages/SignupPage";
import AlertsPage from "./pages/AlertsPage";
import DataEntryPage from "./pages/DataEntryPage";

function App() {
  return (
    <BrowserRouter>
      <div className="app-shell">
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
                <DataEntryPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/forecast-comparison"
            element={
              <ProtectedRoute>
                <ForecastComparisonPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/forecast-actual"
            element={
              <ProtectedRoute>
                <ForecastActualPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/alerts"
            element={
              <ProtectedRoute>
                <AlertsPage />
              </ProtectedRoute>
            }
          />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;