from app import create_app, db
from app.models import User, MealType
from app.models import FoodItem

app = create_app()
with app.app_context():
    # 清空旧数据
    db.drop_all()
    db.create_all()

    # 1. 检查并创建 admin 用户
    admin = User.query.filter_by(email='admin@DailyBite.com').first()
    if not admin:
        admin = User(
            first_name='admin',
            last_name='DailyBite',
            email='admin@DailyBite.com',
            target_calories=2000
        )
        admin.set_password('admin_DailyBite')  # 初始密码
        db.session.add(admin)
        db.session.commit()
        print("Admin user created.")
    else:
        print("Admin user already exists.")

    # 添加用户
    users = [
        {'first_name': 'Veronica',   'last_name': 'DailyBite',    'email': 'Veronica@DailyBite.com',   'password': 'DailyBite'},
        {'first_name': 'Zoe',     'last_name': 'DailyBite',  'email': 'zoe@DailyBite.com',     'password': 'DailyBite'},
        {'first_name': 'Haoran', 'last_name': 'DailyBite',  'email': 'haoran@DailyBite.com', 'password': 'DailyBite'},
        {'first_name': 'William', 'last_name': 'DailyBite',  'email': 'william@DailyBite.com', 'password': 'DailyBite'},

    ]
    for u in users:
        if not User.query.filter_by(email=u['email']).first():
            user = User(
                first_name=u['first_name'],
                last_name=u['last_name'],
                email=u['email'],
            )
            user.set_password(u['password'])
            db.session.add(user)
    db.session.commit()

    print("Seeded initial users.")

default_meal_type_names = ["Breakfast", "Lunch", "Dinner", "Snacks"]

for name in default_meal_type_names:
    existing_system_type = MealType.query.filter_by(type_name=name, user_id=None).first()
    if not existing_system_type:
        db.session.add(MealType(type_name=name, user_id=None))
        print(f"Added system default meal type: {name}")
    else:
        print(f"System default meal type '{name}' already exists.")
try:
    db.session.commit()
    print("Seed data for meal types committed.")
