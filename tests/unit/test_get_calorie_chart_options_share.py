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
    """
    带 share_id 时，应使用分享者的 target_calories 作为 Daily Goal
    """
    # 1) 登录主用户
    primary = login_test_user(client)

    # 2) 创建分享者，并设置不同 target_calories
    sender = User(
        first_name="Sender", last_name="User",
        email="sender@example.com", password_hash="hash",
        target_calories=1800,
        target_protein=0, target_fat=0, target_carbs=0
    )
    db.session.add(sender)
    db.session.commit()

    # 3) 新建 ShareRecord，
    share = ShareRecord(
      sender_id=sender.id,
      receiver_id=primary.id,
      content_type="calorie",
      date_range="week" 
    ) 
    db.session.add(share)  # Add before commit
     
    db.session.commit()

    # 4) 打桩：固定今天，模拟部分数据
    fixed = date(2025, 5, 20)
    monkeypatch.setattr(
        main_mod,
        "date",
        type("D", (), {"today": staticmethod(lambda: fixed)})
    )

    # 模拟聚合结果
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

    # 5) 发起请求，带上 share_id
    resp = client.get(f"/api/get_calorie_chart_options?range=week&share_id={share.id}")
    assert resp.status_code == 200

    text = resp.get_data(as_text=True)
        # 解析 JSON，检查 Daily Goal 系列数据
    payload = resp.get_json()
    # 找到 Daily Goal
    # 支持两种位置：直接 series 或在 option 对象里
    series_list = payload.get("series") or payload.get("options", {}).get("series", [])
    daily = next(s for s in series_list if s["name"] == "Daily Goal")
    # 应正好有 7 个相同值
    data_points = daily["data"]
    values = [pt[1] for pt in data_points]  # 每个 pt 格式为 [label, value]
    assert values == [sender.target_calories] * len(values)