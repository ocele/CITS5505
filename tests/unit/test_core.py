# tests/unit/test_core.py

import json
import pytest
from datetime import date, datetime, timedelta

from flask import Flask
from flask.testing import FlaskClient

from app.models import get_calorie_chart_options, bp  # noqa: F401
from app import create_app, db
from app.models import User, ShareRecord, FoodLog, FoodItem

# —— 1. calculate_daily_nutrition —— #

@pytest.fixture
def app():
    """创建测试用 Flask 应用（使用 testing 配置）"""
    app = create_app("testing")
    app.register_blueprint(bp)  # 确保路由已注册
    return app

@pytest.fixture
def client(app) -> FlaskClient:
    return app.test_client()

@pytest.fixture(autouse=True)
def empty_db(app):
    """在每个测试前后清空数据库表"""
    with app.app_context():
        db.create_all()
        yield
        db.session.remove()
        db.drop_all()


def login_test_user(client):
    """辅助：在测试中快速登录一个用户"""
    # 创建并登录一个用户
    user = User(email="test@example.com", password_hash="fakehash", target_calories=1500)
    db.session.add(user)
    db.session.commit()

    # 直接把用户写入 session
    with client.session_transaction() as sess:
        sess["user_id"] = user.id

    return user


def test_invalid_time_range(client):
    """range 参数不合法时应返回 400 + 错误信息"""
    user = login_test_user(client)

    resp = client.get("/api/get_calorie_chart_options?range=year")
    assert resp.status_code == 400
    assert resp.get_json() == {"error": "Invalid time range parameter"}


def test_week_range_no_data(monkeypatch, client):
    """当 week 范围且数据库无日志时，应返回 7 个标签 & 全 0 数据"""
    user = login_test_user(client)

    # 模拟当前日期固定，方便断言
    fixed_today = date(2025, 5, 10)
    monkeypatch.setattr("app.routes.chart.date", type("D", (), {"today": staticmethod(lambda: fixed_today)}))

    # 模拟数据库查询返回空列表
    class FakeResult:
        pass

    def fake_execute(query):
        return []  # no rows

    monkeypatch.setattr("app.routes.chart.db.session", type("S", (), {"execute": fake_execute}))

    # 发起请求，不传 share_id，默认 user_id 来自 current_user
    resp = client.get("/api/get_calorie_chart_options?range=week")
    assert resp.status_code == 200

    payload = resp.get_json()
    # payload 应包含 x 轴和 series
    assert "xAxis" in payload
    assert payload["xAxis"]["data"] == [  # 7 天的 MM-DD 标签
        "05-04", "05-05", "05-06", "05-07", "05-08", "05-09", "05-10"
    ]
    # 系列中应有两个：Consumed 和 Daily Goal
    series = {serie["name"]: serie["data"] for serie in payload["series"]}
    assert "Consumed" in series and "Daily Goal" in series
    # 没数据时 Consumed 全 0，Daily Goal 全等于 target_calories
    assert series["Consumed"] == [0.0] * 7
    assert series["Daily Goal"] == [round(user.target_calories, 1)] * 7



# —— 2. compute_achievement_rate —— #

def test_compute_achievement_rate_normal():
    summary = NutritionSummary(calories=800, protein=40, carbs=100, fat=20)
    targets = NutritionTargets(calories=1000, protein=50, carbs=100, fat=25)
    rates = compute_achievement_rate(summary, targets)
    # 比例 = summary / targets
    assert pytest.approx(rates.calories, rel=1e-3) == 0.8
    assert pytest.approx(rates.protein, rel=1e-3) == 0.8
    assert pytest.approx(rates.carbs, rel=1e-3) == 1.0
    assert pytest.approx(rates.fat, rel=1e-3) == 0.8

def test_compute_achievement_rate_overflow_and_zero_div():
    # 超额是否 cap 在 1
    summary = NutritionSummary(calories=1200, protein=60, carbs=150, fat=30)
    targets = NutritionTargets(calories=1000, protein=50, carbs=100, fat=25)
    rates = compute_achievement_rate(summary, targets)
    assert rates.calories <= 1.0
    assert rates.protein <= 1.0

    # 分母为 0 的情况
    zero_targets = NutritionTargets(calories=0, protein=0, carbs=0, fat=0)
    rates_zero = compute_achievement_rate(summary, zero_targets)
    # 按你实现可返回 0 或者 None，下面示例假设返回 0
    assert rates_zero.calories == 0
    assert rates_zero.protein == 0
    assert rates_zero.carbs == 0
    assert rates_zero.fat == 0


# —— 3. generate_ranking —— #

def make_user(name, rate):
    return UserData(user_id=1, full_name=name, achievement_rate=rate)

def test_generate_ranking_order():
    users = [
        make_user("Alice", 0.5),
        make_user("Bob",   0.8),
        make_user("Cathy", 0.3),
    ]
    ranked = generate_ranking(users, period="daily")
    # 排名应该按 achievement_rate 降序
    rates = [e.achievement_rate for e in ranked]
    assert rates == [0.8, 0.5, 0.3]
    # 检查返回的 RankEntry 类型
    assert all(isinstance(e, RankEntry) for e in ranked)

def test_generate_ranking_ties():
    users = [
        make_user("A", 0.7),
        make_user("B", 0.7),
        make_user("C", 0.5),
    ]
    ranked = generate_ranking(users, period="weekly")
    # 前两个并列，第三位
    assert ranked[0].achievement_rate == ranked[1].achievement_rate == 0.7
    assert ranked[2].achievement_rate == 0.5


# —— 4. parse_external_food_api —— #

def test_parse_external_food_api_complete():
    resp = {
        "name": "Apple",
        "calories": 95,
        "nutrients": {"protein": 0.5, "carbs": 25, "fat": 0.3},
    }
    item = parse_external_food_api(resp)
    assert isinstance(item, FoodItem)
    assert item.name == "Apple"
    assert item.calories == 95
    assert item.protein == 0.5
    assert item.carbs == 25
    assert item.fat == 0.3

def test_parse_external_food_api_missing_fields():
    # 缺少可选字段，应该使用默认值（例如 0）
    resp = {"name": "Water", "calories": 0}
    item = parse_external_food_api(resp)
    assert item.name == "Water"
    assert item.calories == 0
    assert item.protein == 0
    assert item.carbs == 0
    assert item.fat == 0

def test_parse_external_food_api_invalid():
    # 非期望格式时抛出 ValueError
    with pytest.raises(ValueError):
        parse_external_food_api({"foo": "bar"})
