# ACCOTECH AI – Tally Automation System

AI-powered Windows desktop application that converts Excel/CSV accounting data
into Tally Prime XML entries and pushes them directly into Tally via the
XML HTTP interface (port 9000).

## One-Click Install — pick one

There are four shippable install paths. Each one requires a single command
or a single double-click. All of them end with the app running on the
user's desktop.

### 1. Double-click (Windows — easiest, no typing)

Download the repo as a ZIP → extract → **double-click `install.bat`**.
The batch file self-elevates to Administrator and runs the PowerShell
installer below. Done.

### 2. One-liner (Windows, PowerShell)

```powershell
iwr -useb https://raw.githubusercontent.com/vrajkher/full-sna-ai-app/claude/tally-automation-app-4nVx2/install.ps1 | iex
```

What it does in one run (no further prompts):

1. Installs **Python 3.12** via `winget` (only if missing)
2. Installs **Node.js LTS** via `winget` (only if missing)
3. Installs **Git** via `winget` (only if missing)
4. Clones the repo into `%LOCALAPPDATA%\Accotech\full-SNA-AI-APP`
5. Creates a Python venv and installs backend requirements
6. Installs frontend + electron npm dependencies
7. Builds the React frontend (`vite build`)
8. Creates a **Desktop shortcut** and a **Start-Menu shortcut**
9. Launches the app

### 3. One-liner (macOS / Linux, bash)

```bash
curl -fsSL https://raw.githubusercontent.com/vrajkher/full-sna-ai-app/claude/tally-automation-app-4nVx2/install.sh | bash
```

Uses `brew` / `apt` / `dnf` / `pacman` (auto-detected) to install any
missing prerequisites. Installs the repo under `~/.accotech/` and drops
an `accotech` launcher in `~/.local/bin`. Finishes by launching the app.

### 4. Packaged NSIS installer (`Accotech AI Setup.exe`)

For distribution to end-users who cannot run scripts, build the native
Windows installer:

```bash
cd electron
npm run build:win
```

Produces **`electron/dist/Accotech AI Setup.exe`**. This is a true
one-click installer:

- `oneClick: true`, `runAfterFinish: true`, `createDesktopShortcut: always`
- Custom `electron/build/installer.nsh` auto-installs Python via
  `winget` if it is missing
- Creates a per-user venv at `%APPDATA%\Accotech\venv`
- Uninstall cleans everything up

Ship the `.exe`; the user double-clicks once, no prompts, the app opens.

> **After install:** launch via the Desktop shortcut (Windows),
> the Start Menu entry (Windows), or by typing `accotech` in any terminal
> (macOS / Linux).

## Architecture

```
Excel / CSV  →  FastAPI Backend  →  AI Agent Pipeline  →  Tally XML  →  Tally Prime
                      ↑                                                      │
                      └──────────── Learning Memory  ←───────────────────────┘
```

### Agent Pipeline (OpenClaw-style)

1. **Orchestrator** – coordinates the full run
2. **Extractor** – parses Excel / CSV with pandas
3. **Mapper** – maps budget-lines to Tally ledgers (uses learning memory)
4. **Reviewer** – validates rows (amount, duplicates, ledger, dates)
5. **XML Generator** – builds Tally-compatible payment voucher XML
6. **Tally Executor** – POSTs XML to `http://localhost:9000`
7. **Learning** – persists corrections, improves future mapping

Each agent folder contains three markdown files:

- `agent.md` – role and goal
- `soul.md` – behaviour and intelligence
- `skill.md` – executable actions

## Tech Stack

| Layer      | Technology                              |
|------------|-----------------------------------------|
| Backend    | Python 3.10+, FastAPI, Uvicorn, pandas  |
| Frontend   | React 18 + Vite                         |
| Desktop    | Electron + electron-builder             |
| Transport  | HTTP (Tally XML API, port 9000)         |

## Input Columns (Excel / CSV)

| Column             | Mapped To                         |
|--------------------|-----------------------------------|
| NEW BUDGET LINE    | Debit ledger                      |
| Sr No.             | Row index                         |
| SLS Code           | Metadata                          |
| Agency Code        | Metadata                          |
| Claim No.          | Metadata                          |
| Beneficiary Name   | Narration                         |
| Account No.        | Metadata                          |
| Net Amount         | Debit amount                      |
| Settlement Date    | Voucher date                      |
| Status Code        | Metadata                          |
| Status             | Only rows with "Success" are used |
| In File Name       | Metadata                          |
| UTR No.            | Reference / dedupe key            |
| CIN No.            | Metadata                          |
| Reference No.      | Metadata                          |

## Accounting Rules

- **Voucher Type:** Payment
- **For every successful row:** one DR to the budget-line ledger
- **For the whole file:** one CR to the company bank (e.g. HDFC Bank)
- **Signs:** DR = negative, CR = positive
- **Narration:** `<Beneficiary Name> | UTR: <UTR No.>`

## Save → Push Workflow

The UI exposes the pipeline as two explicit, reviewable steps. The XML is
always written to disk **before** it is sent to Tally, so you can inspect,
version-control, or replay it.

| Step | UI button | API call | Result |
|------|-----------|----------|--------|
| 1 | **Generate & Save XML** | `POST /api/process` (`push=false`) | `backend/app/data/outputs/voucher_<id>.xml` on disk + run cached in `RunStore` |
| — | **Save XML** (download) | `GET /api/runs/{id}/xml/download` | Saves a copy to your computer's Downloads folder |
| 2 | **Push to Tally** | `POST /api/push/{run_id}` | Replays the saved XML against `http://localhost:9000` |

Tally's `<CREATED>` / `<ERRORS>` counters are parsed and displayed inline.
If Tally is unreachable, the executor returns a human-readable message
(*"Tally connection failed. Is Tally Prime running with XML server on port
9000?"*) instead of crashing.

## Quick Start (Development)

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev

# Electron (after frontend + backend are up)
cd electron
npm install
npm start
```

## Windows Build

```bash
cd electron
npm run build:win
```

Produces `dist/Accotech AI Setup.exe`.

## Tally Setup

1. Open Tally Prime
2. `F1 → Help → Settings → Connectivity → Client/Server configuration`
3. Enable `TallyPrime is acting as → Both`
4. Set Port = `9000`
5. Keep the target company open

## Edge Cases Handled

- Duplicate UTR numbers
- Missing / unmapped ledger
- Zero / negative amount
- Invalid settlement date
- Tally connection failure
- Non-success status rows
