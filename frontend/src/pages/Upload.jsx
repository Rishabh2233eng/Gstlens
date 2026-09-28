import { useRef, useState } from "react";
import { extractInvoice, getIssues, uploadInvoice } from "../api/invoices";

const MAX_BYTES = 10 * 1024 * 1024;
const ALLOWED_TYPES = ["application/pdf", "image/png", "image/jpeg"];

const STATUS = {
  queued: { label: "Waiting", color: "text-slate-400" },
  uploading: { label: "Uploading", color: "text-blue-400" },
  extracting: { label: "Reading invoice...", color: "text-yellow-400" },
  done: { label: "Done", color: "text-green-400" },
  failed: { label: "Failed", color: "text-red-400" },
  rejected: { label: "Rejected", color: "text-red-400" },
};

let nextId = 1;

function errorText(err) {
  const detail = err.response?.data?.detail;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) return detail.map((d) => d.msg).join(", ");
  if (!err.response) return "Cannot reach the server";
  return `Server error (${err.response.status})`;
}

export default function Upload() {
  const [items, setItems] = useState([]);
  const [dragging, setDragging] = useState(false);
  const [running, setRunning] = useState(false);
  const inputRef = useRef(null);

  function patch(id, changes) {
    setItems((prev) => prev.map((i) => (i.id === id ? { ...i, ...changes } : i)));
  }

  async function processFile(entry) {
    patch(entry.id, { status: "uploading", progress: 0 });
    let uploaded = false;
    try {
      const invoice = await uploadInvoice(entry.file, (pct) =>
        patch(entry.id, { progress: pct })
      );
      uploaded = true;
      patch(entry.id, { status: "extracting", progress: 100, invoiceId: invoice.id });
      await extractInvoice(invoice.id);
      const issues = await getIssues(invoice.id);
      patch(entry.id, { status: "done", issueCount: issues.length });
    } catch (err) {
      const prefix = uploaded ? "Uploaded, but reading failed: " : "";
      patch(entry.id, { status: "failed", error: prefix + errorText(err) });
    }
  }

  async function addFiles(fileList) {
    if (running) return;
    const entries = Array.from(fileList).map((file) => {
      let error = null;
      if (!ALLOWED_TYPES.includes(file.type)) {
        error = "Only PDF, JPG and PNG files are allowed";
      } else if (file.size > MAX_BYTES) {
        error = "File is larger than 10 MB";
      }
      return {
        id: nextId++,
        file,
        name: file.name,
        status: error ? "rejected" : "queued",
        progress: 0,
        error,
        invoiceId: null,
        issueCount: null,
      };
    });
    if (entries.length === 0) return;

    setItems((prev) => [...entries, ...prev]);
    setRunning(true);
    for (const entry of entries) {
      if (entry.status === "queued") {
        await processFile(entry);
      }
    }
    setRunning(false);
  }

  function onDrop(e) {
    e.preventDefault();
    setDragging(false);
    addFiles(e.dataTransfer.files);
  }

  return (
    <div className="max-w-3xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">Upload invoices</h1>

      <div
        onDragOver={(e) => {
          e.preventDefault();
          if (!running) setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={onDrop}
        onClick={() => !running && inputRef.current?.click()}
        className={`border-2 border-dashed rounded-lg p-10 text-center transition ${
          running
            ? "border-slate-700 text-slate-500 cursor-not-allowed"
            : dragging
            ? "border-blue-400 bg-slate-800 cursor-pointer"
            : "border-slate-600 hover:border-slate-400 cursor-pointer"
        }`}
      >
        <p className="text-lg">
          {running ? "Processing... please wait" : "Drag and drop invoices here, or click to choose"}
        </p>
        <p className="text-sm text-slate-400 mt-1">PDF, JPG or PNG, up to 10 MB each</p>
        <input
          ref={inputRef}
          type="file"
          multiple
          accept="application/pdf,image/png,image/jpeg"
          className="hidden"
          onChange={(e) => {
            addFiles(e.target.files);
            e.target.value = "";
          }}
        />
      </div>

      <ul className="mt-6 space-y-3">
        {items.map((item) => {
          const s = STATUS[item.status];
          return (
            <li key={item.id} className="bg-slate-800 rounded-lg p-4">
              <div className="flex items-center justify-between gap-4">
                <span className="truncate">{item.name}</span>
                <span className={`text-sm whitespace-nowrap ${s.color}`}>
                  {s.label}
                  {item.status === "uploading" && ` ${item.progress}%`}
                </span>
              </div>

              {item.status === "uploading" && (
                <div className="h-2 bg-slate-700 rounded mt-3 overflow-hidden">
                  <div
                    className="h-full bg-blue-500 transition-all"
                    style={{ width: `${item.progress}%` }}
                  />
                </div>
              )}

              {item.status === "done" && (
                <p className="text-sm mt-2 text-slate-300">
                  {item.issueCount === 0
                    ? "No problems found."
                    : `${item.issueCount} problem${item.issueCount === 1 ? "" : "s"} found.`}
                </p>
              )}

              {item.error && <p className="text-sm mt-2 text-red-400">{item.error}</p>}
            </li>
          );
        })}
      </ul>
    </div>
  );
}