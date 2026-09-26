# The Operator's Booth — Meera's Railway Delay API

A pay-per-call FastAPI service that parses Indian Railways delay notices into
clean JSON. Built for the **Road to Devcon VI: x402 Pay-Per-Call** track.

Meera's rule: **nobody pays for a notice she couldn't read.** A commuter app
pays $0.001 in testnet USDC (Base Sepolia) per call and gets clean JSON back
— but if the notice is garbage, the call costs nothing.

## How the refund works

x402's `exact` scheme verifies the payment signature *before* the handler
runs, but only **settles** (actually moves funds) *after* the handler
returns. If the handler returns an HTTP error (status >= 400), the SDK skips
settlement — confirmed directly in the installed SDK's
`x402/http/middleware/fastapi.py` (`# Don't settle on error responses`).

So the parser doesn't implement refunds itself: `app/parser.py` raises
`NoticeRejected` for garbage input, `app/main.py` turns that into a 422, and
the x402 middleware does the rest.

A notice is rejected if:
- the train number is missing or not a valid 5-digit number
- the notice date is in the past
- the notice isn't in a supported language (English, Hindi, or Marathi)
- the origin/destination station isn't recognized
- the delay duration can't be parsed

## Run it

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# edit .env: set X402_PAY_TO_ADDRESS to your Base Sepolia wallet address

uvicorn app.main:app --port 8642
```

```bash
curl -X POST http://127.0.0.1:8642/parse \
  -H "Content-Type: application/json" \
  -d '{"notice_text": "..."}'
# -> HTTP 402 with a PAYMENT-REQUIRED header describing the price/network/asset
```

## Demo client

Shows a real paid call (clean notice, charged) and a real rejected call
(stale notice, not charged) against a running server, using a Base Sepolia
wallet funded with testnet USDC.

```bash
# .env: set EVM_PRIVATE_KEY to a funded testnet wallet
python3 -m demo.client
```

## Tests

Pure parser/validation logic, no network or wallet required:

```bash
pytest tests/ -v
```

## Stack

- FastAPI + x402 Python SDK (`x402[evm,httpx]`)
- x402.org testnet facilitator, Base Sepolia, testnet USDC
- Regex-based field extraction + `langdetect` for language validation
