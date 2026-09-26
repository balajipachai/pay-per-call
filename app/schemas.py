from pydantic import BaseModel


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
    notice_text: str
