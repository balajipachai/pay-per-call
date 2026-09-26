"""Parses Indian Railways delay notices into clean JSON.

Meera's one rule: nobody pays for a notice she couldn't read. This module
is the "couldn't read" judge — every rejection here becomes an HTTP error
response, and the x402 middleware skips settlement on any response with
status >= 400 (verified against the installed SDK's
x402/http/middleware/fastapi.py, "Don't settle on error responses").
"""

import re
from datetime import date, datetime

from dateutil import parser as dateutil_parser
from langdetect import DetectorFactory, LangDetectException, detect_langs

from app.schemas import ParsedNotice
from app.stations import KNOWN_STATION_CODES

DetectorFactory.seed = 0  # deterministic langdetect output

SUPPORTED_LANGUAGES = {"en", "hi", "mr"}
TRAIN_NUMBER_RE = re.compile(r"\b(\d{5})\b")
STATION_CODE_RE = re.compile(r"^[A-Z]{2,5}$")

FIELD_RE = {
    "date": re.compile(r"Date:\s*(.+)", re.IGNORECASE),
    "train": re.compile(r"Train Number/Name:\s*(.+)", re.IGNORECASE),
    "scheduled": re.compile(r"Scheduled Departure/Arrival:\s*(.+)", re.IGNORECASE),
    "status": re.compile(r"Status:\s*(.+)", re.IGNORECASE),
    "estimated": re.compile(r"Estimated Departure Time:\s*(.+)", re.IGNORECASE),
    "platform": re.compile(r"Platform Number:\s*(.+)", re.IGNORECASE),
}

PROSE_RE = re.compile(
    r"depart(?:ing)? from\s+(?P<origin>.+?)\s+to\s+(?P<destination>.+?)\s+is currently running\s+"
    r"(?P<duration>.+?)\s+behind schedule(?:\s+due to\s+(?P<reason>.+?))?[.\n]",
    re.IGNORECASE | re.DOTALL,
)

DURATION_RE = re.compile(r"(\d+)\s*(?:hour|hr)s?\s*(?:(\d+)\s*(?:minute|min)s?)?|(\d+)\s*(?:minute|min)s?")


class NoticeRejected(Exception):
    """Raised when a notice can't be trusted enough to parse. No charge follows."""

    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(reason)


def _find_station(name: str) -> str:
    candidate = name.strip().strip(".,")
    if not candidate:
        raise NoticeRejected("Station name/code is empty.")

    if STATION_CODE_RE.match(candidate.upper()) and candidate.upper() in KNOWN_STATION_CODES:
        return KNOWN_STATION_CODES[candidate.upper()]

    for code, full_name in KNOWN_STATION_CODES.items():
        if candidate.lower() == full_name.lower() or candidate.upper() == code:
            return full_name

    raise NoticeRejected(f"Unrecognized station: '{candidate}' is not a known station code or name.")


def _parse_duration_minutes(text: str) -> int:
    match = DURATION_RE.search(text)
    if not match:
        raise NoticeRejected(f"Could not parse delay duration from '{text}'.")
    hours, minutes_with_hours, minutes_only = match.groups()
    if hours is not None:
        return int(hours) * 60 + int(minutes_with_hours or 0)
    return int(minutes_only)


def _detect_language(text: str) -> str:
    try:
        candidates = detect_langs(text)
    except LangDetectException as exc:
        raise NoticeRejected("Could not determine the notice's language (empty or unreadable text).") from exc

    top = candidates[0]
    if top.lang not in SUPPORTED_LANGUAGES:
        raise NoticeRejected(
            f"Notice language '{top.lang}' is not supported (expected English, Hindi, or Marathi)."
        )
    return top.lang


def parse_notice(raw_text: str) -> ParsedNotice:
    if not raw_text or not raw_text.strip():
        raise NoticeRejected("Notice text is empty.")

    language = _detect_language(raw_text)

    fields: dict[str, str | None] = {key: None for key in FIELD_RE}
    for key, pattern in FIELD_RE.items():
        match = pattern.search(raw_text)
        if match:
            fields[key] = match.group(1).strip()

    date_raw = fields["date"]
    if not date_raw:
        raise NoticeRejected("Notice is missing a Date field.")
    try:
        notice_date = dateutil_parser.parse(date_raw, fuzzy=True, default=datetime.now()).date()
    except (ValueError, OverflowError) as exc:
        raise NoticeRejected(f"Could not parse date '{date_raw}'.") from exc
    if notice_date < date.today():
        raise NoticeRejected(f"Notice date {notice_date.isoformat()} is in the past.")

    train_raw = fields["train"]
    if not train_raw:
        raise NoticeRejected("Notice is missing a Train Number/Name field.")
    number_match = TRAIN_NUMBER_RE.search(train_raw)
    if not number_match:
        raise NoticeRejected(f"No valid 5-digit train number found in '{train_raw}'.")
    train_number = number_match.group(1)
    train_name = train_raw.replace(train_number, "").strip(" /").strip() or None

    prose_match = PROSE_RE.search(raw_text)
    if not prose_match:
        raise NoticeRejected(
            "Could not find origin/destination/delay details in the notice body."
        )

    origin_station = _find_station(prose_match.group("origin"))
    destination_station = _find_station(prose_match.group("destination"))
    delay_minutes = _parse_duration_minutes(prose_match.group("duration"))
    reason = (prose_match.group("reason") or "").strip().strip(".") or None

    return ParsedNotice(
        train_number=train_number,
        train_name=train_name,
        origin_station=origin_station,
        destination_station=destination_station,
        status=fields["status"] or "Delayed",
        delay_minutes=delay_minutes,
        reason=reason,
        scheduled_time=fields["scheduled"],
        estimated_time=fields["estimated"],
        platform=fields["platform"],
        notice_date=notice_date.isoformat(),
        language=language,
    )
