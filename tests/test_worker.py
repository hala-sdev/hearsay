import uuid
from sqlalchemy.orm import Session
from hearsay.db.session import engine
from hearsay.db.models import Check
from hearsay.worker import claim_next, requeue_stuck


def test_claim_next_counts_the_attempt(clean_db):
    check_id = uuid.uuid4()
    with Session(engine) as session:
        session.add(Check(check_id=check_id, text="Cairo is in Egypt."))
        session.commit()

    claimed = claim_next()

    assert claimed == check_id
    with Session(engine) as session:
        check = session.get(Check, check_id)
        assert check.status == "running"
        assert check.attempts == 1

def test_requeue_gives_up_after_max_attempts(clean_db):
    a_id = uuid.uuid4()
    b_id = uuid.uuid4()
    with Session(engine) as session:
        session.add(Check(check_id=a_id, text="Check A", status="running", attempts=3))
        session.add(Check(check_id=b_id, text="Check B", status="running", attempts=1))
        session.commit()

    requeue_stuck()

    with Session(engine) as session:
        a = session.get(Check, a_id)
        b = session.get(Check, b_id)
        assert a.status == "error"
        assert "Gave up" in a.error
        assert b.status == "queued"
        assert b.attempts == 1