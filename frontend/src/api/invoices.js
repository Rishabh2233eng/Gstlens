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