import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { register } from "../api/auth";
import { useAuth } from "../context/AuthContext";

export default function Register() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      await register({ email, password, full_name: fullName });
      await login({ email, password });
      navigate("/");
    } catch (err) {
      setError(err.response?.data?.detail || "Registration failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-900 text-white">
      <form onSubmit={handleSubmit} className="w-80 bg-slate-800 p-6 rounded-lg space-y-4">
        <h1 className="text-2xl font-bold text-center">Create account</h1>
        {error && <p className="text-red-400 text-sm">{error}</p>}
        <input
          type="text"
          placeholder="Full name"
          value={fullName}
          onChange={(e) => setFullName(e.target.value)}
          className="w-full px-3 py-2 rounded bg-slate-700 outline-none"
        />
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          className="w-full px-3 py-2 rounded bg-slate-700 outline-none"
        />
        <input
          type="password"
          placeholder="Password (min 8 characters)"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          minLength={8}
          className="w-full px-3 py-2 rounded bg-slate-700 outline-none"
        />
        <button
          type="submit"
          disabled={busy}
          className="w-full py-2 rounded bg-blue-600 hover:bg-blue-500 disabled:opacity-50"
        >
          {busy ? "Creating..." : "Create account"}
        </button>
        <p className="text-sm text-center text-slate-400">
          Have an account? <Link to="/login" className="text-blue-400">Log in</Link>
        </p>
      </form>
    </div>
  );
}