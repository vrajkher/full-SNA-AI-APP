import React, { useEffect, useState } from "react";
import {
  forgetRule,
  getLearningState,
  saveLearning,
} from "../services/api.js";

function LearningPanel({ unmapped = [] }) {
  const [rules, setRules] = useState({});
  const [draftKey, setDraftKey] = useState("");
  const [draftValue, setDraftValue] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);

  const refresh = async () => {
    try {
      const data = await getLearningState();
      setRules(data.rules || {});
    } catch (err) {
      setError(err.message);
    }
  };

  useEffect(() => {
    refresh();
  }, []);

  const addRule = async () => {
    if (!draftKey.trim() || !draftValue.trim()) return;
    setBusy(true);
    setError(null);
    try {
      await saveLearning([
        { budget_line: draftKey.trim(), correct_ledger: draftValue.trim() },
      ]);
      setDraftKey("");
      setDraftValue("");
      await refresh();
    } catch (err) {
      setError(err?.response?.data?.detail || err.message);
    } finally {
      setBusy(false);
    }
  };

  const removeRule = async (key) => {
    setBusy(true);
    try {
      await forgetRule(key);
      await refresh();
    } finally {
      setBusy(false);
    }
  };

  return (
    <section className="card">
      <h2>Auto-Learning Memory</h2>
      <p className="subtle">
        Rules are persisted on disk at
        <code> backend/app/data/learning/mapping_rules.json</code>.
        Corrections added here apply to every future run automatically.
      </p>

      {unmapped.length > 0 && (
        <div className="callout warn">
          <strong>Unmapped budget lines from last run:</strong>{" "}
          {unmapped.map((b) => (
            <code key={b} onClick={() => setDraftKey(b)} className="click-code">
              {b}
            </code>
          ))}
          <p className="subtle">Click a code to populate the form below.</p>
        </div>
      )}

      <div className="row rule-form">
        <input
          placeholder="NEW BUDGET LINE (e.g. HSS.9.1.108)"
          value={draftKey}
          onChange={(e) => setDraftKey(e.target.value)}
        />
        <input
          placeholder="Tally Ledger (e.g. Health Expense)"
          value={draftValue}
          onChange={(e) => setDraftValue(e.target.value)}
        />
        <button className="btn primary" onClick={addRule} disabled={busy}>
          {busy ? "Saving…" : "Add / Update Rule"}
        </button>
      </div>
      {error && <p className="error-text">{error}</p>}

      <table className="data-table">
        <thead>
          <tr>
            <th>Budget Line</th>
            <th>Tally Ledger</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          {Object.keys(rules)
            .sort()
            .map((key) => (
              <tr key={key}>
                <td><code>{key}</code></td>
                <td>{rules[key]}</td>
                <td>
                  <button
                    className="btn ghost danger"
                    onClick={() => removeRule(key)}
                    disabled={busy}
                  >
                    Forget
                  </button>
                </td>
              </tr>
            ))}
        </tbody>
      </table>
    </section>
  );
}

export default LearningPanel;
