import { useEffect, useState } from "react";
import axios from "axios";

function App() {
  const [message, setMessage] = useState("Loading...");
  const [error, setError] = useState("");

  useEffect(() => {
    axios
      .get("http://127.0.0.1:8000/api/v1/health/")
      .then((response) => {
        setMessage(JSON.stringify(response.data));
      })
      .catch((err) => {
        console.error(err);
        setError(err.message);
      });
  }, []);

  return (
    <div style={{ padding: "2rem", color: "black", background: "white" }}>
      <h1>Sales AI System</h1>
      <p>{message}</p>
      {error && <p style={{ color: "red" }}>{error}</p>}
    </div>
  );
}

export default App;