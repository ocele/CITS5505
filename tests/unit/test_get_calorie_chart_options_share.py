import pytest
from datetime import date
from collections import namedtuple
import app.routes.main as main_mod
from flask.testing import FlaskClient

from app import create_app, db
from app.models import User, ShareRecord

@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    })
    return app

@pytest.fixture
def client(app) -> FlaskClient:
    return app.test_client()

@pytest.fixture(autouse=True)
def empty_db(app):
    with app.app_context():
        db.create_all()
        yield
        db.session.remove()
        db.drop_all()


def login_test_user(client):
    user = User(
        first_name="Test", last_name="User",
        email="test@example.com", password_hash="fakehash",
        target_calories=2000,
        target_protein=0, target_fat=0, target_carbs=0
    )
    db.session.add(user)
    db.session.commit()
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user.id)
        sess["_fresh"] = True
    return user


def test_week_range_with_share(monkeypatch, client):
    primary = login_test_user(client)

    sender = User(
        first_name="Sender", last_name="User",
        email="sender@example.com", password_hash="hash",
        target_calories=1800,
        target_protein=0, target_fat=0, target_carbs=0
    )
    db.session.add(sender)
    db.session.commit()

    share = ShareRecord(
      sender_id=sender.id,
      receiver_id=primary.id,
      content_type="calorie",
      date_range="week" 
    ) 
    db.session.add(share)  # Add before commit
     
    db.session.commit()

    fixed = date(2025, 5, 20)
    monkeypatch.setattr(
        main_mod,
        "date",
        type("D", (), {"today": staticmethod(lambda: fixed)})
    )

    Row = namedtuple("Row", ["log_day_str", "total_calories"] )
    fake_rows = [Row("2025-05-18", 500.0)]
    class FakeResult:
        def __init__(self, rows):
            self._rows = rows
        def all(self):
            return self._rows
    class FakeSession:
        def execute(self, query):
            return FakeResult(fake_rows)
        def rollback(self):
            pass
    fake = FakeSession()
    monkeypatch.setattr(main_mod.db.session, "execute", fake.execute)
    monkeypatch.setattr(main_mod.db.session, "rollback", fake.rollback)

    resp = client.get(f"/api/get_calorie_chart_options?range=week&share_id={share.id}")
    assert resp.status_code == 200

    text = resp.get_data(as_text=True)
    payload = resp.get_json()

    series_list = payload.get("series") or payload.get("options", {}).get("series", [])
    daily = next(s for s in series_list if s["name"] == "Daily Goal")

    data_points = daily["data"]
    values = [pt[1] for pt in data_points]  # [label, value]
    assert values == [sender.target_calories] * len(values)