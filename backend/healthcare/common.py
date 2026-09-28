import json
import os
import re
import sqlite3
from contextlib import contextmanager
from datetime import date, datetime
from uuid import uuid4

from database import get_connection

CONSULTATION_MODES = ("in_person", "online")

# Placeholder teleconsultation URL. No video application is implemented;
# the link is only stored with the appointment. Override with an env var.
CONSULTATION_BASE_URL = os.environ.get(
    "AAROGYA_CONSULT_BASE_URL",
    "http://localhost:5173/consult"
)

_TIME_PATTERN = re.compile(r"^([01]\d|2[0-3]):[0-5]\d$")


class HealthcareError(Exception):
    """Domain error carrying the HTTP status the API layer should use."""

    def __init__(self, status_code: int, detail: str):
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail


def new_id(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex[:8].upper()}"


@contextmanager
def read_connection():
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()


@contextmanager
def transaction():
    """
    Run a block inside one SQLite write transaction.

    BEGIN IMMEDIATE takes the database write lock up front, so
    concurrent bookings are serialised by SQLite itself. Any
    exception rolls the whole block back.
    """
    conn = get_connection()
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("BEGIN IMMEDIATE")
        yield conn
        conn.commit()
    except BaseException:
        conn.rollback()
        raise
    finally:
        conn.close()


# -------- validation helpers --------

def clean_text(value, field: str) -> str:
    text = (value or "").strip()
    if not text:
        raise HealthcareError(422, f"{field} must not be empty")
    return text


def clean_list(values, field: str) -> list[str]:
    cleaned = []
    for value in values or []:
        text = (value or "").strip()
        if text and text not in cleaned:
            cleaned.append(text)
    if not cleaned:
        raise HealthcareError(422, f"{field} must contain at least one value")
    return cleaned


def clean_modes(values) -> list[str]:
    modes = clean_list(values, "consultation_modes")
    for mode in modes:
        check_mode(mode)
    return modes


def check_mode(mode: str) -> str:
    if mode not in CONSULTATION_MODES:
        raise HealthcareError(
            422,
            "consultation_mode must be one of: "
            + ", ".join(CONSULTATION_MODES)
        )
    return mode


def parse_date(value, field: str = "date") -> str:
    """Return a canonical YYYY-MM-DD string or raise a 422."""
    try:
        return date.fromisoformat(str(value)).isoformat()
    except ValueError:
        raise HealthcareError(422, f"{field} must be a valid YYYY-MM-DD date")


def parse_time(value, field: str) -> str:
    text = str(value)
    if not _TIME_PATTERN.match(text):
        raise HealthcareError(422, f"{field} must use 24-hour HH:MM")
    return text


def today_iso() -> str:
    return date.today().isoformat()


def build_consultation_link() -> str:
    return f"{CONSULTATION_BASE_URL.rstrip('/')}/{uuid4().hex}"


def to_json_list(values: list[str]) -> str:
    return json.dumps(values)


def from_json_list(raw) -> list[str]:
    try:
        return json.loads(raw) if raw else []
    except ValueError:
        return []
