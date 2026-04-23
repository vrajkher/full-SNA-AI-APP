import React, { useRef, useState } from "react";
import { previewFile, uploadFile } from "../services/api.js";

function FileUpload({ onUploaded }) {
  const inputRef = useRef(null);
  const [dragging, setDragging] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);

  const handleFiles = async (fileList) => {
    const f = fileList && fileList[0];
    if (!f) return;
    setBusy(true);
    setError(null);
    try {
      const uploaded = await uploadFile(f);
      const preview = await previewFile(uploaded.file_id);
      onUploaded({ file: uploaded, preview });
    } catch (err) {
      setError(err?.response?.data?.detail || err.message || "Upload failed");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div
      className={"upload-zone" + (dragging ? " dragging" : "")}
      onDragOver={(e) => {
        e.preventDefault();
        setDragging(true);
      }}
      onDragLeave={() => setDragging(false)}
      onDrop={(e) => {
        e.preventDefault();
        setDragging(false);
        handleFiles(e.dataTransfer.files);
      }}
      onClick={() => inputRef.current?.click()}
    >
      <input
        ref={inputRef}
        type="file"
        accept=".xlsx,.xls,.csv"
        style={{ display: "none" }}
        onChange={(e) => handleFiles(e.target.files)}
      />
      {busy ? (
        <p>Uploading and analysing…</p>
      ) : (
        <>
          <p className="upload-title">Drop Excel / CSV here</p>
          <p className="subtle">or click to choose (.xlsx, .xls, .csv)</p>
        </>
      )}
      {error && <p className="error-text">{error}</p>}
    </div>
  );
}

export default FileUpload;
