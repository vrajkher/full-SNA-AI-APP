"""FastAPI entrypoint for the Accotech AI backend."""

from __future__ import annotations

import shutil
import uuid
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, PlainTextResponse

from app.agents.extractor import ExtractorAgent
from app.agents.learning import LearningAgent
from app.agents.mapper import MapperAgent
from app.agents.orchestrator import OrchestratorAgent
from app.agents.reviewer import ReviewerAgent
from app.agents.tally_executor import TallyExecutorAgent
from app.agents.xml_generator import XMLGeneratorAgent
from app.core import get_logger, settings
from app.models import LedgerCorrection
from app.services.learning_store import LearningStore
from app.services.run_store import run_store

logger = get_logger("api")

app = FastAPI(title=settings.APP_NAME, version=settings.VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

orchestrator = OrchestratorAgent()
extractor = ExtractorAgent()
mapper = MapperAgent()
reviewer = ReviewerAgent()
xml_agent = XMLGeneratorAgent()
tally_agent = TallyExecutorAgent()
learning_agent = LearningAgent()
store = LearningStore()


# ---------------------------------------------------------------------------
# Health + meta
# ---------------------------------------------------------------------------

@app.get("/")
def root() -> dict:
    return {
        "app": settings.APP_NAME,
        "version": settings.VERSION,
        "tally_url": settings.tally_url,
        "bank_ledger": settings.DEFAULT_BANK_LEDGER,
    }


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/api/agents")
def agents_identity() -> dict:
    return {
        "orchestrator": orchestrator.identity(),
        "extractor": extractor.identity(),
        "mapper": mapper.identity(),
        "reviewer": reviewer.identity(),
        "xml_generator": xml_agent.identity(),
        "tally_executor": tally_agent.identity(),
        "learning": learning_agent.identity(),
    }


# ---------------------------------------------------------------------------
# Upload + Preview
# ---------------------------------------------------------------------------

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)) -> dict:
    suffix = Path(file.filename or "upload.xlsx").suffix or ".xlsx"
    file_id = f"{uuid.uuid4().hex}{suffix}"
    dest = settings.UPLOAD_DIR / file_id
    with dest.open("wb") as fh:
        shutil.copyfileobj(file.file, fh)
    logger.info("Received upload %s -> %s", file.filename, dest)
    return {"file_id": file_id, "original_name": file.filename}


@app.get("/api/preview/{file_id}")
def preview(file_id: str) -> dict:
    path = settings.UPLOAD_DIR / file_id
    if not path.exists():
        raise HTTPException(404, detail="file not found")
    extraction = extractor.run(path)
    mapping = mapper.run(extraction.rows)
    review = reviewer.run(mapping.rows)
    return {
        "total_rows": extraction.total_rows,
        "successful_rows": len(extraction.rows),
        "clean_rows": len(review.rows),
        "skipped": extraction.skipped,
        "duplicates_removed": review.duplicates_removed,
        "total_amount": review.total_amount,
        "unmapped": mapping.unmapped,
        "issues": [i.model_dump() for i in review.issues],
        "rows": [r.model_dump(mode="json") for r in review.rows],
    }


# ---------------------------------------------------------------------------
# Process + Push
# ---------------------------------------------------------------------------

@app.post("/api/process")
def process_file(
    file_id: str = Form(...),
    push: bool = Form(False),
    bank_ledger: Optional[str] = Form(None),
) -> JSONResponse:
    path = settings.UPLOAD_DIR / file_id
    if not path.exists():
        raise HTTPException(404, detail="file not found")
    result = orchestrator.run(path, push_to_tally=push, bank_ledger=bank_ledger)
    return JSONResponse(result.model_dump(mode="json"))


@app.post("/api/push/{run_id}")
def push_existing_run(run_id: str) -> JSONResponse:
    existing = run_store.get(run_id)
    if not existing or not existing.xml:
        raise HTTPException(404, detail="run not found or XML missing")
    tally_result = tally_agent.run(existing.xml.xml)
    existing.tally = tally_result
    existing.success = tally_result.success
    existing.stage = "tally_executor"
    existing.message = (
        "Pushed to Tally successfully."
        if tally_result.success
        else f"Tally push failed: {tally_result.response_text[:200]}"
    )
    run_store.save(existing)
    return JSONResponse(existing.model_dump(mode="json"))


@app.get("/api/runs/{run_id}")
def get_run(run_id: str) -> JSONResponse:
    existing = run_store.get(run_id)
    if not existing:
        raise HTTPException(404, detail="run not found")
    return JSONResponse(existing.model_dump(mode="json"))


@app.get("/api/runs/{run_id}/xml", response_class=PlainTextResponse)
def get_run_xml(run_id: str) -> PlainTextResponse:
    existing = run_store.get(run_id)
    if not existing or not existing.xml:
        raise HTTPException(404, detail="run or xml not found")
    return PlainTextResponse(existing.xml.xml, media_type="application/xml")


@app.get("/api/runs/{run_id}/xml/download")
def download_run_xml(run_id: str) -> FileResponse:
    existing = run_store.get(run_id)
    if not existing or not existing.xml or not existing.xml.output_path:
        raise HTTPException(404, detail="xml file not found")
    return FileResponse(
        existing.xml.output_path,
        media_type="application/xml",
        filename=Path(existing.xml.output_path).name,
    )


# ---------------------------------------------------------------------------
# Learning
# ---------------------------------------------------------------------------

@app.get("/api/learning")
def learning_state() -> dict:
    return learning_agent.state().model_dump()


@app.post("/api/learning/correct")
def learning_correct(corrections: list[LedgerCorrection]) -> dict:
    state = learning_agent.run(corrections)
    return state.model_dump()


@app.delete("/api/learning/{budget_line}")
def learning_forget(budget_line: str) -> dict:
    state = learning_agent.forget(budget_line)
    return state.model_dump()


# ---------------------------------------------------------------------------
# Tally connectivity probe
# ---------------------------------------------------------------------------

@app.get("/api/tally/ping")
def tally_ping() -> dict:
    import requests

    try:
        resp = requests.get(settings.tally_url, timeout=5)
        return {
            "reachable": True,
            "status_code": resp.status_code,
            "url": settings.tally_url,
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "reachable": False,
            "error": str(exc),
            "url": settings.tally_url,
        }
