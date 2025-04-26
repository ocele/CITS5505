from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length, NumberRange
from wtforms import StringField, PasswordField, BooleanField, SubmitField, EmailField, SelectField, SearchField, DecimalField
from app.models import User 

class LoginForm(FlaskForm):
    emailLogin = EmailField('Email', validators=[DataRequired(), Email()]) 
    passwordLogin = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField("Remember me")
    submit = SubmitField('Sign In')

class RegisterForm(FlaskForm):
    firstName = StringField('First Name', validators=[DataRequired(), Length(min=3, max=64)])
    lastName = StringField('Last Name', validators=[DataRequired(), Length(min=3, max=64)])
    # username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    emailRegister = EmailField('Email', validators=[DataRequired(), Email(), Length(max=120)]) 
    passwordRegister = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    passwordRegisterRepeat = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match.')])
    subscription = BooleanField('Subscribe for Sales & New Themes')
    submit = SubmitField('Register')

class AddMealForm(FlaskForm):
    mealType = SelectField('Meal Type', validators=[DataRequired()])
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