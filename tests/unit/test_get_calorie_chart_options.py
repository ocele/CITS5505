# tests/unit/test_get_calorie_chart_options.py

import pytest
from datetime import date
from flask.testing import FlaskClient
from collections import namedtuple

import app.routes.main as main_mod

from app import create_app, db
from app.routes.main import get_calorie_chart_options, bp
from app.models import User, ShareRecord, FoodLog, FoodItem

@pytest.fixture
def app():
    app = create_app()            
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
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
    """Mocks a user login for testing purposes."""
    user = User(
        first_name="Test",      
        last_name="User",       
        email="test@example.com",
        password_hash="fakehash",
        target_calories=2000
    )
    db.session.add(user)
    db.session.commit()

    with client.session_transaction() as sess:
        sess["_user_id"] = str(user.id)

        sess["_fresh"] = True
    return user


def test_week_range_with_some_data(monkeypatch, client):

    user = login_test_user(client)

    # today = 2025-05-10
    fixed_today = date(2025, 5, 10)
    monkeypatch.setattr(
        main_mod,
        "date",
        type("D", (), {"today": staticmethod(lambda: fixed_today)})
    )


    Row = namedtuple("Row", ["log_day_str", "total_calories"])
    fake_rows = [
        Row("2025-05-08", 500.0),
        Row("2025-05-10", 300.0),
    ]
    class FakeResult:
        def __init__(self, rows):
            self._rows = rows
        def all(self):
            return self._rows

    class FakeSession:
        def execute(self, query):
            return FakeResult(fake_rows)
        def rollback(self):
            pass  # no-op for error handling in view

    fake_db = type("DB", (), {"session": FakeSession()})
    monkeypatch.setattr(main_mod, "db", fake_db)


    resp = client.get("/api/get_calorie_chart_options?range=week")
    assert resp.status_code == 200

    text = resp.get_data(as_text=True)

    for label in ["05-04","05-05","05-06","05-07","05-08","05-09","05-10"]:
        assert f'"{label}"' in text

    assert '"Consumed"' in text
    assert "500.0" in text
    assert "300.0" in text

    assert '"Daily Goal"' in text
    assert str(user.target_calories) in text