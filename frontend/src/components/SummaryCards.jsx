import React from "react";

function SummaryCards({ preview }) {
  if (!preview) return null;
  const cards = [
    { label: "Total Rows", value: preview.total_rows },
    { label: "Successful", value: preview.successful_rows },
    { label: "Ready for Tally", value: preview.clean_rows },
    { label: "Skipped", value: preview.skipped },
    { label: "Duplicates Removed", value: preview.duplicates_removed },
    {
      label: "Grand Total",
      value: `₹ ${Number(preview.total_amount).toLocaleString("en-IN", {
        minimumFractionDigits: 2,
      })}`,
      highlight: true,
    },
  ];
  return (
    <section className="summary-grid">
      {cards.map((c) => (
        <div
          key={c.label}
          className={"summary-card" + (c.highlight ? " highlight" : "")}
        >
          <div className="summary-label">{c.label}</div>
          <div className="summary-value">{c.value ?? 0}</div>
        </div>
      ))}
    </section>
  );
}

export default SummaryCards;
