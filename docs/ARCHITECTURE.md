# Architecture

```
 ┌──────────────────────────────────────────────────────────────────────────┐
 │                        Electron Shell (main.js)                          │
 │  ┌─────────────────────────────┐   ┌──────────────────────────────────┐ │
 │  │  React UI (Vite build)      │◄──┤  FastAPI (Uvicorn) spawn child   │ │
 │  │  http-proxy /api → 8000     │   │  python -m uvicorn app.main:app  │ │
 │  └──────────────┬──────────────┘   └──────────────┬───────────────────┘ │
 └─────────────────┼──────────────────────────────────┼─────────────────────┘
                   │                                  │
                   ▼                                  ▼
          ┌─────────────────┐           ┌──────────────────────────┐
          │  Upload / POST  │           │  OrchestratorAgent.run() │
          │  /api/process   │           └──────────────┬───────────┘
          └─────────────────┘                          │
                                                        ▼
          ┌────────────┐  ┌──────────┐  ┌────────────┐  ┌───────────────┐  ┌─────────────┐
          │ Extractor  ├─►│ Mapper   ├─►│ Reviewer   ├─►│ XML Generator ├─►│ Tally Exec. │
          └────────────┘  └────┬─────┘  └─────┬──────┘  └──────┬────────┘  └──────┬──────┘
                                │              │                │                  │
                                ▼              ▼                ▼                  ▼
                          ┌────────────┐  ┌─────────┐    data/outputs/       HTTP POST
                          │  Learning  │  │ Issues  │    voucher_*.xml       :9000
                          │   Store    │  │ Stream  │
                          │ (JSON)     │  └─────────┘
                          └─────┬──────┘
                                │
                                ▼
                         ┌──────────────┐
                         │ LearningAgent │
                         │  /api/learning│
                         └──────────────┘
```

## Data Flow

1. **User uploads** Excel / CSV via `FileUpload`.
2. **Backend** stores it under `data/uploads/<uuid>.<ext>`.
3. **Preview** endpoint runs Extractor + Mapper + Reviewer without XML
   generation and returns the DataFrame view for the UI.
4. **Process** endpoint triggers the full Orchestrator. The XML is written
   to `data/outputs/voucher_<ts>.xml` and the run is cached in `RunStore`.
5. **Push** endpoint replays the cached XML against Tally's XML API.
6. **Correct** endpoint persists operator corrections to
   `data/learning/mapping_rules.json`, which the Mapper reads on the next
   run.

## Tally Compatibility

The generated envelope uses the exact message shape that Tally Prime's
"Vouchers" import accepts. It works with:

- Tally.ERP 9 (6.6+)
- Tally Prime 2.x / 3.x / 4.x
- Any Tally build with the XML HTTP interface enabled (port 9000)

## Packaging

`electron-builder` bundles:

- `frontend/dist/` – static UI assets
- `backend/` – Python source (tests excluded)

At runtime, `main.js` spawns `python -m uvicorn app.main:app` inside the
packaged `backend/` folder. The end user must have Python 3.10+ on `PATH`
(the installer checks this via a helper script in `scripts/check-python.ps1`).
