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
    <div className="page-shell auth-shell">
      <div className="glass-card auth-card fade-up">
        <div className="signup-heading">
          <h1 className="page-title">Create Account</h1>
          <p className="page-subtitle">Create a free account to test the app.</p>
        </div>

        <form onSubmit={handleSignup} className="auth-form">
          <div className="auth-field">
            <label htmlFor="signup-username" className="auth-label">Username</label>
            <input
              id="signup-username"
              name="username"
              type="text"
              placeholder="Choose a username"
              value={formData.username}
              onChange={handleChange}
              required
            />
          </div>

          <div className="auth-field">
            <label htmlFor="signup-email" className="auth-label">Email</label>
            <input
              id="signup-email"
              name="email"
              type="email"
              placeholder="Enter your email"
              value={formData.email}
              onChange={handleChange}
              required
            />
          </div>

          <div className="auth-field">
            <label htmlFor="signup-password" className="auth-label">Password</label>
            <input
              id="signup-password"
              name="password"
              type="password"
              placeholder="Create a strong password"
              value={formData.password}
              onChange={handleChange}
              minLength={8}
              pattern="^(?=.*[A-Z])(?=.*\d)(?=.*[^\w\s]).{8,}$"
              title="Use at least 8 characters, including an uppercase letter, a number, and a special character."
              required
            />
            <span className="field-hint">
              8+ characters, with an uppercase letter, number, and special character.
            </span>
          </div>

          <div className="auth-field">
            <label htmlFor="signup-confirm-password" className="auth-label">
              Confirm Password
            </label>
            <input
              id="signup-confirm-password"
              name="confirm_password"
              type="password"
              placeholder="Re-enter your password"
              value={formData.confirm_password}
              onChange={handleChange}
              required
            />
          </div>

          {error && <div className="auth-error">{error}</div>}

          <button type="submit" disabled={submitting} className="primary-button">
            {submitting ? "Creating account..." : "Sign Up"}
          </button>
        </form>

        <p className="auth-footer">
          Already have an account?{" "}
          <Link to="/login" className="auth-link">Sign in</Link>
        </p>
      </div>
    </div>
  );
}

export default SignupPage;