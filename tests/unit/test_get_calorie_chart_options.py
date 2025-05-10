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
    app = create_app()            # 不传 testing
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
    """在 session 中模拟登录一个用户"""
    user = User(
        first_name="Test",      # 必填
        last_name="User",       # 必填
        email="test@example.com",
        password_hash="fakehash",
        target_calories=2000
    )
    db.session.add(user)
    db.session.commit()

    with client.session_transaction() as sess:
        sess["_user_id"] = str(user.id)
        # 还可以设置登录标志
        sess["_fresh"] = True
    return user


def test_week_range_with_some_data(monkeypatch, client):
    """
    模拟 week 范围下，数据库里有 2 天的数据，其它 5 天都没有。
    - day 05-08: 500 kcal
    - day 05-10: 300 kcal
    """
    user = login_test_user(client)

    # 1) 固定 today = 2025-05-10
    fixed_today = date(2025, 5, 10)
    monkeypatch.setattr(
        main_mod,
        "date",
        type("D", (), {"today": staticmethod(lambda: fixed_today)})
    )

    # 2) 模拟查询结果
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

    # 3) 发请求
    resp = client.get("/api/get_calorie_chart_options?range=week")
    assert resp.status_code == 200

    text = resp.get_data(as_text=True)
    # 检查包含所有七天的标签
    for label in ["05-04","05-05","05-06","05-07","05-08","05-09","05-10"]:
        assert f'"{label}"' in text
    # 检查 “Consumed” 系列 和 模拟的值
    assert '"Consumed"' in text
    assert "500.0" in text
    assert "300.0" in text
    # 检查 “Daily Goal” 系列 和用户目标值
    assert '"Daily Goal"' in text
    assert str(user.target_calories) in text