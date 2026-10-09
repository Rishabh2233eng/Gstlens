import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { exportBatchCsv, exportBatchExcel, listInvoices } from "../api/invoices";

const STATUS_STYLES = {
  uploaded: "bg-slate-700 text-slate-200",
  processing: "bg-yellow-900 text-yellow-300",
  done: "bg-green-900 text-green-300",
  failed: "bg-red-900 text-red-300",
};

function formatMoney(value) {
  if (value === null || value === undefined) return "—";
  return `₹${Number(value).toLocaleString("en-IN", { minimumFractionDigits: 2 })}`;
}

function formatDate(value) {
  if (!value) return "—";
  return new Date(value).toLocaleDateString("en-IN");
}

export default function Invoices() {
  const [invoices, setInvoices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [issuesOnly, setIssuesOnly] = useState(false);
  const [search, setSearch] = useState("");
  const [selected, setSelected] = useState(new Set());

  async function load() {
    setLoading(true);
    setError("");
    try {
      const data = await listInvoices();
      setInvoices(data);
    } catch (err) {
      setError("Could not load invoices. Is the server running?");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  function toggle(id) {
    setSelected((prev) => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  }

  const filtered = useMemo(() => {
    return invoices.filter((inv) => {
      if (statusFilter !== "all" && inv.status !== statusFilter) return false;
      if (issuesOnly && inv.issue_count === 0) return false;
      if (search) {
        const q = search.toLowerCase();
        const haystack = `${inv.supplier_name ?? ""} ${inv.invoice_number ?? ""} ${inv.filename}`.toLowerCase();
        if (!haystack.includes(q)) return false;
      }
      return true;
    });
  }, [invoices, statusFilter, issuesOnly, search]);

  return (
    <div className="max-w-5xl mx-auto">
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-bold">Invoices</h1>
        <Link
          to="/upload"
          className="px-3 py-2 rounded bg-blue-600 hover:bg-blue-500 text-sm"
        >
          + Upload
        </Link>
      </div>

      <div className="flex flex-wrap items-center gap-3 mb-4">
        <input
          type="text"
          placeholder="Search supplier, invoice no., filename..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="px-3 py-2 rounded bg-slate-800 text-sm outline-none flex-1 min-w-[200px]"
        />
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="px-3 py-2 rounded bg-slate-800 text-sm outline-none"
        >
          <option value="all">All statuses</option>
          <option value="uploaded">Uploaded</option>
          <option value="processing">Processing</option>
          <option value="done">Done</option>
          <option value="failed">Failed</option>
        </select>
        <label className="flex items-center gap-2 text-sm text-slate-300">
          <input
            type="checkbox"
            checked={issuesOnly}
            onChange={(e) => setIssuesOnly(e.target.checked)}
          />
          Issues only
        </label>
        <button
          onClick={load}
          className="px-3 py-2 rounded bg-slate-700 hover:bg-slate-600 text-sm"
        >
          Refresh
        </button>
        {selected.size > 0 && (
          <>
            <button
              onClick={() => exportBatchExcel([...selected])}
              className="px-3 py-2 rounded bg-green-700 hover:bg-green-600 text-sm"
            >
              Export {selected.size} to Excel
            </button>
            <button
              onClick={() => exportBatchCsv([...selected])}
              className="px-3 py-2 rounded bg-green-700 hover:bg-green-600 text-sm"
            >
              Export {selected.size} to Tally CSV
            </button>
          </>
        )}
      </div>

      {error && <p className="text-red-400 mb-4">{error}</p>}

      {loading ? (
        <p className="text-slate-400">Loading...</p>
      ) : filtered.length === 0 ? (
        <div className="text-center py-16 text-slate-400">
          {invoices.length === 0 ? (
            <>
              <p className="mb-3">No invoices yet.</p>
              <Link to="/upload" className="text-blue-400">Upload your first invoice</Link>
            </>
          ) : (
            <p>No invoices match your filters.</p>
          )}
        </div>
      ) : (
        <div className="overflow-x-auto rounded-lg border border-slate-700">
          <table className="w-full text-sm">
            <thead className="bg-slate-800 text-slate-300">
              <tr>
                <th className="px-4 py-3 w-8"></th>
                <th className="text-left px-4 py-3">Supplier</th>
                <th className="text-left px-4 py-3">Invoice No.</th>
                <th className="text-left px-4 py-3">Date</th>
                <th className="text-right px-4 py-3">Total</th>
                <th className="text-center px-4 py-3">Status</th>
                <th className="text-center px-4 py-3">Issues</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((inv) => (
                <tr
                  key={inv.id}
                  className="border-t border-slate-700 hover:bg-slate-800"
                >
                  <td className="px-4 py-3" onClick={(e) => e.stopPropagation()}>
                    <input
                      type="checkbox"
                      checked={selected.has(inv.id)}
                      onChange={() => toggle(inv.id)}
                    />
                  </td>
                  <td className="px-4 py-3">
                    <Link to={`/invoices/${inv.id}`} className="block">
                      {inv.supplier_name || <span className="text-slate-500">{inv.filename}</span>}
                    </Link>
                  </td>
                  <td className="px-4 py-3 text-slate-300">{inv.invoice_number || "—"}</td>
                  <td className="px-4 py-3 text-slate-300">{formatDate(inv.invoice_date)}</td>
                  <td className="px-4 py-3 text-right">{formatMoney(inv.total_amount)}</td>
                  <td className="px-4 py-3 text-center">
                    <span className={`px-2 py-1 rounded text-xs ${STATUS_STYLES[inv.status] || ""}`}>
                      {inv.status}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-center">
                    {inv.issue_count > 0 ? (
                      <span className="px-2 py-1 rounded text-xs bg-red-900 text-red-300">
                        {inv.issue_count}
                      </span>
                    ) : inv.status === "done" ? (
                      <span className="text-green-400 text-xs">Clean</span>
                    ) : (
                      "—"
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}