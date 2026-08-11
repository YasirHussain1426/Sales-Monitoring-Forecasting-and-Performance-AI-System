import { useEffect, useState } from "react";
import { Navigate } from "react-router-dom";
import { getCurrentUser } from "../api/auth";

function AdminRoute({ children }) {
  const [checking, setChecking] = useState(true);
  const [isAdmin, setIsAdmin] = useState(false);

  useEffect(() => {
    let active = true;

    const loadUser = async () => {
      try {
        const user = await getCurrentUser();
        if (active) {
          setIsAdmin(Boolean(user.is_staff || user.is_superuser));
        }
      } catch {
        if (active) setIsAdmin(false);
      } finally {
        if (active) setChecking(false);
      }
    };

    loadUser();

    return () => {
      active = false;
    };
  }, []);

  if (checking) {
    return <div style={{ padding: "2rem" }}>Checking admin access...</div>;
  }

  if (!isAdmin) {
    return <Navigate to="/" replace />;
  }

  return children;
}

export default AdminRoute;