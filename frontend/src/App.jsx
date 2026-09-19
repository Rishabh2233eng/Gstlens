import { useEffect, useState } from "react";

function App() {
  const [status, setStatus] = useState("checking...");

  useEffect(() => {
    fetch("http://127.0.0.1:8000/health")
      .then((res) => res.json())
      .then((data) => setStatus(data.status))
      .catch(() => setStatus("backend not reachable"));
  }, []);

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-slate-900 text-white">
      <h1 className="text-4xl font-bold">GSTLens</h1>
      <p className="mt-2 text-slate-300">GST-aware invoice checker</p>
      <p className="mt-6 text-sm">Backend status: {status}</p>
    </div>
  );
}

export default App;