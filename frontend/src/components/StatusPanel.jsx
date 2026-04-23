import React, { useState } from "react";
import { getRunXml } from "../services/api.js";

function StatusPanel({ run }) {
  const [xml, setXml] = useState(null);
  const [loading, setLoading] = useState(false);

  if (!run) return null;

  const stageLabel = {
    extractor: "Extractor",
    mapper: "Mapper",
    reviewer: "Reviewer",
    xml_generator: "XML Generator",
    tally_executor: "Tally Executor",
    error: "Error",
  }[run.stage] || run.stage;

  const loadXml = async () => {
    if (!run.run_id) return;
    setLoading(true);
    try {
      const text = await getRunXml(run.run_id);
      setXml(text);
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="card">
      <h2>3. Pipeline Status</h2>
      <div className={"status-banner " + (run.success ? "ok" : "bad")}>
        <strong>{run.success ? "SUCCESS" : "ATTENTION"}</strong>
        <span className="spacer" />
        <span>Stage: {stageLabel}</span>
        <span className="spacer" />
        <span>Run: <code>{run.run_id}</code></span>
      </div>

      {run.message && <p className="subtle">{run.message}</p>}

      {run.xml && (
        <div className="kv-grid">
          <div><span>Vouchers</span><strong>{run.xml.voucher_count}</strong></div>
          <div>
            <span>Total Amount</span>
            <strong>
              ₹ {Number(run.xml.total_amount).toLocaleString("en-IN", {
                minimumFractionDigits: 2,
              })}
            </strong>
          </div>
          <div>
            <span>Output File</span>
            <code>{run.xml.output_path}</code>
          </div>
        </div>
      )}

      {run.tally && (
        <div className="tally-response">
          <h3>Tally Response</h3>
          <div className="kv-grid">
            <div><span>HTTP</span><strong>{run.tally.status_code}</strong></div>
            <div><span>Created</span><strong>{run.tally.imported ?? "–"}</strong></div>
            <div><span>Errors</span><strong>{run.tally.errors ?? "–"}</strong></div>
          </div>
          <pre className="pre-scroll">{run.tally.response_text}</pre>
        </div>
      )}

      {run.xml && (
        <div className="xml-preview">
          <button className="btn ghost" onClick={loadXml} disabled={loading}>
            {loading ? "Loading…" : xml ? "Refresh XML" : "Show Generated XML"}
          </button>
          {xml && <pre className="pre-scroll">{xml}</pre>}
        </div>
      )}
    </section>
  );
}

export default StatusPanel;
