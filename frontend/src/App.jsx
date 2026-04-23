import React, { useEffect, useState } from "react";
import FileUpload from "./components/FileUpload.jsx";
import DataPreview from "./components/DataPreview.jsx";
import StatusPanel from "./components/StatusPanel.jsx";
import ErrorPanel from "./components/ErrorPanel.jsx";
import LearningPanel from "./components/LearningPanel.jsx";
import SummaryCards from "./components/SummaryCards.jsx";
import {
  processFile,
  pushRun,
  tallyPing,
  health,
} from "./services/api.js";

function App() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [run, setRun] = useState(null);
  const [processing, setProcessing] = useState(false);
  const [pushing, setPushing] = useState(false);
  const [tallyStatus, setTallyStatus] = useState(null);
  const [apiStatus, setApiStatus] = useState(null);
  const [bankLedger, setBankLedger] = useState("HDFC Bank");
  const [tab, setTab] = useState("dashboard");

  useEffect(() => {
    health().then(setApiStatus).catch(() => setApiStatus(null));
    tallyPing().then(setTallyStatus).catch(() => setTallyStatus(null));
  }, []);

  const handleUploaded = ({ file, preview }) => {
    setFile(file);
    setPreview(preview);
    setRun(null);
  };

  const handleProcess = async () => {
    if (!file?.file_id) return;
    setProcessing(true);
    try {
      const result = await processFile(file.file_id, false, bankLedger);
      setRun(result);
    } catch (err) {
      setRun({
        success: false,
        stage: "error",
        message: err?.response?.data?.detail || err.message,
      });
    } finally {
      setProcessing(false);
    }
  };

  const handlePush = async () => {
    if (!run?.run_id) return;
    setPushing(true);
    try {
      const result = await pushRun(run.run_id);
      setRun(result);
      const ping = await tallyPing();
      setTallyStatus(ping);
    } catch (err) {
      setRun((r) => ({
        ...(r || {}),
        success: false,
        message: err?.response?.data?.detail || err.message,
      }));
    } finally {
      setPushing(false);
    }
  };

  return (
    <div className="app-shell">
      <header className="app-header">
        <div className="brand">
          <div className="brand-mark">A</div>
          <div>
            <h1>ACCOTECH AI</h1>
            <p>Tally Automation System</p>
          </div>
        </div>
        <nav className="app-nav">
          <button
            className={tab === "dashboard" ? "nav-btn active" : "nav-btn"}
            onClick={() => setTab("dashboard")}
          >
            Dashboard
          </button>
          <button
            className={tab === "learning" ? "nav-btn active" : "nav-btn"}
            onClick={() => setTab("learning")}
          >
            Learning Memory
          </button>
        </nav>
        <div className="health-indicators">
          <span className={apiStatus ? "pill pill-ok" : "pill pill-bad"}>
            API: {apiStatus ? "online" : "offline"}
          </span>
          <span
            className={
              tallyStatus?.reachable ? "pill pill-ok" : "pill pill-warn"
            }
          >
            Tally: {tallyStatus?.reachable ? "reachable" : "unreachable"}
          </span>
        </div>
      </header>

      {tab === "dashboard" && (
        <main className="app-main">
          <section className="card">
            <h2>1. Upload</h2>
            <FileUpload onUploaded={handleUploaded} />
            {file && (
              <p className="subtle">
                Loaded: <strong>{file.original_name}</strong>
              </p>
            )}
          </section>

          {preview && (
            <>
              <SummaryCards preview={preview} />
              <section className="card">
                <h2>2. Data Preview</h2>
                <DataPreview preview={preview} />
              </section>
              <section className="card actions">
                <div className="row">
                  <label>
                    Bank Ledger (CR)
                    <input
                      value={bankLedger}
                      onChange={(e) => setBankLedger(e.target.value)}
                    />
                  </label>
                  <button
                    className="btn primary"
                    disabled={processing || !preview?.clean_rows}
                    onClick={handleProcess}
                  >
                    {processing ? "Processing…" : "Process & Generate XML"}
                  </button>
                  <button
                    className="btn success"
                    disabled={pushing || !run?.xml}
                    onClick={handlePush}
                    title={
                      !run?.xml
                        ? "Run Process first"
                        : "POST XML to Tally at localhost:9000"
                    }
                  >
                    {pushing ? "Pushing…" : "Push to Tally"}
                  </button>
                </div>
              </section>
            </>
          )}

          {run && (
            <>
              <StatusPanel run={run} />
              <ErrorPanel issues={run?.issues || preview?.issues} />
            </>
          )}
        </main>
      )}

      {tab === "learning" && (
        <main className="app-main">
          <LearningPanel unmapped={run?.data?.unmapped || preview?.unmapped || []} />
        </main>
      )}

      <footer className="app-footer">
        <span>Accotech AI v1.0.0</span>
        <span>Tally URL: {tallyStatus?.url || "http://localhost:9000"}</span>
      </footer>
    </div>
  );
}

export default App;
