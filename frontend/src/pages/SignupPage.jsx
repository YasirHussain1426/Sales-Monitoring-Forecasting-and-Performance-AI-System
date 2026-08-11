import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { registerUser } from "../api/auth";

function formatSignupError(errorData) {
  if (!errorData) return "Signup failed.";

  if (typeof errorData === "string") return errorData;

  const messages = [];

  Object.entries(errorData).forEach(([field, value]) => {
    if (Array.isArray(value)) {
      messages.push(`${field}: ${value.join(" ")}`);
    } else if (typeof value === "string") {
      messages.push(`${field}: ${value}`);
    } else {
      messages.push(`${field}: ${JSON.stringify(value)}`);
    }
  });

  return messages.join(" | ");
}

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
    const { name, value } = event.target;
    setFormData((previous) => ({
      ...previous,
      [name]: value,
    }));
  };

  const handleSignup = async (event) => {
    event.preventDefault();
    setSubmitting(true);
    setError("");

    try {
      const data = await registerUser(formData);
      localStorage.setItem("access_token", data.access);
      localStorage.setItem("refresh_token", data.refresh);
      navigate("/", { replace: true });
    } catch (signupError) {
      console.error(signupError);
      setError(formatSignupError(signupError.response?.data));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="auth-shell">
      <div className="glass-card auth-card">
        <p className="eyebrow">Create account</p>
        <h1 className="page-title">Join Sales AI</h1>
        <p className="page-subtitle">Create a free account to test the app.</p>

        <form className="form-stack" onSubmit={handleSignup}>
          <label className="field">
            <span className="field-label">Username</span>
            <input
              className="text-input"
              name="username"
              type="text"
              value={formData.username}
              onChange={handleChange}
              required
            />
          </label>

          <label className="field">
            <span className="field-label">Email</span>
            <input
              className="text-input"
              name="email"
              type="email"
              value={formData.email}
              onChange={handleChange}
              required
            />
          </label>

          <label className="field">
            <span className="field-label">Password</span>
            <input
              className="text-input"
              name="password"
              type="password"
              value={formData.password}
              onChange={handleChange}
              minLength={8}
              pattern="^(?=.*[A-Z])(?=.*\\d)(?=.*[^\\w\\s]).{8,}$"
              title="Password must be at least 8 characters long and include one uppercase letter, one number, and one special character."
              required
            />
            <span className="field-hint">
              Password must be 8+ characters with 1 uppercase letter, numbers, and 1 special character.
            </span>
          </label>

          <label className="field">
            <span className="field-label">Confirm Password</span>
            <input
              className="text-input"
              name="confirm_password"
              type="password"
              value={formData.confirm_password}
              onChange={handleChange}
              required
            />
          </label>

          {error && <div className="status-banner status-error">{error}</div>}

          <button className="button button-primary" type="submit" disabled={submitting}>
            {submitting ? "Creating account..." : "Sign up"}
          </button>
        </form>

        <p className="auth-footer">
          Already have an account? <Link to="/login">Login</Link>
        </p>
      </div>
    </div>
  );
}

export default SignupPage;