except Exception as e:
    db.session.rollback()
    print(f"Error committing meal type seed data: {e}")

    # 3.预制20种食物
    sample_foods = [
        {'name': 'Apple',      'serving_size': 100, 'serving_unit': 'g', 'calories_per_100': 52,  'protein_per_100': 0.3, 'fat_per_100': 0.2, 'carbs_per_100': 14, 'category': 'Fruit', 'user_id': admin.id},
        {'name': 'Banana',     'serving_size': 100, 'serving_unit': 'g', 'calories_per_100': 89,  'protein_per_100': 1.1, 'fat_per_100': 0.3, 'carbs_per_100': 23, 'category': 'Fruit', 'user_id': admin.id},
        {'name': 'Egg',        'serving_size': 50,  'serving_unit': 'g', 'calories_per_100': 68,  'protein_per_100': 6.3, 'fat_per_100': 4.8, 'carbs_per_100': 0.6, 'category': 'Protein', 'user_id': admin.id},
        {'name': 'Milk',       'serving_size': 100, 'serving_unit': 'ml','calories_per_100': 42,  'protein_per_100': 3.4, 'fat_per_100': 1.0, 'carbs_per_100': 5,   'category': 'Dairy', 'user_id': admin.id},
        {'name': 'Chicken Breast','serving_size': 100,'serving_unit': 'g','calories_per_100': 165,'protein_per_100': 31,  'fat_per_100': 3.6, 'carbs_per_100': 0,  'category': 'Protein', 'user_id': admin.id},
        {'name': 'Broccoli',   'serving_size': 100, 'serving_unit': 'g', 'calories_per_100': 34,  'protein_per_100': 2.8, 'fat_per_100': 0.4, 'carbs_per_100': 7,  'category': 'Vegetable', 'user_id': admin.id},
        {'name': 'White Rice', 'serving_size': 100, 'serving_unit': 'g', 'calories_per_100': 130, 'protein_per_100': 2.7, 'fat_per_100': 0.3, 'carbs_per_100': 28, 'category': 'Grain', 'user_id': admin.id},
        {'name': 'Beef Steak', 'serving_size': 100, 'serving_unit': 'g', 'calories_per_100': 271, 'protein_per_100': 25,  'fat_per_100': 19,  'carbs_per_100': 0,  'category': 'Protein', 'user_id': admin.id},
        {'name': 'Carrot',     'serving_size': 100, 'serving_unit': 'g', 'calories_per_100': 41,  'protein_per_100': 0.9, 'fat_per_100': 0.2, 'carbs_per_100': 10, 'category': 'Vegetable', 'user_id': admin.id},
        {'name': 'Potato',     'serving_size': 100, 'serving_unit': 'g', 'calories_per_100': 77,  'protein_per_100': 2.0, 'fat_per_100': 0.1, 'carbs_per_100': 17, 'category': 'Vegetable', 'user_id': admin.id},
        {'name': 'Almond',     'serving_size': 28,  'serving_unit': 'g', 'calories_per_100': 161, 'protein_per_100': 6,   'fat_per_100': 14,  'carbs_per_100': 6,  'category': 'Nut', 'user_id': admin.id},
        {'name': 'Orange',     'serving_size': 100, 'serving_unit': 'g', 'calories_per_100': 47,  'protein_per_100': 0.9, 'fat_per_100': 0.1, 'carbs_per_100': 12, 'category': 'Fruit', 'user_id': admin.id},
        {'name': 'Cheese',     'serving_size': 28,  'serving_unit': 'g', 'calories_per_100': 113, 'protein_per_100': 7,   'fat_per_100': 9,   'carbs_per_100': 0.4,'category': 'Dairy', 'user_id': admin.id},
        {'name': 'Salmon',     'serving_size': 100, 'serving_unit': 'g', 'calories_per_100': 208, 'protein_per_100': 20,  'fat_per_100': 13,  'carbs_per_100': 0,  'category': 'Protein', 'user_id': admin.id},
        {'name': 'Tofu',       'serving_size': 100, 'serving_unit': 'g', 'calories_per_100': 76,  'protein_per_100': 8,   'fat_per_100': 4.8, 'carbs_per_100': 1.9,'category': 'Protein', 'user_id': admin.id},
        {'name': 'Bread',      'serving_size': 30,  'serving_unit': 'g', 'calories_per_100': 80,  'protein_per_100': 2.6, 'fat_per_100': 1,   'carbs_per_100': 15, 'category': 'Grain', 'user_id': admin.id},
        {'name': 'Yogurt',     'serving_size': 100, 'serving_unit': 'g', 'calories_per_100': 59,  'protein_per_100': 10,  'fat_per_100': 0.4, 'carbs_per_100': 3.6,'category': 'Dairy', 'user_id': admin.id},
        {'name': 'Shrimp',     'serving_size': 100, 'serving_unit': 'g', 'calories_per_100': 99,  'protein_per_100': 24,  'fat_per_100': 0.3, 'carbs_per_100': 0.2,'category': 'Protein', 'user_id': admin.id},
        {'name': 'Tomato',     'serving_size': 100, 'serving_unit': 'g', 'calories_per_100': 18,  'protein_per_100': 0.9, 'fat_per_100': 0.2, 'carbs_per_100': 3.9,'category': 'Vegetable', 'user_id': admin.id},
        {'name': 'Oats',       'serving_size': 40,  'serving_unit': 'g', 'calories_per_100': 150, 'protein_per_100': 5,   'fat_per_100': 2.5, 'carbs_per_100': 27, 'category': 'Grain', 'user_id': admin.id},
    ]


    for item in sample_foods:
        if not FoodItem.query.filter_by(name=item['name']).first():
            db.session.add(FoodItem(**item))
    
    db.session.commit()
    print("Seeded 20 food items.")

