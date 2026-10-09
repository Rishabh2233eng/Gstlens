import api from "./client";

export async function uploadInvoice(file, onProgress) {
  const form = new FormData();
  form.append("file", file);
  const res = await api.post("/invoices/upload", form, {
    onUploadProgress: (e) => {
      if (e.total && onProgress) {
        onProgress(Math.round((e.loaded * 100) / e.total));
      }
    },
  });
  return res.data;
}

export async function extractInvoice(id) {
  const res = await api.post(`/invoices/${id}/extract`, null, { timeout: 120000 });
  return res.data;
}

export async function getIssues(id) {
  const res = await api.get(`/invoices/${id}/issues`);
  return res.data;
}

export async function listInvoices() {
  const res = await api.get("/invoices");
  return res.data;
}

export async function getInvoice(id) {
  const res = await api.get(`/invoices/${id}`);
  return res.data;
}

export async function updateInvoice(id, payload) {
  const res = await api.patch(`/invoices/${id}`, payload);
  return res.data;
}

function triggerDownload(blob, fallbackName) {
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = fallbackName;
  document.body.appendChild(a);
  a.click();
  a.remove();
  window.URL.revokeObjectURL(url);
}

export async function exportOneExcel(id) {
  const res = await api.get(`/invoices/${id}/export/excel`, { responseType: "blob" });
  triggerDownload(res.data, `invoice_${id}.xlsx`);
}

export async function exportOneCsv(id) {
  const res = await api.get(`/invoices/${id}/export/csv`, { responseType: "blob" });
  triggerDownload(res.data, `invoice_${id}_tally.csv`);
}

export async function exportBatchExcel(ids) {
  const res = await api.post(
    "/invoices/export/excel",
    { invoice_ids: ids },
    { responseType: "blob" }
  );
  triggerDownload(res.data, `invoices_${ids.length}.xlsx`);
}

export async function exportBatchCsv(ids) {
  const res = await api.post(
    "/invoices/export/csv",
    { invoice_ids: ids },
    { responseType: "blob" }
  );
  triggerDownload(res.data, `invoices_${ids.length}_tally.csv`);
}