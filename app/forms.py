from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length, NumberRange, Optional
from wtforms import StringField, PasswordField, BooleanField, SubmitField, EmailField, SelectField, SearchField, DecimalField, FloatField, DateField,RadioField
from wtforms_sqlalchemy.fields import QuerySelectField
from flask_wtf.file import FileField, FileAllowed
from app.models import User, FoodItem, MealType
from datetime import date
from flask_login import current_user

class LoginForm(FlaskForm):
    emailLogin = EmailField('Email', validators=[DataRequired(), Email()]) 
    passwordLogin = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField("Remember me")
    submit = SubmitField('Sign In')

class RegisterForm(FlaskForm):
    firstName = StringField('First Name', validators=[DataRequired(), Length(min=3, max=64)])
    lastName = StringField('Last Name', validators=[DataRequired(), Length(min=3, max=64)])
    emailRegister = EmailField('Email', validators=[DataRequired(), Email(), Length(max=120)]) 
    passwordRegister = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    passwordRegisterRepeat = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('passwordRegister', message='Passwords must match.')])
    subscription = BooleanField('Subscribe for Sales & New Themes')
    submit = SubmitField('Register')

   

def meal_type_query():
    return MealType.query

class AddMealForm(FlaskForm):
    mealType = SelectField('Meal Type', validators=[DataRequired()])
    food = SearchField('Food', validators=[DataRequired(), Length(min=2, max=128)])
    quantity = DecimalField('Quantity', validators=[DataRequired(), NumberRange(min=0)])
    unit = StringField('Unit', validators=[DataRequired(), Length(min=1, max=32)])
    submit = SubmitField('Add Meal')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        defaultChoices = [
            ('Breakfast', 'Breakfast'), ('Lunch', 'Lunch'),
            ('Dinner', 'Dinner'), ('Snacks', 'Snacks')
        ]
        user_specific_choices = []
        if current_user and current_user.is_authenticated and hasattr(current_user, 'meal_types'):
            try:
                user_specific_choices = [(meal.type_name, meal.type_name) for meal in current_user.meal_types.all()]
            except Exception as e:
                 print(f"Error in AddMealForm __init__ accessing meal_types: {e}")
        
        final_choices_dict = {val: lbl for val, lbl in defaultChoices}
        for val, lbl in user_specific_choices:
            if val not in final_choices_dict:
                final_choices_dict[val] = lbl
        self.mealType.choices = list(final_choices_dict.items())
        if not self.mealType.choices:
             self.mealType.choices = defaultChoices
        print(f"AddMealForm __init__: mealType.choices = {self.mealType.choices}")    

class AddMealTypeForm(FlaskForm):
    typeName = StringField('Type Name', validators=[DataRequired(), Length(min=1, max = 128)])

class SetGoalForm(FlaskForm):
    goal = DecimalField('kilojoules/ Day', validators=[DataRequired(), NumberRange(min=0)])



class AddNewProductForm(FlaskForm):
    name = StringField('Product Name', validators=[DataRequired(), Length(max=100)])

    calories_per_100 = FloatField('Calories (kcal per 100g/ml)', validators=[DataRequired(message="Calories field cannot be empty."), NumberRange(min=0, message="Calories must be non-negative.")])
    protein_per_100 = FloatField('Protein (g per 100g/ml)', validators=[DataRequired(message="Protein field cannot be empty."), NumberRange(min=0, message="Protein must be non-negative.")])

    fat_per_100 = FloatField('Fat (g per 100g/ml)', validators=[Optional(), NumberRange(min=0, message="Fat must be non-negative.")])
    carbs_per_100 = FloatField('Carbohydrates (g per 100g/ml)', validators=[Optional(), NumberRange(min=0, message="Carbs must be non-negative.")]) 

    serving_size = FloatField('Common Serving Size (Optional)', validators=[Optional(), NumberRange(min=0.01, message="Serving size must be positive if provided.")])
    serving_unit = StringField('Common Serving Unit (Optional)', validators=[Optional(), Length(max=20)])
    category = StringField('Category (Optional)', validators=[Optional(), Length(max=50)])
    submit = SubmitField('Save New Product')

    # check if the food name already exists in the database
    def validate_name(self, name_field):
        existing_food = FoodItem.query.filter(FoodItem.name.ilike(name_field.data)).first() # Check for case-insensitive match
        if existing_food:
            raise ValidationError(f"Product name '{name_field.data}' already exists.")

class ShareForm(FlaskForm):
    search = StringField('Search Friend')
    content_type = RadioField('Content Type', choices=[
       ('ranking', 'My Current Ranking'),
        ('calorie', 'My Calorie Intake'),
        ('nutrition',  'My Nutrition Intake'),
    ], validators=[DataRequired()])

    date_range = RadioField('Date Range', choices=[
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly')
    ], validators=[DataRequired()])

    submit = SubmitField('Search')

class EditProfileForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=64)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=64)])
    avatar = FileField('Upload New Avatar', validators=[
        FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Images only!')
    ])
    submit = SubmitField('Save Changes')