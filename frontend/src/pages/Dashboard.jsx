import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { listInvoices } from "../api/invoices";
import { useAuth } from "../context/AuthContext";

export default function Dashboard() {
  const { user } = useAuth();
  const [invoices, setInvoices] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    listInvoices()
      .then(setInvoices)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const total = invoices.length;
  const withIssues = invoices.filter((i) => i.issue_count > 0).length;
  const clean = invoices.filter((i) => i.status === "done" && i.issue_count === 0).length;
  const recent = [...invoices]
    .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
    .slice(0, 5);

  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold mb-1">Welcome{user?.full_name ? `, ${user.full_name}` : ""}</h1>
      <p className="text-slate-400 mb-6">
        {user?.plan?.name ?? "Free"} plan
      </p>

      {loading ? (
        <p className="text-slate-400">Loading...</p>
      ) : total === 0 ? (
        <div className="text-center py-16 bg-slate-800 rounded-lg">
          <p className="text-slate-300 mb-3">No invoices uploaded yet.</p>
          <Link to="/upload" className="px-4 py-2 rounded bg-blue-600 hover:bg-blue-500 text-sm">
            Upload your first invoice
          </Link>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-3 gap-4 mb-6">
            <div className="bg-slate-800 rounded-lg p-4">
              <p className="text-slate-400 text-sm">Total invoices</p>
              <p className="text-3xl font-bold">{total}</p>
            </div>
            <div className="bg-slate-800 rounded-lg p-4">
              <p className="text-slate-400 text-sm">With issues</p>
              <p className="text-3xl font-bold text-red-400">{withIssues}</p>
            </div>
            <div className="bg-slate-800 rounded-lg p-4">
              <p className="text-slate-400 text-sm">Clean</p>
              <p className="text-3xl font-bold text-green-400">{clean}</p>
            </div>
          </div>

          <h2 className="font-semibold text-slate-300 mb-2">Recent uploads</h2>
          <ul className="divide-y divide-slate-700 bg-slate-800 rounded-lg overflow-hidden">
            {recent.map((inv) => (
              <li key={inv.id}>
                <Link
                  to={`/invoices/${inv.id}`}
                  className="flex items-center justify-between px-4 py-3 hover:bg-slate-700"
                >
                  <span className="truncate">{inv.supplier_name || inv.filename}</span>
                  <span className="text-xs text-slate-400">{inv.status}</span>
                </Link>
              </li>
            ))}
          </ul>
          <Link to="/invoices" className="inline-block mt-4 text-blue-400 text-sm">
            View all invoices →
          </Link>
        </>
      )}
    </div>
  );
}