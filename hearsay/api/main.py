from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uuid
app = FastAPI()

class CheckRequest(BaseModel):
    text: str

jobs = {}

@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/checks", status_code=202)
def claim_check(request: CheckRequest):
    check_id = str(uuid.uuid4())
    text = request.text
    jobs[check_id] = {"text": text, "status": "queued", "result": None}
    return {"check_id": check_id, "status": "queued"}

@app.get("/checks/{check_id}")
def get_check_result(check_id: str):
    if check_id not in jobs:
        raise HTTPException(status_code=404, detail="Check not found")
    return {"check_id": check_id, "status": jobs[check_id]["status"], "result": jobs[check_id]["result"]}