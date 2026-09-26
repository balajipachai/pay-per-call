"""Loads the bundled sample notices from sample_notices/.

Files use {{TODAY}}/{{YESTERDAY}} placeholders instead of a baked-in date,
so the clean sample stays clean (and the past-date sample stays in the
past) no matter what day this repo is cloned and run on.
"""

from datetime import date, timedelta
from pathlib import Path

SAMPLE_NOTICES_DIR = Path(__file__).resolve().parent.parent / "sample_notices"


def _substitute_dates(text: str) -> str:
    today = date.today().strftime("%d %b %Y")
    yesterday = (date.today() - timedelta(days=1)).strftime("%d %b %Y")
    return text.replace("{{TODAY}}", today).replace("{{YESTERDAY}}", yesterday)


def load_sample(name: str) -> str:
    path = SAMPLE_NOTICES_DIR / f"{name}.txt"
    return _substitute_dates(path.read_text(encoding="utf-8"))


def list_samples() -> dict[str, str]:
    return {
        path.stem: _substitute_dates(path.read_text(encoding="utf-8"))
        for path in sorted(SAMPLE_NOTICES_DIR.glob("*.txt"))
    }
