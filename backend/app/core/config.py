"""Runtime configuration for the Accotech AI backend."""

from __future__ import annotations

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = DATA_DIR / "uploads"
OUTPUT_DIR = DATA_DIR / "outputs"
LEARNING_DIR = DATA_DIR / "learning"

for _d in (UPLOAD_DIR, OUTPUT_DIR, LEARNING_DIR):
    _d.mkdir(parents=True, exist_ok=True)


class Settings:
    APP_NAME: str = "ACCOTECH AI – Tally Automation System"
    VERSION: str = "1.0.0"

    # Tally XML HTTP API
    TALLY_HOST: str = os.getenv("TALLY_HOST", "localhost")
    TALLY_PORT: int = int(os.getenv("TALLY_PORT", "9000"))
    TALLY_TIMEOUT: int = int(os.getenv("TALLY_TIMEOUT", "60"))

    # Default CR ledger (company bank)
    DEFAULT_BANK_LEDGER: str = os.getenv("DEFAULT_BANK_LEDGER", "HDFC Bank")

    # Voucher type
    VOUCHER_TYPE: str = "Payment"

    # Storage
    BASE_DIR: Path = BASE_DIR
    DATA_DIR: Path = DATA_DIR
    UPLOAD_DIR: Path = UPLOAD_DIR
    OUTPUT_DIR: Path = OUTPUT_DIR
    LEARNING_DIR: Path = LEARNING_DIR
    LEARNING_FILE: Path = LEARNING_DIR / "mapping_rules.json"

    @property
    def tally_url(self) -> str:
        return f"http://{self.TALLY_HOST}:{self.TALLY_PORT}"


settings = Settings()
