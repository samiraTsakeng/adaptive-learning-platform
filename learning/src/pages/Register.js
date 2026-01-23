import { useState } from "react";
import API from "../services/api";
import "../styles/auth.css";

const Register = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState("student");
  const [adminToken, setAdminToken] = useState("");
  const [message, setMessage] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      await API.post("/auth/register", {
        username,
        password,
        role,
        admin_token: adminToken,  // ✅ Send admin token
      });
      setMessage("✅ Registration successful. You can now login.");
      // Clear form
      setUsername("");
      setPassword("");
      setRole("student");
      setAdminToken("");
    } catch (err) {
      const errorMsg = err.response?.data?.message || "Registration failed. Username may already exist.";
      setMessage(`❌ ${errorMsg}`);
    }
  };

  return (
    <div className="auth-box">
      <h2>Register</h2>

      {message && <p>{message}</p>}

      <form onSubmit={handleSubmit}>
        <input
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
        />

        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />

        <select value={role} onChange={(e) => setRole(e.target.value)}>
          <option value="student">Student</option>
          <option value="teacher">Teacher</option>
        </select>

        {/* ✅ Show admin token field only when teacher is selected */}
        {role === "teacher" && (
          <input
            type="password"
            placeholder="Admin Token (required for teacher)"
            value={adminToken}
            onChange={(e) => setAdminToken(e.target.value)}
            required
          />
        )}

        <button className="btn">Register</button>
      </form>
    </div>
  );
};

export default Register;