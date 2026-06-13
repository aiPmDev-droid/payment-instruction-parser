import Head from "next/head";
import { ChangeEvent, useEffect, useMemo, useState } from "react";
import { CheckCircle2, Clock3, FileText, Loader2, UploadCloud } from "lucide-react";

type Payment = {
  id?: number;
  vendor: string;
  amount: number | null;
  currency: string;
  due_date: string | null;
  payment_method: string;
  confidence: number;
  raw_text_excerpt: string;
  notes: string;
  source_filename?: string | null;
  created_at?: string;
};

type ExtractionResult = {
  payments: Payment[];
  source_type: string;
  source_filename: string | null;
};

const currencyFormatter = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
});

function formatAmount(payment: Payment) {
  if (payment.amount === null || Number.isNaN(payment.amount)) {
    return "Unknown";
  }
  if (payment.currency === "USD") {
    return currencyFormatter.format(payment.amount);
  }
  return `${payment.currency} ${payment.amount.toLocaleString()}`;
}

function confidenceLabel(value: number) {
  return `${Math.round(value * 100)}%`;
}

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] = useState<ExtractionResult | null>(null);
  const [history, setHistory] = useState<Payment[]>([]);
  const [isExtracting, setIsExtracting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const canSubmit = useMemo(() => {
    if (!file) return false;
    return file.name.toLowerCase().endsWith(".txt") || file.name.toLowerCase().endsWith(".eml");
  }, [file]);

  async function loadHistory() {
    try {
      const response = await fetch("/api/payments");
      if (!response.ok) return;
      setHistory(await response.json());
    } catch {
      setHistory([]);
    }
  }

  useEffect(() => {
    loadHistory();
  }, []);

  function handleFileChange(event: ChangeEvent<HTMLInputElement>) {
    setError(null);
    setResult(null);
    setFile(event.target.files?.[0] ?? null);
  }

  async function handleExtract() {
    if (!file || !canSubmit) return;
    setIsExtracting(true);
    setError(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("/api/payments/extract", {
        method: "POST",
        body: formData,
      });
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail ?? "Extraction failed.");
      }

      setResult(data);
      await loadHistory();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Extraction failed.");
    } finally {
      setIsExtracting(false);
    }
  }

  return (
    <>
      <Head>
        <title>Payment Instruction Parser</title>
        <meta
          name="description"
          content="Internal finance tool for extracting structured payment instructions from emails."
        />
      </Head>
      <main className="shell">
        <section className="topbar">
          <div>
            <p className="eyebrow">Finance Operations</p>
            <h1>Payment Instruction Parser</h1>
          </div>
          <div className="status-pill">
            <CheckCircle2 size={16} />
            Vercel-ready workflow
          </div>
        </section>

        <section className="workbench">
          <div className="upload-panel">
            <div className="panel-heading">
              <UploadCloud size={20} />
              <h2>Email Intake</h2>
            </div>
            <label className="dropzone">
              <FileText size={32} />
              <span>{file ? file.name : "Choose a .txt or .eml email"}</span>
              <input accept=".txt,.eml" onChange={handleFileChange} type="file" />
            </label>
            <button className="primary-button" disabled={!canSubmit || isExtracting} onClick={handleExtract}>
              {isExtracting ? <Loader2 className="spin" size={18} /> : <UploadCloud size={18} />}
              {isExtracting ? "Extracting" : "Extract Payment Instructions"}
            </button>
            {!canSubmit && file ? <p className="error">Only .txt and .eml files are supported.</p> : null}
            {error ? <p className="error">{error}</p> : null}
          </div>

          <div className="results-panel">
            <div className="panel-heading">
              <Clock3 size={20} />
              <h2>Extracted Fields</h2>
            </div>
            {result?.payments.length ? (
              <div className="payment-grid">
                {result.payments.map((payment, index) => (
                  <article className="payment-card" key={`${payment.vendor}-${index}`}>
                    <div className="card-row">
                      <strong>{payment.vendor}</strong>
                      <span>{confidenceLabel(payment.confidence)}</span>
                    </div>
                    <dl>
                      <div>
                        <dt>Amount</dt>
                        <dd>{formatAmount(payment)}</dd>
                      </div>
                      <div>
                        <dt>Due Date</dt>
                        <dd>{payment.due_date ?? "Unknown"}</dd>
                      </div>
                      <div>
                        <dt>Method</dt>
                        <dd>{payment.payment_method}</dd>
                      </div>
                    </dl>
                    <p className="excerpt">{payment.raw_text_excerpt}</p>
                    {payment.notes ? <p className="notes">{payment.notes}</p> : null}
                  </article>
                ))}
              </div>
            ) : (
              <div className="empty-state">Upload an email to review structured payment instructions.</div>
            )}
          </div>
        </section>

        <section className="history-section">
          <div className="section-heading">
            <h2>Recent Extractions</h2>
            <span>{history.length} records</span>
          </div>
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Vendor</th>
                  <th>Amount</th>
                  <th>Due Date</th>
                  <th>Method</th>
                  <th>Confidence</th>
                  <th>Source</th>
                </tr>
              </thead>
              <tbody>
                {history.map((payment) => (
                  <tr key={payment.id ?? `${payment.vendor}-${payment.created_at}`}>
                    <td>{payment.vendor}</td>
                    <td>{formatAmount(payment)}</td>
                    <td>{payment.due_date ?? "Unknown"}</td>
                    <td>{payment.payment_method}</td>
                    <td>{confidenceLabel(payment.confidence)}</td>
                    <td>{payment.source_filename ?? "Upload"}</td>
                  </tr>
                ))}
                {!history.length ? (
                  <tr>
                    <td colSpan={6}>No extraction history yet.</td>
                  </tr>
                ) : null}
              </tbody>
            </table>
          </div>
        </section>
      </main>
    </>
  );
}
