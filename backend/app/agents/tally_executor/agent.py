"""Tally Executor Agent – POSTs XML to Tally Prime at localhost:9000."""

from __future__ import annotations

import re

import requests

from app.agents.base import BaseAgent
from app.core import settings
from app.models import TallyPushResult


class TallyExecutorAgent(BaseAgent):
    name = "tally_executor"

    def run(self, xml: str) -> TallyPushResult:  # type: ignore[override]
        url = settings.tally_url
        self.logger.info("Posting voucher XML to %s", url)
        try:
            resp = requests.post(
                url,
                data=xml.encode("utf-8"),
                headers={"Content-Type": "text/xml; charset=utf-8"},
                timeout=settings.TALLY_TIMEOUT,
            )
        except requests.exceptions.ConnectionError as exc:
            self.logger.error("Tally connection failed: %s", exc)
            return TallyPushResult(
                success=False,
                status_code=0,
                response_text=f"Tally connection failed. Is Tally Prime running with XML server on port {settings.TALLY_PORT}?",
            )
        except requests.exceptions.Timeout:
            return TallyPushResult(
                success=False,
                status_code=0,
                response_text="Request to Tally timed out.",
            )
        except requests.exceptions.RequestException as exc:
            return TallyPushResult(
                success=False,
                status_code=0,
                response_text=f"Tally request error: {exc}",
            )

        imported, errors = _parse_response(resp.text)
        success = resp.status_code == 200 and (errors == 0 or errors is None)
        self.logger.info(
            "Tally responded status=%s imported=%s errors=%s",
            resp.status_code,
            imported,
            errors,
        )
        return TallyPushResult(
            success=success,
            status_code=resp.status_code,
            response_text=resp.text,
            imported=imported,
            errors=errors,
        )


def _parse_response(text: str) -> tuple[int | None, int | None]:
    created = re.search(r"<CREATED>(\d+)</CREATED>", text)
    errors = re.search(r"<ERRORS>(\d+)</ERRORS>", text)
    return (
        int(created.group(1)) if created else None,
        int(errors.group(1)) if errors else None,
    )
