const { contextBridge } = require("electron");

contextBridge.exposeInMainWorld("accotech", {
  apiBase: `http://127.0.0.1:${process.env.ACCOTECH_BACKEND_PORT || "8000"}`,
  platform: process.platform,
  version: "1.0.0",
});
