"""Demo commuter app calling all three Operator's Booth routes:

1. GET  /notices/samples  — free, no payment
2. POST /parse            — paid, once with a clean notice (charged) and
                             once with a stale one (rejected, not charged)
3. POST /parse/bulk       — paid at a higher price, once with an all-clean
                             batch (charged) and once with a mixed batch
                             (rejected as a whole, not charged)

Requires a Base Sepolia wallet funded with testnet USDC. Set EVM_PRIVATE_KEY
in your environment or .env file.
"""

import asyncio
import os

import httpx
from dotenv import load_dotenv
from eth_account import Account
from x402.client import x402Client
from x402.http.clients.httpx import x402HttpxClient
from x402.mechanisms.evm import EthAccountSigner
from x402.mechanisms.evm.exact import register_exact_evm_client
from x402.mechanisms.evm.upto import UptoEvmClientScheme

from demo.sample_notices import CLEAN_NOTICE, REJECTED_PAST_DATE

load_dotenv()

SERVER_URL = os.environ.get("PARSER_SERVER_URL", "http://127.0.0.1:8642")
NETWORK = os.environ.get("X402_NETWORK", "eip155:84532")


def build_client() -> x402Client:
    """/parse pays via the exact scheme; /parse/bulk pays via the upto
    scheme (authorize a ceiling, settle for what the batch actually cost).
    Both need to be registered for the client to pay either route."""
    account = Account.from_key(os.environ["EVM_PRIVATE_KEY"])
    signer = EthAccountSigner(account)
    client = x402Client()
    register_exact_evm_client(client, signer)
    client.register(NETWORK, UptoEvmClientScheme(signer))
    return client


async def call_free_samples() -> None:
    async with httpx.AsyncClient(base_url=SERVER_URL) as http:
        response = await http.get("/notices/samples")
        print("--- Free: GET /notices/samples ---")
        print(f"HTTP {response.status_code}, {len(response.json())} bundled samples\n")


async def call_parse(notice_text: str, label: str) -> None:
    async with x402HttpxClient(build_client(), base_url=SERVER_URL) as http:
        response = await http.post("/parse", json={"notice_text": notice_text})
        print(f"--- Paid: POST /parse — {label} ---")
        print(f"HTTP {response.status_code}")
        if response.status_code == 200:
            print("Charged $0.001. Parsed:", response.json())
        else:
            print("Not charged. Server said:", response.json())
        print()


async def call_parse_bulk(notices: list[str], label: str) -> None:
    async with x402HttpxClient(build_client(), base_url=SERVER_URL) as http:
        response = await http.post("/parse/bulk", json={"notices": notices})
        print(f"--- Paid: POST /parse/bulk — {label} ---")
        print(f"HTTP {response.status_code}")
        if response.status_code == 200:
            print(f"Charged $0.0005 x {len(notices)} notices. Parsed:", response.json())
        else:
            print("Not charged (whole batch rejected). Server said:", response.json())
        print()


async def main() -> None:
    await call_free_samples()
    await call_parse(CLEAN_NOTICE, "clean notice, should be charged")
    await call_parse(REJECTED_PAST_DATE, "stale notice, should NOT be charged")
    await call_parse_bulk([CLEAN_NOTICE, CLEAN_NOTICE], "all clean, should be charged")
    await call_parse_bulk(
        [CLEAN_NOTICE, REJECTED_PAST_DATE], "one stale notice, whole batch should NOT be charged"
    )


if __name__ == "__main__":
    asyncio.run(main())
