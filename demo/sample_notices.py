"""Convenience re-exports of the bundled sample notices (sample_notices/)
for the demo client and the test suite.
"""

from app.sample_loader import load_sample

CLEAN_NOTICE = load_sample("clean")
REJECTED_MISSING_TRAIN_NUMBER = load_sample("missing_train_number")
REJECTED_PAST_DATE = load_sample("past_date")
REJECTED_WRONG_LANGUAGE = load_sample("wrong_language")
HINDI_NOTICE = load_sample("hindi_reason")
GARBLED_NOTICE = load_sample("garbled")
