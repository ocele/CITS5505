from datetime import date, datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login_manager
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, Float, DateTime, Boolean, ForeignKey
from datetime import datetime, timezone

# Loads a user object based on the user ID stored in the session.
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Represents a registered user in the application.
class User(UserMixin, db.Model):
    __tablename__ = 'user'

    # Core user identification and credentials.
    id = db.Column(db.Integer, primary_key=True)

    first_name: Mapped[str] = mapped_column(String(64), nullable=False) # Changed length to 64, nullable=False
    last_name: Mapped[str] = mapped_column(String(64), nullable=False)  # Changed length to 64, nullable=False
    email: Mapped[str] = mapped_column(String(120), index=True, unique=True, nullable=False)
    password_hash: Mapped[str | None] = mapped_column(String(128), nullable=True) # Password hash can be initially null before set? Usually False after set.

    # Optional user dietary goals.
    target_calories = db.Column(db.Float, nullable=True, default=2000.0)
    target_protein = db.Column(db.Float, nullable=True)
    target_fat = db.Column(db.Float, nullable=True)
    target_carbs = db.Column(db.Float, nullable=True)

    # Record creation timestamp.
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Defines the one-to-many relationship between User and FoodLog.
    food_logs = db.relationship('FoodLog', backref='logger', lazy='dynamic', cascade='all, delete-orphan')

    # Defines the one-to-many relationship between User and MealType.
    meal_types = db.relationship('MealType', backref='inputter', lazy='dynamic', cascade='all, delete-orphan')

    # Sets the user's password with proper hashing.
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # Checks if the provided password matches the stored hash.
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # String representation for debugging.
    def __repr__(self):
        return f'<User {self.email}>'

# Represents a food item with its standard nutritional information.
class FoodItem(db.Model):
    __tablename__ = 'food_item'

    # Basic food item identification.
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), index=True, unique=True, nullable=False)

    calories_per_100 = db.Column(db.Float, nullable=False, server_default='0.0')
    protein_per_100 = db.Column(db.Float, nullable=False, server_default='0.0')
    fat_per_100 = db.Column(db.Float, nullable=False, server_default='0.0')
    carbs_per_100 = db.Column(db.Float, nullable=False, server_default='0.0')

    # Standard serving information for nutrient reference.
    serving_size = db.Column(db.Float, nullable=True)
    serving_unit = db.Column(db.String(20), nullable=True)

    # Optional metadata.
    category = db.Column(db.String(50), index=True, nullable=True)
    source = db.Column(db.String(50), default='manual')

    # Defines the one-to-many relationship between FoodItem and FoodLog.
    logs = db.relationship('FoodLog', backref='food_details', lazy='dynamic')

    # Sets the user who created the food item.
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', name='fk_fooditem_user_id'), nullable=False, index=True)

    # String representation for debugging.
    def __repr__(self):
        return f'<FoodItem {self.name}>'
    
    @property
    def nutrients_per_100(self):
        return {
            'calories': self.calories_per_100,
            'protein': self.protein_per_100,
            'fat': self.fat_per_100,
            'carbs': self.carbs_per_100
        }

# Represents a single food consumption entry logged by a user.
class FoodLog(db.Model):
    __tablename__ = 'food_log'

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    food_item_id = db.Column(db.Integer, db.ForeignKey('food_item.id'), nullable=False, index=True)

    log_date = db.Column(db.DateTime, index=True, default=date.today)
    meal_type = db.Column(db.String(50), index=True, nullable=False)

    quantity_consumed = db.Column(db.Float, nullable=False)
    unit_consumed = db.Column(db.String(20), nullable=False, default='serving')

    def __repr__(self):
        food_name = self.food_details.name if self.food_details else 'Unknown Food'
        user_identifier = self.logger.email if self.logger else 'Unknown User'
        date_str = self.log_date.strftime('%Y-%m-%d %H:%M') if self.log_date else 'No Date'
        return f'<FoodLog {self.quantity_consumed} {self.unit_consumed} of {food_name} for {user_identifier} at {time_str}>'

class MealType(db.Model):
    __tablename__ = 'meal_type'

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(db.ForeignKey('user.id'), nullable=False, index=True)
    type_name: Mapped[str] = mapped_column(String(128), unique=False, nullable=False)

class ShareRecord(db.Model):
    __tablename__ = 'share_records'

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content_type = db.Column(db.String(20), nullable=False)   # 'ranking' or 'calorie' or 'nutrition'
    date_range = db.Column(db.String(20), nullable=False)     # 'daily', 'weekly', 'monthly'
    timestamp = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    is_read = db.Column(db.Boolean, default=False) # 用于消息提醒系统
    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_shares')
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='received_shares')
