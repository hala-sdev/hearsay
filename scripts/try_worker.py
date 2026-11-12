import uuid
from sqlalchemy.orm import Session
from hearsay.db.models import Check
from hearsay.db.session import engine
from hearsay.worker import claim_next

# Create check A, then check B (separate commits, so A is older)
with Session(engine) as session:
    session.add(Check(check_id=uuid.uuid4(), text="Check A"))
    session.commit()

with Session(engine) as session:
    session.add(Check(check_id=uuid.uuid4(), text="Check B"))
    session.commit()

# Ask for the next check three times
print("1st:", claim_next())
print("2nd:", claim_next())
print("3rd:", claim_next())