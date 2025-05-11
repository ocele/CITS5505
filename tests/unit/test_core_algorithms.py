# tests/unit/test_core_algorithms.py

import pytest
from collections import namedtuple

from app.utils import (
    compute_achievement_rate,
    generate_ranking,
    parse_external_food_api,
    calculate_daily_calories,
    NutritionSummary,
    NutritionTargets,
    AchievementRates,
    UserData,
    RankEntry,
    FoodItem,
)

# —— 1. compute_achievement_rate —— #

def test_compute_achievement_rate_normal():
    summary = NutritionSummary(calories=800, protein=40, carbs=100, fat=20)
    targets = NutritionTargets(calories=1000, protein=50, carbs=100, fat=25)
    rates: AchievementRates = compute_achievement_rate(summary, targets)

    assert pytest.approx(rates.calories, rel=1e-3) == 0.8
    assert pytest.approx(rates.protein,  rel=1e-3) == 0.8
    assert pytest.approx(rates.carbs,    rel=1e-3) == 1.0
    assert pytest.approx(rates.fat,      rel=1e-3) == 0.8

def test_compute_achievement_rate_over_and_zero():
    summary = NutritionSummary(calories=1200, protein=60, carbs=150, fat=30)
    targets = NutritionTargets(calories=1000, protein=50, carbs=100, fat=25)
    rates = compute_achievement_rate(summary, targets)
    assert rates.calories == 1.0
    assert rates.protein  == 1.0

    zero_t = NutritionTargets(calories=0, protein=0, carbs=0, fat=0)
    rates2 = compute_achievement_rate(summary, zero_t)
    assert rates2.calories == 0
    assert rates2.protein  == 0
    assert rates2.carbs    == 0
    assert rates2.fat      == 0


# —— 2. generate_ranking —— #

def make_user(name, rate):
    return UserData(user_id=1, full_name=name, achievement_rate=rate)

def test_generate_ranking_order():
    users = [make_user("Alice", 0.5), make_user("Bob", 0.8), make_user("Cathy", 0.3)]
    ranked = generate_ranking(users, period="daily")
    rates = [u.achievement_rate for u in ranked]
    assert rates == [0.8, 0.5, 0.3]
    assert all(isinstance(e, RankEntry) for e in ranked)

def test_generate_ranking_ties():
    users = [make_user("A", 0.7), make_user("B", 0.7), make_user("C", 0.5)]
    ranked = generate_ranking(users, period="weekly")
    assert ranked[0].achievement_rate == ranked[1].achievement_rate == 0.7
    assert ranked[2].achievement_rate == 0.5


# —— 3. parse_external_food_api —— #

def test_parse_external_food_api_complete():
    resp = {
        "name": "Apple",
        "calories": 95,
        "nutrients": {"protein": 0.5, "carbs": 25, "fat": 0.3},
    }
    item = parse_external_food_api(resp)
    assert isinstance(item, FoodItem)
    assert item.name     == "Apple"
    assert item.calories == 95
    assert item.protein  == 0.5
    assert item.carbs    == 25
    assert item.fat      == 0.3

def test_parse_external_food_api_missing_fields():
    resp = {"name": "Water", "calories": 0}
    item = parse_external_food_api(resp)
    assert item.name     == "Water"
    assert item.calories == 0
    assert item.protein  == 0
    assert item.carbs    == 0
    assert item.fat      == 0

def test_parse_external_food_api_invalid():
    with pytest.raises(ValueError):
        parse_external_food_api({"foo": "bar"})


# —— 4. calculate_daily_calories —— #

def test_calculate_daily_calories_simple():
    from datetime import date
    Log = namedtuple("Log", ["log_date", "quantity_consumed", "food_item_id"])
    Item = namedtuple("Item", ["calories_per_100"])
    logs = [
        Log(log_date=date(2025,5,1), quantity_consumed=200, food_item_id=1),
        Log(log_date=date(2025,5,1), quantity_consumed=100, food_item_id=2),
        Log(log_date=date(2025,5,2), quantity_consumed=50,  food_item_id=1),
    ]
    items = {
        1: Item(calories_per_100=100),  # 100kcal/100g
        2: Item(calories_per_100=200),
    }
    result = calculate_daily_calories(logs, items)
    assert result[date(2025,5,1)] == pytest.approx(200/100*100 + 100/100*200)
    assert result[date(2025,5,2)] == pytest.approx(50/100*100)
