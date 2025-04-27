from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length, NumberRange
from wtforms import StringField, PasswordField, BooleanField, SubmitField, EmailField, SelectField, SearchField, DecimalField, FloatField, DateField
from wtforms_sqlalchemy.fields import QuerySelectField
from app.models import User, FoodItem, MealType
from datetime import date

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

    # def validate_email(self, email):
    # user = User.query.filter_by(email=email.data).first()
    # if user is not None:
    #     raise ValidationError('Email address already registered.')

def meal_type_query():
    return MealType.query

class AddMealForm(FlaskForm):
    MealType = QuerySelectField('Meal Type', query_factory=meal_type_query, allow_blank=True, get_label='typeName',allow_bank=True, validators=[DataRequired()])
# class AddMealForm(FlaskForm):
#     mealType = SelectField('Meal Type', validators=[DataRequired()])
    food = SearchField('Food', validators=[DataRequired(), Length(min=2, max = 128)])
    quantity = DecimalField('Quantity', validators=[DataRequired(), NumberRange(min=0)])
    unit = StringField('unit', validators=[DataRequired(), Length(min=1, max = 32)])

class AddMealTypeForm(FlaskForm):
    typeName = StringField('Type Name', validators=[DataRequired(), Length(min=1, max = 128)])

class SetGoalForm(FlaskForm):
    goal = DecimalField('kilojoules/ Day', validators=[DataRequired(), NumberRange(min=0)])

class AddNewProductForm(FlaskForm):
    productName = StringField('Product Name', validators=[DataRequired(), Length(min=1, max = 128)])
    quantity = DecimalField('Quantity', validators=[DataRequired(), NumberRange(min=0)])
    unit = SelectField('Unit', choices=['gram', 'medium', 'cup', 'ml', 'serving'], validators=[DataRequired()])
    kilojoules = DecimalField('Kilojoules', validators=[DataRequired(), NumberRange(min=0)])