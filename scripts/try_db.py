from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from hearsay.config import sqlalchemy_url
from hearsay.db.models import Check
import uuid
engine = create_engine(sqlalchemy_url, echo=True)
check_id = uuid.uuid4()
with Session(engine) as session:
    check = Check(
        check_id=check_id,
        text="test",
    )
    session.add(check)
    session.commit()
    found = session.get(Check, check_id)
    print(f"Found status: {found.status}, created at: {found.created_at}")