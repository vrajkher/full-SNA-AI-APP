const { app, BrowserWindow, Menu, dialog, shell } = require("electron");
const path = require("path");
const { spawn } = require("child_process");
const fs = require("fs");
const http = require("http");

const isDev = !app.isPackaged;
const BACKEND_PORT = process.env.ACCOTECH_BACKEND_PORT || "8000";
const FRONTEND_DEV_URL =
  process.env.ACCOTECH_FRONTEND_URL || "http://localhost:5173";

let mainWindow = null;
let backendProcess = null;

function resolveBackendPath() {
  if (isDev) {
    return path.join(__dirname, "..", "backend");
  }
  return path.join(process.resourcesPath, "backend");
}

function resolvePython() {
  if (process.env.ACCOTECH_PYTHON) return process.env.ACCOTECH_PYTHON;
  if (process.platform === "win32") {
    const venv = path.join(
      process.env.APPDATA || "",
      "Accotech",
      "venv",
      "Scripts",
      "python.exe"
    );
    if (venv && fs.existsSync(venv)) return venv;
    return "python";
  }
  const unixVenv = path.join(
    process.env.HOME || "",
    ".accotech",
    "full-SNA-AI-APP",
    ".venv",
    "bin",
    "python"
  );
  if (fs.existsSync(unixVenv)) return unixVenv;
  return "python3";
}

function waitForBackend(url, timeoutMs = 30000) {
  const start = Date.now();
  return new Promise((resolve, reject) => {
    const attempt = () => {
      http
        .get(url, (res) => {
          res.resume();
          if (res.statusCode && res.statusCode < 500) return resolve(true);
          retry();
        })
        .on("error", retry);
    };
    const retry = () => {
      if (Date.now() - start > timeoutMs)
        return reject(new Error("Backend did not start in time"));
      setTimeout(attempt, 500);
    };
    attempt();
  });
}

function startBackend() {
  if (isDev && process.env.ACCOTECH_SKIP_BACKEND === "1") {
    return Promise.resolve();
  }

  const backendDir = resolveBackendPath();
  if (!fs.existsSync(backendDir)) {
    dialog.showErrorBox(
      "Backend missing",
      `Could not locate backend directory at ${backendDir}`
    );
    return Promise.reject(new Error("backend missing"));
  }

  const python = resolvePython();
  const args = [
    "-m",
    "uvicorn",
    "app.main:app",
    "--host",
    "127.0.0.1",
    "--port",
    BACKEND_PORT,
  ];

  backendProcess = spawn(python, args, {
    cwd: backendDir,
    env: { ...process.env, PYTHONUNBUFFERED: "1" },
  });

  backendProcess.stdout?.on("data", (buf) =>
    process.stdout.write(`[backend] ${buf}`)
  );
  backendProcess.stderr?.on("data", (buf) =>
    process.stderr.write(`[backend] ${buf}`)
  );
  backendProcess.on("exit", (code) => {
    console.log(`Backend exited with ${code}`);
  });

  return waitForBackend(`http://127.0.0.1:${BACKEND_PORT}/api/health`);
}

function stopBackend() {
  if (backendProcess && !backendProcess.killed) {
    try {
      backendProcess.kill("SIGTERM");
    } catch (err) {
      console.error("Failed to stop backend", err);
    }
    backendProcess = null;
  }
}

function buildMenu() {
  const template = [
    {
      label: "File",
      submenu: [
        { role: "quit", label: "Exit" },
      ],
    },
    {
      label: "View",
      submenu: [
        { role: "reload" },
        { role: "forceReload" },
        { type: "separator" },
        { role: "toggleDevTools" },
        { role: "resetZoom" },
        { role: "zoomIn" },
        { role: "zoomOut" },
      ],
    },
    {
      label: "Help",
      submenu: [
        {
          label: "Open Backend API",
          click: () =>
            shell.openExternal(`http://127.0.0.1:${BACKEND_PORT}/docs`),
        },
      ],
    },
  ];
  Menu.setApplicationMenu(Menu.buildFromTemplate(template));
}

async function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1100,
    minHeight: 720,
    backgroundColor: "#0f1420",
    show: false,
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  mainWindow.loadFile(path.join(__dirname, "splash.html"));
  mainWindow.once("ready-to-show", () => mainWindow.show());

  try {
    await startBackend();
  } catch (err) {
    dialog.showErrorBox(
      "Backend failed to start",
      `${err.message}\n\nMake sure Python 3.10+ is installed and ` +
        `backend dependencies are available (pip install -r backend/requirements.txt).`
    );
  }

  if (isDev) {
    await mainWindow.loadURL(FRONTEND_DEV_URL);
  } else {
    const indexHtml = path.join(__dirname, "..", "frontend", "dist", "index.html");
    await mainWindow.loadFile(indexHtml);
  }
}

app.whenReady().then(() => {
  buildMenu();
  createWindow();
  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on("window-all-closed", () => {
  stopBackend();
  if (process.platform !== "darwin") app.quit();
});

app.on("before-quit", stopBackend);
