from typing import Annotated

from pydantic import BaseModel, Field

# A real delay notice runs a few hundred characters. This caps abusive input
# (someone probing the free language-detection/regex path with megabytes of
# text) well above any legitimate notice.
MAX_NOTICE_LENGTH = 8000

# Bulk calls cost more per call, but still bounded — an unbounded batch would
# let one paid call buy unlimited parsing work.
MAX_BULK_NOTICES = 10

NoticeText = Annotated[str, Field(min_length=1, max_length=MAX_NOTICE_LENGTH)]


class ParsedNotice(BaseModel):
    train_number: str | None = None
    train_name: str | None = None
    origin_station: str
    destination_station: str
    status: str
    delay_minutes: int | None = None
    reason: str | None = None
    scheduled_time: str | None = None
    estimated_time: str | None = None
    platform: str | None = None
    notice_date: str
    language: str


class ParseRequest(BaseModel):
    notice_text: NoticeText


class BulkParseRequest(BaseModel):
    notices: list[NoticeText] = Field(..., min_length=1, max_length=MAX_BULK_NOTICES)


class BulkRejectedItem(BaseModel):
    index: int
    reason: str


class BulkParseResponse(BaseModel):
    results: list[ParsedNotice]
