import asyncio
import logging
import os

import httpx
from mcp.server import MCPServer

logging.basicConfig(level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger("hearsay-mcp")

HEARSAY_URL = os.getenv("HEARSAY_URL", "https://hearsay-production.up.railway.app")
POLL_SECONDS = 2
MAX_WAIT_SECONDS = 300

mcp = MCPServer("hearsay")


def summarize(result):
    if result["status"] == "error":
        return {"error": "Hearsay could not finish this check. Try again later."}
    claims = []
    for c in result["claims"]:
        claims.append({
            "claim": c["claim"],
            "label": c["label"],
            "reasoning": c["reasoning"],
            "evidence": [{"quote": q["quote"], "source": q["path"]} for q in c["cited"]],
        })
    return {"check_id": result["check_id"], "claims": claims}


@mcp.tool()
async def check_claims(text: str):
    """Fact-check a paragraph of English text against Wikipedia.

    Splits the text into individual factual claims and labels each one
    SUPPORTS, REFUTES, or NOT ENOUGH INFO with quotes from Wikipedia as evidence.
    Use it when the user asks whether statements are true or wants sources for facts.
    The text must be at most 1000 characters. A check takes about 10 to 120 seconds.
    """
    async with httpx.AsyncClient(base_url=HEARSAY_URL, timeout=90) as client:
        response = await client.post("/checks", json={"text": text})
        if response.status_code == 429:
            return {"error": response.json()["detail"]}
        if response.status_code == 422:
            return {"error": "The text must be between 1 and 1000 characters."}
        response.raise_for_status()
        check_id = response.json()["check_id"]
        logger.info("started check %s", check_id)

        waited = 0
        while waited < MAX_WAIT_SECONDS:
            await asyncio.sleep(POLL_SECONDS)
            waited += POLL_SECONDS
            try:
                poll = await client.get(f"/checks/{check_id}")
                poll.raise_for_status()
            except httpx.HTTPError:
                logger.warning("poll failed for %s, retrying", check_id)
                continue
            result = poll.json()
            if result["status"] in ("done", "error"):
                return summarize(result)

        return {"error": "Hearsay is still working on this check.", "check_id": check_id}


if __name__ == "__main__":
    mcp.run()