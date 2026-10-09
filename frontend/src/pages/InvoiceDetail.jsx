import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { getInvoice, getIssues, updateInvoice } from "../api/invoices";

const FIELDS = [
  { key: "supplier_name", label: "Supplier name" },
  { key: "supplier_gstin", label: "Supplier GSTIN" },
  { key: "buyer_name", label: "Buyer name" },
  { key: "buyer_gstin", label: "Buyer GSTIN" },
  { key: "invoice_number", label: "Invoice number" },
  { key: "invoice_date", label: "Invoice date", type: "date" },
  { key: "taxable_value", label: "Taxable value", type: "number" },
  { key: "cgst", label: "CGST", type: "number" },
  { key: "sgst", label: "SGST", type: "number" },
  { key: "igst", label: "IGST", type: "number" },
  { key: "total_amount", label: "Total amount", type: "number" },
];

function errorText(err) {
  const detail = err.response?.data?.detail;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) return detail.map((d) => d.msg).join(", ");
  if (!err.response) return "Cannot reach the server";
  return `Server error (${err.response.status})`;
}

export default function InvoiceDetail() {
  const { id } = useParams();
  const [invoice, setInvoice] = useState(null);
  const [issues, setIssues] = useState([]);
  const [form, setForm] = useState({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [savedMsg, setSavedMsg] = useState("");

  async function load() {
    setLoading(true);
    setError("");
    try {
      const [inv, iss] = await Promise.all([getInvoice(id), getIssues(id)]);
      setInvoice(inv);
      setIssues(iss);
      setForm({
        supplier_name: inv.supplier_name ?? "",
        supplier_gstin: inv.supplier_gstin ?? "",
        buyer_name: inv.buyer_name ?? "",
        buyer_gstin: inv.buyer_gstin ?? "",
        invoice_number: inv.invoice_number ?? "",
        invoice_date: inv.invoice_date ?? "",
        taxable_value: inv.taxable_value ?? "",
        cgst: inv.cgst ?? "",
        sgst: inv.sgst ?? "",
        igst: inv.igst ?? "",
        total_amount: inv.total_amount ?? "",
      });
    } catch (err) {
      setError(errorText(err));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, [id]);

  function fieldIssues(key) {
    return issues.filter((i) => i.field === key || (key === "tax" && i.field === "tax"));
  }

  async function handleSave() {
    setSaving(true);
    setError("");
    setSavedMsg("");
    const payload = {};
    for (const f of FIELDS) {
      const value = form[f.key];
      payload[f.key] = value === "" ? null : value;
    }
    try {
      const updated = await updateInvoice(id, payload);
      setInvoice(updated);
      const newIssues = await getIssues(id);
      setIssues(newIssues);
      setSavedMsg("Saved.");
    } catch (err) {
      setError(errorText(err));
    } finally {
      setSaving(false);
    }
  }

  if (loading) return <p className="text-slate-400">Loading...</p>;
  if (error && !invoice) return <p className="text-red-400">{error}</p>;

  return (
    <div className="max-w-5xl mx-auto">
      <Link to="/invoices" className="text-blue-400 text-sm">← Back to invoices</Link>
      <div className="flex items-center justify-between mt-2 mb-4">
        <h1 className="text-2xl font-bold">{invoice.filename}</h1>
        <span className="px-2 py-1 rounded text-xs bg-slate-800">{invoice.status}</span>
      </div>

      {invoice.error_message && (
        <p className="text-red-400 mb-4">Extraction error: {invoice.error_message}</p>
      )}

      <div className="grid md:grid-cols-2 gap-6">
        <div className="space-y-4">
          <h2 className="font-semibold text-slate-300">Fields</h2>
          {FIELDS.map((f) => {
            const relevantIssues = fieldIssues(f.key);
            return (
              <div key={f.key}>
                <label className="text-xs text-slate-400 block mb-1">{f.label}</label>
                <input
                  type={f.type === "number" ? "text" : f.type || "text"}
                  value={form[f.key]}
                  onChange={(e) => setForm((prev) => ({ ...prev, [f.key]: e.target.value }))}
                  className={`w-full px-3 py-2 rounded bg-slate-800 outline-none text-sm ${
                    relevantIssues.length > 0 ? "ring-1 ring-red-500" : ""
                  }`}
                />
                {relevantIssues.map((iss) => (
                  <p key={iss.id} className="text-xs text-red-400 mt-1">{iss.message}</p>
                ))}
              </div>
            );
          })}

          <button
            onClick={handleSave}
            disabled={saving}
            className="px-4 py-2 rounded bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-sm"
          >
            {saving ? "Saving..." : "Save and revalidate"}
          </button>
          {savedMsg && <span className="text-green-400 text-sm ml-3">{savedMsg}</span>}
          {error && <p className="text-red-400 text-sm mt-2">{error}</p>}
        </div>

        <div>
          <h2 className="font-semibold text-slate-300 mb-2">
            Line items ({invoice.items?.length ?? 0})
          </h2>
          {invoice.items?.length ? (
            <div className="overflow-x-auto rounded border border-slate-700">
              <table className="w-full text-xs">
                <thead className="bg-slate-800 text-slate-300">
                  <tr>
                    <th className="text-left px-2 py-2">Description</th>
                    <th className="text-right px-2 py-2">Qty</th>
                    <th className="text-right px-2 py-2">Rate</th>
                    <th className="text-right px-2 py-2">Tax</th>
                  </tr>
                </thead>
                <tbody>
                  {invoice.items.map((item) => (
                    <tr key={item.id} className="border-t border-slate-700">
                      <td className="px-2 py-2">{item.description || "—"}</td>
                      <td className="px-2 py-2 text-right">{item.quantity ?? "—"}</td>
                      <td className="px-2 py-2 text-right">{item.unit_price ?? "—"}</td>
                      <td className="px-2 py-2 text-right">{item.tax_amount ?? "—"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="text-slate-500 text-sm">No line items.</p>
          )}

          <h2 className="font-semibold text-slate-300 mt-6 mb-2">
            All issues ({issues.length})
          </h2>
          {issues.length === 0 ? (
            <p className="text-green-400 text-sm">No problems found.</p>
          ) : (
            <ul className="space-y-2">
              {issues.map((iss) => (
                <li
                  key={iss.id}
                  className={`text-sm px-3 py-2 rounded ${
                    iss.severity === "error"
                      ? "bg-red-950 text-red-300"
                      : "bg-yellow-950 text-yellow-300"
                  }`}
                >
                  <span className="uppercase text-xs opacity-70">{iss.severity}</span> — {iss.message}
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
}