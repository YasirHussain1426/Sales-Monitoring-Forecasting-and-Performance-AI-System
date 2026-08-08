import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { registerUser } from "../api/auth";

function SignupPage() {
  const [formData, setFormData] = useState({
    username: "",
    email: "",
    password: "",
    confirm_password: "",
  });
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const navigate = useNavigate();

  const handleChange = (event) => {
    setFormData((previous) => ({
      ...previous,
      [event.target.name]: event.target.value,
    }));
  };

  const handleSignup = async (event) => {
    event.preventDefault();

    try {
      setSubmitting(true);
      setError("");

      const data = await registerUser(formData);
      localStorage.setItem("access_token", data.access);
      localStorage.setItem("refresh_token", data.refresh);

      navigate("/", { replace: true });
    } catch (err) {
      console.error(err);
      setError(
        err.response?.data
          ? JSON.stringify(err.response.data)
          : "Signup failed."
      );
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="page-shell auth-shell">
      <div className="glass-card auth-card fade-up">
        <div style={{ marginBottom: "1.5rem", textAlign: "center" }}>
          <h1 className="page-title">Create Account</h1>
          <p className="page-subtitle">Start using the sales monitoring and forecasting platform</p>
        </div>

        <form onSubmit={handleSignup} className="auth-form">
          <div className="auth-field">
            <label htmlFor="username" className="auth-label">Username</label>
            <input
              id="username"
              name="username"
              type="text"
              placeholder="Choose a username"
              value={formData.username}
              onChange={handleChange}
              required
            />
          </div>

          <div className="auth-field">
            <label htmlFor="email" className="auth-label">Email</label>
            <input
              id="email"
              name="email"
              type="email"
              placeholder="Enter your email"
              value={formData.email}
              onChange={handleChange}
              required
            />
          </div>

          <div className="auth-field">
            <label htmlFor="password" className="auth-label">Password</label>
            <input
              id="password"
              name="password"
              type="password"
              placeholder="Create a password"
              value={formData.password}
              onChange={handleChange}
              required
            />
          </div>

          <div className="auth-field">
            <label htmlFor="confirm_password" className="auth-label">Confirm Password</label>
            <input
              id="confirm_password"
              name="confirm_password"
              type="password"
              placeholder="Confirm your password"
              value={formData.confirm_password}
              onChange={handleChange}
              required
            />
          </div>

          <button
            type="submit"
            disabled={submitting}
            className="primary-button"
          >
            {submitting ? "Creating account..." : "Sign Up"}
          </button>
        </form>

        {error && <div className="auth-error">{error}</div>}

        <p className="auth-footer">
          Already have an account?{" "}
          <Link to="/login" className="auth-link">
            Login
          </Link>
        </p>
      </div>
    </div>
  );
}

export default SignupPage;