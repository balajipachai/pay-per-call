from pydantic import BaseModel, Field

# A real delay notice runs a few hundred characters. This caps abusive input
# (someone probing the free language-detection/regex path with megabytes of
# text) well above any legitimate notice.
MAX_NOTICE_LENGTH = 8000


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
    notice_text: str = Field(..., min_length=1, max_length=MAX_NOTICE_LENGTH)
