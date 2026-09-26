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
| `POST /parse` | $0.001 testnet USDC (`exact` scheme) | Parse one notice |
| `POST /parse/bulk` | $0.0005/notice, up to 10/call, `upto` scheme | Parse a batch of notices, billed per notice actually in the batch (cheaper per-notice than `/parse`) — all-or-nothing: if any notice in the batch can't be read, the whole batch is rejected and nothing is charged |

`/parse/bulk` uses x402's `upto` scheme: the buyer authorizes a ceiling
($0.005, enough for 10 notices), and `app/main.py` settles only for the
notices actually in the batch via `set_settlement_overrides` — a 2-notice
call costs $0.001, not the $0.005 ceiling.

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

### Verified live

Every route/scenario below has actually been run against a live server with
a funded Base Sepolia testnet wallet — these are real on-chain settlements,
not just wiring checks:

| Call | Result | Transaction |
|---|---|---|
| `/parse`, clean notice | charged $0.001 | [`0xfd2a8b2e...96c59d74`](https://sepolia.basescan.org/tx/0xfd2a8b2ef9643b928af32cd5724db6226f0b517611cfcec54eea303f96c59d74) |
| `/parse`, stale notice | 422, not charged | — |
| `/parse/bulk`, 1 notice | charged $0.0005 (`amount: 500`, not the $0.005 ceiling) | [`0xc0a2e2f6...082742ee4`](https://sepolia.basescan.org/tx/0xc0a2e2f6c2bb2b331999e48778dae4d422bcce7f0bd405bcfb1a85e082742ee4) |
| `/parse/bulk`, mixed batch | 422, whole batch not charged | — |
| Permit2 approval (one-time, required by the `upto` scheme, unlike `exact`'s gasless flow) | confirmed on-chain | [`0xdf51d30b...1138dba9b`](https://sepolia.basescan.org/tx/0xdf51d30bcb7eafabd4aed62e9e89b0cf64b0ff26de80f98991088cd1138dba9b) |

## Tests

Pure parser/validation logic, no network or wallet required:

```bash
pytest tests/ -v
```

## Stack

- FastAPI + x402 Python SDK (`x402[evm,httpx]`)
- x402.org testnet facilitator, Base Sepolia, testnet USDC
- Regex-based field extraction + `langdetect` for language validation
