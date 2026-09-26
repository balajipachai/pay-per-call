import pytest

from app.parser import NoticeRejected, parse_notice
from app.schemas import BulkParseRequest, ParseRequest
from demo.sample_notices import (
    CLEAN_NOTICE,
    GARBLED_NOTICE,
    HINDI_NOTICE,
    REJECTED_MISSING_TRAIN_NUMBER,
    REJECTED_PAST_DATE,
    REJECTED_WRONG_LANGUAGE,
)
from pydantic import ValidationError


def test_clean_notice_parses():
    parsed = parse_notice(CLEAN_NOTICE)
    assert parsed.train_number == "12626"
    assert parsed.origin_station == "Pune Junction"
    assert parsed.destination_station == "New Delhi"
    assert parsed.delay_minutes == 45
    assert parsed.language == "en"


def test_hindi_reason_notice_parses():
    parsed = parse_notice(HINDI_NOTICE)
    assert parsed.train_number == "12626"
    assert parsed.delay_minutes == 45


def test_missing_train_number_rejected():
    with pytest.raises(NoticeRejected, match="train number"):
        parse_notice(REJECTED_MISSING_TRAIN_NUMBER)


def test_past_date_rejected():
    with pytest.raises(NoticeRejected, match="past"):
        parse_notice(REJECTED_PAST_DATE)


def test_wrong_language_rejected():
    with pytest.raises(NoticeRejected, match="not supported"):
        parse_notice(REJECTED_WRONG_LANGUAGE)


def test_empty_notice_rejected():
    with pytest.raises(NoticeRejected):
        parse_notice("")


def test_unknown_station_rejected():
    bad_station_notice = CLEAN_NOTICE.replace("Pune", "Nonexistentville")
    with pytest.raises(NoticeRejected, match="Unrecognized station"):
        parse_notice(bad_station_notice)


def test_garbled_notice_rejected():
    with pytest.raises(NoticeRejected, match="Date"):
        parse_notice(GARBLED_NOTICE)


def test_oversized_notice_rejected_by_schema():
    with pytest.raises(ValidationError):
        ParseRequest(notice_text="A" * 8001)


def test_bulk_request_caps_batch_size():
    with pytest.raises(ValidationError):
        BulkParseRequest(notices=["x"] * 11)
