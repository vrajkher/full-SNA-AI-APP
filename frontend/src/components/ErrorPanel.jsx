import React from "react";

function ErrorPanel({ issues }) {
  if (!issues || !issues.length) {
    return (
      <section className="card">
        <h2>Issues</h2>
        <p className="subtle">No validation issues detected.</p>
      </section>
    );
  }

  const errors = issues.filter((i) => i.severity === "error");
  const warnings = issues.filter((i) => i.severity === "warning");

  return (
    <section className="card">
      <h2>Issues</h2>
      <div className="row pill-row">
        <span className="pill pill-bad">{errors.length} errors</span>
        <span className="pill pill-warn">{warnings.length} warnings</span>
      </div>
      <table className="data-table issues-table">
        <thead>
          <tr>
            <th>Severity</th>
            <th>Sr</th>
            <th>UTR</th>
            <th>Field</th>
            <th>Message</th>
          </tr>
        </thead>
        <tbody>
          {issues.map((i, idx) => (
            <tr key={idx}>
              <td>
                <span
                  className={
                    i.severity === "error" ? "pill pill-bad" : "pill pill-warn"
                  }
                >
                  {i.severity}
                </span>
              </td>
              <td>{i.sr_no ?? "–"}</td>
              <td><code>{i.utr_no || "–"}</code></td>
              <td>{i.field}</td>
              <td>{i.message}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}

export default ErrorPanel;
