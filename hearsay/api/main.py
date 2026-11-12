from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uuid
from sqlalchemy.orm import Session
from hearsay.db.models import Check
from hearsay.db.session import engine
from contextlib import asynccontextmanager
import asyncio
from hearsay.worker import worker_loop, new_check, requeue_stuck

@asynccontextmanager
async def lifespan(app):
    await asyncio.to_thread(requeue_stuck) 
    task = asyncio.create_task(worker_loop())
    yield
    task.cancel()

app = FastAPI(lifespan=lifespan)


class CheckRequest(BaseModel):
    text: str


@app.get("/health")
def health_check():
    return {"status": "ok"}


def save_check(text):
    check_id = uuid.uuid4()
    with Session(engine) as session:
        check = Check(
            check_id=check_id,
            text=text,
        )
        session.add(check)
        session.commit()
        return check_id, check.status
    
@app.post("/checks", status_code=202)    
async def create_check(request: CheckRequest):
    check_id, status = await asyncio.to_thread(save_check, request.text)
    new_check.set()
    return check_id, status

@app.get("/checks/{check_id}")
def get_check_result(check_id: uuid.UUID):
    with Session(engine) as session:
        check = session.get(Check, check_id)
        if not check:
            raise HTTPException(status_code=404, detail="Check not found")
        return {"check_id": check.check_id, "status": check.status, "created_at": check.created_at}


