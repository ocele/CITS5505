from sqlalchemy import or_, and_
from app.models import User, MealType, FoodItem, FoodLog
from flask_login import current_user
from app import db

def load_mealtype_choices(form, current_user):
    admin = User.query.filter_by(email='admin@DailyBite.com').first()
    mealtypes = MealType.query.filter(
        or_(
            MealType.user_id == current_user.id,
            MealType.user_id == admin.id
        )
    ).order_by(MealType.id).all()
    form.mealType.choices = [(m.id, m.type_name) for m in mealtypes]


def search_foods(keyword, current_user):
    admin = User.query.filter_by(email='admin@DailyBite.com').first()
    return FoodItem.query.filter(
        and_(
            FoodItem.name.ilike(f"%{keyword}%"),
            or_(
                FoodItem.user_id == current_user.id,
                FoodItem.user_id == admin.id
            )
        )
    ).order_by(FoodItem.id).all()



# ✅ 获取历史食物并尝试表单预填充
def load_history_items_and_prefill(form, user, item_name=None):
    history_items = FoodItem.query.join(FoodLog).filter(
        FoodLog.user_id == user.id
    ).distinct().all()

    history_names = [item.name for item in history_items]

    if item_name:
        matched_item = next((item for item in history_items if item.name == item_name), None)
        if matched_item:
            form.food.data = matched_item.name
            form.quantity.data = matched_item.serving_size
            form.unit.data = matched_item.serving_unit
        else:
            form.unit.data = "gram"
    else:
        form.unit.data = "gram"

    return history_names


def get_food_suggestions(current_user, limit=10):
    admin = User.query.filter_by(email='admin@DailyBite.com').first()
    return FoodItem.query.filter(
        or_(
            FoodItem.user_id == current_user.id,
            FoodItem.user_id == admin.id
        )
    ).order_by(FoodItem.id).limit(limit).all()