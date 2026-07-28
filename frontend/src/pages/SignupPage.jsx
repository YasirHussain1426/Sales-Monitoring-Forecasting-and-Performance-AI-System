import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
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

  const handleChange = (e) => {
    setFormData((prev) => ({
      ...prev,
      [e.target.name]: e.target.value,
    }));
  };

  const handleSignup = async (e) => {
    e.preventDefault();
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
    <div style={{ padding: "2rem", fontFamily: "Arial, sans-serif" }}>
      <h1>Sign Up</h1>

      <form onSubmit={handleSignup}>
        <div style={{ marginBottom: "1rem" }}>
          <input
            name="username"
            type="text"
            placeholder="Username"
            value={formData.username}
            onChange={handleChange}
          />
        </div>

        <div style={{ marginBottom: "1rem" }}>
          <input
            name="email"
            type="email"
            placeholder="Email"
            value={formData.email}
            onChange={handleChange}
          />
        </div>

        <div style={{ marginBottom: "1rem" }}>
          <input
            name="password"
            type="password"
            placeholder="Password"
            value={formData.password}
            onChange={handleChange}
          />
        </div>

        <div style={{ marginBottom: "1rem" }}>
          <input
            name="confirm_password"
            type="password"
            placeholder="Confirm Password"
            value={formData.confirm_password}
            onChange={handleChange}
          />
        </div>

        <button type="submit" disabled={submitting}>
          {submitting ? "Creating account..." : "Sign Up"}
        </button>
      </form>

      {error && <p style={{ color: "red" }}>{error}</p>}

      <p style={{ marginTop: "1rem" }}>
        Already have an account? <Link to="/login">Login</Link>
      </p>
    </div>
  );
}

export default SignupPage;