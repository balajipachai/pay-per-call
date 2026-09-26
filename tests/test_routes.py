"""Route-level tests: the x402 payment gate itself, not the parser logic
(covered in test_parser.py). No wallet or network access needed — these
only check that routes are gated/ungated correctly and that the two paid
routes advertise different schemes and prices.
"""

import base64
import json
import os

os.environ.setdefault("X402_PAY_TO_ADDRESS", "0x1111111111111111111111111111111111111111")

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402

client = TestClient(app)


def _decode_payment_required(response) -> dict:
    return json.loads(base64.b64decode(response.headers["payment-required"]))


def test_health_is_free():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_samples_route_is_free():
    response = client.get("/notices/samples")
    assert response.status_code == 200
    assert "clean" in response.json()


def test_parse_requires_payment():
    response = client.post("/parse", json={"notice_text": "hello"})
    assert response.status_code == 402
    assert "payment-required" in response.headers


def test_parse_bulk_requires_payment():
    response = client.post("/parse/bulk", json={"notices": ["hello"]})
    assert response.status_code == 402
    assert "payment-required" in response.headers


def test_parse_and_bulk_use_different_schemes_and_prices():
    single = _decode_payment_required(client.post("/parse", json={"notice_text": "hello"}))
    bulk = _decode_payment_required(client.post("/parse/bulk", json={"notices": ["hello"]}))

    assert single["accepts"][0]["scheme"] == "exact"
    assert bulk["accepts"][0]["scheme"] == "upto"
    assert single["accepts"][0]["amount"] != bulk["accepts"][0]["amount"]
