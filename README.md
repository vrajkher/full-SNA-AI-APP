# ACCOTECH AI – Tally Automation System

AI-powered Windows desktop application that converts Excel/CSV accounting data
into Tally Prime XML entries and pushes them directly into Tally via the
XML HTTP interface (port 9000).

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
