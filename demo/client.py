"""Demo commuter app: calls the Operator's Booth with a real x402-signed
payment, once with a clean notice (charged) and once with garbage (not
charged), and prints what happened.

Requires a Base Sepolia wallet funded with testnet USDC. Set EVM_PRIVATE_KEY
in your environment or .env file.
"""

import asyncio
import os

from dotenv import load_dotenv
from eth_account import Account
from x402.client import x402Client
from x402.http.clients.httpx import x402HttpxClient
from x402.mechanisms.evm import EthAccountSigner
from x402.mechanisms.evm.exact import register_exact_evm_client

from demo.sample_notices import CLEAN_NOTICE, REJECTED_PAST_DATE

load_dotenv()

SERVER_URL = os.environ.get("PARSER_SERVER_URL", "http://127.0.0.1:8642")


def build_client() -> x402Client:
    account = Account.from_key(os.environ["EVM_PRIVATE_KEY"])
    client = x402Client()
    register_exact_evm_client(client, EthAccountSigner(account))
    return client


async def call_parse(notice_text: str, label: str) -> None:
    async with x402HttpxClient(build_client(), base_url=SERVER_URL) as http:
        response = await http.post("/parse", json={"notice_text": notice_text})
        print(f"--- {label} ---")
        print(f"HTTP {response.status_code}")
        if response.status_code == 200:
            print("Charged $0.001. Parsed:", response.json())
        else:
            print("Not charged. Server said:", response.json())
        print()


async def main() -> None:
    await call_parse(CLEAN_NOTICE, "Clean notice (should be charged)")
    await call_parse(REJECTED_PAST_DATE, "Stale notice (should NOT be charged)")


if __name__ == "__main__":
    asyncio.run(main())
