from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field
import uuid
from sqlalchemy.orm import Session
from hearsay.db.session import engine
from contextlib import asynccontextmanager
import asyncio
from hearsay.worker import worker_loop, new_check, requeue_stuck
from sqlalchemy import select
from hearsay.db.models import Check, Claim
from hearsay.config import max_text_chars, checks_per_ip_per_hour, checks_per_day
from sqlalchemy import func
from datetime import datetime, timedelta, timezone
import logging
from hearsay.config import log_level
from langfuse import get_client
logging.basicConfig(
    level=log_level,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    force=True,
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpx2").setLevel(logging.WARNING)
logging.getLogger("google_genai").setLevel(logging.WARNING)
logging.getLogger("wikipediaapi").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app):
    await asyncio.to_thread(requeue_stuck) 
    task = asyncio.create_task(worker_loop())
    yield
    task.cancel()
    get_client().shutdown()

app = FastAPI(lifespan=lifespan)


class CheckRequest(BaseModel):
    text: str = Field(min_length=1, max_length=max_text_chars)


@app.get("/health")
def health_check():
    return {"status": "ok"}

def save_check(text, ip):
    with Session(engine) as session:
        since = datetime.now(timezone.utc) - timedelta(hours=1)
        stmt = select(func.count()).select_from(Check).where(
            Check.client_ip == ip,
            Check.created_at > func.now() - timedelta(hours=1),
        )
        stmt_day = select(func.count()).select_from(Check).where(
            Check.created_at > func.now() - timedelta(hours=24),
        )
        if session.scalar(stmt_day) >= checks_per_day:
            raise HTTPException(status_code=429, detail="Hearsay has reached its daily limit. Try again tomorrow.")

        recent = session.scalar(stmt)
        if recent >= checks_per_ip_per_hour:
            raise HTTPException(status_code=429, detail="Too many checks from your address. Try again later.")

        check_id = uuid.uuid4()
        check = Check(check_id=check_id, text=text, client_ip=ip)
        session.add(check)
        session.commit()
        return check_id, check.status
    
@app.post("/checks", status_code=202)    
async def create_check(body: CheckRequest, request: Request):
    ip = request.client.host

    check_id, status = await asyncio.to_thread(save_check, body.text, ip)
    
    new_check.set()
    return {"check_id": check_id, "status": status}

@app.get("/checks/{check_id}")
def get_check_result(check_id: uuid.UUID):
    with Session(engine) as session:
        check = session.get(Check, check_id)
        if not check:
            raise HTTPException(status_code=404, detail="Check not found")
        stmt = select(Claim).where(Claim.check_id == check_id).order_by(Claim.claim_index)
        claims = session.scalars(stmt).all()
        claims_out = []

        for c in claims:
            claims_out.append({
                "claim_index": c.claim_index,
                "claim": c.claim,
                "label": c.label,
                "reasoning": c.reasoning,
                "cited": c.cited,
                "retried": c.retried,
                "first_pass": c.first_pass,
                "warnings": c.warnings,
            })

        return {"check_id": check.check_id, "status": check.status, "created_at": check.created_at,
                "error": check.error, "total_claims": check.total_claims, 
                "done_claims": len(claims), "claims":claims_out}


