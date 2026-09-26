import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from x402.http import FacilitatorConfig, HTTPFacilitatorClient, PaymentOption
from x402.http.middleware.fastapi import PaymentMiddlewareASGI
from x402.http.types import RouteConfig
from x402.mechanisms.evm.exact import ExactEvmServerScheme
from x402.server import x402ResourceServer

from app.parser import NoticeRejected, parse_notice
from app.schemas import ParsedNotice, ParseRequest

load_dotenv()

NETWORK = os.environ.get("X402_NETWORK", "eip155:84532")  # Base Sepolia
PAY_TO_ADDRESS = os.environ["X402_PAY_TO_ADDRESS"]
PRICE = os.environ.get("X402_PRICE", "$0.001")
FACILITATOR_URL = os.environ.get("X402_FACILITATOR_URL", "https://x402.org/facilitator")

facilitator_client = HTTPFacilitatorClient(FacilitatorConfig(url=FACILITATOR_URL))
resource_server = x402ResourceServer(facilitator_client).register(NETWORK, ExactEvmServerScheme())

routes = {
    "POST /parse": RouteConfig(
        accepts=PaymentOption(
            scheme="exact",
            pay_to=PAY_TO_ADDRESS,
            price=PRICE,
            network=NETWORK,
        ),
        description=(
            "Parse an Indian Railways delay notice into structured JSON. "
            "Only readable, valid notices are charged — a rejected notice costs nothing."
        ),
        mime_type="application/json",
    ),
}

app = FastAPI(title="The Operator's Booth", description="Meera's pay-per-call railway delay notice parser")
app.add_middleware(PaymentMiddlewareASGI, routes=routes, server=resource_server)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/parse", response_model=ParsedNotice)
async def parse(payload: ParseRequest):
    try:
        parsed = parse_notice(payload.notice_text)
    except NoticeRejected as exc:
        # Status >= 400 tells the x402 middleware to skip settlement — verified
        # in the installed SDK at x402/http/middleware/fastapi.py
        # ("Don't settle on error responses"). The caller is not charged.
        raise HTTPException(status_code=422, detail=exc.reason) from exc
    return parsed
