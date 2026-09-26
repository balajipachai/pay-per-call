# The Operator's Booth — Meera's Railway Delay API

A pay-per-call FastAPI service that parses Indian Railways delay notices into
clean JSON. Built for the **Road to Devcon VI: x402 Pay-Per-Call** track.

Meera's rule: **nobody pays for a notice she couldn't read.** A commuter app
gets clean JSON back for a readable notice — but if the notice is garbage,
the call costs nothing.

## Routes

| Route | Price | What it does |
|---|---|---|
| `GET /notices/samples` | free | Bundled example notices (`sample_notices/`), for trying the API before paying |
| `POST /parse` | $0.001 testnet USDC | Parse one notice |
| `POST /parse/bulk` | $0.005 testnet USDC | Parse up to 10 notices in one call — all-or-nothing: if any notice in the batch can't be read, the whole batch is rejected and nothing is charged |

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
- it's larger than 8000 characters (`app/schemas.py`, server-side cap)

## Sample notices

`sample_notices/` has six raw `.txt` notices — one clean, one bilingual
(English structure, Hindi reason), and four that each trip exactly one
rejection rule. Dates use `{{TODAY}}`/`{{YESTERDAY}}` placeholders
(`app/sample_loader.py` substitutes them at load time) so the clean sample
never goes stale, no matter what day you clone and run this.

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

Calls all three routes against a running server: the free samples route,
`/parse` once charged and once rejected, and `/parse/bulk` once charged and
once rejected as a whole batch. Needs a Base Sepolia wallet funded with
testnet USDC (get some from the [Circle faucet](https://faucet.circle.com/)).

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
