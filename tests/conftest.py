import os

os.environ["DATABASE_URL"] = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql://postgres:test@localhost:5433/hearsay_test?sslmode=disable",
)
os.environ["LANGFUSE_TRACING_ENABLED"] = "false"
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete
from sqlalchemy.orm import Session

from hearsay.api.main import app
from hearsay.db.models import Check, Claim
from hearsay.db.session import engine


@pytest.fixture
def clean_db():
    with Session(engine) as session:
        session.execute(delete(Claim))
        session.execute(delete(Check))
        session.commit()


@pytest.fixture
def client(clean_db):
    return TestClient(app)