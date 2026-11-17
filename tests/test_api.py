
from hearsay.api import main
import uuid
from datetime import timedelta
from sqlalchemy import func
from sqlalchemy.orm import Session
from hearsay.db.session import engine
from hearsay.db.models import Check

def test_health(client):
    get = client.get("/health")
    assert get.status_code == 200
    assert get.json()["status"]	 == "ok"

def test_post_then_get_returns_the_queued_check(client):
    post = client.post("/checks", json={"text": "Cairo is in Egypt."})

    assert post.status_code == 202
    check_id = post.json()["check_id"]

    get = client.get(f"/checks/{check_id}")

    assert get.status_code == 200
    body = get.json()
    assert body["status"] == "queued"
    assert body["done_claims"] == 0
    assert body["claims"] == []

def test_empty_text_is_rejected(client):
    post = client.post("/checks", json={"text": ""})

    assert post.status_code == 422

def test_too_long_text_is_rejected(client):
    post = client.post("/checks", json={"text": "h" * 1001})

    assert post.status_code == 422

def test_unknown_check_returns_404(client):
    get = client.get("/checks/00000000-0000-0000-0000-000000000000")

    assert get.status_code == 404

def test_bad_check_id_returns_422(client):
    get = client.get("/checks/hello")

    assert get.status_code == 422



def test_per_ip_limit_returns_429(client, monkeypatch):
    monkeypatch.setattr(main, "checks_per_ip_per_hour", 2)
    monkeypatch.setattr(main, "checks_per_day", 100)

    first = client.post("/checks", json={"text": "Cairo is in Egypt."})
    second = client.post("/checks", json={"text": "Cairo is in Egypt."})
    third = client.post("/checks", json={"text": "Cairo is in Egypt."})

    assert first.status_code == 202
    assert second.status_code == 202
    assert third.status_code == 429
    assert "your address" in third.json()["detail"]



def test_daily_limit_returns_429(client, monkeypatch):
    monkeypatch.setattr(main, "checks_per_day", 2)
    monkeypatch.setattr(main, "checks_per_ip_per_hour", 100)

    first = client.post("/checks", json={"text": "Cairo is in Egypt."})
    second = client.post("/checks", json={"text": "Cairo is in Egypt."})
    third = client.post("/checks", json={"text": "Cairo is in Egypt."})

    assert first.status_code == 202
    assert second.status_code == 202
    assert third.status_code == 429
    assert "daily limit" in third.json()["detail"]

def test_old_checks_do_not_count(client, monkeypatch):
    monkeypatch.setattr(main, "checks_per_ip_per_hour", 1)
    monkeypatch.setattr(main, "checks_per_day", 100)

    with Session(engine) as session:
        session.add(Check(
            check_id=uuid.uuid4(),
            text="old check",
            client_ip="testclient",
            created_at=func.now() - timedelta(hours=2),
        ))
        session.commit()

    post = client.post("/checks", json={"text": "Cairo is in Egypt."})

    assert post.status_code == 202
