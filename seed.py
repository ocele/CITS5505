from app import create_app, db
from app.models import User, MealType, FoodItem, FoodLog
from datetime import date, timedelta, datetime
import random

app = create_app()

with app.app_context():
    # db.drop_all()
    # db.create_all()

    admin_email = 'admin@dailybite.com'
    admin = User.query.filter_by(email=admin_email).first()
    if not admin:
        admin = User(
            first_name='admin',
            last_name='DailyBite',
            email=admin_email,
            target_calories=2000
        )
        admin.set_password('admin_DailyBite')
        db.session.add(admin)
        print("Admin user created.")
    else:
        print("Admin user already exists.")

    users_data = [
        {'first_name': 'Veronica', 'last_name': 'DailyBite', 'email': 'Veronica@DailyBite.com', 'password': 'DailyBite', 'target_calories': 1800},
        {'first_name': 'Zoe',      'last_name': 'DailyBite', 'email': 'zoe@DailyBite.com',      'password': 'DailyBite', 'target_calories': 1650},
        {'first_name': 'Haoran',   'last_name': 'DailyBite', 'email': 'haoran@DailyBite.com',   'password': 'DailyBite', 'target_calories': 2200},
        {'first_name': 'William',  'last_name': 'DailyBite', 'email': 'william@DailyBite.com',  'password': 'DailyBite', 'target_calories': 2000},
    ]
    created_user_objects = []
    for u_data in users_data:
        normalized_email = u_data['email'].strip().lower()
        user = User.query.filter_by(email=normalized_email).first()

        if not user:
            user = User(
                first_name=u_data['first_name'],
                last_name=u_data['last_name'],
                email=normalized_email,
                target_calories=u_data.get('target_calories', 2000)
            )
            user.set_password(u_data['password'])
            db.session.add(user)
            print(f"User {u_data['email']} created.")
        else:
            if user.target_calories is None:
                user.target_calories = u_data.get('target_calories', 2000)
                db.session.add(user)
                print(f"Updated target calories for existing user {u_data['email']}.")
        created_user_objects.append(user)

    try:
        db.session.commit()
        print("Seeded/Updated users.")
        default_meal_type_names = ["Breakfast", "Lunch", "Dinner", "Snacks"]
        for mt_name in default_meal_type_names:
            exists = MealType.query.filter_by(user_id=admin.id, type_name=mt_name).first()
            if not exists:
                mt = MealType(user_id=admin.id, type_name=mt_name)
                db.session.add(mt)
                print(f"Default meal type '{mt_name}' created for admin.")
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error seeding/updating users: {e}")

    for name in default_meal_type_names:
        existing_system_type = MealType.query.filter_by(type_name=name, user_id=None).first()
        if not existing_system_type:
            db.session.add(MealType(type_name=name, user_id=None))
    try:
        db.session.commit()
        print("Seeded default meal types.")
    except Exception as e:
        db.session.rollback()
        print(f"Error seeding default meal types: {e}")


    admin_user_for_food = User.query.filter_by(email=admin_email).first()
    admin_id_for_food = admin_user_for_food.id if admin_user_for_food else None

    sample_foods_data = [
        {'name': 'Apple',      'calories_per_100': 52,  'protein_per_100': 0.3, 'fat_per_100': 0.2, 'carbs_per_100': 14, 'category': 'Fruit', 'serving_size': 100, 'serving_unit': 'g', 'user_id': admin_id_for_food},
        {'name': 'Banana',     'calories_per_100': 89,  'protein_per_100': 1.1, 'fat_per_100': 0.3, 'carbs_per_100': 23, 'category': 'Fruit', 'serving_size': 100, 'serving_unit': 'g', 'user_id': admin_id_for_food},
        {'name': 'Egg',        'calories_per_100': 155, 'protein_per_100': 13,  'fat_per_100': 11,  'carbs_per_100': 1.1,'category': 'Protein','serving_size': 50,  'serving_unit': 'g', 'user_id': admin_id_for_food},
        {'name': 'Milk',       'calories_per_100': 42,  'protein_per_100': 3.4, 'fat_per_100': 1.0, 'carbs_per_100': 5,  'category': 'Dairy', 'serving_size': 100, 'serving_unit': 'ml','user_id': admin_id_for_food},
        {'name': 'Chicken Breast','calories_per_100': 165,'protein_per_100': 31,  'fat_per_100': 3.6, 'carbs_per_100': 0,  'category': 'Protein', 'serving_size': 100,'serving_unit': 'g','user_id': admin_id_for_food},
        {'name': 'White Rice', 'calories_per_100': 130, 'protein_per_100': 2.7, 'fat_per_100': 0.3, 'carbs_per_100': 28, 'category': 'Grain', 'serving_size': 100, 'serving_unit': 'g', 'user_id': admin_id_for_food},
    ]
    available_food_items = []
    for item_data in sample_foods_data:
        food_item = FoodItem.query.filter_by(name=item_data['name']).first()
        if not food_item:
            food_item = FoodItem(**item_data)
            db.session.add(food_item)
            print(f"Added food item: {item_data['name']}")
        available_food_items.append(food_item)
    try:
        db.session.commit()
        print("Seeded food items.")
        available_food_items = FoodItem.query.filter(FoodItem.name.in_([f['name'] for f in sample_foods_data])).all()
    except Exception as e:
        db.session.rollback()
        print(f"Error seeding food items: {e}")

    print("Seeding FoodLog data for users...")
    if not available_food_items:
        print("No food items available to create logs. Skipping FoodLog seeding.")
    else:
        LEADERBOARD_LOWER_BOUND_FACTOR = 0.90
        LEADERBOARD_UPPER_BOUND_FACTOR = 1.10

        users_to_seed_logs_for = User.query.filter(User.email != admin_email).all()

        for user_obj in users_to_seed_logs_for:
            print(f"Seeding logs for user: {user_obj.first_name} {user_obj.last_name} (Target: {user_obj.target_calories} kcal)")
            if not user_obj.target_calories or user_obj.target_calories <=0:
                print(f"  Skipping user {user_obj.email}, no valid target calories.")
                continue

            target_kcal = user_obj.target_calories
            days_to_make_goal_met = random.sample(range(7), random.randint(2, 5))

            for i in range(7):
                today = date.today()
                log_day = today - timedelta(days=i)
                daily_total_kcal = 0.0

                try_to_meet_goal_today = i in days_to_make_goal_met

                if random.random() < 0.8:
                    food1 = random.choice(available_food_items)
                    qty1 = random.randint(50, 150) if food1.serving_unit == 'g' else random.randint(1,2) * (food1.serving_size or 50)
                    kcal1 = (qty1 / (food1.serving_size or 100.0)) * (food1.calories_per_100 or 0) 
                    db.session.add(FoodLog(user_id=user_obj.id, food_item_id=food1.id, meal_type='Breakfast', quantity_consumed=qty1, unit_consumed=food1.serving_unit or 'g', log_date=datetime.combine(log_day, datetime.min.time().replace(hour=8))))
                    daily_total_kcal += kcal1

                # 午餐
                if random.random() < 0.9:
                    food2 = random.choice(available_food_items)
                    qty2 = random.randint(100, 300) if food2.serving_unit == 'g' else random.randint(1,2) * (food2.serving_size or 100)
                    kcal2 = (qty2 / (food2.serving_size or 100.0)) * (food2.calories_per_100 or 0)
                    db.session.add(FoodLog(user_id=user_obj.id, food_item_id=food2.id, meal_type='Lunch', quantity_consumed=qty2, unit_consumed=food2.serving_unit or 'g', log_date=datetime.combine(log_day, datetime.min.time().replace(hour=13))))
                    daily_total_kcal += kcal2

                if try_to_meet_goal_today:
                    target_today_kcal = random.uniform(target_kcal * LEADERBOARD_LOWER_BOUND_FACTOR, target_kcal * LEADERBOARD_UPPER_BOUND_FACTOR)
                    remaining_kcal_needed = target_today_kcal - daily_total_kcal
                    print(f"  Day {log_day.isoformat()} - Trying to meet goal. Target for today: {target_today_kcal:.1f}, Remaining needed: {remaining_kcal_needed:.1f}")

                    if remaining_kcal_needed > 50 and len(available_food_items) > 0:
                        food_for_dinner = random.choice(available_food_items)
                        if food_for_dinner.calories_per_100 and food_for_dinner.calories_per_100 > 0:
                            qty_needed_g = (remaining_kcal_needed / food_for_dinner.calories_per_100) * 100.0
                            if qty_needed_g > 10:
                                db.session.add(FoodLog(user_id=user_obj.id, food_item_id=food_for_dinner.id, meal_type='Dinner', quantity_consumed=round(qty_needed_g,1), unit_consumed='g', log_date=datetime.combine(log_day, datetime.min.time().replace(hour=19))))
                                daily_total_kcal += (round(qty_needed_g,1)/100.0) * (food_for_dinner.calories_per_100 or 0)
                else:
                    if random.random() < 0.7:
                        food3 = random.choice(available_food_items)
                        qty3 = random.randint(50, 200) if food3.serving_unit == 'g' else random.randint(1,2) * (food3.serving_size or 100)
                        kcal3 = (qty3 / (food3.serving_size or 100.0)) * (food3.calories_per_100 or 0)
                        db.session.add(FoodLog(user_id=user_obj.id, food_item_id=food3.id, meal_type=random.choice(['Dinner', 'Snacks']), quantity_consumed=qty3, unit_consumed=food3.serving_unit or 'g', log_date=datetime.combine(log_day, datetime.min.time().replace(hour=random.randint(17,21)))))
                        daily_total_kcal += kcal3

                print(f"  Day {log_day.isoformat()}: User {user_obj.first_name} consumed {daily_total_kcal:.1f} kcal")
        try:
            db.session.commit()
            print("Seeded FoodLog data for users.")
        except Exception as e:
            db.session.rollback()
            print(f"Error seeding FoodLog data for users: {e}")
            import traceback
            traceback.print_exc() 