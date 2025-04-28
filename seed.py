from app import create_app, db
from app.models import User, MealType
from app.models import FoodItem

app = create_app()
with app.app_context():
    # 1. 检查并创建 admin 用户
    admin = User.query.filter_by(email='admin@example.com').first()
    if not admin:
        admin = User(
            first_name='admin',
            last_name='admin',
            email='admin@example.com',
            target_calories=2000
        )
        admin.set_password('your_admin_password')  # 换成你想要的初始密码
        db.session.add(admin)
        db.session.commit()
        print("Admin user created.")
    else:
        print("Admin user already exists.")

    # 2. 创建默认餐次类型，绑定给 admin 用户
    mealtypes = ["breakfast", "lunch", "dinner", "supper", "snacks"]

    for name in mealtypes:
        # 检查该 admin 是否已经有这个 type_name 的 MealType
        if not MealType.query.filter_by(type_name=name, user_id=admin.id).first():
            db.session.add(MealType(type_name=name, user_id=admin.id))
    print("Seed data inserted for admin user.")

    # 3.预制20种食物
    sample_foods = [
        {'name': 'Apple',      'serving_size': 100, 'serving_unit': 'g', 'calories': 52,  'protein': 0.3, 'fat': 0.2, 'carbs': 14, 'category': 'Fruit'},
        {'name': 'Banana',     'serving_size': 100, 'serving_unit': 'g', 'calories': 89,  'protein': 1.1, 'fat': 0.3, 'carbs': 23, 'category': 'Fruit'},
        {'name': 'Egg',        'serving_size': 50,  'serving_unit': 'g', 'calories': 68,  'protein': 6.3, 'fat': 4.8, 'carbs': 0.6, 'category': 'Protein'},
        {'name': 'Milk',       'serving_size': 100, 'serving_unit': 'ml','calories': 42,  'protein': 3.4, 'fat': 1.0, 'carbs': 5,   'category': 'Dairy'},
        {'name': 'Chicken Breast','serving_size': 100,'serving_unit': 'g','calories': 165,'protein': 31,   'fat': 3.6, 'carbs': 0,  'category': 'Protein'},
        {'name': 'Broccoli',   'serving_size': 100, 'serving_unit': 'g', 'calories': 34,  'protein': 2.8, 'fat': 0.4, 'carbs': 7,  'category': 'Vegetable'},
        {'name': 'White Rice', 'serving_size': 100, 'serving_unit': 'g', 'calories': 130, 'protein': 2.7, 'fat': 0.3, 'carbs': 28, 'category': 'Grain'},
        {'name': 'Beef Steak', 'serving_size': 100, 'serving_unit': 'g', 'calories': 271, 'protein': 25,  'fat': 19,  'carbs': 0,  'category': 'Protein'},
        {'name': 'Carrot',     'serving_size': 100, 'serving_unit': 'g', 'calories': 41,  'protein': 0.9, 'fat': 0.2, 'carbs': 10, 'category': 'Vegetable'},
        {'name': 'Potato',     'serving_size': 100, 'serving_unit': 'g', 'calories': 77,  'protein': 2.0, 'fat': 0.1, 'carbs': 17, 'category': 'Vegetable'},
        {'name': 'Almond',     'serving_size': 28,  'serving_unit': 'g', 'calories': 161, 'protein': 6,   'fat': 14,  'carbs': 6,  'category': 'Nut'},
        {'name': 'Orange',     'serving_size': 100, 'serving_unit': 'g', 'calories': 47,  'protein': 0.9, 'fat': 0.1, 'carbs': 12, 'category': 'Fruit'},
        {'name': 'Cheese',     'serving_size': 28,  'serving_unit': 'g', 'calories': 113, 'protein': 7,   'fat': 9,   'carbs': 0.4,'category': 'Dairy'},
        {'name': 'Salmon',     'serving_size': 100, 'serving_unit': 'g', 'calories': 208, 'protein': 20,  'fat': 13,  'carbs': 0,  'category': 'Protein'},
        {'name': 'Tofu',       'serving_size': 100, 'serving_unit': 'g', 'calories': 76,  'protein': 8,   'fat': 4.8, 'carbs': 1.9,'category': 'Protein'},
        {'name': 'Bread',      'serving_size': 30,  'serving_unit': 'g', 'calories': 80,  'protein': 2.6, 'fat': 1,   'carbs': 15, 'category': 'Grain'},
        {'name': 'Yogurt',     'serving_size': 100, 'serving_unit': 'g', 'calories': 59,  'protein': 10,  'fat': 0.4, 'carbs': 3.6,'category': 'Dairy'},
        {'name': 'Shrimp',     'serving_size': 100, 'serving_unit': 'g', 'calories': 99,  'protein': 24,  'fat': 0.3, 'carbs': 0.2,'category': 'Protein'},
        {'name': 'Tomato',     'serving_size': 100, 'serving_unit': 'g', 'calories': 18,  'protein': 0.9, 'fat': 0.2, 'carbs': 3.9,'category': 'Vegetable'},
        {'name': 'Oats',       'serving_size': 40,  'serving_unit': 'g', 'calories': 150, 'protein': 5,   'fat': 2.5, 'carbs': 27, 'category': 'Grain'},
    ]

    for item in sample_foods:
        if not FoodItem.query.filter_by(name=item['name']).first():
            db.session.add(FoodItem(**item))
    db.session.commit()
    print("Seeded 20 food items.")

