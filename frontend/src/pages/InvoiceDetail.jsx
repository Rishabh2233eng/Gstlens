import { useParams, Link } from "react-router-dom";

export default function InvoiceDetail() {
  const { id } = useParams();
  return (
    <div>
      <Link to="/invoices" className="text-blue-400 text-sm">← Back to invoices</Link>
      <h1 className="text-2xl font-bold mt-2">Invoice #{id}</h1>
      <p className="text-slate-400 mt-2">Full detail view is coming on Day 18.</p>
    </div>
  );
}