from dataclasses import dataclass
from typing import List, Dict, Optional
from collections import defaultdict

@dataclass
class NutritionSummary:
    calories: float
    protein: float
    carbs: float
    fat: float

@dataclass
class NutritionTargets:
    calories: float
    protein: float
    carbs: float
    fat: float

@dataclass
class AchievementRates:
    calories: float
    protein: float
    carbs: float
    fat: float

@dataclass
class UserData:
    user_id: int
    full_name: str
    achievement_rate: float

@dataclass
class RankEntry:
    user_id: int
    full_name: str
    achievement_rate: float
    rank: int

@dataclass
class FoodItem:
    name: str
    calories: float
    protein: float
    carbs: float
    fat: float


def compute_achievement_rate(summary: NutritionSummary, targets: NutritionTargets) -> AchievementRates:
    def rate(val: float, tgt: float) -> float:
        if tgt <= 0:
            return 0.0
        r = val / tgt
        return min(r, 1.0)

    return AchievementRates(
        calories=rate(summary.calories, targets.calories),
        protein=rate(summary.protein, targets.protein),
        carbs=rate(summary.carbs, targets.carbs),
        fat=rate(summary.fat, targets.fat)
    )


def generate_ranking(users: List[UserData], period: Optional[str] = None) -> List[RankEntry]:
    # sort by achievement_rate descending
    sorted_users = sorted(users, key=lambda u: u.achievement_rate, reverse=True)
    ranked: List[RankEntry] = []
    last_rate = None
    last_rank = 0
    count = 0
    for u in sorted_users:
        count += 1
        if u.achievement_rate != last_rate:
            rank = count
            last_rate = u.achievement_rate
            last_rank = rank
        else:
            rank = last_rank
        ranked.append(RankEntry(
            user_id=u.user_id,
            full_name=u.full_name,
            achievement_rate=u.achievement_rate,
            rank=rank
        ))
    return ranked


def parse_external_food_api(resp: dict) -> FoodItem:
    # expected keys: name, calories, nutrients
    if not isinstance(resp, dict) or 'name' not in resp or 'calories' not in resp:
        raise ValueError("Invalid external food API response")
    name = resp.get('name')
    calories = resp.get('calories', 0)
    nutr = resp.get('nutrients', {}) or {}
    protein = nutr.get('protein', 0)
    carbs = nutr.get('carbs', 0)
    fat = nutr.get('fat', 0)
    return FoodItem(name=name, calories=calories, protein=protein, carbs=carbs, fat=fat)


def calculate_daily_calories(logs: List, items: Dict[int, object]) -> Dict:
    # logs: objects with .log_date (date), .quantity_consumed (float), .food_item_id
    # items: mapping from id to object with .calories_per_100
    result: Dict = defaultdict(float)
    for log in logs:
        item = items.get(log.food_item_id)
        if item is None:
            continue
        # calculate calories for this log
        c = (log.quantity_consumed / 100.0) * getattr(item, 'calories_per_100', 0)
        result[log.log_date] += c
    return dict(result)
