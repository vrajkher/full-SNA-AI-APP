import React from "react";

function DataPreview({ preview }) {
  const rows = preview?.rows || [];
  if (!rows.length) return <p className="subtle">No rows to preview.</p>;

  return (
    <div className="table-scroll">
      <table className="data-table">
        <thead>
          <tr>
            <th>Sr</th>
            <th>Budget Line</th>
            <th>Ledger</th>
            <th>Beneficiary</th>
            <th>UTR</th>
            <th>Date</th>
            <th className="num">Amount</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r, i) => (
            <tr key={r.utr_no || `row-${i}`}>
              <td>{r.sr_no ?? i + 1}</td>
              <td><code>{r.budget_line}</code></td>
              <td>{r.mapped_ledger || <em className="muted">unmapped</em>}</td>
              <td>{r.beneficiary_name}</td>
              <td><code>{r.utr_no}</code></td>
              <td>{r.settlement_date}</td>
              <td className="num">
                {Number(r.net_amount).toLocaleString("en-IN", {
                  minimumFractionDigits: 2,
                })}
              </td>
              <td>
                <span className="pill pill-ok">{r.status}</span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default DataPreview;
